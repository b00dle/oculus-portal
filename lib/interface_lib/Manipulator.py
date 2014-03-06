
import avango
import avango.gua
import avango.script
from avango.script import field_has_changed
import avango.oculus
import avango.daemon

import math


from ..Device import *

from Interface import *
from InteractivGeometry import *

class Manipulator(avango.script.Script):
  sf_righthand = avango.gua.SFMatrix4()
  sf_XOutput = avango.SFFloat()

  def __init__(self):
    self.super(Manipulator).__init__()

    self.left_picked_object = avango.gua.nodes.GeometryNode()
    self.right_picked_object = avango.gua.nodes.GeometryNode()
    self.Keyboard = KeyboardMouseDevice()

    self.LeftPointer = PointerDevice()
    self.LeftPointer.my_constructor("2.4G Presenter")
    self.LeftPicker = ManipulatorPicker()
    self.LeftRay = avango.gua.nodes.RayNode(Name = "pick_ray_left")

    self.RightPointer = PointerDevice()
    self.RightPointer.my_constructor("MOUSE USB MOUSE")
    self.RightPicker = ManipulatorPicker()
    self.RightRay = avango.gua.nodes.RayNode(Name = "pick_ray_right")

    self.LeftPointerPicked = False
    self.RightPointerPicked = False

    self.PlaneModeFlag = False

    self.always_evaluate(True)

  def my_constructor(self, SCENEGRAPH, LEFTHAND, RIGHTHAND):
    self.SCENEGRAPH = SCENEGRAPH
    self.LEFTHAND = LEFTHAND
    self.RIGHTHAND = RIGHTHAND

    self.sf_righthand.connect_from(self.RIGHTHAND.Transform)

    self.initialize_left_picker()
    self.initialize_right_picker()
    self.loader = avango.gua.nodes.GeometryLoader()

    self.display = avango.gua.nodes.TransformNode(Name = "display_node")
    self.display.Transform.value = avango.gua.make_rot_mat(-90,1,0,0) * avango.gua.make_scale_mat(0.25,0.25,0.25)

    self.inv_plane = self.loader.create_geometry_from_file('inv_plane', 'data/objects/plane.obj', 'Stones', avango.gua.LoaderFlags.DEFAULTS | avango.gua.LoaderFlags.MAKE_PICKABLE)
    self.inv_plane.GroupNames.value = ["inv_plane", "do_not_display_group"]
    self.inv_plane.Transform.value = avango.gua.make_rot_mat(90, 1, 0, 0) * avango.gua.make_scale_mat(1,1,20)


  # todo - wenn was gepickt wurde auf pointer klicks warten um objekt zu aktivieren und interface aufzurufen
  def evaluate(self):

    # pick button left hand
    if self.LeftPointer.sf_key_pageup.value and self.LeftPointerPicked == False and\
                                                (len(self.LeftPicker.Results.value) > 0):
      self.LeftPointerPicked = True

      self.left_picked_object = self.LeftPicker.Results.value[0].Object.value
      self.left_picked_object.InteractivGeometry.value.enable_menu(self.LEFTHAND)
      
      print "picked ",self.left_picked_object.Name.value
  
    # unpick button left hand
    if self.LeftPointer.sf_key_pagedown.value and self.LeftPointerPicked == True:
      self.LeftPointerPicked = False
      
      self.left_picked_object.InteractivGeometry.value.disable_menu(self.LEFTHAND)
      
      print "closed display"


    # Change the slider
    if self.PlaneModeFlag == True and (len(self.RightPicker.Results.value) > 0):
      if self.RightPicker.Results.value[0].Object.value.Name.value == 'inv_plane':
        self.sf_XOutput.value = self.RightPicker.Results.value[0].Position.value.x

    # pick button right hand
    if self.RightPointer.sf_key_pageup.value and self.RightPointerPicked == False and\
        self.LeftPointerPicked == True and (len(self.RightPicker.Results.value) > 0):
      self.RightPointerPicked = True
      
      print "Interact with ",self.RightPicker.Results.value[0].Object.value.Name.value

      self.right_picked_object = self.RightPicker.Results.value[0].Object.value
      self.right_picked_object.Material.value = "AvatarRed"

      # Invisible Plane Intersect
      self.left_picked_object.InteractivGeometry.value.menu_node.Children.value.append(self.inv_plane)
      self.PlaneModeFlag = True


      self.RightPicker.Mask.value = "inv_plane"

      # Listen Test
      for element in self.left_picked_object.InteractivGeometry.value.interface_elements:
        
        if element.NAME == "size" and self.right_picked_object.Name.value == "slider_size":          
          element.object = self.left_picked_object
          element.sfPositionXInput.connect_from(self.sf_XOutput)

        elif element.NAME == "y_pos" and self.right_picked_object.Name.value == "slider_y_pos":
          element.object = self.left_picked_object
          element.sfPositionXInput.connect_from(self.sf_XOutput)

        elif element.NAME == "red" and self.right_picked_object.Name.value == "slider_red":
          element.object = self.left_picked_object
          element.sfPositionXInput.connect_from(self.sf_XOutput)

        elif element.NAME == "green" and self.right_picked_object.Name.value == "slider_green":
          element.object = self.left_picked_object
          element.sfPositionXInput.connect_from(self.sf_XOutput)


      '''
      # Invertierte Scale-Mat:
      inv_scale = self.inv_plane.Transform.value.get_scale()
      inv_scale = avango.gua.make_scale_mat(inv_scale)
      inv_scale = avango.gua.make_inverse_mat(inv_scale)

      self.interface2.inv_plane_scale_mat = inv_scale
      self.interface2.object = self.picked_object
      '''
        
    # unpick button
    if self.RightPointer.sf_key_pagedown.value and self.RightPointerPicked == True:
      self.RightPointerPicked = False
      self.left_picked_object.InteractivGeometry.value.menu_node.Children.value.remove(self.inv_plane)
      self.RightPicker.Mask.value = "interface_element"

      for element in self.left_picked_object.InteractivGeometry.value.interface_elements:
        if element.NAME == "size" and self.right_picked_object.Name.value == "slider_size":
          element.sfPositionXInput.disconnect_from(self.sf_XOutput)

        elif element.NAME == "y_pos" and self.right_picked_object.Name.value == "slider_y_pos":
          element.sfPositionXInput.disconnect_from(self.sf_XOutput)

        elif element.NAME == "red" and self.right_picked_object.Name.value == "slider_red":
          element.sfPositionXInput.disconnect_from(self.sf_XOutput)

        elif element.NAME == "green" and self.right_picked_object.Name.value == "slider_green":
          element.sfPositionXInput.disconnect_from(self.sf_XOutput)

      self.right_picked_object.Material.value = "Stone"

      print "OFF"
    

  def initialize_left_picker(self):
    print "init picker left"
    # create ray
    loader = avango.gua.nodes.GeometryLoader()


    self.LeftRay.Transform.value = avango.gua.make_scale_mat(1.0, 1.0, 50.0)

    ray_left_avatar = loader.create_geometry_from_file('ray_left' , 'data/objects/cube.obj',
                                                    'White', avango.gua.LoaderFlags.DEFAULTS)
    ray_left_avatar.Transform.value = avango.gua.make_trans_mat(0.0, 0.0, -20.0) *\
                                       avango.gua.make_scale_mat(0.008, 0.008, 20)
    pick_transform = avango.gua.nodes.TransformNode(Name = "pick_transform")
   

    # set picker values
    self.LeftPicker.SceneGraph.value = self.SCENEGRAPH
    self.LeftPicker.Ray.value = self.LeftRay
    self.LeftPicker.Mask.value = "interactiv"
    pick_transform.Children.value = [self.LeftPicker.Ray.value, ray_left_avatar]
    self.LEFTHAND.Children.value.append(pick_transform)


  def initialize_right_picker(self):
    print "init picker right"
    # create ray

    loader = avango.gua.nodes.GeometryLoader()
    self.RightRay.Transform.value = avango.gua.make_scale_mat(1.0, 1.0, 50.0)
    ray_right_avatar = loader.create_geometry_from_file('ray_right' , 'data/objects/cube.obj',
                                                     'Bright', avango.gua.LoaderFlags.DEFAULTS)
    ray_right_avatar.Transform.value = avango.gua.make_trans_mat(0.0, 0.0, -5.0) *\
                                       avango.gua.make_scale_mat(0.003, 0.003, 5)
    pick_transform = avango.gua.nodes.TransformNode(Name = "pick_transform")
    pick_transform.Children.value = [self.RightRay, ray_right_avatar]

    # set picker values
    self.RightPicker.SceneGraph.value = self.SCENEGRAPH
    self.RightPicker.Ray.value = self.RightRay
    self.RightPicker.Mask.value = "interface_element"

    self.RIGHTHAND.Children.value.append(pick_transform)


class ManipulatorPicker(avango.script.Script):
  SceneGraph = avango.gua.SFSceneGraph()
  Ray        = avango.gua.SFRayNode()
  Options    = avango.SFInt()
  Mask       = avango.SFString()
  Results    = avango.gua.MFPickResult()

  def __init__(self):
    self.super(ManipulatorPicker).__init__()
    self.always_evaluate(True)

    self.SceneGraph.value = avango.gua.nodes.SceneGraph()
    self.Ray.value  = avango.gua.nodes.RayNode()
    self.Options.value = avango.gua.PickingOptions.PICK_ONLY_FIRST_OBJECT \
                         | avango.gua.PickingOptions.PICK_ONLY_FIRST_FACE\
                         | avango.gua.PickingOptions.GET_POSITIONS
    self.Mask.value = ""
    
  def evaluate(self):
    results = self.SceneGraph.value.ray_test(self.Ray.value,
                                             self.Options.value,
                                             self.Mask.value)
    self.Results.value = results.value