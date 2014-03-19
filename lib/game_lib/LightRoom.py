#!/usr/bin/python

## @file
# Contains classes LineCreator, LightCube.

# import guacamole libraries
import avango
import avango.gua
import avango.script

# import framework libraries
from ..LineCreator import *
from LightCube import *

## Class of a lightroom for the oculus rift demo.
class LightRoom(avango.script.Script):

  ## default constructor
  def __init__(self):
    self.super(LightRoom).__init__()
    self.NAME = "default"
    self.SCENEGRAPH = avango.gua.nodes.SceneGraph()
    self.POSITION = avango.gua.Mat4()
    self.COLOR = "White"
    self.portal_cubes = [] #lsit with portal cubes
    self.console_node = avango.gua.nodes.TransformNode(Name = "menu_node")

  ## Custom constructor
  # @param NAME The Name of the lightroom.
  # @param SCENEGRAPH Reference to the scenegraph of the currently displayed scene.
  # @param POSITION The position of the lightroom in the scene.
  # @param EXITS List that describes the where the lightcube of the room has its exits(1=x,2=-x,3=y,4=-y,5=z,6=-z).
  # @param ACTIV Describes if the room is an emitter, that always has light.
  # @param COLOR The color of the room.
  def my_constructor(self,NAME,SCENEGRAPH, POSITION, EXITS, ACTIV, COLOR):
    self.NAME = NAME
    self.SCENEGRAPH = SCENEGRAPH
    self.POSITION = POSITION
    self.COLOR = COLOR

    self.loader = avango.gua.nodes.GeometryLoader()

    self.room_transform = avango.gua.nodes.TransformNode(Name = self.NAME + "_transform")
    self.room_transform.Transform.value = self.POSITION
    self.SCENEGRAPH.Root.value.Children.value.append(self.room_transform)

    plane = self.loader.create_geometry_from_file('room_floor',
                                                  'data/objects/plane.obj',
                                                  "Stone",
                                                  avango.gua.LoaderFlags.DEFAULTS)
    plane.Transform.value = avango.gua.make_scale_mat(2.4,1,2)
    plane.GroupNames.value.append("do_not_display_group")
    self.room_transform.Children.value.append(plane)

    room = self.loader.create_geometry_from_file('room_solid',
                                                 'data/objects/lightroom_light.obj',
                                                 "PhongWhite",
                                                 avango.gua.LoaderFlags.DEFAULTS)
    room.Transform.value = avango.gua.make_trans_mat(0,1.5,0) *\
                           avango.gua.make_scale_mat(0.3,0.3,0.2)
    self.room_transform.Children.value.append(room)

    self.console_box = self.loader.create_geometry_from_file('console_box',
                                                             'data/objects/terminal.obj',
                                                             COLOR,
                                                             avango.gua.LoaderFlags.DEFAULTS)
    self.console_box.Transform.value = avango.gua.make_trans_mat(0.0, 0.8, -0.21) *\
                                       avango.gua.make_rot_mat(75, 1, 0, 0)*\
                                       avango.gua.make_scale_mat(0.25, 0.25, 0.25) 

                                       
    self.room_transform.Children.value.append(self.console_box)

    self.lightcube = LightCube()
    self.lightcube.my_constructor(self.NAME,
                                  self.SCENEGRAPH,
                                  self.room_transform,
                                  ACTIV,
                                  EXITS,
                                  self.console_box, COLOR)

    create_line_visualization2(self.loader,
                               self.room_transform, 
                               avango.gua.Vec3(0.0,0.0,-0.20),
                               avango.gua.Vec3(0.0, 0.8, -0.20),
                               self.COLOR,
                               0.03)
   





