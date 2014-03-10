#!/usr/bin/python

# import guacamole libraries
import avango
import avango.gua

from Portal import *
from PortalController import *

class PortalManager():
  def __init__(self, VIEWINGMANAGER):
    self.create_portals(VIEWINGMANAGER)

  def create_portals(self, VIEWINGMANAGER):
    for u in VIEWINGMANAGER.powerwall_user_list:
      # collection of !!ALL!! portals
      portals = []

      # Size for every Portal:
      portal_width = 2.0
      portal_height = 3.0

      ###### portal 1
      # position of portal in the active world 
      entry_pos = avango.gua.make_trans_mat(0,1.95,-6)
      # position of portal in the world we are looking into
      exit_pos = avango.gua.make_trans_mat(2.0,1.95,0.0)

      portal_name = "portal_" + str(u.id)
      
      portal = Portal()
      portal.my_constructor(portal_name,
                            self.viewer.SceneGraphs.value[0], #simplescene
                            self.viewer.SceneGraphs.value[0],
                            entry_pos,
                            exit_pos,
                            portal_width,
                            portal_height
                            )
      
      # Change Pipeline Settings
      portal.PRE_PIPE.BackgroundTexture.value = "data/textures/painted_ships.jpg"
      portal.PRE_PIPE.EnableBackfaceCulling.value = False

      portals.append(portal)

      #TODO NAV_NODE, NAVIGATOR (platform of user)
      u.portal_controller.my_constructor(VIEWINGMANAGER.SCENEGRAPH,
                                         "controller_" + str(u.id),
                                         VIEWINGMANAGER.viewer.Pipelines,
                                         u.pipeline,
                                         portals,
                                         VIEWINGMANAGER.navigation_list[u.portal_controller.PLATFORM],
                                         u.head_transform,
                                         u.screen
                                         )

    for u in VIEWINGMANAGER.ovr_user_list:
      # collection of !!ALL!! portals
      portals = []

      # Size for every Portal:
      portal_width = 2.0
      portal_height = 3.0

      ###### portal 1
      # position of portal in the active world 
      entry_pos = avango.gua.make_trans_mat(0,1.95,-6)
      # position of portal in the world we are looking into
      exit_pos = avango.gua.make_trans_mat(2.0,1.95,0.0)

      portal_name = "portal_" + str(u.id)
      
      portal = Portal()
      portal.my_constructor(portal_name,
                            VIEWINGMANAGER.viewer.SceneGraphs.value[0], #simplescene
                            VIEWINGMANAGER.viewer.SceneGraphs.value[0],
                            entry_pos,
                            exit_pos,
                            portal_width,
                            portal_height
                            )
      
      # Change Pipeline Settings
      portal.PRE_PIPE.BackgroundTexture.value = "data/textures/painted_ships.jpg"
      portal.PRE_PIPE.EnableBackfaceCulling.value = False

      portals.append(portal)

      #TODO NAV_NODE, NAVIGATOR (platform of user)
      u.portal_controller.my_constructor(VIEWINGMANAGER.SCENEGRAPH,
                                         "controller_" + str(u.id),
                                         VIEWINGMANAGER.viewer.Pipelines,
                                         u.pipeline,
                                         portals,
                                         VIEWINGMANAGER.navigation_list[u.portal_controller.PLATFORM],
                                         u.head_transform,
                                         u.left_screen
                                         )

    for u in VIEWINGMANAGER.desktop_user_list:
      # collection of !!ALL!! portals
      portals = []

      # Size for every Portal:
      portal_width = 2.0
      portal_height = 3.0

      ###### portal 1
      # position of portal in the active world 
      entry_pos = avango.gua.make_trans_mat(0,1.95,-6)
      # position of portal in the world we are looking into
      exit_pos = avango.gua.make_trans_mat(2.0,1.95,0.0)

      portal_name = "portal_" + str(u.id)
      
      portal = Portal()
      portal.my_constructor(portal_name,
                            VIEWINGMANAGER.viewer.SceneGraphs.value[0], #simplescene
                            VIEWINGMANAGER.viewer.SceneGraphs.value[0],
                            entry_pos,
                            exit_pos,
                            portal_width,
                            portal_height
                            )
      
      # Change Pipeline Settings
      portal.PRE_PIPE.BackgroundTexture.value = "data/textures/painted_ships.jpg"
      portal.PRE_PIPE.EnableBackfaceCulling.value = False

      portals.append(portal)

      #TODO NAV_NODE, NAVIGATOR (platform of user)
      u.portal_controller.my_constructor(VIEWINGMANAGER.SCENEGRAPH,
                                         "controller_" + str(u.id),
                                         VIEWINGMANAGER.viewer.Pipelines,
                                         u.pipeline,
                                         portals,
                                         VIEWINGMANAGER.navigation_list[u.portal_controller.PLATFORM],
                                         u.head_transform,
                                         u.screen
                                         )




