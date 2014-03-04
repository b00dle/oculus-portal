
import avango
import avango.gua
import avango.script
from avango.script import field_has_changed
import avango.oculus
import avango.daemon

import math


from ..Device import *

from Interface import *

class Manipulator(avango.script.Script):
  SFrighthand = avango.gua.SFMatrix4()

  def __init__(self):
    self.super(Manipulator).__init__()

    self.picked_object = avango.gua.nodes.GeometryNode()
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

    #self.left_picker_updater = MaterialUpdater()
    #self.right_picker_updater = MaterialUpdater()

    self.always_evaluate(True)

  def my_constructor(self, SCENEGRAPH, LEFTHAND, RIGHTHAND):
    self.SCENEGRAPH = SCENEGRAPH
    self.LEFTHAND = LEFTHAND
    self.RIGHTHAND = RIGHTHAND

    self.initialize_left_picker()
    self.initialize_right_picker()
    self.loader = avango.gua.nodes.GeometryLoader()

    self.display = avango.gua.nodes.TransformNode(Name = "display_node")
    self.display.Transform.value = avango.gua.make_rot_mat(-90,1,0,0) * avango.gua.make_scale_mat(0.25,0.25,0.25)

    # add slider to display
    self.interface1 = Slider()
    self.interface1.my_constructor("Nr1", avango.gua.make_trans_mat(0.0, 0.0, 0.0), self.display, self.loader)
    self.interface2 = Slider()
    self.interface2.my_constructor("Nr2", avango.gua.make_trans_mat(0.0, 0.4, 0.0), self.display, self.loader)




  # todo - wenn was gepickt wurde auf pointer klicks warten um objekt zu aktivieren und interface aufzurufen
  def evaluate(self):
    self.SFrighthand.value = self.RIGHTHAND.Transform.value
    # Pointer-Buttons:

    # pick button left hand
    if self.LeftPointer.sf_key_pageup.value and self.LeftPointerPicked == False and\
                                                (len(self.LeftPicker.Results.value) > 0):
      self.LeftPointerPicked = True
      self.picked_object = self.LeftPicker.Results.value[0].Object.value
      self.LEFTHAND.Children.value.append(self.display)
      print "picked ",self.picked_object.Name.value
  
    if self.LeftPointer.sf_key_pageup.value and self.LeftPointerPicked == False:
      print "nothing picked - try to aim"
      
    # unpick button left hand
    if self.LeftPointer.sf_key_pagedown.value and self.LeftPointerPicked == True:
      self.LeftPointerPicked = False
      self.LEFTHAND.Children.value.remove(self.display)
      print "closed display"

    # pick button right hand
    if self.RightPointer.sf_key_pageup.value and self.RightPointerPicked == False and\
       self.LeftPointerPicked == True and (len(self.RightPicker.Results.value) > 0):

      self.RightPointerPicked = True
      print "Interact with ",self.RightPicker.Results.value[0].Object.value.Name.value
      self.RightPicker.Results.value[0].Object.value.Material.value = "AvatarRed"

      
      self.SFrighthand.value = self.RIGHTHAND.Transform.value
      #sffloatx_ = avango.SFFloat()
      #sffloatx_.value = self.invisible_plane_intersect()

      if (self.RightPicker.Results.value[0].Object.value.Name.value == "slider_Nr1"):
        self.interface1.sfTransformInput.connect_from(self.SFrighthand)
      if (self.RightPicker.Results.value[0].Object.value.Name.value == "slider_Nr2"):
        self.interface2.sfTransformInput.connect_from(self.SFrighthand)

    if self.RightPointer.sf_key_pagedown.value and self.RightPointerPicked == True:
      self.RightPointerPicked = False
      print "OFF"

  '''
  def invisible_plane_intersect(self):
    loader = avango.gua.nodes.GeometryLoader()
    plane = loader.create_geometry_from_file('floor', 'data/objects/plane.obj', 'Stones', avango.gua.LoaderFlags.DEFAULTS | avango.gua.LoaderFlags.MAKE_PICKABLE)
    plane.Transform.value = avango.gua.make_rot_mat(90, 1, 0, 0) * avango.gua.make_scale_mat(20,1,20)

    self.display.Children.value.append(plane)

    if (len(self.RightPicker.Results.value) > 0):
      _x = self.RightPicker.Results.value[0].Position.value.x
      print _x

    return _x
    '''

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
    self.LeftPicker.Mask.value = "pickable"
    pick_transform.Children.value = [self.LeftPicker.Ray.value, ray_left_avatar]
    self.LEFTHAND.Children.value.append(pick_transform)

    #self.left_picker_updater.DefaultMaterial.value = "Stone"
    #self.left_picker_updater.TargetMaterial.value = "Bright"
    #self.left_picker_updater.PickedNodes.connect_from(self.LeftPicker.Results)

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

    #elf.right_picker_updater.DefaultMaterial.value = "Stone"
    #self.right_picker_updater.TargetMaterial.value = "Bright"
    #self.right_picker_updater.PickedNodes.connect_from(self.RightPicker.Results)


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
    #print "Resutlslist:   " , len(results.value)




    ##############################################
''' # INFO ZU ADD AND INIT FIELD
  @field_has_changed(PickedNodes)
  def update_materials(self):
    #print "field PickedNodes has changed"
    print len(self.PickedNodes.value)
    #for i in range(0, len(self.OldNodes.value)):
    #  print "old"
    #  if isinstance(self.OldNodes.value[i].Object.value, avango.gua.GeometryNode):
    #    self.OldNodes.value[i].Object.value.Material.value = self.DefaultMaterial.value
    print len(self.OldNodes.value)
    for i in range(0, len(self.PickedNodes.value)):
      if isinstance(self.PickedNodes.value[i].Object.value, avango.gua.GeometryNode):
        self.PickedNodes.value[i].Object.value.Material.value = self.TargetMaterial.value

        test_object = self.PickedNodes.value[i].Object.value
        #if test_object.has_field("Feld_test"):
        #  print "test object has field", test_object.Feld_test.value

        # Material Change
        print self.LeftPointer.sf_key_pageup.value
        if self.LeftPointer.sf_key_pageup.value:
          test_object.Material.value = 'AvatarBlue'
          #pass

        if test_object.has_field("ObjectHandler"):
          _object_handler = test_object.ObjectHandler.value

          _object_handler.test_function()

    self.OldNodes.value = self.PickedNodes.value
'''