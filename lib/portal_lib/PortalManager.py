#!/usr/bin/python

# import guacamole libraries
import avango
import avango.gua

from Portal import *
from PortalController import *

class PortalManager():
  def __init__(self, VIEWINGMANAGER):
    # lists of all portals for each user
    self.PW_user_portals    = [ [] for i in range( len(VIEWINGMANAGER.powerwall_user_list) )]
    self.OVR_user_portals   = [ [] for i in range( len(VIEWINGMANAGER.ovr_user_list)       )]
    self.DESK_user_portals  = [ [] for i in range( len(VIEWINGMANAGER.desktop_user_list)   )]
    self.group_names        = []

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
      portal_width = 3.0
      portal_height = 3.0

      
      # position of portal in the active world 
      entry_pos = avango.gua.make_trans_mat(0,1.50,-6)
      # position of portal in the world we are looking into
      exit_pos = avango.gua.make_trans_mat(2.0,1.70,0.0) * avango.gua.make_trans_mat(0.0, 5.0, 40.0)
      

      #############PORTAL 1##############
      loader = avango.gua.nodes.GeometryLoader()
      frame = loader.create_geometry_from_file('frame',
                                                'data/objects/portal_edgy_no_plane_size_one.obj',
                                                'Stones',
                                                avango.gua.LoaderFlags.DEFAULTS | \
                                                avango.gua.LoaderFlags.MAKE_PICKABLE)
      frame.Transform.value = avango.gua.make_scale_mat(portal_width, portal_height, 3.0)

      portalGeom = loader.create_geometry_from_file('portal',
                                                    'data/objects/portal_edgy_size_one.obj',
                                                    'Stones',
                                                    avango.gua.LoaderFlags.DEFAULTS | \
                                                    avango.gua.LoaderFlags.MAKE_PICKABLE)

      self.PW_user_portals[PW_user.id].append(Portal())
      self.PW_user_portals[PW_user.id][0].my_constructor("portal_0_PW_" + str(PW_user.id),
                                            VIEWINGMANAGER.viewer.SceneGraphs.value[0], #simplescene
                                            VIEWINGMANAGER.viewer.SceneGraphs.value[1],
                                            entry_pos,
                                            exit_pos,
                                            portal_width,
                                            portal_height,
                                            "PW_" + str(PW_user.id) + "_portals",
                                            self.group_names,
                                            portalGeom
                                            )


      # Change Pipeline Settings
      self.PW_user_portals[PW_user.id][0].PRE_PIPE.BackgroundTexture.value = "data/textures/painted_ships.jpg"
      self.PW_user_portals[PW_user.id][0].PRE_PIPE.EnableBackfaceCulling.value = False

      #############PORTAL 2##############
      portal_width = 2.0
      portal_height = 3.0

      entry_pos = avango.gua.make_trans_mat(-1.4,1.50,-5.1)
      exit_pos  = avango.gua.make_trans_mat(2.0,1.70,0.0)

      self.PW_user_portals[PW_user.id].append(Portal())
      self.PW_user_portals[PW_user.id][1].my_constructor("portal_1_PW_" + str(PW_user.id),
                                            VIEWINGMANAGER.viewer.SceneGraphs.value[1], #simplescene
                                            VIEWINGMANAGER.viewer.SceneGraphs.value[0],
                                            entry_pos,
                                            exit_pos,
                                            portal_width,
                                            portal_height,
                                            "PW_" + str(PW_user.id) + "_portals",
                                            self.group_names
                                            )
      self.PW_user_portals[OVR_user.id][0].append_node(frame)

      ########PORTALCONTROLLER########
      PW_user.portal_controller.my_constructor(VIEWINGMANAGER.SCENEGRAPH,
                                         "controller_PW_" + str(PW_user.id),
                                         VIEWINGMANAGER.viewer.Pipelines,
                                         PW_user.pipeline,
                                         self.PW_user_portals[PW_user.id],
                                         VIEWINGMANAGER.navigation_list[PW_user.portal_controller.PLATFORM],
                                         PW_user.head_transform,
                                         PW_user.screen.WorldTransform
                                         )

    for OVR_user in VIEWINGMANAGER.ovr_user_list:
      # Size for Portal:
      portal_width = 3.0
      portal_height = 3.0

      
      # position of portal in the active world 
      entry_pos = avango.gua.make_trans_mat(0,1.50,-6)
      # position of portal in the world we are looking into
      exit_pos = avango.gua.make_trans_mat(2.0,1.70,0.0) * avango.gua.make_trans_mat(0.0, 5.0, 40.0)
      

      #############PORTAL 1##############
      loader = avango.gua.nodes.GeometryLoader()
      frame = loader.create_geometry_from_file('frame',
                                                'data/objects/portal_edgy_no_plane_size_one.obj',
                                                'Stones',
                                                avango.gua.LoaderFlags.DEFAULTS | \
                                                avango.gua.LoaderFlags.MAKE_PICKABLE)
      frame.Transform.value = avango.gua.make_scale_mat(portal_width, portal_height, 3.0)

      portalGeom = loader.create_geometry_from_file('portal',
                                                    'data/objects/portal_edgy_size_one.obj',
                                                    'Stones',
                                                    avango.gua.LoaderFlags.DEFAULTS | \
                                                    avango.gua.LoaderFlags.MAKE_PICKABLE)

      self.OVR_user_portals[OVR_user.id].append(Portal())
      self.OVR_user_portals[OVR_user.id][0].my_constructor("portal_0_OVR_" + str(OVR_user.id),
                                            VIEWINGMANAGER.viewer.SceneGraphs.value[0], #simplescene
                                            VIEWINGMANAGER.viewer.SceneGraphs.value[1],
                                            entry_pos,
                                            exit_pos,
                                            portal_width,
                                            portal_height,
                                            "OVR_" + str(OVR_user.id) + "_portals",
                                            self.group_names,
                                            portalGeom
                                            )
      self.OVR_user_portals[OVR_user.id][0].append_node(frame)      

      # Change Pipeline Settings
      self.OVR_user_portals[OVR_user.id][0].PRE_PIPE.BackgroundTexture.value = "data/textures/painted_ships.jpg"
      self.OVR_user_portals[OVR_user.id][0].PRE_PIPE.EnableBackfaceCulling.value = False

      #############PORTAL 2##############
      portal_width = 2.0
      portal_height = 3.0

      entry_pos = avango.gua.make_trans_mat(-1.4,1.50,-5.1)
      exit_pos  = avango.gua.make_trans_mat(2.0,1.70,0.0)

      self.OVR_user_portals[OVR_user.id].append(Portal())
      self.OVR_user_portals[OVR_user.id][1].my_constructor("portal_1_OVR_" + str(OVR_user.id),
                                            VIEWINGMANAGER.viewer.SceneGraphs.value[1], #simplescene
                                            VIEWINGMANAGER.viewer.SceneGraphs.value[0],
                                            entry_pos,
                                            exit_pos,
                                            portal_width,
                                            portal_height,
                                            "OVR_" + str(OVR_user.id) + "_portals",
                                            self.group_names
                                            )

      ########PORTALCONTROLLER########
      OVR_user.portal_controller.my_constructor(VIEWINGMANAGER.SCENEGRAPH,
                                         "controller_OVR_" + str(OVR_user.id),
                                         VIEWINGMANAGER.viewer.Pipelines,
                                         OVR_user.pipeline,
                                         self.OVR_user_portals[OVR_user.id],
                                         VIEWINGMANAGER.navigation_list[OVR_user.portal_controller.PLATFORM],
                                         OVR_user.head_transform,
                                         OVR_user.left_screen.WorldTransform,
                                         True #apply additional rule for portal_controller > UpdatePortalTransform
                                         )

    for DESK_user in VIEWINGMANAGER.desktop_user_list:
      # Size for Portal:
      portal_width = 3.0
      portal_height = 3.0

      
      # position of portal in the active world 
      entry_pos = avango.gua.make_trans_mat(0,1.50,-6)
      exit_pos = avango.gua.make_trans_mat(2.0,1.70,0.0) * avango.gua.make_trans_mat(0.0, 5.0, 40.0)
      

      #############PORTAL 1##############
      loader = avango.gua.nodes.GeometryLoader()
      frame = loader.create_geometry_from_file('frame',
                                                'data/objects/portal_edgy_no_plane_size_one.obj',
                                                'Stones',
                                                avango.gua.LoaderFlags.DEFAULTS | \
                                                avango.gua.LoaderFlags.MAKE_PICKABLE)
      frame.Transform.value = avango.gua.make_scale_mat(portal_width, portal_height, 3.0)

      portalGeom = loader.create_geometry_from_file('portal',
                                                    'data/objects/portal_edgy_size_one.obj',
                                                    'Stones',
                                                    avango.gua.LoaderFlags.DEFAULTS | \
                                                    avango.gua.LoaderFlags.MAKE_PICKABLE)

      self.DESK_user_portals[DESK_user.id].append(Portal())
      self.DESK_user_portals[DESK_user.id][0].my_constructor("portal_0_DESK_" + str(DESK_user.id),
                                            VIEWINGMANAGER.viewer.SceneGraphs.value[0], #simplescene
                                            VIEWINGMANAGER.viewer.SceneGraphs.value[1],
                                            entry_pos,
                                            exit_pos,
                                            portal_width,
                                            portal_height,
                                            "DESK_" + str(DESK_user.id) + "_portals",
                                            self.group_names,
                                            portalGeom
                                            )
      self.DESK_user_portals[DESK_user.id][0].append_node(frame)
      
      # Change Pipeline Settings
      self.DESK_user_portals[DESK_user.id][0].PRE_PIPE.BackgroundTexture.value = "data/textures/painted_ships.jpg"
      self.DESK_user_portals[DESK_user.id][0].PRE_PIPE.EnableBackfaceCulling.value = False

      #############PORTAL 2##############
      portal_width = 2.0
      portal_height = 3.0

      entry_pos = avango.gua.make_trans_mat(-1.4,1.50,-5.1)
      exit_pos  = avango.gua.make_trans_mat(2.0,1.70,0.0)

      self.DESK_user_portals[DESK_user.id].append(Portal())
      self.DESK_user_portals[DESK_user.id][1].my_constructor("portal_1_DESK_" + str(DESK_user.id),
                                            VIEWINGMANAGER.viewer.SceneGraphs.value[1], #simplescene
                                            VIEWINGMANAGER.viewer.SceneGraphs.value[0],
                                            entry_pos,
                                            exit_pos,
                                            portal_width,
                                            portal_height,
                                            "DESK_" + str(DESK_user.id) + "_portals",
                                            self.group_names
                                            )

      ########PORTALCONTROLLER########
      DESK_user.portal_controller.my_constructor(VIEWINGMANAGER.SCENEGRAPH,
                                         "controller_DESK_" + str(DESK_user.id),
                                         VIEWINGMANAGER.viewer.Pipelines,
                                         DESK_user.pipeline,
                                         self.DESK_user_portals[DESK_user.id],
                                         VIEWINGMANAGER.navigation_list[DESK_user.portal_controller.PLATFORM],
                                         DESK_user.head_transform,
                                         DESK_user.screen.WorldTransform
                                         )
