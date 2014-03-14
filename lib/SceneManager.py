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


class ObjectHandler(avango.script.Script):

  def __init__(self):
    self.super(ObjectHandler).__init__()

  #def my_constructor(self, NODE):
  #  self.NODE = NODE


  def test_function(self):
    #self.NODE.Material.value = 'AvatarBlue'
    print "test"


## Class for building a scene and appending the necessary nodes to the scenegraph.
#
# The concrete member variables vary from scene to scene and can be chosen at will.
class SceneManager:

  ## Custom constructor
  def __init__(self):
    self.graphs = []
    self.create_simplescene()
    self.create_harbourscene()
    #self.create_weimarscene()

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

    # Create Monkey
    #monkey = loader.create_geometry_from_file('monkey', 'data/objects/monkey.obj', 'Stones', avango.gua.LoaderFlags.DEFAULTS | avango.gua.LoaderFlags.MAKE_PICKABLE)
    #monkey.Transform.value = avango.gua.make_trans_mat(0.0, 3.0, -1.0) * avango.gua.make_scale_mat(2.0,2.0,2.0)
    
    #monkey_object_handler = ObjectHandler()
    #monkey_object_handler.my_constructor(monkey)

    #monkey.add_and_init_field(avango.SFFloat(), "Feld_test", 10.0)
    #monkey.add_and_init_field(avango.script.SFObject(), "ObjectHandler", monkey_object_handler)
    #monkey.add_and_init_field(avango.SFBool, "Resizeable", True)
    #monkey.GroupNames.value = ["pickable"]
    #graph.Root.value.Children.value.append(monkey)



    interactiv_object = InteractivGeometry()
    interactiv_object.my_constructor('monkey', 'data/objects/cube.obj', 'Stones', graph.Root.value, ["size", "red", "blue", "green"])

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

  


    
