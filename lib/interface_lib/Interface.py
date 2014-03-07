
import avango
import avango.gua
import avango.script
from avango.script import field_has_changed
import avango.oculus

import math

def create_line_visualization(LOADER, PARENT_NODE, START_POINT, END_POINT, MATERIAL_NAME):
  _line = LOADER.create_geometry_from_file('line_geometry',
                                          'data/objects/cube.obj',
                                          MATERIAL_NAME,
                                          avango.gua.LoaderFlags.DEFAULTS)

  _vector = avango.gua.Vec3(END_POINT.x - START_POINT.x, END_POINT.y - START_POINT.y, END_POINT.z - START_POINT.z)
  _distance = _vector.length()

  _line_center_position = START_POINT + avango.gua.Vec3(0.5 * _vector.x, 0.5 * _vector.y, 0.5 * _vector.z)
  _line_scale = 0.5 * _distance
  vec1 = avango.gua.Vec3(0, 0, -1)
  _line_rotation_mat = get_rotation_between_vectors(vec1, _vector)

  _line.Transform.value = avango.gua.make_trans_mat(_line_center_position) * \
                          _line_rotation_mat * \
                          avango.gua.make_scale_mat(0.05, 0.05, _line_scale)

  PARENT_NODE.Children.value.append(_line)



def get_rotation_between_vectors(VEC1, VEC2):

  VEC1.normalize()
  VEC2.normalize()

  _angle = math.degrees(math.acos(VEC1.dot(VEC2)))
  _axis = VEC1.cross(VEC2)

  return avango.gua.make_rot_mat(_angle, _axis) 




class Switch(avango.script.Script):

  def __init__(self):
    self.super(Switch).__init__()
    #self.always_evaluate(True)
    self.NAME = ""
    self.SWITCHPOS = avango.gua.Mat4()
    self.PARENT_NODE = avango.gua.nodes.TransformNode()
    self.switch_geometry = avango.gua.nodes.GeometryNode()
    self.switch_transform = avango.gua.nodes.TransformNode()

    self.switch_bool = False

  def my_constructor(self, NAME, SWITCHPOS, PARENT_NODE):
    self.NAME = NAME
    self.SWITCHPOS = SWITCHPOS
    self.PARENT_NODE = PARENT_NODE

    self.LOADER = avango.gua.nodes.GeometryLoader()

    self.switch_scale = avango.gua.make_scale_mat(0.2, 0.2, 0.2)

    self.switch_geometry = self.LOADER.create_geometry_from_file('switch_' + NAME, 'data/objects/sphere.obj',
                                                            'Tiles', avango.gua.LoaderFlags.DEFAULTS | avango.gua.LoaderFlags.MAKE_PICKABLE)
    self.switch_geometry.Transform.value = avango.gua.make_trans_mat(-0.5, 0.0, 0.0) * self.switch_scale
    self.switch_geometry.GroupNames.value = ["interface_element"]
    self.switch_transform = avango.gua.nodes.TransformNode(Name = 'switch_' + NAME)
    self.switch_transform.Transform.value = avango.gua.make_trans_mat(self.SWITCHPOS.get_translate())
    self.switch_transform.Children.value.append(self.switch_geometry)
    self.PARENT_NODE.Children.value.append(self.switch_transform)


    # Red Line
    line_begin1 = avango.gua.Vec3(self.switch_transform.Transform.value.get_translate().x - 0.5,
                                 self.switch_transform.Transform.value.get_translate().y,
                                 self.switch_transform.Transform.value.get_translate().z)

    line_end1 = avango.gua.Vec3(self.switch_transform.Transform.value.get_translate().x,
                                 self.switch_transform.Transform.value.get_translate().y,
                                 self.switch_transform.Transform.value.get_translate().z)


    create_line_visualization(self.LOADER, self.PARENT_NODE, line_begin1, line_end1, 'AvatarBlue')


    # Blue Line
    line_begin2 = avango.gua.Vec3(self.switch_transform.Transform.value.get_translate().x,
                                 self.switch_transform.Transform.value.get_translate().y,
                                 self.switch_transform.Transform.value.get_translate().z)

    line_end2 = avango.gua.Vec3(self.switch_transform.Transform.value.get_translate().x + 0.5,
                                 self.switch_transform.Transform.value.get_translate().y,
                                 self.switch_transform.Transform.value.get_translate().z)


    create_line_visualization(self.LOADER, self.PARENT_NODE, line_begin2, line_end2, 'AvatarRed')

    self.switch_pos_on = avango.gua.make_trans_mat(
                              self.switch_geometry.Transform.value.get_translate().x + 0.25,
                              self.switch_geometry.Transform.value.get_translate().y,
                              self.switch_geometry.Transform.value.get_translate().z) *\
                              self.switch_scale

    self.switch_pos_off = avango.gua.make_trans_mat(
                              self.switch_geometry.Transform.value.get_translate().x - 0.25,
                              self.switch_geometry.Transform.value.get_translate().y,
                              self.switch_geometry.Transform.value.get_translate().z) *\
                              self.switch_scale
'''
  def evaluate(self):
    if self.switch_bool:
      print "on"
      self.switch_geometry.Transform.value = self.switch_pos_on

    if not self.switch_bool:
      print "off"
      self.switch_geometry.Transform.value = self.switch_pos_off
'''

class Slider(avango.script.Script):

  sfObjectTransformOut = avango.SFFloat()
  sfTransformInput = avango.gua.SFMatrix4()
  sfPositionXInput = avango.SFFloat()
  sf_float_output = avango.SFFloat()

  def __init__(self):
    self.super(Slider).__init__()
    self.always_evaluate(True)
    self.NAME = ""
    self.SLIDERPOS = avango.gua.Mat4()
    self.PARENT_NODE = avango.gua.nodes.TransformNode()
    self.slider_geometry = avango.gua.nodes.GeometryNode()
    self.slider_transform = avango.gua.nodes.TransformNode()
    self.slider_min = -0.5
    self.slider_max = 0.5

    self.slider_scale = avango.gua.make_scale_mat(0.2, 0.2, 0.2)
    self.transformation_at_start = avango.gua.make_identity_mat()
    self.object = avango.gua.nodes.GeometryNode()

    self.inv_plane_scale_mat = avango.gua.make_identity_mat()

    # RGB
    self.value_r = 0
    self.value_g = 0
    self.value_b = 0


  def my_constructor(self, NAME, SLIDERPOS, PARENT_NODE):
    self.NAME = NAME
    self.SLIDERPOS = SLIDERPOS
    self.PARENT_NODE = PARENT_NODE
    self.LOADER = avango.gua.nodes.GeometryLoader()

    self.slider_geometry = self.LOADER.create_geometry_from_file('slider_' + NAME, 'data/objects/sphere.obj',
                                                            'Stone', avango.gua.LoaderFlags.DEFAULTS | avango.gua.LoaderFlags.MAKE_PICKABLE)
    self.slider_geometry.Transform.value = self.slider_scale
    self.slider_geometry.GroupNames.value = ["interface_element"]
    self.slider_transform = avango.gua.nodes.TransformNode(Name = 'slider_trans_' + NAME)
    self.slider_transform.Transform.value = avango.gua.make_trans_mat(self.SLIDERPOS.get_translate())
    self.slider_transform.Children.value.append(self.slider_geometry)
    self.PARENT_NODE.Children.value.append(self.slider_transform)

    line_begin = avango.gua.Vec3(self.slider_transform.Transform.value.get_translate().x - 0.5,
                                 self.slider_transform.Transform.value.get_translate().y,
                                 self.slider_transform.Transform.value.get_translate().z)

    line_end = avango.gua.Vec3(self.slider_transform.Transform.value.get_translate().x + 0.5,
                                 self.slider_transform.Transform.value.get_translate().y,
                                 self.slider_transform.Transform.value.get_translate().z)
    create_line_visualization(self.LOADER, self.PARENT_NODE, line_begin, line_end, 'White')



  @field_has_changed(sfPositionXInput)
  def change_slider_transformation(self):

    self.slider_geometry.Transform.value = avango.gua.make_trans_mat(
                                            self.sfPositionXInput.value,
                                            self.slider_geometry.Transform.value.get_translate().y,
                                            self.slider_geometry.Transform.value.get_translate().z) *\
                                            self.slider_scale

    value_x = self.sfPositionXInput.value

    if value_x < self.slider_min:
      value_x = self.slider_min

    if value_x > self.slider_max:
      value_x = self.slider_max

    value_x = (self.sfPositionXInput.value + 0.5)

    old_trans  = self.object.Transform.value.get_translate()
    old_rot    = self.object.Transform.value.get_rotate()
    old_scale  = self.object.Transform.value.get_scale()

    scale_factor = 2

    if self.NAME == "size":
      self.object.Transform.value = avango.gua.make_trans_mat(old_trans) *\
                    avango.gua.make_scale_mat(value_x * scale_factor, value_x * scale_factor, value_x * scale_factor) *\
                    avango.gua.make_rot_mat(old_rot)

    if self.NAME == "y_pos":
      self.object.Transform.value = avango.gua.make_trans_mat(old_trans.x, (value_x * scale_factor), old_trans.z) *\
                                    avango.gua.make_scale_mat(old_scale) *\
                                    avango.gua.make_rot_mat(old_rot)

    if self.NAME == "red":
      pass
      #self.value_r = value_x
      #_new_color = avango.gua.Vec3(self.value_r, self.value_g, self.value_b)
      #avango.gua.set_material_uniform("Bright", "diffuse_color", _new_color)

    if self.NAME == "green":
      pass
      #self.value_g = value_x
      #_new_color = avango.gua.Vec3(self.value_r, self.value_g, self.value_b)
      #avango.gua.set_material_uniform("Bright", "diffuse_color", _new_color)

    if self.NAME == "blue":
      pass
      #self.value_b = value_x
      #_new_color = avango.gua.Vec3(self.value_r, self.value_g, self.value_b)
      #avango.gua.set_material_uniform("Bright", "diffuse_color", _new_color)

    self.sf_float_output.value = value_x



# Ansatz mit Abstand zwischen den beiden Pointern
    '''
    slider_x = self.sfTransformInput.value.get_translate().x

    value_x = 2.0 * (slider_x - self.transformation_at_start.get_translate().x)

    if slider_x < self.slider_min:
      slider_x = self.slider_min

    if slider_x > self.slider_max:
      slider_x = self.slider_max
    '''


''' 
    self.slider_geometry.Transform.value = avango.gua.make_trans_mat(
                                            value_x,
                                            self.slider_transform.Transform.value.get_translate().y,
                                            self.slider_transform.Transform.value.get_translate().z) *\
                                            self.slider_scale


    old_trans = self.object.Transform.value.get_translate()
    old_rot = self.object.Transform.value.get_rotate()

    value_x = (value_x + 1)
    scale_factor = 2

    self.object.Transform.value = avango.gua.make_trans_mat(old_trans) *\
                  avango.gua.make_scale_mat(value_x * scale_factor, value_x * scale_factor, value_x * scale_factor) *\
                  avango.gua.make_rot_mat(old_rot)
'''


'''    
class Slider(avango.script.Script):

  sfObjectTransformOut = avango.SFFloat()
  sfTransformInput = avango.gua.SFMatrix4()
  #sfFloatXInput = avango.SFFloat()

  def __init__(self):
    self.super(Slider).__init__()
    self.always_evaluate(True)

    self.NAME = ""
    self.SLIDERPOS = avango.gua.Mat4()
    self.PARENT_NODE = avango.gua.nodes.TransformNode()
    self.slider_geometry = avango.gua.nodes.GeometryNode()
    self.slider_transform = avango.gua.nodes.TransformNode()
    self.slider_min = -1
    self.slider_max = 1
    #self.always_evaluate(True)

  def my_constructor(self, NAME, SLIDERPOS, PARENT_NODE, LOADER):
    self.NAME = NAME
    self.SLIDERPOS = SLIDERPOS
    self.PARENT_NODE = PARENT_NODE

    self.slider_geometry = LOADER.create_geometry_from_file('slider_' + NAME, 'data/objects/sphere.obj',
                                                            'Tiles', avango.gua.LoaderFlags.DEFAULTS | avango.gua.LoaderFlags.MAKE_PICKABLE)
    self.slider_geometry.Transform.value = avango.gua.make_scale_mat(0.2, 0.2, 0.2)
    self.slider_geometry.GroupNames.value = ["interface_element"]
    self.slider_transform = avango.gua.nodes.TransformNode(Name = 'slider_trans_' + NAME)
    self.slider_transform.Transform.value = avango.gua.make_trans_mat(self.SLIDERPOS.get_translate())
    self.slider_transform.Children.value.append(self.slider_geometry)
    self.PARENT_NODE.Children.value.append(self.slider_transform)

    line_begin = avango.gua.Vec3(self.slider_transform.Transform.value.get_translate().x - 1.0,
                                 self.slider_transform.Transform.value.get_translate().y,
                                 self.slider_transform.Transform.value.get_translate().z)

    line_end = avango.gua.Vec3(self.slider_transform.Transform.value.get_translate().x + 1.0,
                                 self.slider_transform.Transform.value.get_translate().y,
                                 self.slider_transform.Transform.value.get_translate().z)
    create_line_visualization(LOADER, self.PARENT_NODE, line_begin, line_end, 'White')


  #@field_has_changed(sfTransformInput)
  #def change_slider_transformation(self):
  def evaluate(self):
    slider_x = self.sfTransformInput.value.get_translate().x
    #print slider_x

    #slider_x = self.sfFloatXInput.value

    if slider_x < self.slider_min:
      slider_x = self.slider_min

    if slider_x > self.slider_max:
      slider_x = self.slider_max

    self.slider_geometry.Transform.value *= avango.gua.make_trans_mat(slider_x,
                                                                      self.slider_transform.Transform.value.get_translate().y,
                                                                      self.slider_transform.Transform.value.get_translate().z)

    self.sfObjectTransformOut.value = slider_x # TODO: Umrechnung von Pos auf Prozentwert
'''