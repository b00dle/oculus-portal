#!/usr/bin/python

# import guacamole libraries
import avango
import avango.gua

from Portal import *
from PortalController import *
from PortalCube import *

class PortalManager():
  def __init__(self):
    self.PW_user_portals        = [[]]
    self.PW_user_portalcubes    = [[]]
    self.OVR_user_portals       = [[]]
    self.OVR_user_portalcubes   = [[]]
    self.DESK_user_portals      = [[]]
    self.DESK_user_portalcubes  = [[]]
    self.group_names            = []
    
  def my_constructor(self, VIEWINGMANAGER, SCENEMANAGER):
    # lists of all portals for each user
    self.PW_user_portals        = [ [] for i in range( len(VIEWINGMANAGER.powerwall_user_list) )]
    self.PW_user_portalcubes    = [ [] for i in range( len(VIEWINGMANAGER.powerwall_user_list) )]
    self.OVR_user_portals       = [ [] for i in range( len(VIEWINGMANAGER.ovr_user_list)       )]
    self.OVR_user_portalcubes   = [ [] for i in range( len(VIEWINGMANAGER.ovr_user_list)       )]
    self.DESK_user_portals      = [ [] for i in range( len(VIEWINGMANAGER.desktop_user_list)   )]
    self.DESK_user_portalcubes  = [ [] for i in range( len(VIEWINGMANAGER.desktop_user_list)   )]

    self.group_names            = []

    self.create_group_names(VIEWINGMANAGER)
    self.create_portals(VIEWINGMANAGER, SCENEMANAGER)


  def create_group_names(self, VIEWINGMANAGER):
    for PW_user in VIEWINGMANAGER.powerwall_user_list:
      self.group_names.append("PW_" + str(PW_user.id) + "_portals")
    for OVR_user in VIEWINGMANAGER.ovr_user_list:
      self.group_names.append("OVR_" + str(OVR_user.id) + "_portals")
    for DESK_user in VIEWINGMANAGER.desktop_user_list:
      self.group_names.append("DESK_" + str(DESK_user.id) + "_portals") 

  def create_portals(self, VIEWINGMANAGER, SCENEMANAGER):
    for PW_user in VIEWINGMANAGER.powerwall_user_list:

      # Size for Portal:
      portal_width = 1.0
      portal_height = 1.0

      origin_entry = avango.gua.Vec3(0.0, 1.5, 2.0)
      origin_exit = avango.gua.Vec3(0.0, 1.5, -8.0)
      box_size = 0.5

      ######PORTALBOX#######
      self.PW_user_portalcubes[PW_user.id].append(PortalCube())
      self.PW_user_portalcubes[PW_user.id][0].my_constructor("portalCube",
                                                        VIEWINGMANAGER.viewer.SceneGraphs.value[0],
                                                        VIEWINGMANAGER.viewer.SceneGraphs.value[0],
                                                        origin_entry,
                                                        origin_exit,
                                                        box_size,
                                                        self.group_names,
                                                        0,
                                                        "PW",
                                                        str(PW_user.id)
                                                        )

      for room in SCENEMANAGER.light_rooms:
        if room.NAME == "room1":
          self.PW_user_portalcubes[PW_user.id][0].sf_visibility.connect_from(room.lightcube.sf_visible)

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

      origin_entry = avango.gua.Vec3()
      origin_exit = avango.gua.Vec3()

      # Size for Portal:
      portal_width = 1.0
      portal_height = 1.0

      box_size = 0.5

      ######PORTALBOX#######

      ######PORTALCUBE ROOM 1#######
      for room in SCENEMANAGER.light_rooms:
        if room.NAME == "room1":
          origin_entry = avango.gua.Vec3(room.POSITION.get_translate().x,
                                         room.POSITION.get_translate().y + 1.5,
                                         room.POSITION.get_translate().z)
          
        if room.NAME == "room2":
          origin_exit  = avango.gua.Vec3(room.POSITION.get_translate().x,
                                         room.POSITION.get_translate().y + 1.5,
                                         room.POSITION.get_translate().z)

      self.OVR_user_portalcubes[OVR_user.id].append(PortalCube())
      self.OVR_user_portalcubes[OVR_user.id][0].my_constructor("portalCube",
                                                        VIEWINGMANAGER.viewer.SceneGraphs.value[0],
                                                        VIEWINGMANAGER.viewer.SceneGraphs.value[0],
                                                        origin_entry,
                                                        origin_exit,
                                                        box_size,
                                                        self.group_names,
                                                        0,
                                                        "OVR",
                                                        str(OVR_user.id)
                                                        )
      for room in SCENEMANAGER.light_rooms:
        if room.NAME == "room1":
          self.OVR_user_portalcubes[OVR_user.id][0].sf_visibility.connect_from(room.lightcube.sf_visible)

      ######PORTALCUBE ROOM 2#######
      for room in SCENEMANAGER.light_rooms:
        if room.NAME == "room2":
          origin_entry = avango.gua.Vec3(room.POSITION.get_translate().x,
                                         room.POSITION.get_translate().y + 1.5,
                                         room.POSITION.get_translate().z)
          
        if room.NAME == "room3":
          origin_exit  = avango.gua.Vec3(room.POSITION.get_translate().x,
                                         room.POSITION.get_translate().y + 1.5,
                                         room.POSITION.get_translate().z)

      self.OVR_user_portalcubes[OVR_user.id].append(PortalCube())
      self.OVR_user_portalcubes[OVR_user.id][1].my_constructor("portalCube",
                                                        VIEWINGMANAGER.viewer.SceneGraphs.value[0],
                                                        VIEWINGMANAGER.viewer.SceneGraphs.value[0],
                                                        origin_entry,
                                                        origin_exit,
                                                        box_size,
                                                        self.group_names,
                                                        6,
                                                        "OVR",
                                                        str(OVR_user.id)
                                                        )
      for room in SCENEMANAGER.light_rooms:
        if room.NAME == "room2":
          self.OVR_user_portalcubes[OVR_user.id][1].sf_visibility.connect_from(room.lightcube.sf_visible)

      ######PORTALCUBE ROOM 3#######
      for room in SCENEMANAGER.light_rooms:
        if room.NAME == "room3":
          origin_entry = avango.gua.Vec3(room.POSITION.get_translate().x,
                                         room.POSITION.get_translate().y + 1.5,
                                         room.POSITION.get_translate().z)
          
        if room.NAME == "room4":
          origin_exit  = avango.gua.Vec3(room.POSITION.get_translate().x,
                                         room.POSITION.get_translate().y + 1.5,
                                         room.POSITION.get_translate().z)

      self.OVR_user_portalcubes[OVR_user.id].append(PortalCube())
      self.OVR_user_portalcubes[OVR_user.id][2].my_constructor("portalCube",
                                                        VIEWINGMANAGER.viewer.SceneGraphs.value[0],
                                                        VIEWINGMANAGER.viewer.SceneGraphs.value[0],
                                                        origin_entry,
                                                        origin_exit,
                                                        box_size,
                                                        self.group_names,
                                                        12,
                                                        "OVR",
                                                        str(OVR_user.id)
                                                        )
      for room in SCENEMANAGER.light_rooms:
        if room.NAME == "room3":
          self.OVR_user_portalcubes[OVR_user.id][2].sf_visibility.connect_from(room.lightcube.sf_visible)

      ######PORTALCUBE ROOM 4#######
      for room in SCENEMANAGER.light_rooms:
        if room.NAME == "room4":
          origin_entry = avango.gua.Vec3(room.POSITION.get_translate().x,
                                         room.POSITION.get_translate().y + 1.5,
                                         room.POSITION.get_translate().z)
          
        if room.NAME == "room1":
          origin_exit  = avango.gua.Vec3(room.POSITION.get_translate().x,
                                         room.POSITION.get_translate().y + 1.5,
                                         room.POSITION.get_translate().z)

      self.OVR_user_portalcubes[OVR_user.id].append(PortalCube())
      self.OVR_user_portalcubes[OVR_user.id][3].my_constructor("portalCube",
                                                        VIEWINGMANAGER.viewer.SceneGraphs.value[0],
                                                        VIEWINGMANAGER.viewer.SceneGraphs.value[0],
                                                        origin_entry,
                                                        origin_exit,
                                                        box_size,
                                                        self.group_names,
                                                        18,
                                                        "OVR",
                                                        str(OVR_user.id)
                                                        )
      for room in SCENEMANAGER.light_rooms:
        if room.NAME == "room4":
          self.OVR_user_portalcubes[OVR_user.id][3].sf_visibility.connect_from(room.lightcube.sf_visible)

      # ######PORTALCUBE ROOM 5#######
      # for room in SCENEMANAGER.light_rooms:
      #   if room.NAME == "room5":
      #     origin_entry = avango.gua.Vec3(room.POSITION.get_translate().x,
      #                                    room.POSITION.get_translate().y + 1.5,
      #                                    room.POSITION.get_translate().z)
          
      #   if room.NAME == "room6":
      #     origin_exit  = avango.gua.Vec3(room.POSITION.get_translate().x,
      #                                    room.POSITION.get_translate().y + 1.5,
      #                                    room.POSITION.get_translate().z)

      # self.OVR_user_portalcubes[OVR_user.id].append(PortalCube())
      # self.OVR_user_portalcubes[OVR_user.id][4].my_constructor("portalCube",
      #                                                   VIEWINGMANAGER.viewer.SceneGraphs.value[0],
      #                                                   VIEWINGMANAGER.viewer.SceneGraphs.value[0],
      #                                                   origin_entry,
      #                                                   origin_exit,
      #                                                   box_size,
      #                                                   self.group_names,
      #                                                   24,
      #                                                   "OVR",
      #                                                   str(OVR_user.id)
      #                                                   )
      # for room in SCENEMANAGER.light_rooms:
      #   if room.NAME == "room5":
      #     self.OVR_user_portalcubes[OVR_user.id][4].sf_visibility.connect_from(room.lightcube.sf_visible)

      # ######PORTALCUBE ROOM 6#######
      # for room in SCENEMANAGER.light_rooms:
      #   if room.NAME == "room6":
      #     origin_entry = avango.gua.Vec3(room.POSITION.get_translate().x,
      #                                    room.POSITION.get_translate().y + 1.5,
      #                                    room.POSITION.get_translate().z)
          
      #   if room.NAME == "room1":
      #     origin_exit  = avango.gua.Vec3(room.POSITION.get_translate().x,
      #                                    room.POSITION.get_translate().y + 1.5,
      #                                    room.POSITION.get_translate().z)

      # self.OVR_user_portalcubes[OVR_user.id].append(PortalCube())
      # self.OVR_user_portalcubes[OVR_user.id][5].my_constructor("portalCube",
      #                                                   VIEWINGMANAGER.viewer.SceneGraphs.value[0],
      #                                                   VIEWINGMANAGER.viewer.SceneGraphs.value[0],
      #                                                   origin_entry,
      #                                                   origin_exit,
      #                                                   box_size,
      #                                                   self.group_names,
      #                                                   30,
      #                                                   "OVR",
      #                                                   str(OVR_user.id)
      #                                                   )
      # for room in SCENEMANAGER.light_rooms:
      #   if room.NAME == "room6":
      #     self.OVR_user_portalcubes[OVR_user.id][5].sf_visibility.connect_from(room.lightcube.sf_visible)

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

      origin_entry = avango.gua.Vec3(0.0, 1.5, 2.0)
      origin_exit = avango.gua.Vec3(0.0, 1.5, -8.0)
      box_size = 0.5

      ######PORTALBOX#######
      self.DESK_user_portalcubes[DESK_user.id].append(PortalCube())
      self.DESK_user_portalcubes[DESK_user.id][0].my_constructor("portalCube",
                                                        VIEWINGMANAGER.viewer.SceneGraphs.value[0],
                                                        VIEWINGMANAGER.viewer.SceneGraphs.value[0],
                                                        origin_entry,
                                                        origin_exit,
                                                        box_size,
                                                        self.group_names,
                                                        0,
                                                        "DESK",
                                                        str(DESK_user.id)
                                                        )

      for room in SCENEMANAGER.light_rooms:
        if room.NAME == "room1":
          self.DESK_user_portalcubes[DESK_user.id][0].sf_visibility.connect_from(room.lightcube.sf_visible)

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
