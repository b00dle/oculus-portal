#!/usr/bin/python

# import guacamole libraries
import avango
import avango.gua

from Portal import *
from PortalController import *
from PortalCube import *

class PortalManager():
  def __init__(self, VIEWINGMANAGER):
    # lists of all portals for each user
    self.PW_user_portals        = [ [] for i in range( len(VIEWINGMANAGER.powerwall_user_list) )]
    self.PW_user_portalcubes    = [ [] for i in range( len(VIEWINGMANAGER.powerwall_user_list) )]
    self.OVR_user_portals       = [ [] for i in range( len(VIEWINGMANAGER.ovr_user_list)       )]
    self.OVR_user_portalcubes   = [ [] for i in range( len(VIEWINGMANAGER.ovr_user_list)       )]
    self.DESK_user_portals      = [ [] for i in range( len(VIEWINGMANAGER.desktop_user_list)   )]
    self.DESK_user_portalcubes  = [ [] for i in range( len(VIEWINGMANAGER.desktop_user_list)   )]
    self.group_names            = []

    self.create_group_names(VIEWINGMANAGER)
    self.create_portals(VIEWINGMANAGER)

  def create_group_names(self, VIEWINGMANAGER):
    for PW_user in VIEWINGMANAGER.powerwall_user_list:
      self.group_names.append("PW_" + str(PW_user.id) + "_portals")
    for OVR_user in VIEWINGMANAGER.ovr_user_list:
      self.group_names.append("OVR_" + str(OVR_user.id) + "_portals")
    for DESK_user in VIEWINGMANAGER.desktop_user_list:
      self.group_names.append("DESK_" + str(DESK_user.id) + "_portals") 

  def create_portals(self, VIEWINGMANAGER):
    for PW_user in VIEWINGMANAGER.powerwall_user_list:
      # Size for Portal:
      portal_width = 1.0
      portal_height = 1.0

      origin_entry = avango.gua.Vec3(0.0, 2.0, 0.0)
      origin_exit = avango.gua.Vec3(2.0, 6.7, 40.0)
      box_size = 1.0

      ######PORTALBOX#######
      self.PW_user_portalcubes[PW_user.id].append(PortalCube())
      self.PW_user_portalcubes[PW_user.id][0].my_constructor("portalCube",
                                                        VIEWINGMANAGER.viewer.SceneGraphs.value[0],
                                                        VIEWINGMANAGER.viewer.SceneGraphs.value[1],
                                                        origin_entry,
                                                        origin_exit,
                                                        1.0,
                                                        self.group_names,
                                                        0,
                                                        "PW",
                                                        str(PW_user.id)
                                                        )

      ########PORTALCONTROLLER########
      PW_user.portal_controller.my_constructor(VIEWINGMANAGER.SCENEGRAPH,
                                         "controller_DESK_" + str(PW_user.id),
                                         VIEWINGMANAGER.viewer.Pipelines,
                                         PW_user.pipeline,
                                         self.PW_user_portals[PW_user.id],
                                         self.PW_user_portalcubes[PW_user.id],
                                         VIEWINGMANAGER.navigation_list[PW_user.portal_controller.PLATFORM],
                                         PW_user.head_transform,
                                         )

    for OVR_user in VIEWINGMANAGER.ovr_user_list:
      # Size for Portal:
      portal_width = 1.0
      portal_height = 1.0

      origin_entry = avango.gua.Vec3(0.0, 2.0, 0.0)
      origin_exit = avango.gua.Vec3(2.0, 6.7, 40.0)
      box_size = 1.0

      ######PORTALBOX#######
      self.OVR_user_portalcubes[OVR_user.id].append(PortalCube())
      self.OVR_user_portalcubes[OVR_user.id][0].my_constructor("portalCube",
                                                        VIEWINGMANAGER.viewer.SceneGraphs.value[0],
                                                        VIEWINGMANAGER.viewer.SceneGraphs.value[1],
                                                        origin_entry,
                                                        origin_exit,
                                                        1.0,
                                                        self.group_names,
                                                        0,
                                                        "OVR",
                                                        str(OVR_user.id)
                                                        )

      ########PORTALCONTROLLER########
      OVR_user.portal_controller.my_constructor(VIEWINGMANAGER.SCENEGRAPH,
                                         "controller_DESK_" + str(OVR_user.id),
                                         VIEWINGMANAGER.viewer.Pipelines,
                                         OVR_user.pipeline,
                                         self.OVR_user_portals[OVR_user.id],
                                         self.OVR_user_portalcubes[OVR_user.id],
                                         VIEWINGMANAGER.navigation_list[OVR_user.portal_controller.PLATFORM],
                                         OVR_user.head_transform,
                                         )

    for DESK_user in VIEWINGMANAGER.desktop_user_list:
      # Size for Portal:
      portal_width = 1.0
      portal_height = 1.0

      origin_entry = avango.gua.Vec3(0.0, 2.0, 0.0)
      origin_exit = avango.gua.Vec3(2.0, 6.7, 40.0)
      box_size = 1.0

      ######PORTALBOX#######
      self.DESK_user_portalcubes[DESK_user.id].append(PortalCube())
      self.DESK_user_portalcubes[DESK_user.id][0].my_constructor("portalCube",
                                                        VIEWINGMANAGER.viewer.SceneGraphs.value[0],
                                                        VIEWINGMANAGER.viewer.SceneGraphs.value[1],
                                                        origin_entry,
                                                        origin_exit,
                                                        1.0,
                                                        self.group_names,
                                                        0,
                                                        "DESK",
                                                        str(DESK_user.id)
                                                        )

      ########PORTALCONTROLLER########
      DESK_user.portal_controller.my_constructor(VIEWINGMANAGER.SCENEGRAPH,
                                         "controller_DESK_" + str(DESK_user.id),
                                         VIEWINGMANAGER.viewer.Pipelines,
                                         DESK_user.pipeline,
                                         self.DESK_user_portals[DESK_user.id],
                                         self.DESK_user_portalcubes[DESK_user.id],
                                         VIEWINGMANAGER.navigation_list[DESK_user.portal_controller.PLATFORM],
                                         DESK_user.head_transform,
                                         )
