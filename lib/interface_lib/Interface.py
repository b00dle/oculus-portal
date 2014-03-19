#!/usr/bin/python

## @file
# Contains class LineCreator.

# import guacamole libraries
import avango
import avango.gua
import avango.script
from avango.script import field_has_changed
import avango.oculus

# import python libraries
import math

# import framework libraries
from ..LineCreator import *

## Class that instantiates an Switch-InterfaceElement.
class Switch(avango.script.Script):

  ## @var sf_bool_switch 
  # Bool field which represents the status of the switch. Manipulator connects to this field.
  sf_bool_switch = avango.SFBool()

  ## Default constructor.
  def __init__(self):
    self.super(Switch).__init__()

    self.NAME                 = ""
    self.SWITCH_POSITION      = avango.gua.Mat4()
    self.PARENT_NODE          = avango.gua.nodes.TransformNode()


    self.switch_geometry      = avango.gua.nodes.GeometryNode()
    self.switch_transform     = avango.gua.nodes.TransformNode()

    self.sf_bool_switch.value = False

  ## Custom constructor
  # @param NAME The name of the Switch.
  # @param SWITCH_POSITION The position of the switch in world coordinates.
  # @param PARENT_NODE The node in the scenegraph to which the switch is appended.
  def my_constructor(self, NAME, SWITCH_POSITION, PARENT_NODE):
    self.NAME = NAME
    self.SWITCH_POSITION = SWITCH_POSITION
    self.PARENT_NODE = PARENT_NODE

    self.switch_scale = avango.gua.make_scale_mat(0.2, 0.2, 0.2)
    self.loader = avango.gua.nodes.GeometryLoader()
    self.switch_geometry = self.loader.create_geometry_from_file('switch_' + NAME,
                                                                 'data/objects/sphere.obj',
                                                                 'AvatarRed',
                                                                 avango.gua.LoaderFlags.DEFAULTS |\
                                                                 avango.gua.LoaderFlags.MAKE_PICKABLE)
    self.switch_geometry.Transform.value = avango.gua.make_trans_mat(-0.3, 0.0, 0.0) * self.switch_scale
    self.switch_geometry.GroupNames.value = ["interface_element"]
    self.switch_transform = avango.gua.nodes.TransformNode(Name = 'switch_' + NAME)
    self.switch_transform.Transform.value = avango.gua.make_trans_mat(self.SWITCH_POSITION.get_translate())
    self.switch_transform.Children.value.append(self.switch_geometry)
    self.PARENT_NODE.Children.value.append(self.switch_transform)

    # Red Line
    line_begin1 = avango.gua.Vec3(self.switch_transform.Transform.value.get_translate().x - 0.5,
                                 self.switch_transform.Transform.value.get_translate().y,
                                 self.switch_transform.Transform.value.get_translate().z)

    line_end1 = avango.gua.Vec3(self.switch_transform.Transform.value.get_translate().x,
                                 self.switch_transform.Transform.value.get_translate().y,
                                 self.switch_transform.Transform.value.get_translate().z)
    create_line_visualization(self.loader,
                              self.PARENT_NODE,
                              line_begin1,
                              line_end1,
                              'AvatarBlue')


    # Blue Line
    line_begin2 = avango.gua.Vec3(self.switch_transform.Transform.value.get_translate().x,
                                 self.switch_transform.Transform.value.get_translate().y,
                                 self.switch_transform.Transform.value.get_translate().z)

    line_end2 = avango.gua.Vec3(self.switch_transform.Transform.value.get_translate().x + 0.5,
                                 self.switch_transform.Transform.value.get_translate().y,
                                 self.switch_transform.Transform.value.get_translate().z)
    create_line_visualization(self.loader, 
                              self.PARENT_NODE,
                              line_begin2,
                              line_end2,
                              'AvatarRed')

    self.switch_pos_on = avango.gua.make_trans_mat(0.3, 0.0, 0.0) * self.switch_scale

    self.switch_pos_off = avango.gua.make_trans_mat(-0.3, 0.0, 0.0) * self.switch_scale





## Class that instantiates a Button-InterfaceElement.
# This ConsoleButton looks like an arrow and has different directions.
class ConsoleButton(avango.script.Script):

  ## @var sf_bool_button 
  # Bool field which represents the status of the Consolebutton. Manipulator connects to this field.
  sf_bool_button = avango.SFBool()

  ## Default constructor.
  def __init__(self):
    self.super(ConsoleButton).__init__()
    self.always_evaluate(True)

    self.NAME                 = ""
    self.BUTTONPOS            = avango.gua.Mat4()
    self.PARENT_NODE          = avango.gua.nodes.TransformNode()
    self.button_geometry      = avango.gua.nodes.GeometryNode()
    self.button_transform     = avango.gua.nodes.TransformNode()

    self.button_scale         = avango.gua.make_scale_mat(1, 1, 1)

    self.sf_bool_button.value = False
    self.just_rotated         = False

  ## Custom constructor
  # @param NAME The name of the Button.
  # @param SWITCH_POSITION The position of the switch in world coordinates.
  # @param PARENT_NODE The node in the scenegraph to which the button is appended.
  # @param COLOR The color of the button.
  # @param DIRECTION String that defines the direction of the arrow button (left, right, up, down).
  def my_constructor(self, NAME, BUTTON_POSITION, PARENT_NODE, COLOR, DIRECTION):
    self.NAME = NAME
    self.BUTTON_POSITION = BUTTON_POSITION
    self.PARENT_NODE = PARENT_NODE

    self.loader = avango.gua.nodes.GeometryLoader()
    if (DIRECTION == "left"):
      self.button_geometry = self.loader.create_geometry_from_file('button_' + NAME,
                                                                   'data/objects/left_arrow.obj',
                                                                   COLOR,
                                                                   avango.gua.LoaderFlags.DEFAULTS |\
                                                                   avango.gua.LoaderFlags.MAKE_PICKABLE)
    elif (DIRECTION == "right"):
      self.button_geometry = self.loader.create_geometry_from_file('button_' + NAME,
                                                                   'data/objects/right_arrow.obj',
                                                                   COLOR,
                                                                   avango.gua.LoaderFlags.DEFAULTS |\
                                                                   avango.gua.LoaderFlags.MAKE_PICKABLE)
    elif (DIRECTION == "up"):
      self.button_geometry = self.loader.create_geometry_from_file('button_' + NAME,
                                                                   'data/objects/upper_arrow.obj',
                                                                   COLOR,
                                                                   avango.gua.LoaderFlags.DEFAULTS |\
                                                                   avango.gua.LoaderFlags.MAKE_PICKABLE)
    elif (DIRECTION == "down"):
      self.button_geometry = self.loader.create_geometry_from_file('button_' + NAME,
                                                                   'data/objects/lower_arrow.obj',
                                                                   COLOR,
                                                                   avango.gua.LoaderFlags.DEFAULTS |\
                                                                   avango.gua.LoaderFlags.MAKE_PICKABLE)
    
    self.button_geometry.Transform.value = self.button_scale
    self.button_geometry.GroupNames.value = ["console"]
    self.button_geometry.add_and_init_field(avango.script.SFObject(),
                                            "Button",
                                            self)

    self.button_transform = avango.gua.nodes.TransformNode(Name = 'switch_' + NAME)
    self.button_transform.Transform.value = self.BUTTON_POSITION
    self.button_transform.Children.value.append(self.button_geometry)
    self.PARENT_NODE.Children.value.append(self.button_transform)

  ## Evaluated every frame.
  # Checks if the Button got pressed.
  def evaluate(self):

    if self.sf_bool_button.value and self.just_rotated:
      self.sf_bool_button.value = False
      self.just_rotated = False
    elif self.sf_bool_button.value:
      self.sf_bool_button.value = False
    elif self.sf_bool_button.value == False:
      self.button_geometry.Transform.value = self.button_scale





## Class that instantiates a Slider-InterfaceElement.
# Provides a float value field that can be manipulated.
class Slider(avango.script.Script):

  ## @var sf_position_input 
  # Float field which represents the status of the Slider. Manipulator connects to this field.
  sf_position_input = avango.SFFloat()

  ## @var sf_float_output 
  # Float output field that provides float values. Connect interactiv geometrys to this field. 
  sf_float_output = avango.SFFloat()

  ## Default constructor.
  def __init__(self):
    self.super(Slider).__init__()
    self.always_evaluate(True)
    self.NAME = ""
    self.SLIDER_POSITION = avango.gua.Mat4()
    self.PARENT_NODE = avango.gua.nodes.TransformNode()
    self.slider_geometry = avango.gua.nodes.GeometryNode()
    self.slider_transform = avango.gua.nodes.TransformNode()
    self.slider_min = -0.5
    self.slider_max = 0.5

    self.slider_scale = avango.gua.make_scale_mat(0.2, 0.2, 0.2)
    self.transformation_at_start = avango.gua.make_identity_mat()
    self.object = avango.gua.nodes.GeometryNode()

    self.inv_plane_scale_mat = avango.gua.make_identity_mat()
    self.sf_float_output.value = 1

  ## Custom constructor
  # @param NAME The name of the SLider.
  # @param SLIDER_POSITION The position of the slider in world coordinates.
  # @param PARENT_NODE The node in the scenegraph to which the slider is appended.
  def my_constructor(self, NAME, SLIDER_POSITION, PARENT_NODE):
    self.NAME = NAME
    self.SLIDER_POSITION = SLIDER_POSITION
    self.PARENT_NODE = PARENT_NODE

    self.loader = avango.gua.nodes.GeometryLoader()
    self.slider_geometry = self.loader.create_geometry_from_file('slider_' + NAME,
                                                                 'data/objects/sphere.obj',
                                                                 'Stone',
                                                                 avango.gua.LoaderFlags.DEFAULTS |\
                                                                 avango.gua.LoaderFlags.MAKE_PICKABLE)
    self.slider_geometry.Transform.value = self.slider_scale
    self.slider_geometry.GroupNames.value = ["interface_element"]
    self.slider_transform = avango.gua.nodes.TransformNode(Name = 'slider_trans_' + NAME)
    self.slider_transform.Transform.value = avango.gua.make_trans_mat(self.SLIDER_POSITION.get_translate())
    self.slider_transform.Children.value.append(self.slider_geometry)
    self.PARENT_NODE.Children.value.append(self.slider_transform)

    line_begin = avango.gua.Vec3(self.slider_transform.Transform.value.get_translate().x - 0.5,
                                 self.slider_transform.Transform.value.get_translate().y,
                                 self.slider_transform.Transform.value.get_translate().z)

    line_end = avango.gua.Vec3(self.slider_transform.Transform.value.get_translate().x + 0.5,
                                 self.slider_transform.Transform.value.get_translate().y,
                                 self.slider_transform.Transform.value.get_translate().z)

    create_line_visualization(self.loader,
                              self.PARENT_NODE,
                              line_begin,
                              line_end,
                              'White')
  ## Called whenever sf_position_input changes.
  # Changes the output field of this class
  @field_has_changed(sf_position_input)
  def change_slider_transformation(self):

    self.slider_geometry.Transform.value = avango.gua.make_trans_mat(
                                            self.sf_position_input.value,
                                            self.slider_geometry.Transform.value.get_translate().y,
                                            self.slider_geometry.Transform.value.get_translate().z) *\
                                            self.slider_scale

    value_x = self.sf_position_input.value

    if value_x < self.slider_min:
      value_x = self.slider_min

    if value_x > self.slider_max:
      value_x = self.slider_max

    value_x = (self.sf_position_input.value + 0.5)

    self.sf_float_output.value = value_x


