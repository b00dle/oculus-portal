
import avango
import avango.gua
import avango.script

from ..line_creater import *
from LightCube import *

class LightRoom(avango.script.Script):

  def __init__(self):
    self.super(LightRoom).__init__()
    self.NAME = "default"
    self.SCENEGRAPH = avango.gua.nodes.SceneGraph()
    self.POSITION = avango.gua.Mat4()
    self.COLOR = "White"
    self.portal_cubes = [] #lsit with portal cubes
    self.console_node = avango.gua.nodes.TransformNode(Name = "menu_node")

  def my_constructor(self,NAME,SCENEGRAPH,POSITION, EXITS, ACTIV, COLOR):
    self.NAME = NAME
    self.SCENEGRAPH = SCENEGRAPH
    self.POSITION = POSITION
    self.COLOR = COLOR

    self.loader = avango.gua.nodes.GeometryLoader()

    self.room_transform = avango.gua.nodes.TransformNode(Name = self.NAME + "_transform")
    self.room_transform.Transform.value = self.POSITION
    self.SCENEGRAPH.Root.value.Children.value.append(self.room_transform)

    plane = self.loader.create_geometry_from_file('room_floor', 'data/objects/plane.obj', "Stone" , avango.gua.LoaderFlags.DEFAULTS)
    plane.Transform.value = avango.gua.make_scale_mat(2.4,1,2)
    plane.GroupNames.value.append("do_not_display_group")
    self.room_transform.Children.value.append(plane)

    room = self.loader.create_geometry_from_file('room_solid', 'data/objects/lightroom_light.obj', "PhongWhite" , avango.gua.LoaderFlags.DEFAULTS)
    room.Transform.value = avango.gua.make_trans_mat(0,1.5,0) * avango.gua.make_scale_mat(0.3,0.3,0.2)#avango.gua.make_scale_mat(2.4,1,2)
    
    room_l = self.loader.create_geometry_from_file('room_light', 'data/objects/lightroom_frame.obj', "PhongGrey" , avango.gua.LoaderFlags.DEFAULTS)
    #room_l.Transform.value = avango.gua.make_trans_mat(0,1.5,0) * avango.gua.make_scale_mat(0.3,0.3,0.2)#avango.gua.make_scale_mat(2.4,1,2)
    
    room.Children.value.append(room_l)
    self.room_transform.Children.value.append(room)


    self.console_box = self.loader.create_geometry_from_file('console_box', 'data/objects/terminal.obj', COLOR , avango.gua.LoaderFlags.DEFAULTS)
    self.console_box.Transform.value = avango.gua.make_trans_mat(0.0, 0.8, -0.21) *\
                                       avango.gua.make_rot_mat(75, 1, 0, 0)*\
                                       avango.gua.make_scale_mat(0.25, 0.25, 0.25) 

                                       
    self.room_transform.Children.value.append(self.console_box)
    self.init_room_lines()

    self.lightcube = LightCube()
    self.lightcube.my_constructor(self.NAME, self.SCENEGRAPH, self.room_transform, ACTIV, EXITS, self.console_box, COLOR)


  def init_room_lines(self):
    right_upper_cornor  = avango.gua.Vec3( 1.2, 0, -1)
    right_bottom_cornor = avango.gua.Vec3( 1.2, 0, 1)
    left_upper_cornor   = avango.gua.Vec3( -1.2, 0, -1)
    left_bottom_cornor  = avango.gua.Vec3( -1.2, 0, 1)

    top_right_upper_cornor  = avango.gua.Vec3( 1.2, 2.7, -1)
    top_right_bottom_cornor = avango.gua.Vec3( 1.2, 2.7, 1)
    top_left_upper_cornor   = avango.gua.Vec3( -1.2, 2.7, -1)
    top_left_bottom_cornor  = avango.gua.Vec3( -1.2, 2.7, 1)

    create_line_visualization2(self.loader, self.room_transform, avango.gua.Vec3(0.0, 0.0, -0.20), avango.gua.Vec3(0.0, 0.8, -0.20), self.COLOR, 0.03)
    #create_line_visualization2(self.loader, self.room_transform, avango.gua.Vec3(0.0, 0.0, -0.20), avango.gua.Vec3(0.0, 0.0, -1.5), self.COLOR, 0.03)





