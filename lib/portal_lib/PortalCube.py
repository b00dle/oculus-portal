#!/usr/bin/python

# import guacamole libraries
import avango
import avango.script
from avango.script import field_has_changed
import avango.gua

from Portal import *

class PortalCube(avango.script.Script):
  
  sf_visibility = avango.SFBool()

  def __init__(self):
    self.super(PortalCube).__init__()

    self.Portals              = []
    
    self.NAME                 = ""
    self.ENTRYSCENE           = avango.gua.nodes.SceneGraph()
    self.EXITSCENE            = avango.gua.nodes.SceneGraph()
    self.ENTRYORIGIN          = avango.gua.Vec3()
    self.EXITORIGIN           = avango.gua.Vec3()
    self.SIZE                 = 1.0
    self.EXCLUDEGROUPS        = []
    self.FIRSTPORTALID        = 0
    self.USERTYPE             = ""
    self.USERID               = 0

    self.sf_visibility.value  = True
    self.visibility_updated  = False

  def my_constructor(self, NAME, ENTRYSCENE, EXITSCENE, ENTRYORIGIN, EXITORIGIN, SIZE, EXCLUDEGROUPS, FIRSTPORTALID, USERTYPE, USERID, VISIBLE = True):
    self.NAME                 = NAME
    self.ENTRYSCENE           = ENTRYSCENE
    self.EXITSCENE            = EXITSCENE
    self.ENTRYORIGIN          = ENTRYORIGIN
    self.EXITORIGIN           = EXITORIGIN
    self.SIZE                 = SIZE
    self.EXCLUDEGROUPS        = EXCLUDEGROUPS
    self.FIRSTPORTALID        = FIRSTPORTALID
    self.USERTYPE             = USERTYPE
    self.USERID               = USERID

    self.sf_visibility.value  = VISIBLE
    if VISIBLE == False:
      self.visibility_updated = True

    self.create_portals()

  @field_has_changed(sf_visibility)
  def resolve_visibility(self):
    self.visibility_updated = True

  def create_portals(self):
    #############PORTAL 1##############
    entry_pos = avango.gua.make_trans_mat(self.ENTRYORIGIN.x,
                                          self.ENTRYORIGIN.y,
                                          self.ENTRYORIGIN.z + self.SIZE/2)
      
    exit_pos  = avango.gua.make_trans_mat(self.EXITORIGIN.x,
                                          self.EXITORIGIN.y,
                                          self.EXITORIGIN.z + self.SIZE/2)
    
    self.Portals.append(Portal())
    self.Portals[0].my_constructor("portal_" + str(self.FIRSTPORTALID) + "_" + self.USERTYPE + "_" + str(self.USERID),
                                  self.ENTRYSCENE, #simplescene
                                  self.EXITSCENE,
                                  entry_pos,
                                  exit_pos,
                                  self.SIZE,
                                  self.SIZE,
                                  self.USERTYPE + "_" + str(self.USERID) + "_portals",
                                  self.EXCLUDEGROUPS,
                                  True
                                  )

    #############PORTAL 1##############
    entry_pos = avango.gua.make_trans_mat(self.ENTRYORIGIN.x,
                                          self.ENTRYORIGIN.y,
                                          self.ENTRYORIGIN.z - self.SIZE/2) * \
                avango.gua.make_rot_mat(180, 0, 1, 0)

    exit_pos  = avango.gua.make_trans_mat(self.EXITORIGIN.x,
                                          self.EXITORIGIN.y,
                                          self.EXITORIGIN.z - self.SIZE/2) * \
                avango.gua.make_rot_mat(180, 0, 1, 0)

    self.Portals.append(Portal())
    self.Portals[1].my_constructor("portal_" + str(self.FIRSTPORTALID + 1) + "_" + self.USERTYPE + "_" + str(self.USERID),
                                  self.ENTRYSCENE, #simplescene
                                  self.EXITSCENE,
                                  entry_pos,
                                  exit_pos,
                                  self.SIZE,
                                  self.SIZE,
                                  self.USERTYPE + "_" + str(self.USERID) + "_portals",
                                  self.EXCLUDEGROUPS,
                                  False
                                  )

    #############PORTAL 2##############
    entry_pos = avango.gua.make_trans_mat(self.ENTRYORIGIN.x,
                                          self.ENTRYORIGIN.y - self.SIZE/2,
                                          self.ENTRYORIGIN.z) * \
                avango.gua.make_rot_mat(-90, 1, 0, 0) * \
                avango.gua.make_rot_mat(180, 0, 1, 0)

    exit_pos  = avango.gua.make_trans_mat(self.EXITORIGIN.x,
                                          self.EXITORIGIN.y - self.SIZE/2,
                                          self.EXITORIGIN.z) * \
                avango.gua.make_rot_mat(-90, 1, 0, 0) * \
                avango.gua.make_rot_mat(180, 0, 1, 0)

    self.Portals.append(Portal())
    self.Portals[2].my_constructor("portal_" + str(self.FIRSTPORTALID + 2) + "_" + self.USERTYPE + "_" + str(self.USERID),
                                  self.ENTRYSCENE, #simplescene
                                  self.EXITSCENE,
                                  entry_pos,
                                  exit_pos,
                                  self.SIZE,
                                  self.SIZE,
                                  self.USERTYPE + "_" + str(self.USERID) + "_portals",
                                  self.EXCLUDEGROUPS,
                                  False
                                  )

    #############PORTAL 3##############
    entry_pos = avango.gua.make_trans_mat(self.ENTRYORIGIN.x,
                                          self.ENTRYORIGIN.y + self.SIZE/2,
                                          self.ENTRYORIGIN.z) * \
                avango.gua.make_rot_mat(90, 1, 0, 0) * \
                avango.gua.make_rot_mat(180, 0, 1, 0)

    exit_pos  = avango.gua.make_trans_mat(self.EXITORIGIN.x,
                                          self.EXITORIGIN.y + self.SIZE/2,
                                          self.EXITORIGIN.z) * \
                avango.gua.make_rot_mat(90, 1, 0, 0) * \
                avango.gua.make_rot_mat(180, 0, 1, 0)

    self.Portals.append(Portal())
    self.Portals[3].my_constructor("portal_" + str(self.FIRSTPORTALID + 3) + "_"  + self.USERTYPE + "_" + str(self.USERID),
                                  self.ENTRYSCENE, #simplescene
                                  self.EXITSCENE,
                                  entry_pos,
                                  exit_pos,
                                  self.SIZE,
                                  self.SIZE,
                                  self.USERTYPE + "_" + str(self.USERID) + "_portals",
                                  self.EXCLUDEGROUPS,
                                  False
                                  )

    #############PORTAL 4##############
    entry_pos = avango.gua.make_trans_mat(self.ENTRYORIGIN.x - self.SIZE/2,
                                          self.ENTRYORIGIN.y,
                                          self.ENTRYORIGIN.z) * \
                avango.gua.make_rot_mat(-90, 0, 1, 0)

    exit_pos  = avango.gua.make_trans_mat(self.EXITORIGIN.x - self.SIZE/2,
                                          self.EXITORIGIN.y,
                                          self.EXITORIGIN.z) * \
                avango.gua.make_rot_mat(-90, 0, 1, 0)

    self.Portals.append(Portal())
    self.Portals[4].my_constructor("portal_" + str(self.FIRSTPORTALID + 4) + "_" + self.USERTYPE + "_" + str(self.USERID),
                                  self.ENTRYSCENE, #simplescene
                                  self.EXITSCENE,
                                  entry_pos,
                                  exit_pos,
                                  self.SIZE,
                                  self.SIZE,
                                  self.USERTYPE + "_" + str(self.USERID) + "_portals",
                                  self.EXCLUDEGROUPS,
                                  False
                                  )

    #############PORTAL 5##############
    entry_pos = avango.gua.make_trans_mat(self.ENTRYORIGIN.x + self.SIZE/2,
                                          self.ENTRYORIGIN.y,
                                          self.ENTRYORIGIN.z) * \
                avango.gua.make_rot_mat(90, 0, 1, 0)

    exit_pos  = avango.gua.make_trans_mat(self.EXITORIGIN.x + self.SIZE/2,
                                          self.EXITORIGIN.y,
                                          self.EXITORIGIN.z) * \
                avango.gua.make_rot_mat(90, 0, 1, 0)

    self.Portals.append(Portal())
    self.Portals[5].my_constructor("portal_" + str(self.FIRSTPORTALID + 5) + "_"  + self.USERTYPE + "_" + str(self.USERID),
                                  self.ENTRYSCENE, #simplescene 
                                  self.EXITSCENE,
                                  entry_pos,
                                  exit_pos,
                                  self.SIZE,
                                  self.SIZE,
                                  self.USERTYPE + "_" + str(self.USERID) + "_portals",
                                  self.EXCLUDEGROUPS,
                                  False
                                  )

    if self.sf_visibility == False:
      for portal in self.Portals:
        if "do_not_display_group" not in portal.GEOMETRY.GroupNames.value:
          portal.GEOMETRY.GroupNames.value.append("do_not_display_group")

