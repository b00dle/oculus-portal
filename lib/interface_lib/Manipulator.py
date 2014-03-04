
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


  def evaluate(self):
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










class ManipulatorPicker(avango.script.Script):
  SceneGraph = avango.gua.SFSceneGraph()
  Ray        = avango.gua.SFRayNode()
  Options    = avango.SFInt()
  Mask       = avango.SFString()
  Results    = avango.gua.MFPickResult()

  def __init__(self):
    self.super(PortalPicker).__init__()
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