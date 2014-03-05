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

# import python libraries
import sys


## Main method for the application
def start():

  ####### CREATE MATERIAL FILE FOR EACH PORTAL ########
  portalNames = ["portal_0_DESK_0", "portal_0_OVR_0", "portal_1_DESK_0", "portal_1_OVR_0"]
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
  viewing_manager = ViewingManager(scene_manager.graphs, "configs/desktop_ovr.xml")

  # initialize portals
  portal_manager = PortalManager(viewing_manager)

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

  # run application loop
  viewing_manager.run(locals(), globals())

if __name__ == '__main__':
  start()
