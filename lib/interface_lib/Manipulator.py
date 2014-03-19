#!/usr/bin/python

## @file
# Contains classes Device, Interface and InteractivGeometry.

# import guacamole libraries
import avango
import avango.gua
import avango.script
from avango.script import field_has_changed
import avango.oculus
import avango.daemon

# import python libraries
import math

# import framework libraries
from ..Device import *
from Interface import *
from InteractivGeometry import *


## Class that makes interaction possible.
# Two PointerDevices are needed for this class.
# Choose interactiv objects with the left hand and open their menus.
# Change interface elements with the right hand to manipulate the choosen object.
class Manipulator(avango.script.Script):

  ## @var sf_righthand 
  # The absolute matrix of the righthand read from the tracking system.
  sf_righthand = avango.gua.SFMatrix4()

  ## @var sf_x_output 
  # Float output field for sliders
  sf_x_output = avango.SFFloat()

  ## @var sf_key_right_pointer 
  # Bool output field for buttons, switches and other interfaceelements
  sf_key_right_pointer = avango.SFBool()

  ## @var sf_key_left_pointer 
  # Bool output field for buttons and switches
  sf_key_left_pointer  = avango.SFBool()

  ## Default constructor.
  def __init__(self):
    self.super(Manipulator).__init__()

    self.left_picked_object = avango.gua.nodes.GeometryNode()
    self.right_picked_object = avango.gua.nodes.GeometryNode()
    self.Keyboard = KeyboardMouseDevice()

    self.LeftPointer = PointerDevice()
    self.LeftPointer.my_constructor("MOUSE USB MOUSE") #"2.4G Presenter"
    self.LeftPicker = ManipulatorPicker()
    self.LeftRay = avango.gua.nodes.RayNode(Name = "pick_ray_left")

    self.RightPointer = PointerDevice()
    self.RightPointer.my_constructor("MOSART Semi. Input Device") #MOUSE USB MOUSE 
    self.RightPicker = ManipulatorPicker()
    self.RightRay = avango.gua.nodes.RayNode(Name = "pick_ray_right")

    self.LeftPointerPicked = False
    self.RightPointerPicked = False

    self.PlaneModeFlag = False

    # Handler fuer rechten Pointer Button
    self.right_pointer_pressed = False
    self.right_pointer_one_press = False
    self.sf_key_right_pointer.connect_from(self.RightPointer.sf_key_pageup)

    self.left_pointer_pressed = False
    self.sf_key_left_pointer.connect_from(self.LeftPointer.sf_key_pageup)

    self.always_evaluate(True)

  ## Custom constructor
  # @param SCENEGRAPH Reference to the scenegraph of the currently displayed scene.
  # @param LEFTHAND Tracking matrix of the lefthand
  # @param RIGHTHAND Tracking matrix of the righthand 
  def my_constructor(self, SCENEGRAPH, LEFTHAND, RIGHTHAND):
    self.SCENEGRAPH = SCENEGRAPH
    self.LEFTHAND = LEFTHAND
    self.RIGHTHAND = RIGHTHAND

    self.sf_righthand.connect_from(self.RIGHTHAND.Transform)
    self.loader = avango.gua.nodes.GeometryLoader()
    self.initialize_left_picker()
    self.initialize_right_picker()

    self.display = avango.gua.nodes.TransformNode(Name = "display_node")
    self.display.Transform.value = avango.gua.make_rot_mat(-90,1,0,0) * avango.gua.make_scale_mat(0.25,0.25,0.25)

    self.inv_plane = self.loader.create_geometry_from_file('inv_plane', 'data/objects/plane.obj', 'Stones', avango.gua.LoaderFlags.DEFAULTS | avango.gua.LoaderFlags.MAKE_PICKABLE)
    self.inv_plane.GroupNames.value = ["inv_plane", "do_not_display_group"]
    self.inv_plane.Transform.value = avango.gua.make_rot_mat(90, 1, 0, 0) * avango.gua.make_scale_mat(1,1,20)

  ## Evaluated every frame.
  # Checks if an interactiv object got picked or if a interfaceelemen got manipulated.
  def evaluate(self):
    ##### BUTTONS #####
    # Button picked: (Button zum rotieren der LightCubes und Button zum aktivieren der Portals)
    if (len(self.RightPicker.Results.value) > 0) and self.right_pointer_pressed and\
        self.RightPointer.sf_key_pageup.value:

      picked_object = self.RightPicker.Results.value[0].Object.value

      if picked_object.has_field("Button"):
        picked_object.Button.value.sf_bool_button.value = True

      self.right_pointer_pressed = False

    #### INTERACTIVE GEOMETRY #####
    # pick button left hand
    if self.LeftPointer.sf_key_pageup.value and self.LeftPointerPicked == False and\
       self.left_pointer_pressed == True and (len(self.LeftPicker.Results.value) > 0):

      self.left_picked_object = self.LeftPicker.Results.value[0].Object.value

      if self.left_picked_object.has_field("InteractivGeometry"): 
        self.left_picked_object.InteractivGeometry.value.enable_menu(self.LEFTHAND)
      
        self.LeftPointerPicked = True
      
      self.left_pointer_pressed = False
  
    # unpick button left hand
    if self.LeftPointer.sf_key_pageup.value and self.LeftPointerPicked == True and\
       self.left_pointer_pressed == True:
      
      self.LeftPointerPicked = False
      self.left_pointer_pressed = False
      self.left_picked_object.InteractivGeometry.value.disable_menu(self.LEFTHAND)

    # Change the slider
    if self.PlaneModeFlag == True and (len(self.RightPicker.Results.value) > 0):
      if self.RightPicker.Results.value[0].Object.value.Name.value == 'inv_plane':
        self.sf_x_output.value = self.RightPicker.Results.value[0].Position.value.x
    

    # pick button right hand
    if self.RightPointer.sf_key_pageup.value and self.RightPointerPicked == False and\
        self.LeftPointerPicked == True and (len(self.RightPicker.Results.value) > 0) and self.right_pointer_one_press:

      self.right_pointer_one_press = False
      self.RightPointerPicked = True

      self.right_picked_object = self.RightPicker.Results.value[0].Object.value

      # Invisible Plane Intersect
      self.left_picked_object.InteractivGeometry.value.menu_node.Children.value.append(self.inv_plane)
      self.PlaneModeFlag = True

      self.RightPicker.Mask.value = "inv_plane"

      # Listen Test
      for element in self.left_picked_object.InteractivGeometry.value.interface_elements:
        if element.NAME == "size" and self.right_picked_object.Name.value == "slider_size":          
          element.object = self.left_picked_object
          element.sf_position_input.connect_from(self.sf_x_output)
          self.right_picked_object.Material.value = "AvatarWhite"

        elif element.NAME == "red" and self.right_picked_object.Name.value == "slider_red":
          element.object = self.left_picked_object
          element.sf_position_input.connect_from(self.sf_x_output)
          self.right_picked_object.Material.value = "AvatarRed"
          self.left_picked_object.InteractivGeometry.value.sf_color_red.connect_from(self.sf_x_output)

        elif element.NAME == "green" and self.right_picked_object.Name.value == "slider_green":
          element.object = self.left_picked_object
          element.sf_position_input.connect_from(self.sf_x_output)
          self.right_picked_object.Material.value = "AvatarGreen"
          self.left_picked_object.InteractivGeometry.value.sf_color_green.connect_from(self.sf_x_output)

        elif element.NAME == "blue" and self.right_picked_object.Name.value == "slider_blue":
          element.object = self.left_picked_object
          element.sf_position_input.connect_from(self.sf_x_output)
          self.right_picked_object.Material.value = "AvatarBlue"
          self.left_picked_object.InteractivGeometry.value.sf_color_blue.connect_from(self.sf_x_output)
          
        elif element.NAME == "enable" and self.right_picked_object.Name.value == "switch_enable":        
          if element.sf_bool_switch.value == False:
            element.switch_geometry.Transform.value = element.switch_pos_on
            element.sf_bool_switch.value = True
            element.switch_geometry.Material.value = "AvatarBlue"
            self.left_picked_object.InteractivGeometry.value.sf_switch_enable.connect_from(element.sf_bool_switch)

    # unpick button
    if self.RightPointer.sf_key_pageup.value and self.RightPointerPicked == True and self.right_pointer_one_press:
      self.RightPointerPicked = False
      self.right_pointer_one_press = False

      self.left_picked_object.InteractivGeometry.value.menu_node.Children.value.remove(self.inv_plane)
      self.RightPicker.Mask.value = "interface_element || console"

      self.disconnect_interface_fields()


  ## Called whenever sf_key_left_pointer changes.
  @field_has_changed(sf_key_left_pointer)
  def key_left_handler(self):
    if self.sf_key_left_pointer.value == False:
      self.left_pointer_pressed = True

  ## Called whenever sf_key_right_pointer changes.
  @field_has_changed(sf_key_right_pointer)
  def key_right_handler_buttons(self):
    self.right_pointer_pressed = True
    if self.sf_key_right_pointer.value == False:
      self.right_pointer_one_press = True


  ## Called when we close the interface.
  def disconnect_interface_fields(self):
    for element in self.left_picked_object.InteractivGeometry.value.interface_elements:
      if element.NAME == "size" and self.right_picked_object.Name.value == "slider_size":
        element.sf_position_input.disconnect_from(self.sf_x_output)
        self.right_picked_object.Material.value = "Stone"

      elif element.NAME == "red" and self.right_picked_object.Name.value == "slider_red":
        element.sf_position_input.disconnect_from(self.sf_x_output)
        self.left_picked_object.InteractivGeometry.value.sf_color_red.disconnect_from(self.sf_x_output)
        self.right_picked_object.Material.value = "Stone"

      elif element.NAME == "green" and self.right_picked_object.Name.value == "slider_green":
        element.sf_position_input.disconnect_from(self.sf_x_output)
        self.left_picked_object.InteractivGeometry.value.sf_color_green.disconnect_from(self.sf_x_output)
        self.right_picked_object.Material.value = "Stone"

      elif element.NAME == "blue" and self.right_picked_object.Name.value == "slider_blue":
        element.sf_position_input.disconnect_from(self.sf_x_output)
        self.left_picked_object.InteractivGeometry.value.sf_color_blue.disconnect_from(self.sf_x_output)
        self.right_picked_object.Material.value = "Stone"

      elif element.NAME == "enable" and self.right_picked_object.Name.value == "switch_enable":
        if element.sf_bool_switch.value:
          element.switch_geometry.Transform.value = element.switch_pos_off
          element.sf_bool_switch.value = False
          element.switch_geometry.Material.value = "AvatarRed"    

  ## Initializes the leftpicker and its ray.
  def initialize_left_picker(self):
    self.LeftRay.Transform.value = avango.gua.make_scale_mat(1.0, 1.0, 50.0)

    ray_left_avatar = self.loader.create_geometry_from_file('ray_left',
                                                            'data/objects/cube.obj',
                                                            'Grey',
                                                            avango.gua.LoaderFlags.DEFAULTS)
    ray_left_avatar.Transform.value = avango.gua.make_trans_mat(0.0, 0.0, -2.0) *\
                                      avango.gua.make_scale_mat(0.004, 0.004, 2)
    pick_transform = avango.gua.nodes.TransformNode(Name = "pick_transform")
   

    self.LeftPicker.SceneGraph.value = self.SCENEGRAPH
    self.LeftPicker.Ray.value = self.LeftRay
    self.LeftPicker.Mask.value = "interactiv"
    pick_transform.Children.value = [self.LeftPicker.Ray.value, ray_left_avatar]
    self.LEFTHAND.Children.value.append(pick_transform)

  ## Initializes the rightpicker and its ray.
  def initialize_right_picker(self):
    self.RightRay.Transform.value = avango.gua.make_scale_mat(1.0, 1.0, 5.0)
    ray_right_avatar = self.loader.create_geometry_from_file('ray_right',
                                                              'data/objects/cube.obj',
                                                              'Grey',
                                                              avango.gua.LoaderFlags.DEFAULTS)
    ray_right_avatar.Transform.value = avango.gua.make_trans_mat(0.0, 0.0, -0.5) *\
                                       avango.gua.make_scale_mat(0.003, 0.003, 0.5)
    pick_transform = avango.gua.nodes.TransformNode(Name = "pick_transform")
    pick_transform.Children.value = [self.RightRay, ray_right_avatar]

    # set picker values
    self.RightPicker.SceneGraph.value = self.SCENEGRAPH
    self.RightPicker.Ray.value = self.RightRay
    self.RightPicker.Mask.value = "interface_element || console"

    self.RIGHTHAND.Children.value.append(pick_transform)

## Class that creates a picker
class ManipulatorPicker(avango.script.Script):
  SceneGraph = avango.gua.SFSceneGraph()
  Ray        = avango.gua.SFRayNode()
  Options    = avango.SFInt()
  Mask       = avango.SFString()
  Results    = avango.gua.MFPickResult()

  ## Default constructor.
  def __init__(self):
    self.super(ManipulatorPicker).__init__()
    self.always_evaluate(True)

    self.SceneGraph.value = avango.gua.nodes.SceneGraph()
    self.Ray.value  = avango.gua.nodes.RayNode()
    self.Options.value = avango.gua.PickingOptions.PICK_ONLY_FIRST_OBJECT \
                         | avango.gua.PickingOptions.PICK_ONLY_FIRST_FACE\
                         | avango.gua.PickingOptions.GET_POSITIONS
    self.Mask.value = ""
  
  ## Evaluated every frame.
  # Refreshes the picking results.
  def evaluate(self):
    results = self.SceneGraph.value.ray_test(self.Ray.value,
                                             self.Options.value,
                                             self.Mask.value)
    self.Results.value = results.value
