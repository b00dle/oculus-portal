
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
    self.ROOM_PORTALS = [] #list with indexes
    self.portal_cubes = [] #lsit with portal cubes
    self.console_node = avango.gua.nodes.TransformNode(Name = "menu_node")

  def my_constructor(self,NAME,SCENEGRAPH,POSITION, EXITS, ACTIV, COLOR, ROOM_PORTALS):
    self.NAME = NAME
    self.SCENEGRAPH = SCENEGRAPH
    self.POSITION = POSITION
    self.COLOR = COLOR
    self.ROOM_PORTALS = ROOM_PORTALS


    self.loader = avango.gua.nodes.GeometryLoader()

    self.room_transform = avango.gua.nodes.TransformNode(Name = self.NAME + "_transform")
    self.room_transform.Transform.value = self.POSITION
    self.SCENEGRAPH.Root.value.Children.value.append(self.room_transform)

    plane = self.loader.create_geometry_from_file('room_floor', 'data/objects/plane.obj', "Stone" , avango.gua.LoaderFlags.DEFAULTS)
    plane.Transform.value = avango.gua.make_scale_mat(2.4,1,2)
    plane.GroupNames.value.append("do_not_display_group")
    self.room_transform.Children.value.append(plane)



    self.console_box = self.loader.create_geometry_from_file('console_box', 'data/objects/cube.obj', "Black" , avango.gua.LoaderFlags.DEFAULTS)
    self.console_box.Transform.value = avango.gua.make_trans_mat(0.0, 0.8, -0.17) *\
                                       avango.gua.make_rot_mat(75, 1, 0, 0) *\
                                       avango.gua.make_scale_mat(0.25, 0.016, 0.25) 
    self.console_node.Transform.value = avango.gua.make_trans_mat(0.0, 0.8, -0.14) *\
                                        avango.gua.make_scale_mat(0.45,0.45,0.45)*\
                                        avango.gua.make_rot_mat(75, 1, 0, 0)
                                       
    self.room_transform.Children.value.append(self.console_box)
    self.init_room_lines()

    #self.init_portal_cubes()

    self.lightcube = LightCube()
    self.lightcube.my_constructor(self.NAME, self.SCENEGRAPH, self.room_transform, ACTIV, EXITS, self.console_node, self.ROOM_PORTALS)


  def init_portal_cubes(self):
    for p in self.ROOM_PORTALS:
      if (p == 1):
        self.portal_cubes.append(PortalCube( ) )
      if (p == 2):
        self.portal_cubes.append(PortalCube( ) )
      if (p == 3):
        self.portal_cubes.append(PortalCube( ) )
      if (p == 4):
        self.portal_cubes.append(PortalCube( ) )
      if (p == 5):
        self.portal_cubes.append(PortalCube( ) )
      if (p == 6):
        self.portal_cubes.append(PortalCube( ) )

  def init_room_lines(self):
    right_upper_cornor  = avango.gua.Vec3( 1.2, 0, -1)
    right_bottom_cornor = avango.gua.Vec3( 1.2, 0, 1)
    left_upper_cornor   = avango.gua.Vec3( -1.2, 0, -1)
    left_bottom_cornor  = avango.gua.Vec3( -1.2, 0, 1)

    top_right_upper_cornor  = avango.gua.Vec3( 1.2, 2.7, -1)
    top_right_bottom_cornor = avango.gua.Vec3( 1.2, 2.7, 1)
    top_left_upper_cornor   = avango.gua.Vec3( -1.2, 2.7, -1)
    top_left_bottom_cornor  = avango.gua.Vec3( -1.2, 2.7, 1)

    create_line_visualization2(self.loader, self.room_transform, right_upper_cornor, right_bottom_cornor, self.COLOR, 0.01)
    create_line_visualization2(self.loader, self.room_transform, right_bottom_cornor, left_bottom_cornor, self.COLOR, 0.01)
    create_line_visualization2(self.loader, self.room_transform, left_bottom_cornor, left_upper_cornor, self.COLOR, 0.01)
    create_line_visualization2(self.loader, self.room_transform, left_upper_cornor, right_upper_cornor, self.COLOR, 0.01)

    create_line_visualization2(self.loader, self.room_transform, top_right_upper_cornor, top_right_bottom_cornor, self.COLOR, 0.01)
    create_line_visualization2(self.loader, self.room_transform, top_right_bottom_cornor, top_left_bottom_cornor, self.COLOR, 0.01)
    create_line_visualization2(self.loader, self.room_transform, top_left_bottom_cornor, top_left_upper_cornor, self.COLOR, 0.01)
    create_line_visualization2(self.loader, self.room_transform, top_left_upper_cornor, top_right_upper_cornor, self.COLOR, 0.01)

    create_line_visualization2(self.loader, self.room_transform, right_upper_cornor, top_right_upper_cornor, self.COLOR, 0.01)
    create_line_visualization2(self.loader, self.room_transform, right_bottom_cornor, top_right_bottom_cornor, self.COLOR, 0.01)
    create_line_visualization2(self.loader, self.room_transform, left_bottom_cornor, top_left_bottom_cornor, self.COLOR, 0.01)
    create_line_visualization2(self.loader, self.room_transform, left_upper_cornor, top_left_upper_cornor, self.COLOR, 0.01)

    create_line_visualization2(self.loader, self.room_transform, avango.gua.Vec3(0.0, 0.0, -0.20), avango.gua.Vec3(0.0, 0.8, -0.20), self.COLOR, 0.03)





