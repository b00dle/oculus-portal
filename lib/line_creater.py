
import avango
import avango.gua
import avango.script

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

def create_line_visualization2(LOADER, PARENT_NODE, START_POINT, END_POINT, MATERIAL_NAME, SIZE):
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
                          avango.gua.make_scale_mat(SIZE, SIZE, _line_scale)

  PARENT_NODE.Children.value.append(_line)



def get_rotation_between_vectors(VEC1, VEC2):

  VEC1.normalize()
  VEC2.normalize()

  _angle = math.degrees(math.acos(VEC1.dot(VEC2)))
  _axis = VEC1.cross(VEC2)

  return avango.gua.make_rot_mat(_angle, _axis) 
