
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
    self.LeftManiPicker = ManipulatorPicker()

    self.RightPointer = PointerDevice()
    self.RightPointer.my_constructor("2.4G Presenter")

    self.LeftPointerPicked = False
    self.RightPointerPicked = False

    # 2 pickers needed

    self.always_evaluate(True)

  def my_constructor(self, SCENEGRAPH):
    self.SCENEGRAPH = SCENEGRAPH
    #self.
    # todo!

    # Picker and Updater:
    self.MainResults = ManipulatorPicker()
    self.pick_ray = avango.gua.nodes.RayNode(Name = "pick_ray")
    self.pick_ray.Transform.value = avango.gua.make_trans_mat(0.0, -1.0, 0.0) * \
                                     avango.gua.make_scale_mat(1.0, 1.0, 50.0)

    self.picker = Picker()
    self.picker.SceneGraph.value = SCENEGRAPH
    self.picker.Ray.value = self.pick_ray

    #USER
    eye.Children.value = [screen, pick_ray]


    material_updater = ManipulatorPickerResults()
    material_updater.DefaultMaterial.value = "Stone"
    material_updater.TargetMaterial.value = "Bright"
    material_updater.PickedNodes.connect_from(picker.Results)


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

    # PickResults:



class ManipulatorPicker(avango.script.Script):

  Ray        = avango.gua.SFRayNode()
  Options    = avango.SFInt()
  Mask       = avango.SFString()
  Results    = avango.gua.MFPickResult()

  def __init__(self):
    self.super(ManipulatorPicker).__init__()
    self.always_evaluate(True)

    self.Ray.value  = avango.gua.nodes.RayNode()
    self.Options.value = avango.gua.PickingOptions.PICK_ONLY_FIRST_OBJECT \
                         | avango.gua.PickingOptions.PICK_ONLY_FIRST_FACE
    self.Mask.value = ""

  def my_constructor(self, SCENEGRAPH):
    self.SCENEGRAPH = SCENEGRAPH
    
  def evaluate(self):
    results = self.SCENEGRAPH.value.ray_test(self.Ray.value,
                                             self.Options.value,
                                             self.Mask.value)
    self.Results.value = results.value


class ManipulatorPickerResults(avango.script.Script):
  PickedNodes     = avango.gua.MFPickResult()
  OldNodes        = avango.gua.MFPickResult()
  DefaultMaterial = avango.SFString()
  TargetMaterial  = avango.SFString()

  @field_has_changed(PickedNodes)
  def update(self):

    for i in range(0, len(self.OldNodes.value)):
      if isinstance(self.OldNodes.value[i].Object.value, avango.gua.GeometryNode):
        self.OldNodes.value[i].Object.value.Material.value = self.DefaultMaterial.value

    for i in range(0, len(self.PickedNodes.value)):
      if isinstance(self.PickedNodes.value[i].Object.value, avango.gua.GeometryNode):
        self.PickedNodes.value[i].Object.value.Material.value = self.TargetMaterial.value
        avango.gua.set_material_uniform("Bright", "pointer_pos",
                                        self.PickedNodes.value[i].TextureCoords.value)
        avango.gua.set_material_uniform("Bright", "color",
                                        self.PickedNodes.value[i].WorldNormal.value)

    self.OldNodes.value = self.PickedNodes.value