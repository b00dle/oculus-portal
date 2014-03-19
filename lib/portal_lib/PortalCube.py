#!/usr/bin/python

# import guacamole libraries
import avango
import avango.script
from avango.script import field_has_changed
import avango.gua

from Portal import *

## Internal representation of a portal in cube shape
#
# this class instances 6 portals in a cube ordered manner
# it works as a container and does not provide further functionality
class PortalCube(avango.script.Script):
  
  sf_visibility = avango.SFBool()

  def __init__(self):
    self.super(PortalCube).__init__()

    self.NAME                   = ""
    self.ENTRY_SCENE            = avango.gua.nodes.SceneGraph()
    self.EXIT_SCENE             = avango.gua.nodes.SceneGraph()
    self.ENTRY_ORIGIN           = avango.gua.Vec3()
    self.EXIT_ORIGIN            = avango.gua.Vec3()
    self.SIZE                   = 1.0
    self.EXCLUDE_GROUPS         = []
    self.FIRST_PORTAL_ID        = 0
    self.USER_TYPE              = ""
    self.USER_ID                = 0

    self.Portals              = []
    self.sf_visibility.value    = True
    self.visibility_updated     = False

  ## Custom constructor
  # 
  # NAME              Name of the portal cube
  # ENTRY_SCENE       SceneGraph to append the portal geometries to
  # EXIT_SCENE        SceneGraph to be displayed by the portal cube
  # ENTRY_ORIGIN      Center of mass of the portal cube in the scene it is displayed in
  # EXIT_ORIGIN       Center of mass of the portal cube in the scene it displayes
  # SIZE              Scaling factor for the portal geometries
  # EXCLUDE_GROUPS    Extends the RenderMask of the camera rendering the view being displayed
  # FIRST_PORTAL_ID   Starting id to be used for naming all portals in the cube (will be iteratively raised for each protal)
  # USER_TYPE         Type of the user the cube should belong to (OVR"/"PW"/"DESK")
  # USER_ID           ID of the user the cube should belong to
  def my_constructor(self, NAME, ENTRY_SCENE, EXIT_SCENE, ENTRY_ORIGIN, EXIT_ORIGIN, SIZE, EXCLUDE_GROUPS, FIRST_PORTAL_ID, USER_TYPE, USER_ID, VISIBLE = True):
    self.NAME                   = NAME
    self.ENTRY_SCENE            = ENTRY_SCENE
    self.EXIT_SCENE             = EXIT_SCENE
    self.ENTRY_ORIGIN           = ENTRY_ORIGIN
    self.EXIT_ORIGIN            = EXIT_ORIGIN
    self.SIZE                   = SIZE
    self.EXCLUDE_GROUPS         = EXCLUDE_GROUPS
    self.FIRST_PORTAL_ID        = FIRST_PORTAL_ID
    self.USER_TYPE              = USER_TYPE
    self.USER_ID                = USER_ID

    self.sf_visibility.value  = VISIBLE
    if VISIBLE == False:
      self.visibility_updated = True

    self.create_portals()

  ## toggles the visibility_updated flag if sf_visibility field changes
  @field_has_changed(sf_visibility)
  def resolve_visibility(self):
    self.visibility_updated = True

  ## creates all 6 faces of the portal cube
  def create_portals(self):
    #############PORTAL 0##############
    entry_pos = avango.gua.make_trans_mat(self.ENTRY_ORIGIN.x,
                                          self.ENTRY_ORIGIN.y,
                                          self.ENTRY_ORIGIN.z + self.SIZE/2)
      
    exit_pos  = avango.gua.make_trans_mat(self.EXIT_ORIGIN.x,
                                          self.EXIT_ORIGIN.y,
                                          self.EXIT_ORIGIN.z + self.SIZE/2)
    
    self.Portals.append(Portal())
    self.Portals[0].my_constructor("portal_" + str(self.FIRST_PORTAL_ID) + "_" + self.USER_TYPE + "_" + str(self.USER_ID),
                                  self.ENTRY_SCENE, 
                                  self.EXIT_SCENE,
                                  entry_pos,
                                  exit_pos,
                                  self.SIZE,
                                  self.SIZE,
                                  self.USER_TYPE + "_" + str(self.USER_ID) + "_portals",
                                  self.EXCLUDE_GROUPS,
                                  True
                                  )
    
    #############PORTAL 1##############
    entry_pos = avango.gua.make_trans_mat(self.ENTRY_ORIGIN.x,
                                          self.ENTRY_ORIGIN.y,
                                          self.ENTRY_ORIGIN.z - self.SIZE/2) * \
                avango.gua.make_rot_mat(180, 0, 1, 0)

    exit_pos  = avango.gua.make_trans_mat(self.EXIT_ORIGIN.x,
                                          self.EXIT_ORIGIN.y,
                                          self.EXIT_ORIGIN.z - self.SIZE/2) * \
                avango.gua.make_rot_mat(180, 0, 1, 0)

    self.Portals.append(Portal())
    self.Portals[1].my_constructor("portal_" + str(self.FIRST_PORTAL_ID + 1) + "_" + self.USER_TYPE + "_" + str(self.USER_ID),
                                  self.ENTRY_SCENE,
                                  self.EXIT_SCENE,
                                  entry_pos,
                                  exit_pos,
                                  self.SIZE,
                                  self.SIZE,
                                  self.USER_TYPE + "_" + str(self.USER_ID) + "_portals",
                                  self.EXCLUDE_GROUPS,
                                  True
                                  )
    
    #############PORTAL 2##############
    entry_pos = avango.gua.make_trans_mat(self.ENTRY_ORIGIN.x,
                                          self.ENTRY_ORIGIN.y - self.SIZE/2,
                                          self.ENTRY_ORIGIN.z) * \
                avango.gua.make_rot_mat(-90, 1, 0, 0) * \
                avango.gua.make_rot_mat(180, 0, 1, 0)

    exit_pos  = avango.gua.make_trans_mat(self.EXIT_ORIGIN.x,
                                          self.EXIT_ORIGIN.y - self.SIZE/2,
                                          self.EXIT_ORIGIN.z) * \
                avango.gua.make_rot_mat(-90, 1, 0, 0) * \
                avango.gua.make_rot_mat(180, 0, 1, 0)

    self.Portals.append(Portal())
    self.Portals[2].my_constructor("portal_" + str(self.FIRST_PORTAL_ID + 2) + "_" + self.USER_TYPE + "_" + str(self.USER_ID),
                                  self.ENTRY_SCENE,
                                  self.EXIT_SCENE,
                                  entry_pos,
                                  exit_pos,
                                  self.SIZE,
                                  self.SIZE,
                                  self.USER_TYPE + "_" + str(self.USER_ID) + "_portals",
                                  self.EXCLUDE_GROUPS,
                                  True
                                  )
    
    #############PORTAL 3##############
    entry_pos = avango.gua.make_trans_mat(self.ENTRY_ORIGIN.x,
                                          self.ENTRY_ORIGIN.y + self.SIZE/2,
                                          self.ENTRY_ORIGIN.z) * \
                avango.gua.make_rot_mat(90, 1, 0, 0) * \
                avango.gua.make_rot_mat(180, 0, 1, 0)

    exit_pos  = avango.gua.make_trans_mat(self.EXIT_ORIGIN.x,
                                          self.EXIT_ORIGIN.y + self.SIZE/2,
                                          self.EXIT_ORIGIN.z) * \
                avango.gua.make_rot_mat(90, 1, 0, 0) * \
                avango.gua.make_rot_mat(180, 0, 1, 0)

    self.Portals.append(Portal())
    self.Portals[3].my_constructor("portal_" + str(self.FIRST_PORTAL_ID + 3) + "_"  + self.USER_TYPE + "_" + str(self.USER_ID),
                                  self.ENTRY_SCENE,
                                  self.EXIT_SCENE,
                                  entry_pos,
                                  exit_pos,
                                  self.SIZE,
                                  self.SIZE,
                                  self.USER_TYPE + "_" + str(self.USER_ID) + "_portals",
                                  self.EXCLUDE_GROUPS,
                                  True
                                  )
    
    #############PORTAL 4##############
    entry_pos = avango.gua.make_trans_mat(self.ENTRY_ORIGIN.x - self.SIZE/2,
                                          self.ENTRY_ORIGIN.y,
                                          self.ENTRY_ORIGIN.z) * \
                avango.gua.make_rot_mat(-90, 0, 1, 0)

    exit_pos  = avango.gua.make_trans_mat(self.EXIT_ORIGIN.x - self.SIZE/2,
                                          self.EXIT_ORIGIN.y,
                                          self.EXIT_ORIGIN.z) * \
                avango.gua.make_rot_mat(-90, 0, 1, 0)

    self.Portals.append(Portal())
    self.Portals[4].my_constructor("portal_" + str(self.FIRST_PORTAL_ID + 4) + "_" + self.USER_TYPE + "_" + str(self.USER_ID),
                                  self.ENTRY_SCENE,
                                  self.EXIT_SCENE,
                                  entry_pos,
                                  exit_pos,
                                  self.SIZE,
                                  self.SIZE,
                                  self.USER_TYPE + "_" + str(self.USER_ID) + "_portals",
                                  self.EXCLUDE_GROUPS,
                                  True
                                  )
    
    #############PORTAL 5##############
    entry_pos = avango.gua.make_trans_mat(self.ENTRY_ORIGIN.x + self.SIZE/2,
                                          self.ENTRY_ORIGIN.y,
                                          self.ENTRY_ORIGIN.z) * \
                avango.gua.make_rot_mat(90, 0, 1, 0)

    exit_pos  = avango.gua.make_trans_mat(self.EXIT_ORIGIN.x + self.SIZE/2,
                                          self.EXIT_ORIGIN.y,
                                          self.EXIT_ORIGIN.z) * \
                avango.gua.make_rot_mat(90, 0, 1, 0)

    self.Portals.append(Portal())
    self.Portals[5].my_constructor("portal_" + str(self.FIRST_PORTAL_ID + 5) + "_"  + self.USER_TYPE + "_" + str(self.USER_ID),
                                  self.ENTRY_SCENE,
                                  self.EXIT_SCENE,
                                  entry_pos,
                                  exit_pos,
                                  self.SIZE,
                                  self.SIZE,
                                  self.USER_TYPE + "_" + str(self.USER_ID) + "_portals",
                                  self.EXCLUDE_GROUPS,
                                  True
                                  )
