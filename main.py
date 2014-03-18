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
from lib.interface_lib.Manipulator import *


# import python libraries
import sys


## Main method for the application
def start():

  ####### CREATE MATERIAL FILE FOR EACH PORTAL ########
  portalNames = []

  for i in range(0, 12):
    #portalNames.append("portal_" + str(i) + "_DESK_0")
    #portalNames.append("portal_" + str(i) + "_DESK_1")
    portalNames.append("portal_" + str(i) + "_OVR_0")
    #portalNames.append("portal_" + str(i) + "_OVR_1")
    #portalNames.append("portal_" + str(i) + "_PW_0")
    #portalNames.append("portal_" + str(i) + "_PW_1")
  
  for name in portalNames:
    newGMD = open('data/materials/Portal' + name + '.gmd', 'w+')
    with open('data/materials/Portal.gmd', 'r') as content_file:
      newGMD.write(content_file.read() + '\n')
    newGMD.close()
  #####################################################

  # initialize materials
  avango.gua.load_shading_models_from("data/materials")
  avango.gua.load_materials_from("data/materials")

  # initialize scene
  scene_manager = SceneManager()

  # initialize viewing setup
  #viewing_manager = ViewingManager(scene_manager.graphs, sys.argv[1])
  viewing_manager = ViewingManager(scene_manager.graphs, "configs/controller_one_ovr.xml")

  # initialize portals
  portal_manager = PortalManager()
  portal_manager.my_constructor(viewing_manager, scene_manager)

  viewing_manager.setup_portal_render_masks()

  # print("user 0 pipes:")
  # print("pipe count:" + str(len(viewing_manager.viewer.Pipelines.value[0].PreRenderPipelines.value)))
  # for pipe in viewing_manager.viewer.Pipelines.value[0].PreRenderPipelines.value:
  #   print("pipe name: " + pipe.Name.value)
  #   print("texture name: " + pipe.OutputTextureName.value)

  # print("\nuser 1 pipes:")
  # print("pipe count:" + str(len(viewing_manager.viewer.Pipelines.value[1].PreRenderPipelines.value)))
  # for pipe in viewing_manager.viewer.Pipelines.value[1].PreRenderPipelines.value:
  #   print("pipe name: " + pipe.Name.value)
  #   print("texture name: " + pipe.OutputTextureName.value)

  #### --- INTERFACE TESTS --- ####

  # add manipulator
  #manipulator = Manipulator()

  # add display
  #display = avango.gua.nodes.TransformNode(Name = "display_node")
  #scene_manager.graphs[0].Root.value.Children.value.append(display)

  # add switch
  #switch1 = Switch()
  #switch1.my_constructor("Switch1", avango.gua.make_trans_mat(5.0, 1.0, 2.0), display, loader)

  # run application loop
  viewing_manager.run(locals(), globals())

if __name__ == '__main__':
  start()
