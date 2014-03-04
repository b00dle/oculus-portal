#!/usr/bin/python

## @file
# Contains class PowerWallUser.

# import guacamole libraries
import avango.daemon

from examples_common.GuaVE import GuaVE

# import framework libraries
from User import *
from TrackingReader import *

# import math libraries
import math

## Internal representation of a Powerwall user.
#
# Upon construction, this class appends the necessary nodes to the scenegraph, creates screens, eyes, camera, pipeline
# and initializes the headtracking.

class PowerWallUser(User):

  ## Custom constructor.
  # @param VIEWING_MANAGER Reference to the ViewingManager instance from which the user is created.
  # @param HEADTRACKING_TARGET_NAME Name of the glasses' tracking target as chosen in daemon.
  # @param WALL_USER_ID Identification number of the PowerWallUser to be created, starting from 0.
  # @param INITIAL_PLATFORM_ID Platform to append the constructed PowerWallUser to.
  # @param NO_TRACKING_MAT Matrix to be applied if no headtracking of the glasses is available.
  # @param TRANSMITTER_OFFSET The transmitter offset to be applied.
  def __init__(self, VIEWING_MANAGER, HEADTRACKING_TARGET_NAME, WALL_USER_ID, INITIAL_PLATFORM_ID, NO_TRACKING_MAT, TRANSMITTER_OFFSET, SCENEGRAPH):
    User.__init__(self, "wall")

    # variables
    ## @var id
    # Identification number of the PowerWallUser, starting from 0.
    self.id = WALL_USER_ID

    ## @var left_eye_resolution
    # The user's left eye resolution in pixels.
    self.left_eye_resolution  = avango.gua.Vec2ui(1920, 1200)

    ## @var right_eye_resolution
    # The user's right eye resolution in pixels.
    self.right_eye_resolution = avango.gua.Vec2ui(1920, 1200) 

    ## @var window_size
    # The resolution in pixels to be applied on the window.
    self.window_size          = avango.gua.Vec2ui(1920*2, 1200) 

    ## @var warp_matrices_path
    # Path of the warp matrices to be applied on the rendered image.
    self.warp_matrices_path   = "/opt/lcd-warpmatrices/"

    ## @var screen_size
    # Physical screen size of the Powerwall in meters.
    self.screen_size          = avango.gua.Vec2(3.0, 1.98)   

    ## @var screen_transform
    # Physical transformation of the screen in meters.
    self.screen_transform     = avango.gua.make_trans_mat(0.0, 1.42, 0.0)

    ## @var transmitter_offset
    # The transmitter offset to be applied.
    self.transmitter_offset   = TRANSMITTER_OFFSET

    # init viewing setup 
    ## @var head_transform
    # Scenegraph node representing the head position of the user with respect to platform.
    self.head_transform = avango.gua.nodes.TransformNode(Name = "wall_head_" + str(self.id))
    self.append_to_platform(SCENEGRAPH, INITIAL_PLATFORM_ID, self.head_transform)

    ## @var headtracking_reader
    # Instance of a child class of TrackingReader to supply translation input.
    if HEADTRACKING_TARGET_NAME == None:
      self.headtracking_reader = TrackingDefaultReader()
      self.headtracking_reader.set_no_tracking_matrix(NO_TRACKING_MAT)
    else:
      self.headtracking_reader = TrackingTargetReader()
      self.headtracking_reader.my_constructor(HEADTRACKING_TARGET_NAME)
      self.headtracking_reader.set_transmitter_offset(self.transmitter_offset)
      self.headtracking_reader.set_receiver_offset(avango.gua.make_identity_mat())
    
    # connect the tracking input to the scenegraph node
    self.head_transform.Transform.connect_from(self.headtracking_reader.sf_abs_mat)

    # create the eyes
    ## @var left_eye
    # Scenegraph node representing the user's left eye.
    self.left_eye = avango.gua.nodes.TransformNode(Name = "wall_eyeL_" + str(self.id))
    self.left_eye.Transform.value = avango.gua.make_identity_mat()
    self.head_transform.Children.value.append(self.left_eye)

    ## @var right_eye
    # Scenegraph node representing the user's right eye.
    self.right_eye = avango.gua.nodes.TransformNode(Name = "wall_eyeR_" + str(self.id))
    self.right_eye.Transform.value = avango.gua.make_identity_mat()
    self.head_transform.Children.value.append(self.right_eye)

    # create the screen
    ## @var screen
    # Scenegraph node representing the user's screen.
    self.screen = avango.gua.nodes.ScreenNode(Name = "wall_screen_" + str(self.id))
    self.screen.Width.value = self.screen_size.x
    self.screen.Height.value = self.screen_size.y
    self.screen.Transform.value = self.screen_transform
    self.append_to_platform(SCENEGRAPH, INITIAL_PLATFORM_ID, self.screen)
    SCENEGRAPH["/platform_" + str(INITIAL_PLATFORM_ID)].Children.value.append(self.screen)
    
    # create the camera
    ## @var camera
    # Camera to represent the user's viewport to be rendered.
    self.camera = avango.gua.nodes.Camera()
    self.camera.SceneGraph.value = SCENEGRAPH.Name.value
    self.camera.LeftScreen.value = self.screen.Path.value
    self.camera.RightScreen.value = self.screen.Path.value
    self.camera.LeftEye.value = self.left_eye.Path.value
    self.camera.RightEye.value = self.right_eye.Path.value
    
    self.render_mask = "!do_not_display_group && !wall_avatar_group_" + str(INITIAL_PLATFORM_ID) + " && !couple_group_" + str(INITIAL_PLATFORM_ID)

    for i in range(0, 10):
        if i != INITIAL_PLATFORM_ID:
            self.render_mask = self.render_mask + " && !platform_group_" + str(i)

    self.camera.RenderMask.value = self.render_mask

    # create the window
    ## @var window
    # Window to display the rendered image to.
    self.window = avango.gua.nodes.Window()
    self.window.Size.value                  = self.window_size
    self.window.Title.value                 = "PowerWallUser_" + str(self.id)
    self.window.LeftResolution.value        = self.left_eye_resolution
    self.window.LeftPosition.value          = avango.gua.Vec2ui(0, 0)
    self.window.RightResolution.value       = self.right_eye_resolution
    self.window.RightPosition.value         = avango.gua.Vec2ui(int(self.window_size.x * 0.5), 0)
    self.window.StereoMode.value            = avango.gua.StereoMode.SIDE_BY_SIDE
    self.window.WarpMatrixRedRight.value    = "{0}lcd_4_warp_P{1}.warp".format(self.warp_matrices_path, (self.id)*2 + 2)
    self.window.WarpMatrixGreenRight.value  = "{0}lcd_4_warp_P{1}.warp".format(self.warp_matrices_path, (self.id)*2 + 2)
    self.window.WarpMatrixBlueRight.value   = "{0}lcd_4_warp_P{1}.warp".format(self.warp_matrices_path, (self.id)*2 + 2)
    self.window.WarpMatrixRedLeft.value     = "{0}lcd_4_warp_P{1}.warp".format(self.warp_matrices_path, (self.id)*2 + 1)
    self.window.WarpMatrixGreenLeft.value   = "{0}lcd_4_warp_P{1}.warp".format(self.warp_matrices_path, (self.id)*2 + 1)
    self.window.WarpMatrixBlueLeft.value    = "{0}lcd_4_warp_P{1}.warp".format(self.warp_matrices_path, (self.id)*2 + 1)

    # Display setup on medusa
    if self.id == 0:
      self.window.Display.value = ":0.0"
    elif self.id == 1:
      self.window.Display.value = ":0.1"

    ## @var pipeline
    # Pipeline for rendering purposes.
    self.pipeline = avango.gua.nodes.Pipeline(Window = self.window, 
                                              LeftResolution = self.window_size,
                                              RightResolution = self.window_size)

    self.pipeline.BackgroundTexture.value = VIEWING_MANAGER.background_texture
    self.pipeline.Camera.value = self.camera
    self.pipeline.EnableStereo.value = True

    self.set_pipeline_values()

    # create avatar representation
    self.create_avatar_representation(SCENEGRAPH, INITIAL_PLATFORM_ID, self.headtracking_reader.sf_avatar_body_mat)

    self.set_eye_distance(0.06)

    VIEWING_MANAGER.viewer.Pipelines.value.append(self.pipeline)