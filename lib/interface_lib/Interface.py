
import avango
import avango.gua
import avango.script
from avango.script import field_has_changed
import avango.oculus

import math

class Slider(avango.script.Script):

  sfObjectTransform = avango.gua.SFVec2()

  def __init__(self):
    self.super(Slider).__init__()
    self.NAME = ""
    self.SLIDERPOS = avango.gua.Mat4()
    self.PARENT_NODE = avango.gua.nodes.TransformNode()
    self.slider_geometry = avango.gua.nodes.GeometryNode()
    self.slider_transform = avango.gua.nodes.TransformNode()
    #self.always_evaluate(True)

  def my_constructor(self, NAME, SLIDERPOS, PARENT_NODE, LOADER):
    self.NAME = NAME
    self.SLIDERPOS = SLIDERPOS
    self.PARENT_NODE = PARENT_NODE

    self.slider_geometry = LOADER.create_geometry_from_file('slider_' + NAME, 'data/objects/sphere.obj',
                                                            'Tiles', avango.gua.LoaderFlags.DEFAULTS | avango.gua.LoaderFlags.MAKE_PICKABLE)
    self.slider_geometry.Transform.value = avango.gua.make_scale_mat(0.2, 0.2, 0.2)
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
    self.create_line_visualization(LOADER, self.PARENT_NODE, line_begin, line_end, 'White')




  #@field_has_changed(TimeIn)0





  def create_line_visualization(self, LOADER, PARENT_NODE, START_POINT, END_POINT, MATERIAL_NAME):
    _line = LOADER.create_geometry_from_file('line_geometry',
                                            'data/objects/cube.obj',
                                            MATERIAL_NAME,
                                            avango.gua.LoaderFlags.DEFAULTS)

    _vector = avango.gua.Vec3(END_POINT.x - START_POINT.x, END_POINT.y - START_POINT.y, END_POINT.z - START_POINT.z)
    _distance = _vector.length()

    _line_center_position = START_POINT + avango.gua.Vec3(0.5 * _vector.x, 0.5 * _vector.y, 0.5 * _vector.z)
    _line_scale = 0.5 * _distance
    vec1 = avango.gua.Vec3(0, 0, -1)
    _line_rotation_mat = self.get_rotation_between_vectors(vec1, _vector)

    _line.Transform.value = avango.gua.make_trans_mat(_line_center_position) * \
                            _line_rotation_mat * \
                            avango.gua.make_scale_mat(0.05, 0.05, _line_scale)

    PARENT_NODE.Children.value.append(_line)

  def get_rotation_between_vectors(self, VEC1, VEC2):

    VEC1.normalize()
    VEC2.normalize()

    _angle = math.degrees(math.acos(VEC1.dot(VEC2)))
    _axis = VEC1.cross(VEC2)

    return avango.gua.make_rot_mat(_angle, _axis) 



