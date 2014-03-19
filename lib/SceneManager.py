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

## Class for building a scene and appending the necessary nodes to the scenegraph.
#
# The concrete member variables vary from scene to scene and can be chosen at will.
class SceneManager:

  ## Custom constructor
  def __init__(self):
    self.graphs = []

    self.light_rooms  = []
    #self.create_simplescene()
    #self.create_harbourscene()
    self.scene_names = []
    self.rooms = []
    
    self.create_gamescene()
    #self.create_simplescene()
    #self.create_harbourscene()
    #self.create_simplescene()
    #self.create_level_2()
    #self.create_harbourscene()
    #self.create_weimarscene()


  def create_gamescene(self):
    self.scene_names.append("gamescene")
    graph = avango.gua.nodes.SceneGraph(Name = "gamescene")
    loader = avango.gua.nodes.GeometryLoader()

    # create light
    light = avango.gua.nodes.PointLightNode(Name = "sun",
                                          Color = avango.gua.Color(1.0, 1.0, 1.0),
                                          Falloff = 0.009,
                                          #Softness = 0.003,
                                          EnableShadows = True,
                                          EnableGodrays = True,
                                          EnableDiffuseShading = True,
                                          EnableSpecularShading = True)
                                          #ShadowMapSize = 2048,
                                          #ShadowOffset = 0.001)

    light.Transform.value = avango.gua.make_trans_mat(-5.0, 10.0, 20.0) * \
                          avango.gua.make_rot_mat(-45.0, 1.0, 0.0, 0.0) * \
                          avango.gua.make_scale_mat(100.0, 100.0, 160.0)

    graph.Root.value.Children.value.append(light)

    earth = loader.create_geometry_from_file("earth", 'data/objects/sphere.obj', 'earth', avango.gua.LoaderFlags.DEFAULTS)
    earth.Transform.value = avango.gua.make_trans_mat(20.0, 5.0, 0.0) * \
                            avango.gua.make_scale_mat(10.0, 10.0, 10.0)
    
    self.timer                  = avango.nodes.TimeSensor()
    self.timedRotate            = TimedRotate()
    self.timedRotate.my_constructor(avango.gua.Vec3(0.0,1.0,0.0), avango.gua.Vec3(0.0,0.0,-40.0))
    self.timedRotate.TimeIn.connect_from(self.timer.Time)
    self.timedRotate.TransformIn.value = earth.Transform.value
    earth.Transform.connect_from(self.timedRotate.TransformOut)

    graph.Root.value.Children.value.append(earth)
    #####      Create LightRooms       #####

    #level1 = LightRoom()
    #level1.my_constructor("room1", graph, avango.gua.make_trans_mat(0,0,0), [1], True, "White")
    #self.rooms.append(level1)

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
    sphere.my_constructor('sphere1', 'data/objects/sphere.obj', 'moon', avango.gua.make_trans_mat(-7.8,1.5,-12) * avango.gua.make_scale_mat(0.8,0.8,0.8),
          graph.Root.value, ["size"])

    teapot = InteractivGeometry()
    teapot.my_constructor('teapot', 'data/objects/teapot.obj', 'slider_mat_1', avango.gua.make_trans_mat(2.0,3.5,-18) *\
                                                                               avango.gua.make_scale_mat(1.4,1.4,1.4) *\
                                                                               avango.gua.make_rot_mat(36.0, 1, 0, 1) *\
                                                                               avango.gua.make_rot_mat(-30.0, 0, 1, 0),
          graph.Root.value, ["red", "green", "blue"])


    trophy = InteractivGeometry()
    trophy.my_constructor('trophy', 'data/objects/trophy.obj', 'CarPaintBlue', avango.gua.make_trans_mat(0,1.5,-25) * avango.gua.make_scale_mat(0.5,0.5,0.5) * avango.gua.make_rot_mat(30,1.0,0.0,0.0) * avango.gua.make_rot_mat(180,0.0,1.0,0.0),
      graph.Root.value, ["enable"])

    #sphere = InteractivGeometry()
    #sphere.my_constructor('sphere', 'data/objects/cube.obj', 'slider_mat_3', avango.gua.make_trans_mat(0,5.5,-2) * avango.gua.make_scale_mat(0.9,0.9,0.9) * avango.gua.make_rot_mat(45,0,1,1),
    #  graph.Root.value, ["red", "green", "blue"])



    # screen
    screen = avango.gua.nodes.ScreenNode(Name = "screen", Width = 1.6, Height = 0.9)
    #screen.Transform.value = avango.gua.make_rot_mat(-90.0, 0, 1, 0) * \
    #                         avango.gua.make_trans_mat(0, 1.5, 0)

    # head, mono_eye, left und right eye
    head = avango.gua.nodes.TransformNode(Name = "head")
    head.Transform.value = avango.gua.make_trans_mat(0.0, 0.0, 1.7)

    mono_eye = avango.gua.nodes.TransformNode(Name = "mono_eye")

    left_eye = avango.gua.nodes.TransformNode(Name = "left_eye")
    left_eye.Transform.value = avango.gua.make_trans_mat(-0.05, 0.0, 0.0)

    right_eye = avango.gua.nodes.TransformNode(Name = "right_eye")
    right_eye.Transform.value = avango.gua.make_trans_mat(0.05, 0.0, 0.0)

    head.Children.value = [mono_eye, left_eye, right_eye]

    # head an screen
    screen.Children.value.append(head)
    # screen an root
    graph.Root.value.Children.value.append(screen)

    self.graphs.append(graph)

  def create_simplescene(self):
    graph = avango.gua.nodes.SceneGraph(Name = "simplescene")
    loader = avango.gua.nodes.GeometryLoader()
    
    # create light
    spot = avango.gua.nodes.SpotLightNode(Name = "sun",
                                          Color = avango.gua.Color(1.0, 1.0, 1.0),
                                          Falloff = 0.009,
                                          Softness = 0.003,
                                          EnableShadows = True,
                                          EnableGodrays = False,
                                          EnableDiffuseShading = True,
                                          EnableSpecularShading = True,
                                          ShadowMapSize = 2048,
                                          ShadowOffset = 0.001)

    spot.Transform.value = avango.gua.make_trans_mat(0.0, 40.0, 40.0) * \
                          avango.gua.make_rot_mat(-45.0, 1.0, 0.0, 0.0) * \
                          avango.gua.make_scale_mat(100.0, 100.0, 160.0)

    graph.Root.value.Children.value.append(spot)

    # create floor
    plane = loader.create_geometry_from_file('floor', 'data/objects/plane.obj', 'Stones', avango.gua.LoaderFlags.DEFAULTS | avango.gua.LoaderFlags.MAKE_PICKABLE)
    plane.Transform.value = avango.gua.make_scale_mat(50,1,50)

    graph.Root.value.Children.value.append(plane)

    # screen
    screen = avango.gua.nodes.ScreenNode(Name = "screen", Width = 1.6, Height = 0.9)

    #screen.Transform.value = avango.gua.make_rot_mat(-90.0, 0,  1, 0) * \
    #                                                   avango.gua.make_trans_mat(0, 1.5, 0)

    # head, mono_eye, left und right eye
    head = avango.gua.nodes.TransformNode(Name = "head")
    head.Transform.value = avango.gua.make_trans_mat(0.0, 0.0, 1.7)

    mono_eye = avango.gua.nodes.TransformNode(Name = "mono_eye")

    left_eye = avango.gua.nodes.TransformNode(Name = "left_eye")
    left_eye.Transform.value = avango.gua.make_trans_mat(-0.05, 0.0, 0.0)

    right_eye = avango.gua.nodes.TransformNode(Name = "right_eye")
    right_eye.Transform.value = avango.gua.make_trans_mat(0.05, 0.0, 0.0)

    head.Children.value = [mono_eye, left_eye, right_eye]

    # head an screen
    screen.Children.value.append(head)
    # screen an root
    graph.Root.value.Children.value.append(screen)

    self.graphs.append(graph)
  def create_level_2(self):
    self.scene_names.append("level_2")
    graph = avango.gua.nodes.SceneGraph(Name = "level_2")
    loader = avango.gua.nodes.GeometryLoader()
    
    # create light
    spot = avango.gua.nodes.SpotLightNode(Name = "sun",
                                          Color = avango.gua.Color(1.0, 1.0, 1.0),
                                          Falloff = 0.009,
                                          Softness = 0.003,
                                          EnableShadows = True,
                                          EnableGodrays = False,
                                          EnableDiffuseShading = True,
                                          EnableSpecularShading = True,
                                          ShadowMapSize = 2048,
                                          ShadowOffset = 0.001)

    spot.Transform.value = avango.gua.make_trans_mat(0.0, 40.0, 40.0) * \
                          avango.gua.make_rot_mat(-45.0, 1.0, 0.0, 0.0) * \
                          avango.gua.make_scale_mat(100.0, 100.0, 160.0)

    graph.Root.value.Children.value.append(spot)

    # create floorans_mat(-2.0,5.0,1.0) * avango.gua.make_scale_mat(3.0,3.0,3.0), graph.Root.value, ["size","green","red","blue"])
    plane = loader.create_geometry_from_file('floor', 'data/objects/plane.obj', 'Tiles', avango.gua.LoaderFlags.DEFAULTS)
    plane.Transform.value = avango.gua.make_scale_mat(20,1,20)

    graph.Root.value.Children.value.append(plane)

    # screen
    screen = avango.gua.nodes.ScreenNode(Name = "screen", Width = 1.6, Height = 0.9)

    #screen.Transform.value = avango.gua.make_rot_mat(-90.0, 0, 1, 0) * \
    #                                                   avango.gua.make_trans_mat(0, 1.5, 0)

    # head, mono_eye, left und right eye
    head = avango.gua.nodes.TransformNode(Name = "head")
    head.Transform.value = avango.gua.make_trans_mat(0.0, 0.0, 1.7)

    mono_eye = avango.gua.nodes.TransformNode(Name = "mono_eye")

    left_eye = avango.gua.nodes.TransformNode(Name = "left_eye")
    left_eye.Transform.value = avango.gua.make_trans_mat(-0.05, 0.0, 0.0)

    right_eye = avango.gua.nodes.TransformNode(Name = "right_eye")
    right_eye.Transform.value = avango.gua.make_trans_mat(0.05, 0.0, 0.0)

    head.Children.value = [mono_eye, left_eye, right_eye]

    # head an screen
    screen.Children.value.append(head)
    # screen an root
    graph.Root.value.Children.value.append(screen)

    self.graphs.append(graph)


  def create_harbourscene(self):
    graph = avango.gua.nodes.SceneGraph(Name = "harbourscene")
    loader = avango.gua.nodes.GeometryLoader()
   
    town = loader.create_geometry_from_file("town",
                                              "data/objects/medieval_harbour/town.obj",
                                              "White",
                                              avango.gua.LoaderFlags.LOAD_MATERIALS | avango.gua.LoaderFlags.DEFAULTS | avango.gua.LoaderFlags.MAKE_PICKABLE)

    town.Transform.value = avango.gua.make_scale_mat(7.5, 7.5, 7.5)

    spot = avango.gua.nodes.SpotLightNode(Name = "sun",
                                          Color = avango.gua.Color(1.0, 1.0, 1.0),
                                          Falloff = 0.009,
                                          Softness = 0.003,
                                          EnableShadows = True,
                                          EnableGodrays = False,
                                          EnableDiffuseShading = True,
                                          EnableSpecularShading = True,
                                          ShadowMapSize = 2048,
                                          ShadowOffset = 0.001)

    spot.Transform.value = avango.gua.make_trans_mat(0.0, 40.0, 40.0) * \
                           avango.gua.make_rot_mat(-45.0, 1.0, 0.0, 0.0) * \
                           avango.gua.make_scale_mat(100.0, 100.0, 160.0)


    screen = avango.gua.nodes.ScreenNode(Name = "screen", Width = 1.6, Height = 0.9)

    screen.Transform.value =   avango.gua.make_trans_mat(0,1.95,0.0) *\
                              avango.gua.make_scale_mat(3.0,3.0,3.0)

    head = avango.gua.nodes.TransformNode(Name = "head")

    mono_eye = avango.gua.nodes.TransformNode(Name = "mono_eye")

    left_eye = avango.gua.nodes.TransformNode(Name = "left_eye")
    left_eye.Transform.value = avango.gua.make_trans_mat(-0.05, 0.0, 0.0)

    right_eye = avango.gua.nodes.TransformNode(Name = "right_eye")
    right_eye.Transform.value = avango.gua.make_trans_mat(0.05, 0.0, 0.0)

    head.Children.value = [mono_eye, left_eye, right_eye]

    screen.Children.value.append(head)

    graph.Root.value.Children.value = [town, screen, spot]

    self.graphs.append(graph)
    
  def create_weimarscene(self):
    graph = avango.gua.nodes.SceneGraph(Name = "weimarscene")
    loader = avango.gua.nodes.GeometryLoader()
    
    weimar = loader.create_geometry_from_file("weimar",
                                            "/opt/3d_models/architecture/weimar_geometry/weimar_stadtmodell_latest_version/weimar_stadtmodell_final.obj",
                                            "White",
                                             avango.gua.LoaderFlags.DEFAULTS | avango.gua.LoaderFlags.MAKE_PICKABLE)

    weimar.Transform.value = avango.gua.make_scale_mat(0.1, 0.1, 0.1)

    spot = avango.gua.nodes.SpotLightNode(Name = "sun",
                                          Color = avango.gua.Color(1.0, 1.0, 1.0),
                                          Falloff = 0.009,
                                          Softness = 0.003,
                                          EnableShadows = True,
                                          EnableGodrays = False,
                                          EnableDiffuseShading = True,
                                          EnableSpecularShading = True,
                                          ShadowMapSize = 2048,
                                          ShadowOffset = 0.001)

    spot.Transform.value = avango.gua.make_trans_mat(0.0, 40.0, 40.0) * \
                           avango.gua.make_rot_mat(-45.0, 1.0, 0.0, 0.0) * \
                           avango.gua.make_scale_mat(100.0, 100.0, 160.0)


    screen = avango.gua.nodes.ScreenNode(Name = "screen", Width = 1.6, Height = 0.9)

    screen.Transform.value =  avango.gua.make_trans_mat(0,0,0.0) *\
                              avango.gua.make_scale_mat(3.0,3.0,3.0)

    head = avango.gua.nodes.TransformNode(Name = "head")

    mono_eye = avango.gua.nodes.TransformNode(Name = "mono_eye")

    left_eye = avango.gua.nodes.TransformNode(Name = "left_eye")
    left_eye.Transform.value = avango.gua.make_trans_mat(-0.05, 0.0, 0.0)

    right_eye = avango.gua.nodes.TransformNode(Name = "right_eye")
    right_eye.Transform.value = avango.gua.make_trans_mat(0.05, 0.0, 0.0)

    head.Children.value = [mono_eye, left_eye, right_eye]

    screen.Children.value.append(head)

    graph.Root.value.Children.value = [weimar, screen, spot]   

    self.graphs.append(graph)

  


    
