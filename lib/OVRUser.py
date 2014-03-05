#!/usr/bin/python

## @file
# Contains class OVRUser and TrackingRotationCombiner.

# import guacamole libraries
import avango
import avango.gua
import avango.oculus

# import framework libraries
from User import *
from OVRRotationReader import *
from TrackingReader import *

# import math libraries
import math

## Internal representation of an Oculus Rift user.
#
# Upon construction, this class appends the necessary nodes to the scenegraph, creates screens, eyes, camera, pipeline
# and initializes the headtracking.

class OVRUser(User):

  ## @var window_size
  # The Oculus Rift's resolution in pixels to be applied on the window.
  window_size      = avango.gua.Vec2ui(1280, 800)

  ## @var screen_size
  # Physical screen size of the Oculus Rift in meters.
  screen_size      = avango.gua.Vec2(0.16, 0.1) 

  ## Custom constructor.
  # @param VIEWING_MANAGER Reference to the ViewingManager instance from which the user is created.
  # @param HEADTRACKING_TARGET_NAME Name of the Oculus Rift's tracking target as chosen in daemon.
  # @param OVR_USER_ID Identification number of the OVRUser to be created, starting from 0.
  # @param INITIAL_PLATFORM_ID Platform to append the constructed OVRUser to.
  # @param NO_TRACKING_MAT Matrix to be applied if no headtracking of the Oculus Rift is available.
  def __init__(self, VIEWING_MANAGER, HEADTRACKING_TARGET_NAME, OVR_USER_ID, INITIAL_PLATFORM_ID, NO_TRACKING_MAT, SCENEGRAPH):
    User.__init__(self, "ovr")

    # initialize the OVR framework
    avango.oculus.initOVR()

    ## @var id
    # Identification number of the OVRUser, starting from 0.
    self.id = OVR_USER_ID
    
    # create platform transform node
    ## @var head_transform
    # Scenegraph node representing the head position of the user with respect to platform.
    self.head_transform = avango.gua.nodes.TransformNode(Name = "ovr_head_" + str(self.id))

    # create screens
    ## @var left_screen
    # Scenegraph node representing the user's left screen.
    self.left_screen = avango.gua.nodes.ScreenNode(Name = "ovr_screenL_" + str(self.id))
    self.left_screen.Width.value = self.screen_size.x / 2
    self.left_screen.Height.value = self.screen_size.y
    self.left_screen.Transform.value = avango.gua.make_trans_mat(-0.04, 0.0, -0.05)

    ## @var right_screen
    # Scenegraph node representing the user's right screen.
    self.right_screen = avango.gua.nodes.ScreenNode(Name = "ovr_screenR_" + str(self.id))
    self.right_screen.Width.value = self.screen_size.x / 2
    self.right_screen.Height.value = self.screen_size.y
    self.right_screen.Transform.value = avango.gua.make_trans_mat(0.04, 0.0, -0.05)

    ## @var left_eye
    # Scenegraph node representing the user's left eye.
    self.left_eye = avango.gua.nodes.TransformNode(Name = "ovr_eyeL_" + str(self.id))

    ## @var right_eye
    # Scenegraph node representing the user's right eye.
    self.right_eye = avango.gua.nodes.TransformNode(Name = "ovr_eyeR_" + str(self.id))
    self.set_eye_distance(0.064)

    # viewing setup
    self.append_to_platform(SCENEGRAPH, INITIAL_PLATFORM_ID, self.head_transform)
    self.head_transform.Children.value.append(self.left_screen)
    self.head_transform.Children.value.append(self.right_screen)
    self.head_transform.Children.value.append(self.left_eye)
    self.head_transform.Children.value.append(self.right_eye)

    # create the camera
    ## @var camera
    # Camera to represent the user's viewport to be rendered.
    self.camera = avango.gua.nodes.Camera()
    self.camera.SceneGraph.value = SCENEGRAPH.Name.value
    self.camera.LeftScreen.value = self.left_screen.Path.value
    self.camera.RightScreen.value = self.right_screen.Path.value
    self.camera.LeftEye.value = self.left_eye.Path.value
    self.camera.RightEye.value = self.right_eye.Path.value

    self.render_mask = "!do_not_display_group && !ovr_avatar_group_" + str(INITIAL_PLATFORM_ID) + " && !couple_group_" + str(INITIAL_PLATFORM_ID)

    for i in range(0, 10):
      if i != INITIAL_PLATFORM_ID:
        self.render_mask = self.render_mask + " && !platform_group_" + str(i)

    self.camera.RenderMask.value = self.render_mask

    # create oculus node
    ## @var oculus_window
    # Window to display the rendered image to.
    self.oculus_window = avango.oculus.nodes.OculusRift()
    self.oculus_window.Title.value = "OVRUser_" + str(self.id)
    self.oculus_window.Size.value = self.window_size
    self.oculus_window.LeftResolution.value = avango.gua.Vec2ui(self.window_size.x / 2, self.window_size.y)
    self.oculus_window.RightResolution.value = avango.gua.Vec2ui(self.window_size.x / 2, self.window_size.y)

    # Combine tracking and Oculus Input
    ## @var tracking_rotation_combiner
    # Instance of TrackingRotationCombiner to determine the user's position on the platform.
    self.tracking_rotation_combiner = TrackingRotationCombiner()
    self.tracking_rotation_combiner.my_constructor(self.oculus_window.Transform, HEADTRACKING_TARGET_NAME, NO_TRACKING_MAT)
    self.head_transform.Transform.connect_from(self.tracking_rotation_combiner.sf_combined_mat)

    # create pipeline
    ## @var pipeline
    # Pipeline for rendering purposes.
    self.pipeline = avango.gua.nodes.Pipeline()
    self.pipeline.BackgroundTexture.value = VIEWING_MANAGER.background_texture
    self.pipeline.Window.value = self.oculus_window
    self.pipeline.LeftResolution.value = self.oculus_window.LeftResolution.value
    self.pipeline.RightResolution.value = self.oculus_window.RightResolution.value
    self.pipeline.EnableStereo.value = True
    self.pipeline.Camera.value = self.camera
    self.set_pipeline_values()

    # Setup User Hands
    self.left_hand_trackingreader = TrackingTargetReader()
    self.left_hand_trackingreader.my_constructor("tracking-pointer-blue")
    self.left_hand_transform = avango.gua.nodes.TransformNode(Name = "ovr_left_hand_" + str(self.id))
    self.left_hand_transform.Transform.connect_from(self.left_hand_trackingreader.sf_tracking_mat)

    self.right_hand_trackingreader = TrackingTargetReader()
    self.right_hand_trackingreader.my_constructor("tracking-pointer-green")
    self.right_hand_transform = avango.gua.nodes.TransformNode(Name = "ovr_right_hand_" + str(self.id))
    self.right_hand_transform.Transform.connect_from(self.right_hand_trackingreader.sf_tracking_mat)

    self.append_to_platform(SCENEGRAPH, INITIAL_PLATFORM_ID, self.left_hand_transform)
    self.append_to_platform(SCENEGRAPH, INITIAL_PLATFORM_ID, self.right_hand_transform)
    # create avatar representation
    self.create_avatar_representation(SCENEGRAPH, INITIAL_PLATFORM_ID, self.tracking_rotation_combiner.get_sf_avatar_body_matrix(), self.left_hand_trackingreader.sf_tracking_mat, self.right_hand_trackingreader.sf_tracking_mat)

    self.manipulator = Manipulator()
    self.manipulator.my_constructor(SCENEGRAPH, self.left_hand_transform, self.right_hand_transform)

    # add newly created pipeline to the list of all pipelines in the viewer
    VIEWING_MANAGER.viewer.Pipelines.value.append(self.pipeline)

## Helper class to combine the rotation input from an Oculus Rift with the
# translation input of a tracking system.

class TrackingRotationCombiner(avango.script.Script):

  # output field
  ## @var sf_combined_mat
  # Combination of rotation and translation input.
  sf_combined_mat = avango.gua.SFMatrix4()
  sf_combined_mat.value = avango.gua.make_identity_mat()
  
  ## Default constructor.
  def __init__(self):
    self.super(TrackingRotationCombiner).__init__()

  ## Custom constructor.
  # @param SF_OCULUS_TRANSFORM Transform field of the Oculus Rift to be used as rotation input.
  # @param HEADTRACKING_TARGET_NAME Name of the Oculus Rift's tracking target to be used as translation input.
  # @param NO_TRACKING_MAT Matrix to be used if no tracking target name was specified.
  def my_constructor(self, SF_OCULUS_TRANSFORM, HEADTRACKING_TARGET_NAME, NO_TRACKING_MAT):
    
    ## @var ovr_rotation_reader
    # Instance of OVRRotationReader to capture the Oculus Rift's rotation input.
    self.ovr_rotation_reader = OVRRotationReader()
    self.ovr_rotation_reader.my_constructor(SF_OCULUS_TRANSFORM)
    
    ## @var headtracking_reader
    # Instance of a child class of TrackingReader to supply translation input.
    if HEADTRACKING_TARGET_NAME == None:
      self.headtracking_reader = TrackingDefaultReader()
      self.headtracking_reader.set_no_tracking_matrix(NO_TRACKING_MAT)
    else:
      self.headtracking_reader = TrackingTargetReader()
      self.headtracking_reader.my_constructor(HEADTRACKING_TARGET_NAME)

    self.always_evaluate(True)

  ## Returns the avatar body matrix of the headtracking reader.
  def get_sf_avatar_body_matrix(self):
    return self.headtracking_reader.sf_avatar_body_mat
 
  ## Evaluated every frame.
  def evaluate(self):
    self.sf_combined_mat.value = avango.gua.make_trans_mat(self.headtracking_reader.sf_abs_vec.value) * self.ovr_rotation_reader.sf_abs_mat.value