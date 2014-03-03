#!/usr/bin/python

## @file
# Contains class GroundFollowing.

# import guacamole libraries
import avango
import avango.gua
import avango.script
from   avango.script import field_has_changed

# import framework libraries
from Intersection import *

# import python libraries
import math

## Class to realize a simple ground following method.
# 
# This class takes a matrix as an input and corrects it with
# respect to gravity using the scenegraph. Therefore, a ray
# is shot from a specific start height downwards and the intersection
# point is compared to the position of the device belonging to the platform.

class GroundFollowing(avango.script.Script):

  # input field
  ## @var sf_abs_input_mat
  # The input matrix to be corrected by the ground following algorithm.
  sf_abs_input_mat = avango.gua.SFMatrix4()
  sf_abs_input_mat.value = avango.gua.make_identity_mat()

  # output field
  ## @var sf_abs_output_mat
  # The corrected matrix after the ground following algorithm was applied.
  sf_abs_output_mat = avango.gua.SFMatrix4()
  sf_abs_output_mat.value = avango.gua.make_identity_mat()

  # internal fields
  ## @var sf_gf_start_mat
  # The matrix representing the position where the sent ray to the ground starts. 
  sf_gf_start_mat = avango.gua.SFMatrix4()
  sf_gf_start_mat.value = avango.gua.make_identity_mat()

  ## @var sf_station_mat
  # The matrix representing the position of the device belonging to the platform.
  sf_station_mat = avango.gua.SFMatrix4()
  sf_station_mat.value = avango.gua.make_identity_mat()

  ## @var mf_ground_pick_result
  # Intersections of the ground following ray with the objects in the scene.
  mf_ground_pick_result = avango.gua.MFPickResult()

  ## Default constructor.
  def __init__(self):
    self.super(GroundFollowing).__init__()

  ## Custom constructor.
  # @param SCENEGRAPH Reference to the scenegraph of the currently displayed scene.
  # @param SF_STATION_MAT The field containing the current position of the device belonging to the platform.
  # @param SETTINGS A list of a boolean and a floating number representing self.activated and self.ray_start_height 
  def my_constructor(self, SCENEGRAPH, SF_STATION_MAT, SETTINGS):
    
    # attributes
    ## @var activated
    # Indicates if the ground following algorithm is activated or deactivated. In the last case,
    # the input matrix is simply passed through.
    self.activated = False

    ## @var falling
    # A boolean indicating if the user is currently falling. Used for fall speed computations.
    self.falling = False

    ## @var initial_fall_velocity
    # The starting velocity when the user is falling in meters per frame. Is increased the longer the falling process goes on.
    self.initial_fall_velocity = 0.05

    ## @var scale_factor
    # Scaling factor used for the modification of up and down vectors.
    self.scale_factor = 0.1

    # fall velocity in meter per frame
    ## @var fall_velocity
    # Speed when the user is falling in meters per frame.
    self.fall_velocity = self.initial_fall_velocity

    # pick length in meter
    ## @var ground_pick_length
    # Length of the ground following ray.
    self.ground_pick_length = 100.0

    ## @var ground_pick_direction
    # Direction of the ground following ray (downwards).
    self.ground_pick_direction = avango.gua.Vec3(0.0, -1.0, 0.0)

    ## @var SCENEGRAPH
    # Reference to the scenegraph to intersect the ground following ray with.
    self.SCENEGRAPH = SCENEGRAPH

    ## @var ray_start_height
    # Starting height of the ground following ray.
    self.ray_start_height = SETTINGS[1]

    # initialize shoot and output matrices
    self.sf_abs_output_mat.value = self.sf_abs_input_mat.value

    # init field connections
    self.sf_station_mat.connect_from(SF_STATION_MAT)


    # init internal class
    ## @var ground_intersection
    # Intersection class to determine the intersections of the ground following ray with the objects in the scenegraph.
    self.ground_intersection = Intersection()
    self.ground_intersection.my_constructor(SCENEGRAPH, self.sf_gf_start_mat, self.ground_pick_length, self.ground_pick_direction)
    self.mf_ground_pick_result.connect_from(self.ground_intersection.mf_pick_result)

    # activate or deactive ground following
    if SETTINGS[0] == True:
      self.activate()
    else:
      self.deactivate()

  ## Evaluated every frame.
  def evaluate(self):
    if self.activated:
      # prepare ground following matrix
      _platform_trans_vec = self.sf_abs_input_mat.value.get_translate()
      _device_trans_vec = self.sf_station_mat.value.get_translate()

      _gf_start_pos = self.sf_abs_input_mat.value * avango.gua.Vec3(self.sf_station_mat.value.get_element(0,3), self.ray_start_height, self.sf_station_mat.value.get_element(2,3))
      self.sf_gf_start_mat.value = avango.gua.make_trans_mat(_gf_start_pos.x, _gf_start_pos.y, _gf_start_pos.z)  

      if len(self.mf_ground_pick_result.value) > 0:                    # an intersection with the ground was found

        _pick_result = self.mf_ground_pick_result.value[0]             # get first intersection target

        _distance_to_ground = _pick_result.Distance.value * self.ground_pick_length
        _difference = _distance_to_ground - self.ray_start_height
        _difference = round(_difference, 3)

        if _difference < 0:
          # climb up
          if self.falling:
            self.falling = False
            self.fall_velocity = self.initial_fall_velocity 

          _up_vec = avango.gua.Vec3(0.0, _difference * -1.0 * self.scale_factor, 0.0)
          self.sf_abs_output_mat.value = avango.gua.make_trans_mat(_up_vec) * self.sf_abs_input_mat.value

        elif _difference > 0:
          if _difference > self.ray_start_height:
            # falling
            self.falling = True
            _fall_vec = avango.gua.Vec3(0.0, -self.fall_velocity, 0.0)
            self.sf_abs_output_mat.value = avango.gua.make_trans_mat(_fall_vec) * self.sf_abs_input_mat.value
            self.fall_velocity += 0.005

          else:
            # climb down
            if self.falling:
              self.falling = False
              self.fall_velocity = self.initial_fall_velocity 

            _down_vec = avango.gua.Vec3(0.0, _difference * -1.0 * self.scale_factor, 0.0)
            self.sf_abs_output_mat.value = avango.gua.make_trans_mat(_down_vec) * self.sf_abs_input_mat.value

        else:
          self.sf_abs_output_mat.value = self.sf_abs_input_mat.value        # player remains on ground

      else:
        self.sf_abs_output_mat.value = self.sf_abs_input_mat.value          # no intersection with ground was found
  
    else:
      self.sf_abs_output_mat.value = self.sf_abs_input_mat.value            # ground following is deactivated

  ## Activates the ground following algorithm.
  def activate(self):
    self.activated = True
    self.ground_intersection.activate()

  ## Deactivates the ground following algorithm. The input matrix is just passed through after calling this method.
  def deactivate(self):
    self.activated = False
    self.ground_intersection.deactivate()