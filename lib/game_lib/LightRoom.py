
import avango
import avango.gua
import avango.script

from ..line_creater import *

class LightRoom(avango.script.Script):

  def __init__(self):
    self.super(LightRoom).__init__()
    self.NAME = "default"
    self.SCENEGRAPH = avango.gua.nodes.SceneGraph()
    self.POSITION = avango.gua.nodes.TransformNode()

  def my_constructor(self,NAME,SCENEGRAPH,POSITION):
    self.NAME = NAME
    self.SCENEGRAPH = SCENEGRAPH
    self.POSITION = POSITION

    loader = avango.gua.nodes.GeometryLoader()

    room_transform = avango.gua.nodes.TransformNode()
    room_transform.Transform.value = self.POSITION
    self.SCENEGRAPH.Root.value.Children.value.append(room_transform)

    plane = loader.create_geometry_from_file('room_floor', 'data/objects/plane.obj', 'Stone', avango.gua.LoaderFlags.DEFAULTS)
    plane.Transform.value = avango.gua.make_scale_mat(2.2,1,1.8)
    room_transform.Children.value.append(plane)

    right_upper_cornor  = avango.gua.Vec3( 1.1, 0, -0.9)
    right_bottom_cornor = avango.gua.Vec3( 1.1, 0, 0.9)
    left_upper_cornor   = avango.gua.Vec3( -1.1, 0, -0.9)
    left_bottom_cornor  = avango.gua.Vec3( -1.1, 0, 0.9)

    top_right_upper_cornor  = avango.gua.Vec3( 1.1, 2, -0.9)
    top_right_bottom_cornor = avango.gua.Vec3( 1.1, 2, 0.9)
    top_left_upper_cornor   = avango.gua.Vec3( -1.1, 2, -0.9)
    top_left_bottom_cornor  = avango.gua.Vec3( -1.1, 2, 0.9)

    create_line_visualization2(loader, room_transform, right_upper_cornor, right_bottom_cornor, 'White', 0.01)
    create_line_visualization2(loader, room_transform, right_bottom_cornor, left_bottom_cornor, 'White', 0.01)
    create_line_visualization2(loader, room_transform, left_bottom_cornor, left_upper_cornor, 'White', 0.01)
    create_line_visualization2(loader, room_transform, left_upper_cornor, right_upper_cornor, 'White', 0.01)

    create_line_visualization2(loader, room_transform, top_right_upper_cornor, top_right_bottom_cornor, 'White', 0.01)
    create_line_visualization2(loader, room_transform, top_right_bottom_cornor, top_left_bottom_cornor, 'White', 0.01)
    create_line_visualization2(loader, room_transform, top_left_bottom_cornor, top_left_upper_cornor, 'White', 0.01)
    create_line_visualization2(loader, room_transform, top_left_upper_cornor, top_right_upper_cornor, 'White', 0.01)




