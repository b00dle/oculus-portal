
import avango
import avango.gua
import avango.script
from avango.script import field_has_changed
import avango.oculus
import avango.daemon

import math


from ..Device import *

class Manipulator(avango.script.Script):

  def __init__(self):
    self.super(Manipulator).__init__()


    self.Keyboard = KeyboardMouseDevice()

    self.LeftPointer = PointerDevice()
    self.LeftPointer.my_constructor("MOUSE USB MOUSE")
    self.LeftPicker = ManipulatorPicker()

    self.RightPointer = PointerDevice()
    self.RightPointer.my_constructor("2.4G Presenter")
    self.RightPicker = ManipulatorPicker()

    self.LeftPointerPicked = False
    self.RightPointerPicked = False

    self.left_picker_updater = MaterialUpdater()
    self.right_picker_updater = MaterialUpdater()

    self.always_evaluate(True)

  def my_constructor(self, SCENEGRAPH, LEFTHAND, RIGHTHAND):
    self.SCENEGRAPH = SCENEGRAPH
    self.LEFTHAND = LEFTHAND
    self.RIGHTHAND = RIGHTHAND

    self.initialize_left_picker()
    self.initialize_right_picker()



  # todo - wenn was gepickt wurde auf pointer klicks warten um objekt zu aktivieren und interface aufzurufen
  def evaluate(self):
    # Pointer-Buttons:
    if self.LeftPointer.sf_key_pageup.value and self.LeftPointerPicked == False:
      self.LeftPointerPicked = True
      print "hello Mani"
    if self.LeftPointer.sf_key_pagedown.value and self.LeftPointerPicked == True:
      self.LeftPointerPicked = False
      print "byebye Mani"
    if self.RightPointer.sf_key_pageup.value and self.RightPointerPicked == False:
      self.RightPointerPicked = True
      print "ON"
    if self.RightPointer.sf_key_pagedown.value and self.RightPointerPicked == True:
      self.RightPointerPicked = False
      print "OFF"




  def initialize_left_picker(self):
    print "init picker left"
    # create ray

    loader = avango.gua.nodes.GeometryLoader()
    pick_ray = avango.gua.nodes.RayNode(Name = "pick_ray_left")
    pick_ray.Transform.value = avango.gua.make_scale_mat(1.0, 1.0, 500.0)
    ray_left_avatar = loader.create_geometry_from_file('ray_left' , 'data/objects/cube.obj',
                                                    'White', avango.gua.LoaderFlags.DEFAULTS)
    ray_left_avatar.Transform.value = avango.gua.make_scale_mat(0.01, 0.01, 50)
    pick_transform = avango.gua.nodes.TransformNode(Name = "pick_transform")
    pick_transform.Children.value = [pick_ray, ray_left_avatar]

    # set picker values
    self.LeftPicker.SceneGraph.value = self.SCENEGRAPH
    self.LeftPicker.Ray.value = pick_ray
    self.LeftPicker.Mask.value = "pickable"

    self.LEFTHAND.Children.value.append(pick_transform)

    self.left_picker_updater.DefaultMaterial.value = "Stone"
    self.left_picker_updater.TargetMaterial.value = "Bright"
    self.left_picker_updater.PickedNodes.connect_from(self.LeftPicker.Results)

  def initialize_right_picker(self):
    print "init picker right"
    # create ray

    loader = avango.gua.nodes.GeometryLoader()
    pick_ray = avango.gua.nodes.RayNode(Name = "pick_ray_right")
    pick_ray.Transform.value = avango.gua.make_scale_mat(1.0, 1.0, 50.0)
    ray_right_avatar = loader.create_geometry_from_file('ray_right' , 'data/objects/cube.obj',
                                                     'Bright', avango.gua.LoaderFlags.DEFAULTS)
    ray_right_avatar.Transform.value = avango.gua.make_scale_mat(0.01, 0.01, 50)
    pick_transform = avango.gua.nodes.TransformNode(Name = "pick_transform")
    pick_transform.Children.value = [pick_ray, ray_right_avatar]

    # set picker values
    self.RightPicker.SceneGraph.value = self.SCENEGRAPH
    self.RightPicker.Ray.value = pick_ray
    self.RightPicker.Mask.value = "pickable"

    self.RIGHTHAND.Children.value.append(pick_transform)

    self.right_picker_updater.DefaultMaterial.value = "Stone"
    self.right_picker_updater.TargetMaterial.value = "Bright"
    self.right_picker_updater.PickedNodes.connect_from(self.RightPicker.Results)


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
                         | avango.gua.PickingOptions.PICK_ONLY_FIRST_FACE
    self.Mask.value = ""
    
  def evaluate(self):
    results = self.SceneGraph.value.ray_test(self.Ray.value,
                                             self.Options.value,
                                             self.Mask.value)
    self.Results.value = results.value


class MaterialUpdater(avango.script.Script):
  PickedNodes     = avango.gua.MFPickResult()
  OldNodes        = avango.gua.MFPickResult()
  DefaultMaterial = avango.SFString()
  TargetMaterial  = avango.SFString()

  @field_has_changed(PickedNodes)
  def update_materials(self):
    print "field PickedNodes has changed"
    print len(self.PickedNodes.value)
    #for i in range(0, len(self.OldNodes.value)):
    #  print "old"
    #  if isinstance(self.OldNodes.value[i].Object.value, avango.gua.GeometryNode):
    #    self.OldNodes.value[i].Object.value.Material.value = self.DefaultMaterial.value
    print len(self.OldNodes.value)
    for i in range(0, len(self.PickedNodes.value)):
      print "in"
      print self.PickedNodes.value

      if isinstance(self.PickedNodes.value[i].Object.value, avango.gua.GeometryNode):
        print "pick"
        self.PickedNodes.value[i].Object.value.Material.value = self.TargetMaterial.value
        avango.gua.set_material_uniform("Bright", "pointer_pos",
                                        self.PickedNodes.value[i].TextureCoords.value)
        avango.gua.set_material_uniform("Bright", "color",
                                        self.PickedNodes.value[i].WorldNormal.value)

    self.OldNodes.value = self.PickedNodes.value
