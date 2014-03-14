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

  ## Custom constructor
  def __init__(self):
    self.graphs = []
    self.scene_names = []
    self.create_gamescene()
    #self.create_simplescene()
    #self.create_level_2()
    #self.create_harbourscene()
    #self.create_weimarscene()


  def create_gamescene(self):
    self.scene_names.append("gamescene")
    graph = avango.gua.nodes.SceneGraph(Name = "gamescene")
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

    level1 = LightRoom()
    level1.my_constructor("room1", graph, avango.gua.make_trans_mat(0,0,2), [1], True, "White")

    level2 = LightRoom()
    level2.my_constructor("room2",graph,avango.gua.make_trans_mat(0,0,-8), [3,4,5], False, "Green")

    level3 = LightRoom()
    level3.my_constructor("room3",graph,avango.gua.make_trans_mat(-10,0,-8), [1,6], False, "Blue")

    box2 = InteractivGeometry()
    box2.my_constructor('box2', 'data/objects/cube.obj', 'Stone', avango.gua.make_trans_mat(-10.6,1.5,-13) * avango.gua.make_scale_mat(0.8,0.8,0.8),
      graph.Root.value, ["size"])

    level4 = LightRoom()
    level4.my_constructor("room4",graph,avango.gua.make_trans_mat(-10,0,-18), [2,5], False, "Red")

    level5 = LightRoom()
    level5.my_constructor("room5",graph,avango.gua.make_trans_mat(0,0,-18), [1,2], False, "Purple")

    level6 = LightRoom()
    level6.my_constructor("room6",graph,avango.gua.make_trans_mat(0,0,-28), [5], False, "White")


    box = loader.create_geometry_from_file('box', 'data/objects/cube.obj', 'Stone', avango.gua.LoaderFlags.DEFAULTS | avango.gua.LoaderFlags.MAKE_PICKABLE)
    box.Transform.value = avango.gua.make_trans_mat(-10,0,0) * avango.gua.make_scale_mat(2,2,2)
    box.GroupNames.value = ["obsticale", "interactiv"]
    #graph.Root.value.Children.value.append(box)


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

  def create_simplescene(self):
    self.scene_names.append("simplescene")
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

    # create floorans_mat(-2.0,5.0,1.0) * avango.gua.make_scale_mat(3.0,3.0,3.0), graph.Root.value, ["size","green","red","blue"])
    #plane = loader.create_geometry_from_file('floor', 'data/objects/plane.obj', 'Stones', avango.gua.LoaderFlags.DEFAULTS)
    #plane.Transform.value = avango.gua.make_scale_mat(20,1,20)
    #testroom = LightRoom()
    #testroom.my_constructor("test_roon",graph,avango.gua.make_trans_mat(0,0,0))
    #graph.Root.value.Children.value.append(plane)

    # Create Monkey
    monkey_interface = InteractivGeometry()
    monkey_interface.my_constructor('monkey', 'data/objects/monkey.obj', 'Stones', avango.gua.make_trans_mat(2.0,3.0,2.0), graph.Root.value, ["enable"])

    box_interface = InteractivGeometry()
    box_interface.my_constructor('box', 'data/objects/cube.obj', 'slider_mat_1', avango.gua.make_trans_mat(-3.0,3.0,2.0), graph.Root.value, ["green","red","blue"])

    sphere_interface = InteractivGeometry()
    sphere_interface.my_constructor('sphere', 'data/objects/sphere.obj', 'slider_mat_2', avango.gua.make_trans_mat(-2.0,5.0,1.0) * avango.gua.make_scale_mat(3.0,3.0,3.0), graph.Root.value, ["size","green","red","blue"])


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
    self.scene_names.append("harbourscene")
    graph = avango.gua.nodes.SceneGraph(Name = "harbourscene")
    loader = avango.gua.nodes.GeometryLoader()
   
    weimar = loader.create_geometry_from_file("town",
                                              "data/objects/medieval_harbour/town.obj",
                                              "White",
                                              avango.gua.LoaderFlags.LOAD_MATERIALS | avango.gua.LoaderFlags.DEFAULTS)

    weimar.Transform.value = avango.gua.make_scale_mat(7.5, 7.5, 7.5)

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

    graph.Root.value.Children.value = [weimar, screen, spot]

    self.graphs.append(graph)
    
  def create_weimarscene(self):
    self.scene_names.append("weimarscene")
    graph = avango.gua.nodes.SceneGraph(Name = "weimarscene")
    loader = avango.gua.nodes.GeometryLoader()
    
    weimar = loader.create_geometry_from_file("weimar",
                                            "/opt/3d_models/architecture/weimar_geometry/weimar_stadtmodell_latest_version/weimar_stadtmodell_final.obj",
                                            "White",
                                             avango.gua.LoaderFlags.DEFAULTS)

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

  


    
