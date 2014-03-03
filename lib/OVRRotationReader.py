#!/usr/bin/python

## @file
# Contains class OVRRotationReader.

# import guacamole libraries
import avango
import avango.gua
import avango.script
import avango.daemon


## As the Oculus Rift's Transform field does not fire actively when its value changed,
# this class captures the transformation value of an Oculus Rift every frame.

class OVRRotationReader(avango.script.Script):

  # output fields
  ## @var sf_abs_mat
  # The current transformation matrix of the Oculus Rift.
  sf_abs_mat = avango.gua.SFMatrix4()
  sf_abs_mat.value = avango.gua.make_identity_mat()

  ## Default constructor.
  def __init__(self):
    self.super(OVRRotationReader).__init__()

  ## Custom constructor.
  # @param SF_OCULUS_ROTATION_MATRIX The Transform field of an Oculus Rift window to capture every frame.
  def my_constructor(self, SF_OCULUS_ROTATION_MATRIX):

    ## @var SF_OCULUS_ROTATION_MATRIX
    # The Transform field of an Oculus Rift window to capture every frame.
    self.SF_OCULUS_ROTATION_MATRIX = SF_OCULUS_ROTATION_MATRIX

    self.always_evaluate(True) # define class-wide evaluation policy

  ## Evaluated every frame.
  def evaluate(self):

    # set the whole rotation matrix
    self.sf_abs_mat.value = self.SF_OCULUS_ROTATION_MATRIX.value