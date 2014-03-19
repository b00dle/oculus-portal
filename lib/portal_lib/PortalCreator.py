#!/usr/bin/python

# import guacamole libraries
import avango
import avango.gua

from Portal import *
from PortalController import *
from PortalCube import *

from ..interface_lib.PortalButton import *

## Class for instancing all portals and portal controllers
#
# the actual portals and portal controllers to be added for each user have to be specified in the create_portals function.
class PortalCreator():
  def __init__(self):
    self.PW_user_portals        = [[]]
    self.PW_user_portalcubes    = [[]]
    
    self.OVR_user_portals       = [[]]
    self.OVR_user_portalcubes   = [[]]
    
    self.DESK_user_portals      = [[]]
    self.DESK_user_portalcubes  = [[]]
    
    self.group_names            = []
  
  ## Custom constructor
  # 
  # VIEWING_MANAGER   ViewingManager instance used in the application (containing users, navigation and rendering specific data)
  # SCENE_MANAGER     SceneManager instance used in the application (containing SceneGraphs)
  def my_constructor(self, VIEWING_MANAGER, SCENE_MANAGER):
    # lists of all portals for each user
    self.PW_user_portals        = [ [] for i in range( len(VIEWING_MANAGER.powerwall_user_list) )]
    self.PW_user_portalcubes    = [ [] for i in range( len(VIEWING_MANAGER.powerwall_user_list) )]
    
    self.OVR_user_portals       = [ [] for i in range( len(VIEWING_MANAGER.ovr_user_list)       )]
    self.OVR_user_portalcubes   = [ [] for i in range( len(VIEWING_MANAGER.ovr_user_list)       )]
    
    self.DESK_user_portals      = [ [] for i in range( len(VIEWING_MANAGER.desktop_user_list)   )]
    self.DESK_user_portalcubes  = [ [] for i in range( len(VIEWING_MANAGER.desktop_user_list)   )]

    self.group_names            = []

    self.create_group_names(VIEWING_MANAGER)
    self.apply_portal_description(VIEWING_MANAGER, SCENE_MANAGER)

  ## determines GroupNames used by all portals in the application 
  def create_group_names(self, VIEWING_MANAGER):
    for OVR_user in VIEWING_MANAGER.ovr_user_list:
      self.group_names.append("OVR_" + str(OVR_user.id) + "_portals")

    for PW_user in VIEWING_MANAGER.powerwall_user_list:
      self.group_names.append("PW_" + str(PW_user.id) + "_portals")
    
    for DESK_user in VIEWING_MANAGER.desktop_user_list:
      self.group_names.append("DESK_" + str(DESK_user.id) + "_portals")

  ## triggers portal_creation for each user
  def apply_portal_description(self, VIEWING_MANAGER, SCENE_MANAGER):
      for OVR_user in VIEWING_MANAGER.ovr_user_list:
        self.create_portals(VIEWING_MANAGER, SCENE_MANAGER, OVR_user, "OVR")

      for PW_user in VIEWING_MANAGER.powerwall_user_list:
        self.create_portals(VIEWING_MANAGER, SCENE_MANAGER, PW_user, "PW")

      for DESK_user in VIEWING_MANAGER.desktop_user_list:
        self.create_portals(VIEWING_MANAGER, SCENE_MANAGER, DESK_user, "DESK")

  ## creates portals and portal controllers for each user
  #
  # The concrete functionality varies from app to app and can be chosen at will
  ############################################################################
  #############################MODEL HERE#####################################
  ############################################################################
  def create_portals(self, VIEWING_MANAGER, SCENE_MANAGER, USER, USER_TYPE):
    
    origin_entry = avango.gua.Vec3()
    origin_exit = avango.gua.Vec3()

    portal_width = 1.0
    portal_height = 1.0

    box_size = 0.5

    ############################PORTALBOX#####################################

    ###### ROOM 2#######
    
    ## PortalCube 1

    for room in SCENE_MANAGER.light_rooms:
      if room.NAME == "room2":
        origin_entry = avango.gua.Vec3(room.POSITION.get_translate().x,
                                       room.POSITION.get_translate().y + 1.5,
                                       room.POSITION.get_translate().z)
        
      if room.NAME == "room3":
        origin_exit  = avango.gua.Vec3(room.POSITION.get_translate().x,
                                       room.POSITION.get_translate().y + 1.5,
                                       room.POSITION.get_translate().z)

    self.create_portalcube("portalCube",
                            VIEWING_MANAGER.viewer.SceneGraphs.value[0],
                            VIEWING_MANAGER.viewer.SceneGraphs.value[0],
                            origin_entry,
                            origin_exit,
                            box_size,
                            0,
                            USER.id,
                            USER_TYPE)

    ## PortalCube 2
    
    for room in SCENE_MANAGER.light_rooms:
      if room.NAME == "room2":
        origin_entry = avango.gua.Vec3(room.POSITION.get_translate().x,
                                       room.POSITION.get_translate().y + 1.5,
                                       room.POSITION.get_translate().z)
        
      if room.NAME == "room5":
        origin_exit  = avango.gua.Vec3(room.POSITION.get_translate().x,
                                       room.POSITION.get_translate().y + 1.5,
                                       room.POSITION.get_translate().z)

    self.create_portalcube("portalCube",
                            VIEWING_MANAGER.viewer.SceneGraphs.value[0],
                            VIEWING_MANAGER.viewer.SceneGraphs.value[0],
                            origin_entry,
                            origin_exit,
                            box_size,
                            6,
                            USER.id,
                            USER_TYPE)

    for room in SCENE_MANAGER.light_rooms:
      if room.NAME == "room2":
        # connect PortalCube 1
        room.lightcube.PORTAL_BUTTONS.append(PortalButton())
        index = len(room.lightcube.PORTAL_BUTTONS) - 1
        room.lightcube.PORTAL_BUTTONS[index].my_constructor("room3", room.room_transform, "front")
        self.connect_button_to_cube(USER, USER_TYPE, 0, index, room)

        # connect PortalCube 2
        room.lightcube.PORTAL_BUTTONS.append(PortalButton())
        index = len(room.lightcube.PORTAL_BUTTONS) - 1
        room.lightcube.PORTAL_BUTTONS[index].my_constructor("room5", room.room_transform, "left")
        self.connect_button_to_cube(USER, USER_TYPE, 1, index, room)

    ##### ROOM 3 #####

    ## PortalCube 3

    for room in SCENE_MANAGER.light_rooms:
      if room.NAME == "room3":
        origin_entry = avango.gua.Vec3(room.POSITION.get_translate().x,
                                       room.POSITION.get_translate().y + 1.5,
                                       room.POSITION.get_translate().z)
        
      if room.NAME == "room2":
        origin_exit  = avango.gua.Vec3(room.POSITION.get_translate().x,
                                       room.POSITION.get_translate().y + 1.5,
                                       room.POSITION.get_translate().z)

    self.create_portalcube("portalCube",
                            VIEWING_MANAGER.viewer.SceneGraphs.value[0],
                            VIEWING_MANAGER.viewer.SceneGraphs.value[0],
                            origin_entry,
                            origin_exit,
                            box_size,
                            12,
                            USER.id,
                            USER_TYPE)
    
    ## PortalCube 4

    for room in SCENE_MANAGER.light_rooms:
      if room.NAME == "room3":
        origin_entry = avango.gua.Vec3(room.POSITION.get_translate().x,
                                       room.POSITION.get_translate().y + 1.5,
                                       room.POSITION.get_translate().z)
        
      if room.NAME == "room4":
        origin_exit  = avango.gua.Vec3(room.POSITION.get_translate().x,
                                       room.POSITION.get_translate().y + 1.5,
                                       room.POSITION.get_translate().z)

    self.create_portalcube("portalCube",
                            VIEWING_MANAGER.viewer.SceneGraphs.value[0],
                            VIEWING_MANAGER.viewer.SceneGraphs.value[0],
                            origin_entry,
                            origin_exit,
                            box_size,
                            18,
                            USER.id,
                            USER_TYPE)

    ## PortalCube 5

    for room in SCENE_MANAGER.light_rooms:
      if room.NAME == "room3":
        origin_entry = avango.gua.Vec3(room.POSITION.get_translate().x,
                                       room.POSITION.get_translate().y + 1.5,
                                       room.POSITION.get_translate().z)
        
      if room.NAME == "room6":
        origin_exit  = avango.gua.Vec3(room.POSITION.get_translate().x,
                                       room.POSITION.get_translate().y + 1.5,
                                       room.POSITION.get_translate().z)

    self.create_portalcube("portalCube",
                            VIEWING_MANAGER.viewer.SceneGraphs.value[0],
                            VIEWING_MANAGER.viewer.SceneGraphs.value[0],
                            origin_entry,
                            origin_exit,
                            box_size,
                            24,
                            USER.id,
                            USER_TYPE)
    
    for room in SCENE_MANAGER.light_rooms:
      if room.NAME == "room3":
        # connect portalcube 3
        room.lightcube.PORTAL_BUTTONS.append(PortalButton())
        index = len(room.lightcube.PORTAL_BUTTONS) - 1
        room.lightcube.PORTAL_BUTTONS[index].my_constructor("room2", room.room_transform, "back")
        self.connect_button_to_cube(USER, USER_TYPE, 2, index, room)

        # connect PortalCube 4
        room.lightcube.PORTAL_BUTTONS.append(PortalButton())
        index = len(room.lightcube.PORTAL_BUTTONS) - 1
        room.lightcube.PORTAL_BUTTONS[index].my_constructor("room4", room.room_transform, "front")
        self.connect_button_to_cube(USER, USER_TYPE, 3, index, room)

        # connect PortalCube 5
        room.lightcube.PORTAL_BUTTONS.append(PortalButton())
        index = len(room.lightcube.PORTAL_BUTTONS) - 1
        room.lightcube.PORTAL_BUTTONS[index].my_constructor("room6", room.room_transform, "left")
        self.connect_button_to_cube(USER, USER_TYPE, 4, index, room)

    ##### ROOM 5 #####
   
    ## PortalCube 6
    
    for room in SCENE_MANAGER.light_rooms:
      if room.NAME == "room5":
        origin_entry = avango.gua.Vec3(room.POSITION.get_translate().x,
                                       room.POSITION.get_translate().y + 1.5,
                                       room.POSITION.get_translate().z)
        
      if room.NAME == "room2":
        origin_exit  = avango.gua.Vec3(room.POSITION.get_translate().x,
                                       room.POSITION.get_translate().y + 1.5,
                                       room.POSITION.get_translate().z)

    self.create_portalcube("portalCube",
                            VIEWING_MANAGER.viewer.SceneGraphs.value[0],
                            VIEWING_MANAGER.viewer.SceneGraphs.value[0],
                            origin_entry,
                            origin_exit,
                            box_size,
                            30,
                            USER.id,
                            USER_TYPE)

    ## PortalCube 7
    
    for room in SCENE_MANAGER.light_rooms:
      if room.NAME == "room5":
        origin_entry = avango.gua.Vec3(room.POSITION.get_translate().x,
                                       room.POSITION.get_translate().y + 1.5,
                                       room.POSITION.get_translate().z)
        
      if room.NAME == "room6":
        origin_exit  = avango.gua.Vec3(room.POSITION.get_translate().x,
                                       room.POSITION.get_translate().y + 1.5,
                                       room.POSITION.get_translate().z)

    self.create_portalcube("portalCube",
                            VIEWING_MANAGER.viewer.SceneGraphs.value[0],
                            VIEWING_MANAGER.viewer.SceneGraphs.value[0],
                            origin_entry,
                            origin_exit,
                            box_size,
                            36,
                            USER.id,
                            USER_TYPE)

    for room in SCENE_MANAGER.light_rooms:
      if room.NAME == "room5":
        #connect PortalCube 6
        room.lightcube.PORTAL_BUTTONS.append(PortalButton())
        index = len(room.lightcube.PORTAL_BUTTONS) - 1
        room.lightcube.PORTAL_BUTTONS[index].my_constructor("room2", room.room_transform, "right")
        self.connect_button_to_cube(USER, USER_TYPE, 5, index, room)

        #connect PortalCube 7
        room.lightcube.PORTAL_BUTTONS.append(PortalButton())
        index = len(room.lightcube.PORTAL_BUTTONS) - 1
        room.lightcube.PORTAL_BUTTONS[index].my_constructor("room6", room.room_transform, "front")
        self.connect_button_to_cube(USER, USER_TYPE, 6, index, room)

    ##### ROOM 6 #####
    
    ## PortalCube 8
    
    for room in SCENE_MANAGER.light_rooms:
      if room.NAME == "room6":
        origin_entry = avango.gua.Vec3(room.POSITION.get_translate().x,
                                       room.POSITION.get_translate().y + 1.5,
                                       room.POSITION.get_translate().z)
        
      if room.NAME == "room3":
        origin_exit  = avango.gua.Vec3(room.POSITION.get_translate().x,
                                       room.POSITION.get_translate().y + 1.5,
                                       room.POSITION.get_translate().z)

    self.create_portalcube("portalCube",
                            VIEWING_MANAGER.viewer.SceneGraphs.value[0],
                            VIEWING_MANAGER.viewer.SceneGraphs.value[0],
                            origin_entry,
                            origin_exit,
                            box_size,
                            42,
                            USER.id,
                            USER_TYPE)

    ## PortalCube 9
    
    for room in SCENE_MANAGER.light_rooms:
      if room.NAME == "room6":
        origin_entry = avango.gua.Vec3(room.POSITION.get_translate().x,
                                       room.POSITION.get_translate().y + 1.5,
                                       room.POSITION.get_translate().z)
        
      if room.NAME == "room5":
        origin_exit  = avango.gua.Vec3(room.POSITION.get_translate().x,
                                       room.POSITION.get_translate().y + 1.5,
                                       room.POSITION.get_translate().z)

    self.create_portalcube("portalCube",
                            VIEWING_MANAGER.viewer.SceneGraphs.value[0],
                            VIEWING_MANAGER.viewer.SceneGraphs.value[0],
                            origin_entry,
                            origin_exit,
                            box_size,
                            48,
                            USER.id,
                            USER_TYPE)


    
    for room in SCENE_MANAGER.light_rooms: 
      if room.NAME == "room6":
        # connect PortalCube 8
        room.lightcube.PORTAL_BUTTONS.append(PortalButton())
        index = len(room.lightcube.PORTAL_BUTTONS) - 1
        room.lightcube.PORTAL_BUTTONS[index].my_constructor("room3", room.room_transform, "right")
        self.connect_button_to_cube(USER, USER_TYPE, 7, index, room)

        # connect PortalCube 9
        room.lightcube.PORTAL_BUTTONS.append(PortalButton())
        index = len(room.lightcube.PORTAL_BUTTONS) - 1
        room.lightcube.PORTAL_BUTTONS[index].my_constructor("room5", room.room_transform, "back")
        self.connect_button_to_cube(USER, USER_TYPE, 8, index, room)
   
   
    ########PORTALCONTROLLER########
    
    self.create_portal_controller(VIEWING_MANAGER, USER, USER_TYPE)  

  ## Helper function to create a portal cube for a specified user
  def create_portalcube(self, NAME, ENTRY_SCENE, EXIT_SCENE, ORIGIN_ENTRY, ORIGIN_EXIT, BOX_SIZE, FIRST_PORTAL_ID, USER_ID, USER_TYPE):
    if USER_TYPE == "OVR":
      self.OVR_user_portalcubes[USER_ID].append(PortalCube())
      index = len(self.OVR_user_portalcubes[USER_ID]) - 1
      self.OVR_user_portalcubes[USER_ID][index].my_constructor(NAME,
                                                              ENTRY_SCENE,
                                                              EXIT_SCENE,
                                                              ORIGIN_ENTRY,
                                                              ORIGIN_EXIT,
                                                              BOX_SIZE,
                                                              self.group_names,
                                                              FIRST_PORTAL_ID,
                                                              "OVR",
                                                              str(USER_ID)
                                                              )
    elif USER_TYPE == "PW":
      self.PW_user_portalcubes[USER_ID].append(PortalCube())
      index = len(self.PW_user_portalcubes[USER_ID]) - 1
      self.PW_user_portalcubes[USER_ID][index].my_constructor(NAME,
                                                              ENTRY_SCENE,
                                                              EXIT_SCENE,
                                                              ORIGIN_ENTRY,
                                                              ORIGIN_EXIT,
                                                              BOX_SIZE,
                                                              self.group_names,
                                                              FIRST_PORTAL_ID,
                                                              "PW",
                                                              str(USER_ID)
                                                              )

    elif USER_TYPE == "DESK":
      self.DESK_user_portalcubes[USER_ID].append(PortalCube())
      index = len(self.PW_user_portalcubes[USER_ID]) - 1
      self.DESK_user_portalcubes[USER_ID][index].my_constructor(NAME,
                                                              ENTRY_SCENE,
                                                              EXIT_SCENE,
                                                              ORIGIN_ENTRY,
                                                              ORIGIN_EXIT,
                                                              BOX_SIZE,
                                                              self.group_names,
                                                              FIRST_PORTAL_ID,
                                                              "DESK",
                                                              str(USER_ID)
                                                              )

  ## Helper function to create a portal controller for a specified user
  def create_portal_controller(self, VIEWING_MANAGER, USER, USER_TYPE):
    if USER_TYPE == "OVR":
      USER.portal_controller.my_constructor("controller_OVR_" + str(USER.id),
                                       VIEWING_MANAGER.SCENEGRAPH,
                                       VIEWING_MANAGER.viewer.Pipelines,
                                       USER.pipeline,
                                       self.OVR_user_portals[USER.id],
                                       self.OVR_user_portalcubes[USER.id],
                                       VIEWING_MANAGER.navigation_list[USER.portal_controller.PLATFORM],
                                       USER.head_transform,
                                       ) 
    elif USER_TYPE == "PW":
      USER.portal_controller.my_constructor("controller_PW_" + str(USER.id),
                                       VIEWING_MANAGER.SCENEGRAPH,
                                       VIEWING_MANAGER.viewer.Pipelines,
                                       USER.pipeline,
                                       self.PW_user_portals[USER.id],
                                       self.PW_user_portalcubes[USER.id],
                                       VIEWING_MANAGER.navigation_list[USER.portal_controller.PLATFORM],
                                       USER.head_transform,
                                       )

    elif USER_TYPE == "DESK":
      USER.portal_controller.my_constructor("controller_DESK_" + str(USER.id),
                                       VIEWING_MANAGER.SCENEGRAPH,
                                       VIEWING_MANAGER.viewer.Pipelines,
                                       USER.pipeline,
                                       self.DESK_user_portals[USER.id],
                                       self.DESK_user_portalcubes[USER.id],
                                       VIEWING_MANAGER.navigation_list[USER.portal_controller.PLATFORM],
                                       USER.head_transform,
                                       )

  ## Helper function to connect a field to the visibility property of a PortalCube 
  def connect_button_to_cube(self, USER, USER_TYPE, NUM_CUBE, NUM_BUTTON, ROOM):
    if USER_TYPE == "OVR":
      self.OVR_user_portalcubes[USER.id][NUM_CUBE].sf_visibility.connect_from(ROOM.lightcube.PORTAL_BUTTONS[NUM_BUTTON].sf_portal_active)
    elif USER_TYPE == "PW":
      self.PW_user_portalcubes[USER.id][NUM_CUBE].sf_visibility.connect_from(ROOM.lightcube.PORTAL_BUTTONS[NUM_BUTTON].sf_portal_active)
    elif USER_TYPE == "DESK":
      self.DESK_user_portalcubes[USER.id][NUM_CUBE].sf_visibility.connect_from(ROOM.lightcube.PORTAL_BUTTONS[NUM_BUTTON].sf_portal_active)
