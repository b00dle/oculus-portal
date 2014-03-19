#!/usr/bin/python

## @file
# Starting point of the application.

# import guacamole libraries
import avango
import avango.gua

# import framwork libraries
from lib.SceneManager import *
from lib.ViewingManager import *
from lib.portal_lib.PortalCreator import *
from lib.interface_lib.Interface import *
from lib.interface_lib.Manipulator import *


# import python libraries
import sys

## Main method for the application
def start():

  ####### CREATE MATERIAL FILE FOR EACH PORTAL ########
  #
  # guacamole does not allow dynamic material creation
  # which is why this cannot be done during portal construction
  # ALSO this has to be done prior to: 
  # avango.gua.load_shading_models_from("data/materials")
  # avango.gua.load_materials_from("data/materials")
  # in order to have the database find the created .gmd files
  #
  # range depends on the count of portals
  # which portalnames are appended depends on the users in the viewing setup
  # uncomment lines if nessesary
  portalNames = []

  for i in range(0, 54):
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
  viewing_manager = ViewingManager(scene_manager.graphs, "configs/controller_one_ovr.xml")

  # initialize portals
  portal_creator = PortalCreator()
  portal_creator.my_constructor(viewing_manager, scene_manager)

  viewing_manager.setup_portal_render_masks()

  # run application loop
  viewing_manager.run(locals(), globals())

if __name__ == '__main__':
  start()
