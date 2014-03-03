#!/usr/bin/python

## @file
# Contains class InputMapping.

# import guacamole libraries
import avango
import avango.gua
import avango.script
import avango.daemon
from avango.script import field_has_changed

# import framework libraries
from GroundFollowing import *
import Tools

# import of other libraries
import math

## This class accumulates the relative device inputs to an absolute matrix for the platform
# and uses an instance of GroundFollowing to correct this matrix with respect to gravity.

class InputMapping(avango.script.Script):

  ## @var mf_rel_input_values
  # The relative input values of the device.
  mf_rel_input_values = avango.MFFloat()
  mf_rel_input_values.value = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

  ## @var sf_station_mat
  # The absolute matrix indicating where the device is placed in space.
  sf_station_mat = avango.gua.SFMatrix4()
  sf_station_mat.value = avango.gua.make_identity_mat()

  # internal field
  ## @var sf_abs_uncorrected_mat
  # The absolute matrix to accumulate the relative inputs on. Will be corrected by GroundFollowing instance.
  sf_abs_uncorrected_mat = avango.gua.SFMatrix4()
  sf_abs_uncorrected_mat.value = avango.gua.make_identity_mat()

  # output field
  ## @var sf_abs_mat
  # The absolute matrix after GroundFollowing correction.
  sf_abs_mat = avango.gua.SFMatrix4()
  sf_abs_mat.value = avango.gua.make_identity_mat()

  # factors for input amplifying
  ## @var input_trans_factor
  # Factor to modify the translation input.
  input_trans_factor  = 1.0

  ## @var input_rot_factor
  # Factor to modify the rotation input.
  input_rot_factor    = 1.0

  ## Default constructor.
  def __init__(self):
    self.super(InputMapping).__init__()

    # attributes
    ## @var realistic
    # Boolean value to indicate if the user is navigating in 3-DOF (realistic) or 6-DOF (unrealistic) mode.
    self.realistic = True

  ## Custom constructor.
  # @param NAVIGATION The navigation instance from which this input mapping is created.
  # @param DEVICE_INSTANCE Instance of Device class to take the input values from.
  # @param GROUND_FOLLOWING_INSTANCE Instance of GroundFollowing to be used for matrix correction.
  # @param STARTING_MATRIX Initial matrix to accumulate the relative inputs on.
  def my_constructor(self, NAVIGATION, DEVICE_INSTANCE, GROUND_FOLLOWING_INSTANCE, STARTING_MATRIX):

    ## @var NAVIGATION
    # Reference to the Navigation instance from which this InputMapping is created.
    self.NAVIGATION = NAVIGATION

    ## @var GROUND_FOLLOWING_INSTANCE
    # Reference to the GroundFollowing instance used by this InputMapping.
    self.GROUND_FOLLOWING_INSTANCE = GROUND_FOLLOWING_INSTANCE

    # connect device fields
    self.mf_rel_input_values.connect_from(DEVICE_INSTANCE.mf_dof)
    self.sf_station_mat.connect_from(DEVICE_INSTANCE.sf_station_mat)

    # connect ground following fields
    GROUND_FOLLOWING_INSTANCE.sf_abs_input_mat.connect_from(self.sf_abs_uncorrected_mat)
    self.sf_abs_mat.connect_from(GROUND_FOLLOWING_INSTANCE.sf_abs_output_mat)

    # create feedback loop
    self.sf_abs_uncorrected_mat.connect_weak_from(self.sf_abs_mat)

    # set the starting position
    self.set_abs_mat(STARTING_MATRIX)

    ## @var lf_quat_angle
    # Quaternion angle of last frame to prevent blackscreen. Used if new angle is nan.
    self.lf_quat_angle = 0.0


  ## Evaluated when device input values change.
  @field_has_changed(mf_rel_input_values)
  def mf_rel_input_values_changed(self):
    
    # get translation values from input device
    _trans_vec = avango.gua.Vec3(0, 0, 0)
    _trans_vec.x = self.mf_rel_input_values.value[0]
    _trans_vec.y = self.mf_rel_input_values.value[1]
    _trans_vec.z = self.mf_rel_input_values.value[2]
    _trans_vec *= math.pow(_trans_vec.length()/math.sqrt(3), 3) * self.input_trans_factor

    # get rotation values from input device
    _rot_vec = avango.gua.Vec3(0, 0, 0)
    _rot_vec.x = self.mf_rel_input_values.value[3] * self.input_rot_factor
    _rot_vec.y = self.mf_rel_input_values.value[4] * self.input_rot_factor
    _rot_vec.z = self.mf_rel_input_values.value[5] * self.input_rot_factor

    # delete certain values that create an unrealistic movement
    if self.realistic:
      _trans_vec.y = 0.0
      _rot_vec.x = 0.0
      _rot_vec.z = 0.0

    # only accumulate inputs on absolute matrix when the device values change
    if _trans_vec.length() != 0.0 or _rot_vec.length() != 0.0:

      # global platform rotation in the world
      _platform_quat = self.sf_abs_mat.value.get_rotate()

      # Fix if quaternion angle is nan
      _quat_angle = _platform_quat.get_angle()

      if math.isnan(_quat_angle) == False:
        _platform_rot_mat = avango.gua.make_rot_mat(_quat_angle, _platform_quat.get_axis())
        self.lf_quat_angle = _quat_angle
      else:
        _platform_rot_mat = avango.gua.make_rot_mat(self.lf_quat_angle, _platform_quat.get_axis())

      # global rotation of the device in the world
      _device_forward_yaw = Tools.get_yaw(self.sf_station_mat.value)
      _device_rot_mat = avango.gua.make_rot_mat(math.degrees(_device_forward_yaw), 0, 1, 0)

      # combined platform and device rotation
      _combined_rot_mat = _platform_rot_mat * _device_rot_mat
 
      # rotation center of the device
      _rot_center = self.sf_station_mat.value.get_translate()

      # transformed translation, rotation and rotation center
      _transformed_trans_vec = self.transform_vector_with_matrix(_trans_vec, _combined_rot_mat)

      _transformed_rot_vec = self.transform_vector_with_matrix(_rot_vec, _combined_rot_mat)
      _transformed_rot_center = self.transform_vector_with_matrix(_rot_center, _platform_rot_mat)
      
      # create new transformation matrix
      _new_mat = avango.gua.make_trans_mat(_transformed_trans_vec) * \
                                             self.sf_abs_mat.value * \
                                             avango.gua.make_trans_mat(_rot_center) * \
                                             avango.gua.make_rot_mat( _rot_vec.y, 0, 1, 0) * \
                                             avango.gua.make_rot_mat( _rot_vec.x, 1, 0, 0) * \
                                             avango.gua.make_rot_mat( _rot_vec.z, 0, 0, 1) * \
                                             avango.gua.make_trans_mat(_rot_center * -1)

      # update matrix on coupled navigations
      _global_rot_center = self.sf_abs_mat.value * _rot_center
      _global_rot_center = avango.gua.Vec3(_global_rot_center.x, _global_rot_center.y, _global_rot_center.z)

      for _navigation in self.NAVIGATION.coupled_navigations:
        _navigation.inputmapping.modify_abs_uncorrected_mat(_transformed_trans_vec, _transformed_rot_vec, _global_rot_center)

    else:
      # the device values are all equal to zero
      _new_mat = self.sf_abs_mat.value

    # save the computed new matrix
    self.sf_abs_uncorrected_mat.value = _new_mat


  ## Modify the uncorrected matrix of this input mapping with specific values. Used for coupling purposes.
  # @param TRANSFORMED_TRANS_VECTOR The translation vector to be applied.
  # @param TRANSFORMED_ROT_VECTOR The vector containing the rotation values to be applied.
  # @param ROTATION_CENTER The center to rotate around.
  def modify_abs_uncorrected_mat(self, TRANSFORMED_TRANS_VECTOR, TRANSFORMED_ROT_VECTOR, ROTATION_CENTER):
    
    # compute new translation
    _new_pos = TRANSFORMED_TRANS_VECTOR + self.sf_abs_mat.value.get_translate()
    
    # compute offset to rotation center
    _rot_center_offset = ROTATION_CENTER - _new_pos

    # create new transformation matrix
    _quat = self.sf_abs_mat.value.get_rotate()

    _new_mat = avango.gua.make_trans_mat(_new_pos) * \
               avango.gua.make_trans_mat(_rot_center_offset) * \
               avango.gua.make_rot_mat( TRANSFORMED_ROT_VECTOR.y, 0, 1, 0) * \
               avango.gua.make_rot_mat( TRANSFORMED_ROT_VECTOR.x, 1, 0, 0) * \
               avango.gua.make_rot_mat( TRANSFORMED_ROT_VECTOR.z, 0, 0, 1) * \
               avango.gua.make_trans_mat(_rot_center_offset * -1) * \
               avango.gua.make_rot_mat(_quat.get_angle(), _quat.get_axis())
    
    # save the computed new matrix
    self.sf_abs_mat.value = _new_mat
  
  ## Transforms a vector using a transformation matrix.
  # @param VECTOR The vector to be transformed.
  # @param MATRIX The matrix to be applied for transformation.
  def transform_vector_with_matrix(self, VECTOR, MATRIX):
    
    _trans_vec = MATRIX * VECTOR
    return avango.gua.Vec3(_trans_vec.x, _trans_vec.y, _trans_vec.z)

  ## Set a value for sf_abs_mat.
  # @param MATRIX The matrix to be set to.
  def set_abs_mat(self, MATRIX):

    self.sf_abs_mat.value = MATRIX

  ## Sets the translation and rotation input factors.
  # @param TRANSLATION_FACTOR Translation modification factor to be set. 1.0 by default.
  # @param ROTATION_FACTOR Rotation modification factor to be set. 1.0 by default.
  def set_input_factors(self, TRANSLATION_FACTOR = 1.0, ROTATION_FACTOR = 1.0):
    self.input_trans_factor = TRANSLATION_FACTOR
    self.input_rot_factor   = ROTATION_FACTOR

  ## Activates the realistic mode (only 3 DOF navigation, GroundFollowing enabled)
  def activate_realistic_mode(self):
    self.realistic = True
    self.GROUND_FOLLOWING_INSTANCE.activate()

  ## Activates the unrealistic mode (6 DOF navigation, GroundFollowing disabled)
  def deactivate_realistic_mode(self):
    self.realistic = False
    self.GROUND_FOLLOWING_INSTANCE.deactivate()