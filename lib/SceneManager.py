#!/usr/bin/python

## @file
# Contains classes SceneManager, TimedMaterialUniformUpdate and TimedRotationUpdate.

# import guacamole libraries
import avango
import avango.gua
import avango.script
from   avango.script import field_has_changed
import avango.daemon

# import framework libraries
import Tools

# import python libraries
import math
import time

from interface_lib.InteractivGeometry import *
from game_lib.LightRoom import *

## Class for building a scene and appending the necessary nodes to the scenegraph.
#
# The concrete member variables vary from scene to scene and can be chosen at will.
class SceneManager:

  def __init__(self):
    self.graphs = []
    self.light_rooms  = []
    self.scene_names = []
    self.rooms = []
    self.timer = avango.nodes.TimeSensor()
    self.timedRotate            = TimedRotate()
    self.water_updater = TimedMaterialUniformUpdate()
    
    self.create_gamescene()
  
  # creates SceneGraph for game level  
  def create_gamescene(self):
    self.scene_names.append("gamescene")
    
    graph   = avango.gua.nodes.SceneGraph(Name = "gamescene")
    loader  = avango.gua.nodes.GeometryLoader()

    #####      Create simple scene objects       #####

    light = avango.gua.nodes.PointLightNode(Name = "sun",
                                          Color = avango.gua.Color(1.0, 1.0, 1.0),
                                          Falloff = 0.009,
                                          EnableShadows = True,
                                          EnableGodrays = True,
                                          EnableDiffuseShading = True,
                                          EnableSpecularShading = True)
                                          
    light.Transform.value = avango.gua.make_trans_mat(-5.0, 10.0, 20.0) * \
                          avango.gua.make_rot_mat(-45.0, 1.0, 0.0, 0.0) * \
                          avango.gua.make_scale_mat(100.0, 100.0, 160.0)

    graph.Root.value.Children.value.append(light)

    earth = loader.create_geometry_from_file("earth", 'data/objects/sphere.obj', 'earth', avango.gua.LoaderFlags.DEFAULTS)
    earth.Transform.value = avango.gua.make_trans_mat(20.0, 5.0, 0.0) * \
                            avango.gua.make_scale_mat(10.0, 10.0, 10.0)
    
    self.timedRotate.my_constructor(avango.gua.Vec3(0.0,1.0,0.0), avango.gua.Vec3(0.0,0.0,-40.0))
    self.timedRotate.TimeIn.connect_from(self.timer.Time)
    self.timedRotate.TransformIn.value = earth.Transform.value
    earth.Transform.connect_from(self.timedRotate.TransformOut)

    graph.Root.value.Children.value.append(earth)

    #####       Material Update         #####

    self.water_updater.MaterialName.value  = "Ray"
    self.water_updater.UniformName.value   = "time"
    self.water_updater.TimeIn.connect_from(self.timer.Time)

    #####      Create LightRooms       #####

    level2 = LightRoom()
    level2.my_constructor("room2",graph,avango.gua.make_trans_mat(0,0,-7.5), [2,3,5], True, "Green")
    self.rooms.append(level2)

    level3 = LightRoom()
    level3.my_constructor("room3",graph,avango.gua.make_trans_mat(0,0,-15), [1,2], False, "Yellow",)
    self.rooms.append(level3)

    level4 = LightRoom()
    level4.my_constructor("room4",graph,avango.gua.make_trans_mat(0,0,-22.5), [5], False, "Red")
    self.rooms.append(level4)

    level5 = LightRoom()
    level5.my_constructor("room5",graph,avango.gua.make_trans_mat(-7.5,0,-7.5), [1,3], False, "Purple")
    self.rooms.append(level5)

    level6 = LightRoom()
    level6.my_constructor("room6",graph,avango.gua.make_trans_mat(-7.5,0,-15), [2,5], False, "Blue")
    self.rooms.append(level6)

    self.light_rooms = [level2, level3, level4, level5, level6]

    #####     Create InteractivGeometries     #####

    sphere = InteractivGeometry()
    sphere.my_constructor('sphere1',
                          'data/objects/sphere.obj',
                          'moon',
                          avango.gua.make_trans_mat(-7.8,1.5,-12) * \
                          avango.gua.make_scale_mat(0.8,0.8,0.8),
                          graph.Root.value, ["size"])

    teapot = InteractivGeometry()
    teapot.my_constructor('teapot',
                          'data/objects/teapot.obj',
                          'slider_mat_1',
                          avango.gua.make_trans_mat(2.0,3.5,-18) * \
                          avango.gua.make_scale_mat(1.4,1.4,1.4) * \
                          avango.gua.make_rot_mat(36.0, 1, 0, 1) * \
                          avango.gua.make_rot_mat(-30.0, 0, 1, 0),
                          graph.Root.value, ["red", "green", "blue"])


    trophy = InteractivGeometry()
    trophy.my_constructor('trophy',
                          'data/objects/trophy.obj',
                          'CarPaintBlue',
                          avango.gua.make_trans_mat(0,1.5,-25) * \
                          avango.gua.make_scale_mat(0.5,0.5,0.5) * \
                          avango.gua.make_rot_mat(30,1.0,0.0,0.0) * \
                          avango.gua.make_rot_mat(180,0.0,1.0,0.0),
                          graph.Root.value, ["enable"])

    #####      Append Graph to member collection      #####

    self.graphs.append(graph)

## Helper class to update material values with respect to the current time.
class TimedRotate(avango.script.Script):

  TransformOut  = avango.gua.SFMatrix4()
  TransformIn   = avango.gua.SFMatrix4()
  TimeIn        = avango.SFFloat()
  RotationAngleIn = avango.gua.SFVec3()
  RotationPointIn = avango.gua.SFVec3()

  def my_constructor(self, ROTATIONANGLE, ROTATIONPOINT):
    self.RotationAngleIn.value = ROTATIONANGLE
    self.RotationPointIn.value = ROTATIONPOINT

  @field_has_changed(TimeIn)
  def update(self):
    self.TransformOut.value = avango.gua.make_rot_mat(self.TimeIn.value * 3.0,
                                                      self.RotationAngleIn.value.x,
                                                      self.RotationAngleIn.value.y,
                                                      self.RotationAngleIn.value.z) * \
                              avango.gua.make_trans_mat(self.RotationPointIn.value) * \
                              self.TransformIn.value * \
                              avango.gua.make_rot_mat(self.TimeIn.value * 4.0, 0.0, 1.0, 0.0)

## Helper class to update material values with respect to the current time.
class TimedMaterialUniformUpdate(avango.script.Script):

  TimeIn = avango.SFFloat()
  MaterialName = avango.SFString()
  UniformName = avango.SFString()
  
  @field_has_changed(TimeIn)
  def update(self):
    avango.gua.set_material_uniform(self.MaterialName.value,
                                    self.UniformName.value,
                                    self.TimeIn.value)