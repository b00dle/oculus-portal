#!/usr/bin/python

## @file
# Starting point of the application.

# import guacamole libraries
import avango
import avango.gua

# import framwork libraries
from lib.SceneManager import *
from lib.ViewingManager import *
from lib.portal_lib.PortalManager import *
from lib.interface_lib.Interface import *

# import python libraries
import sys


## Main method for the application
def start():

  ####### CREATE MATERIAL FILE FOR EACH PORTAL ########
  portalNames = ["portal_0", "portal_1"]
  for name in portalNames:
    newGMD = open('data/materials/Portal' + name + '.gmd', 'w+')
    with open('data/materials/Portal.gmd', 'r') as content_file:
      newGMD.write(content_file.read() + '\n')
    newGMD.close()
  #####################################################

  loader = avango.gua.nodes.GeometryLoader()

  # initialize materials
  avango.gua.load_shading_models_from("data/materials")
  avango.gua.load_materials_from("data/materials")

  # initialize scene
  scene_manager = SceneManager()

  # initialize viewing setup
  viewing_manager = ViewingManager(scene_manager.graphs, sys.argv[1])

  # initialize portals
  portal_manager = PortalManager(viewing_manager)




  #### --- INTERFACE TESTS --- ####

  # add display
  display = avango.gua.nodes.TransformNode(Name = "display_node")
  scene_manager.graphs[0].Root.value.Children.value.append(display)

  # add slider to display
  interface1 = Slider()
  interface1.my_constructor("Nr1", avango.gua.make_trans_mat(0.0, 1.0, 2.0), display, loader)
  interface2 = Slider()
  interface2.my_constructor("Nr1", avango.gua.make_trans_mat(0.0, 1.4, 2.0), display, loader)


  # run application loop
  viewing_manager.run(locals(), globals())

if __name__ == '__main__':
  start()
