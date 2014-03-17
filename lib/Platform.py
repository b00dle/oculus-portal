#!/usr/bin/python

## @file
# Contains class Platform.

# import guacamole libraries
import avango
import avango.gua
import avango.script
import avango.daemon
from   avango.script import field_has_changed

## Internal representation of a platform which is controlled by an input device.
#
# Users can stick themselves to a platform and explore the scene on it.

class Platform(avango.script.Script):

  # input and output field
  ## @var sf_abs_mat
  # Matrix representing the current translation and rotation of the platform in the scene.
  sf_abs_mat = avango.gua.SFMatrix4()
  sf_abs_mat.value = avango.gua.make_identity_mat()
  
  ## Default constructor.
  def __init__(self):
    self.super(Platform).__init__()

  ## Custom constructor.
  # @param SCENEGRAPH Reference to the scenegraph.
  # @param PLATFORM_SIZE Physical size of the platform in meters. Passed in an two-element list: [width, depth]
  # @param INPUT_MAPPING_INSTANCE An instance of InputMapping which accumulates the device inputs for this platform.
  # @param PLATFORM_ID The id number assigned to this platform, starting from 0.
  def my_constructor(self, SCENEGRAPH, PLATFORM_SIZE, INPUT_MAPPING_INSTANCE, PLATFORM_ID):

    ## @var INPUT_MAPPING_INSTANCE
    # Reference to an InputMapping which accumulates the device inputs for this platform.
    self.INPUT_MAPPING_INSTANCE = INPUT_MAPPING_INSTANCE

    ## @var width
    # Physical width of the platform in meters.
    self.width = PLATFORM_SIZE[0]

    ## @var depth
    # Physical depth of the platform in meters.
    self.depth = PLATFORM_SIZE[1]

    # connect to input mapping instance
    self.sf_abs_mat.connect_from(INPUT_MAPPING_INSTANCE.sf_abs_mat)

    # extend scenegraph with platform node
    ## @var platform_transform_node
    # Scenegraph node representing this platform's transformation.
    self.platform_transform_node = avango.gua.nodes.TransformNode(Name = "platform_" + str(PLATFORM_ID))
    #self.platform_transform_node.Transform.connect_from(self.sf_abs_mat)
    self.platform_transform_node.Transform.connect_from(self.INPUT_MAPPING_INSTANCE.sf_abs_mat)
    SCENEGRAPH.Root.value.Children.value.append(self.platform_transform_node)

    # create four boundary planes
    _loader = avango.gua.nodes.GeometryLoader()

    self.geometry = _loader.create_geometry_from_file('ground_geometry',
                                                      'data/objects/plane.obj',
                                                      'Stones',
                                                      avango.gua.LoaderFlags.DEFAULTS)
    self.geometry.Transform.value = avango.gua.make_trans_mat(0.0, 0.0, self.depth/2) * \
                                    avango.gua.make_scale_mat(self.width, 0.0, self.depth)

    #self.platform_transform_node.Children.value.append(self.geometry)

    sphere        = _loader.create_geometry_from_file('ground_sphere',
                                                      'data/objects/sphere.obj',
                                                      'Blue',
                                                      avango.gua.LoaderFlags.DEFAULTS)
    #self.platform_transform_node.Children.value.append(sphere)

    ## @var left_border
    # Geometry scenegraph node of the platform's left border
    self.left_border = _loader.create_geometry_from_file('left_border_geometry',
                                                         'data/objects/plane.obj',
                                                         'PlatformBorder',
                                                         avango.gua.LoaderFlags.DEFAULTS)
    self.left_border.Transform.value = avango.gua.make_trans_mat(-self.width/2, 1.0, self.depth/2) * \
                                       avango.gua.make_rot_mat(90, 1, 0, 0) * \
                                       avango.gua.make_rot_mat(270, 0, 0, 1) * \
                                       avango.gua.make_scale_mat(self.depth, 1, 2)
    self.left_border.GroupNames.value = ["do_not_display_group", "platform_group_" + str(PLATFORM_ID), "portal_display_exclude"]
    self.platform_transform_node.Children.value.append(self.left_border)
    
    ## @var right_border
    # Geometry scenegraph node of the platform's left border
    self.right_border = _loader.create_geometry_from_file('right_border_geometry',
                                                         'data/objects/plane.obj',
                                                         'PlatformBorder',
                                                         avango.gua.LoaderFlags.DEFAULTS)
    self.right_border.Transform.value = avango.gua.make_trans_mat(self.width/2, 1.0, self.depth/2) * \
                                        avango.gua.make_rot_mat(90, 1, 0, 0) * \
                                        avango.gua.make_rot_mat(90, 0, 0, 1) * \
                                        avango.gua.make_scale_mat(self.depth, 1, 2)
    self.right_border.GroupNames.value = ["do_not_display_group", "platform_group_" + str(PLATFORM_ID), "portal_display_exclude"]
    self.platform_transform_node.Children.value.append(self.right_border)

    ## @var front_border
    # Geometry scenegraph node of the platform's front border
    self.front_border = _loader.create_geometry_from_file('front_border_geometry',
                                                         'data/objects/plane.obj',
                                                         'PlatformBorder',
                                                         avango.gua.LoaderFlags.DEFAULTS)
    self.front_border.Transform.value = avango.gua.make_trans_mat(0.0, 1.0, 0.0) * \
                                        avango.gua.make_rot_mat(90, 1, 0, 0) * \
                                        avango.gua.make_scale_mat(self.width, 1, 2)
    self.front_border.GroupNames.value = ["do_not_display_group", "platform_group_" + str(PLATFORM_ID), "portal_display_exclude"]
    self.platform_transform_node.Children.value.append(self.front_border)

    ## @var back_border
    # Geometry scenegraph node of the platform's back border
    self.back_border = _loader.create_geometry_from_file('back_border_geometry',
                                                         'data/objects/plane.obj',
                                                         'PlatformBorder',
                                                         avango.gua.LoaderFlags.DEFAULTS)
    self.back_border.Transform.value = avango.gua.make_trans_mat(0.0, 1.0, self.depth) * \
                                        avango.gua.make_rot_mat(90, 1, 0, 0) * \
                                        avango.gua.make_rot_mat(180, 0, 0, 1) * \
                                        avango.gua.make_scale_mat(self.width, 1, 2)
    self.back_border.GroupNames.value = ["do_not_display_group", "platform_group_" + str(PLATFORM_ID), "portal_display_exclude"]
    self.platform_transform_node.Children.value.append(self.back_border)

    ## @var platform_id
    # The id number of this platform, starting from 0.
    self.platform_id = PLATFORM_ID      
    
  def change_scene(self, ORIGIN, DESTINATION, PIPELINE):
    self.platform_transform_node.Transform.disconnect_from(self.INPUT_MAPPING_INSTANCE.sf_abs_mat)
    self.sf_abs_mat.disconnect_from(self.INPUT_MAPPING_INSTANCE.sf_abs_mat)
    ORIGIN.Root.value.Children.value.remove(self.platform_transform_node)
    DESTINATION.Root.value.Children.value.append(self.platform_transform_node)
    
    PIPELINE.Camera.value.SceneGraph.value = DESTINATION.Name.value

    self.sf_abs_mat.connect_from(self.INPUT_MAPPING_INSTANCE.sf_abs_mat)
    self.platform_transform_node.Transform.connect_from(self.INPUT_MAPPING_INSTANCE.sf_abs_mat)

  ## Toggles visibility of left platform border.
  # @param VISIBLE A boolean value if the platform should be set visible or not.
  def display_left_border(self, VISIBLE):
    if VISIBLE:
      self.left_border.GroupNames.value[0] = "display_group"
    else:
      self.left_border.GroupNames.value[0] = "do_not_display_group"

  ## Toggles visibility of right platform border.
  # @param VISIBLE A boolean value if the platform should be set visible or not.
  def display_right_border(self, VISIBLE):
    if VISIBLE:
      self.right_border.GroupNames.value[0] = "display_group"
    else:
      self.right_border.GroupNames.value[0] = "do_not_display_group"

  ## Toggles visibility of front platform border.
  # @param VISIBLE A boolean value if the platform should be set visible or not.
  def display_front_border(self, VISIBLE):
    if VISIBLE:
      self.front_border.GroupNames.value[0] = "display_group"
    else:
      self.front_border.GroupNames.value[0] = "do_not_display_group"

  ## Toggles visibility of back platform border.
  # @param VISIBLE A boolean value if the platform should be set visible or not.
  def display_back_border(self, VISIBLE):
    if VISIBLE:
      self.back_border.GroupNames.value[0] = "display_group"
    else:
      self.back_border.GroupNames.value[0] = "do_not_display_group"