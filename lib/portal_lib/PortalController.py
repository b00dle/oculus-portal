#!/usr/bin/python

import avango
import avango.script
from avango.script import field_has_changed
import avango.gua
import time
import math

from examples_common.GuaVE import GuaVE

from ..Navigation import *

class PortalPicker(avango.script.Script):
  SceneGraph = avango.gua.SFSceneGraph()
  Ray        = avango.gua.SFRayNode()
  Options    = avango.SFInt()
  Mask       = avango.SFString()
  Results    = avango.gua.MFPickResult()

  def __init__(self):
    self.super(PortalPicker).__init__()
    self.always_evaluate(True)

    self.SceneGraph.value = avango.gua.nodes.SceneGraph()
    self.Ray.value  = avango.gua.nodes.RayNode()
    self.Options.value = avango.gua.PickingOptions.PICK_ONLY_FIRST_OBJECT \
                         | avango.gua.PickingOptions.PICK_ONLY_FIRST_FACE
    self.Mask.value = ""
    
  def evaluate(self):
    results = self.SceneGraph.value.ray_test(self.Ray.value,
                                             self.Options.value,
                                             self.Mask.value)
    self.Results.value = results.value

class UpdatePortalTransform(avango.script.Script):

  PortalTransformIn     = avango.gua.SFMatrix4()
  ViewTransformIn       = avango.gua.SFMatrix4()
  ScreenTransformIn     = avango.gua.SFMatrix4()
  ViewTransformOut      = avango.gua.SFMatrix4()

  def __init__(self):
    self.super(UpdatePortalTransform).__init__()
    self.NAME = ""

  def my_constructor(self, NAME):
    self.NAME = NAME

  def evaluate(self):
    self.ViewTransformOut.value = avango.gua.make_inverse_mat(self.PortalTransformIn.value) *\
                                    self.ScreenTransformIn.value * avango.gua.make_trans_mat(0.0,0.0,self.ViewTransformIn.value.get_translate().z)
    
class PortalController(avango.script.Script):
  PickedPortals     = avango.gua.MFPickResult()
  sfUserHead        = avango.gua.SFMatrix4()
  sfUserScreen      = avango.gua.SFMatrix4()
  
  def __init__(self):
    self.super(PortalController).__init__()
    self.NAME           = ""
    self.ACTIVESCENE    = avango.gua.nodes.SceneGraph()
    self.PORTALPICKER   = PortalPicker()
    self.PIPELINE       = avango.gua.nodes.Pipeline()
    self.PORTALS        = []
    self.ACTIVEPORTALS  = []
    self.NAVIGATION     = Navigation()
    self.PORTALUPDATERS = []
    self.PLATFORM       = -1
    self.stop_eval      = False

  def my_constructor(self, ACTIVESCENE, NAME, VIEWINGPIPELINES, PIPELINE, PORTALS, NAVIGATION, SF_USERHEAD, SF_USERSCREEN, USER):
    self.NAME             = NAME
    self.ACTIVESCENE      = ACTIVESCENE
    self.VIEWINGPIPELINES = VIEWINGPIPELINES
    self.PIPELINE         = PIPELINE
    self.PORTALS          = PORTALS
    
    self.update_prepipes()

    self.ACTIVEPORTALS    = self.create_active_portals()      
    self.NAVIGATION       = NAVIGATION

    self.USER             = USER

    #self.sfUserHead.connect_from(SF_USERHEAD)
    #self.sfUserScreen.connect_from(SF_USERSCREEN)     

    #self.PORTALUPDATERS   = self.create_portal_updaters()
    #self.create_portal_updaters()
    
    self.initialize_portal_group_names()
    self.update_prepipes()
    self.update_portal_picker()

  #@field_has_changed(PickedPortals)
  #def evaluate_scene_change(self):
    #_platform = self.ACTIVESCENE["/platform_" + str(self.PLATFORM)]

    #_pos_p1 = _platform.Transform.value.get_translate()
    
    #for i in range(0, len(self.PickedPortals.value)):
    #  if(self.PickedPortals.value[i].Distance.value < 0.5):
    #    portalName = self.PickedPortals.value[i].Object.value.Name.value
    #    for p in self.ACTIVEPORTALS:
    #      if(p.GEOMETRY.Name.value == portalName):
    #        _pos_p2 = p.GEOMETRY.Transform.value.get_translate()
    #        _distance_x = _pos_p1.x - _pos_p2.x
    #        _distance_y = _pos_p1.y - _pos_p2.y
    #        self.change_scene(p, _distance_x, _distance_y)
    #        break
    #  break

    #self.adjust_nearplane()

  def evaluate(self):
    if self.PLATFORM != -1:
      self.sfUserScreen.connect_from(self.USER.screen.WorldTransform)
      self.sfUserHead.connect_from(self.USER.head_transform.Transform)
      self.adjust_nearplane()
    
  def change_scene(self, PORTAL, DISTANCE_X, DISTANCE_Y):
    #_platform = self.NAVIGATION.platform
    _platform = self.ACTIVESCENE["/platform_" + str(self.PLATFORM)]

    _rotate_old_scene = _platform.Transform.value.get_rotate()
    
    # Disconnect old members
    self.PORTALPICKER.Ray.value.Transform.disconnect_from(_platform.Transform)

    for p in self.ACTIVEPORTALS:
      p.EXITSCENE[p.HEAD].disconnect_all_fields()
      p.EXITSCENE["/" + p.NAME + "Screen"].disconnect_all_fields()
      p.GEOMETRY.disconnect_all_fields()
    
    for up in self.PORTALUPDATERS:
      up.disconnect_all_fields()
        
    # Set new Members
    self.ACTIVESCENE = PORTAL.EXITSCENE
    
    self.NAVIGATION.platform.change_scene(self.ACTIVESCENE)

    # Starting Position
    new_pos = avango.gua.make_trans_mat(PORTAL.EXITPOS.get_translate().x + DISTANCE_X, 
                                        PORTAL.EXITPOS.get_translate().y + DISTANCE_Y,
                                        PORTAL.EXITPOS.get_translate().z)

    # Starting Rotation
    new_rot = avango.gua.make_rot_mat(_rotate_old_scene)

    self.NAVIGATION.set_to_pos(new_rot * new_pos)
    #self.SCENEGRAPH["/" + self.ACTIVEBRANCH.Name.value + "/screen"].Transform.value         = new_rot * new_pos
    #self.SCENEGRAPH["/" + self.ACTIVEBRANCH.Name.value + "/screen/head"].Transform.value    = avango.gua.make_trans_mat(0,0,1.7)

    # Change Navigator
    #self.USERHEAD = self.SCENEGRAPH["/" + self.ACTIVEBRANCH.Name.value + "/screen"]
    #self.NAVIGATOR.StartLocation.value = self.USERHEAD.Transform.value.get_translate()
    #self.NAVIGATOR.OutTransform.connect_from(self.USERHEAD.Transform)
    #self.USERHEAD.Transform.connect_from(self.NAVIGATOR.OutTransform)
    #self.UserPositionIn.connect_from(self.USERHEAD.Transform)
    
    # Change Main Pipe
    #camera_active_branch = avango.gua.nodes.Camera(LeftEye   = "/" + ACTIVEBRANCH.Name.value + "/screen/head" + "/mono_eye",
    #                                            RightEye    = "/" + ACTIVEBRANCH.Name.value + "/screen/head" + "/mono_eye",
    #                                            LeftScreen  = "/" + ACTIVEBRANCH.Name.value + "/screen",
    #                                            RightScreen = "/" + ACTIVEBRANCH.Name.value + "/screen",
    #                                            SceneGraph  = SCENEGRAPH.Name.value)


    #self.PIPELINE.Camera.value                 = camera_active_branch
    self.PIPELINE.BackgroundTexture.value      = PORTAL.PRE_PIPE.BackgroundTexture.value
    self.PIPELINE.EnableBackfaceCulling.value  = PORTAL.PRE_PIPE.EnableBackfaceCulling.value
    self.update_pipe_render_mask()

    self.ACTIVEPORTALS  = self.create_active_portals()
    #self.PORTALUPDATERS = self.create_portal_updaters() 
    self.create_portal_updaters()

    # probably not useful!?!?!
    #for p in self.ACTIVEPORTALS:
    #  self.ACTIVEBRANCH.Children.value.append(p.GEOMETRY)

    self.update_portal_picker()


  def create_portal_updaters(self):
    self.PORTALUPDATERS = []
    
    for p in self.ACTIVEPORTALS:
      self.PORTALUPDATERS.append(UpdatePortalTransform())
      self.PORTALUPDATERS[len(self.PORTALUPDATERS) - 1].my_constructor(p.NAME + "_updater")
      self.PORTALUPDATERS[len(self.PORTALUPDATERS) - 1].PortalTransformIn.connect_from(p.sf_portal_pos)
      #updater.ViewTransformIn.connect_from(self.SCENEGRAPH["/" + self.ACTIVEBRANCH.Name.value + "/screen/head"].Transform)
      #updater.ScreenTransformIn.connect_from(self.SCENEGRAPH["/" + self.ACTIVEBRANCH.Name.value + "/screen"].Transform)
      self.PORTALUPDATERS[len(self.PORTALUPDATERS) - 1].ViewTransformIn.connect_from(self.sfUserHead)
      self.PORTALUPDATERS[len(self.PORTALUPDATERS) - 1].ScreenTransformIn.connect_from(self.sfUserScreen)
      p.EXITSCENE[p.HEAD].Transform.connect_from(self.PORTALUPDATERS[len(self.PORTALUPDATERS) - 1].ViewTransformOut)
    
  def create_active_portals(self):
    activeportals = []
    pre_pipes = []      
    for p in self.PORTALS:
      if p.ENTRYSCENE.Name.value == self.ACTIVESCENE.Name.value:
        activeportals.append(p)
        pre_pipes.append(p.PRE_PIPE)

    self.PIPELINE.PreRenderPipelines.value = pre_pipes     
    return activeportals
      
  def update_prepipes(self):
    pre_pipes = []      
    for p in self.PORTALS:
      #p.PRE_PIPE.Camera.value.RenderMask.value = self.PIPELINE.Camera.value.RenderMask.value
      pre_pipes.append(p.PRE_PIPE)

    self.PIPELINE.PreRenderPipelines.value = pre_pipes

  def initialize_portal_group_names(self):
    for p in self.PORTALS:
      p.GEOMETRY.GroupNames.value.append(self.NAME + "portals")

  def adjust_nearplane(self):
    for p in self.ACTIVEPORTALS:
      _pos_p1 = p.EXITSCENE["/" + p.NAME + "Screen"].Transform.value.get_translate().z
      _pos_p2 = p.EXITSCENE["/" + p.NAME + "Screen/head"].Transform.value.get_translate().z
      _distance = abs (_pos_p1 - _pos_p2)
      p.PRE_PIPE.NearClip.value = _distance
      #print _distance
  
  def update_portal_picker(self):
    self.PORTALPICKER.Mask.value = self.NAME + "portals"
    self.PORTALPICKER.SceneGraph.value = self.ACTIVESCENE
    self.ACTIVESCENE["/platform_" + str(self.PLATFORM)].Children.value.append(self.PORTALPICKER.Ray.value)
    self.PickedPortals.connect_from(self.PORTALPICKER.Results)

