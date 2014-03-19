#!/usr/bin/python

import avango
import avango.script
from avango.script import field_has_changed
import avango.gua
import time
import math

from examples_common.GuaVE import GuaVE

from ..Navigation import *

from PortalCube import *

## Controller used to handle functional tasks in a portal application
#
# This class is in charge of activating a dynamic view on portals, being updated by the users movement.
# It also coordinates all interactivity provided by the portal concept. This includes 
# walking through a portal (changing scenes), toggling the visibility of portals
# and activating/deactivating the above functionalities
class PortalController(avango.script.Script):
  
  PickedPortals     = avango.gua.MFPickResult()
  sf_user_head        = avango.gua.SFMatrix4()
  
  def __init__(self):
    self.super(PortalController).__init__()
    
    self.NAME               = ""
    self.ACTIVE_SCENE       = avango.gua.nodes.SceneGraph()
    self.PIPELINE           = avango.gua.nodes.Pipeline()
    self.VIEWING_PIPELINES  = []
    self.PORTALS            = []
    self.PORTAL_CUBES       = []
    self.NAVIGATION         = Navigation()
    self.PLATFORM           = -1
    self.USER_HEAD          = avango.gua.nodes.TransformNode()
    
    self.portal_picker      = PortalPicker()
    self.active_portals     = []
    self.portal_updaters    = []
    self.visible_cube       = PortalCube()
    self.timer              = avango.nodes.TimeSensor()
    self.start_time         = 0.0
  
  ## Custom constructor
  #
  # NAME                !unique! Name of a portalController
  # ACTIVE_SCENE        SceneGraph in which portal functionalities have got to be applied (users SceneGraph)
  # VIEWING_PIPELINES   Reference to the Pipelines used by the main guacamole viewer object
  # PIPELINE            Pipeline of the user interacting with the portal application
  # PORTALS             List of all portals to be controlled by this class (excluding complex portals such as PortalCubes)
  # PORTAL_CUBES        List of all PortalCubes to be controlled by this class
  # NAVIGATION          Reference to the navigation used to manipulate the users position
  # USER_HEAD           TransformNode specifying the users head position 
  def my_constructor(self, NAME, ACTIVE_SCENE, VIEWING_PIPELINES, PIPELINE, PORTALS, PORTAL_CUBES, NAVIGATION, USER_HEAD):
    self.NAME                 = NAME
    self.ACTIVE_SCENE         = ACTIVE_SCENE
    self.PIPELINE             = PIPELINE
    self.VIEWING_PIPELINES    = VIEWING_PIPELINES
    self.PORTALS              = PORTALS
    self.PORTAL_CUBES         = PORTAL_CUBES
    self.NAVIGATION           = NAVIGATION
    self.USER_HEAD            = USER_HEAD

    for p_cube in self.PORTAL_CUBES:
      for portal in p_cube.Portals:
        self.PORTALS.append(portal)
    
    self.create_active_portals()      
    self.start_time         = self.timer.Time.value

    self.create_portal_updaters()     
    self.initialize_portal_group_names()
    self.initialize_prepipes()
    self.initialize_portal_picker()

    self.always_evaluate(True) # evaluate() is called each frame

  ## evaluate function to be called each frame
  # updates the sf_user_head field (waiting for guacamole bug fix: connection to WorldTransform does not work)
  # checks whether the visibility property of a PortalCube has been toggled and hides portals if nessesary
  def evaluate(self):
    self.sf_user_head.value = self.USER_HEAD.WorldTransform.value

    for p_cube in self.PORTAL_CUBES:
      
      if p_cube.visibility_updated == True and self.timer.Time.value - self.start_time > 20.0:
          p_cube.visibility_updated = False

          if p_cube.sf_visibility.value == False:
            for c_portal in p_cube.Portals:
              portal = next((p for p in self.PORTALS if c_portal.NAME == p.NAME), None)
              if portal in self.active_portals:
                self.active_portals.remove(portal)
                portal.pre_pipe.Enabled.value = False
              if "do_not_display_group" not in portal.geometry.GroupNames.value:
                portal.geometry.GroupNames.value.append("do_not_display_group")
                portal.geometry.Transform.value = portal.geometry.Transform.value * \
                                                  avango.gua.make_trans_mat(0.0,0.0,0.5) * \
                                                  avango.gua.make_scale_mat(0.5,0.5,0.5)
        
          else: # p_cube.sf_visibility.value == True
            for c_portal in p_cube.Portals:
              portal = next((p for p in self.PORTALS if c_portal.NAME == p.NAME), None)
              if portal not in self.active_portals:
                self.active_portals.append(portal)
                portal.pre_pipe.Enabled.value = True
              if "do_not_display_group" in portal.geometry.GroupNames.value:
                portal.geometry.GroupNames.value.remove("do_not_display_group")
                portal.geometry.Transform.value = portal.geometry.Transform.value * \
                                                  avango.gua.make_inverse_mat(avango.gua.make_trans_mat(0.0,0.0,0.5) * \
                                                                              avango.gua.make_scale_mat(0.5,0.5,0.5))
            self.visible_cube = p_cube
            self.hide_invisible_portal_cubes()

  ## handles whether a user intersects a portal and needs to be repositioned
  @field_has_changed(PickedPortals)
  def evaluate_scene_change(self):
    pos_p1 = self.USER_HEAD.Transform.value.get_translate()

    for portal in self.PickedPortals.value:
      if portal.Distance.value < 0.19:
        for p in self.active_portals:
          if p.geometry.Name.value == portal.Object.value.Name.value:
            pos_p2 = p.geometry.Transform.value.get_translate()
            distance_x = pos_p1.x - pos_p2.x
            distance_y = pos_p1.y - pos_p2.y
            self.change_scene(p, distance_x, distance_y)
            break
        break

  ## repositions the user to the exit of a portal (called by evaluate_scene_change) 
  def change_scene(self, PORTAL, DISTANCE_X, DISTANCE_Y):

    platform = self.ACTIVE_SCENE["/platform_" + str(self.PLATFORM)]
    rotate_old_scene = platform.Transform.value.get_rotate()

    PORTAL.EXIT_SCENE.Root.value.Children.value.append(platform)

    self.PIPELINE.Camera.value.SceneGraph.value = PORTAL.EXIT_SCENE.Name.value

    for view_pipe in self.VIEWING_PIPELINES.value:
      if view_pipe == self.PIPELINE:
        view_pipe.Camera.value = self.PIPELINE.Camera.value

    PORTAL.ENTRY_SCENE.Root.value.Children.value.remove(platform)

    self.ACTIVE_SCENE = PORTAL.EXIT_SCENE


    pos_correction = avango.gua.make_trans_mat(PORTAL.sf_portal_pos.value.get_translate() - platform.Transform.value.get_translate())

    # Starting Position
    new_pos = avango.gua.make_trans_mat(PORTAL.EXIT_POS.get_translate().x,
                                        PORTAL.EXIT_POS.get_translate().y,
                                        PORTAL.EXIT_POS.get_translate().z) * \
              avango.gua.make_trans_mat(-1.0 * pos_correction.get_translate().x,
                                        -1.0 * pos_correction.get_translate().y,
                                        -1.0 * pos_correction.get_translate().z)
    
    # Starting Rotation
    new_rot = avango.gua.make_rot_mat(rotate_old_scene)

    self.NAVIGATION.set_to_pos(new_pos * new_rot)

    self.create_active_portals()
    self.create_portal_updaters()
    
    self.portal_picker.SceneGraph.value = self.ACTIVE_SCENE
  
  ## instances PortalUpdaters for all active portals in the scene 
  def create_portal_updaters(self):
    self.portal_updaters = []
    
    for p in self.active_portals:
      self.portal_updaters.append(UpdatePortalTransform())
      self.portal_updaters[len(self.portal_updaters) - 1].my_constructor(p.NAME + "_updater")
      self.portal_updaters[len(self.portal_updaters) - 1].PortalTransformIn.connect_from(p.sf_portal_pos)
      self.portal_updaters[len(self.portal_updaters) - 1].ViewTransformIn.connect_from(self.sf_user_head)
      p.EXIT_SCENE[p.head].Transform.connect_from(self.portal_updaters[len(self.portal_updaters) - 1].ViewTransformOut)
    
  ## fills a list with all portals active in the active scene 
  def create_active_portals(self):
    self.active_portals = []
    
    for p in self.PORTALS:
      if p.ENTRY_SCENE.Name.value == self.ACTIVE_SCENE.Name.value and "do_not_display_group" not in p.geometry.GroupNames.value:
        self.active_portals.append(p)
  
  ## appends all portal pipelines to the users PreRenderPipelines property
  def initialize_prepipes(self):
    pre_pipes = []
    for p in self.PORTALS:
      pre_pipes.append(p.pre_pipe)
      
    self.PIPELINE.PreRenderPipelines.value = pre_pipes

  ## appends default GroupName to GroupNames property of portal geometry
  def initialize_portal_group_names(self):
    for p in self.PORTALS:
      p.geometry.GroupNames.value.append(self.NAME + "portals")

  ## adjusts the nearplane of the camera rendering the view of each portal (can be used for clipping objects occluding the view)
  def adjust_nearplane(self):
    for p in self.active_portals:
      _pos_p1 = p.EXIT_SCENE["/" + p.NAME + "Screen"].Transform.value.get_translate().z
      _pos_p2 = p.EXIT_SCENE["/" + p.NAME + "Screen/head"].Transform.value.get_translate().z
      _distance = abs (_pos_p1 - _pos_p2)
      p.pre_pipe.NearClip.value = _distance
  
  ## instances a ray testing portal picker for each active portal
  def initialize_portal_picker(self):
    self.portal_picker.Mask.value = self.PORTALS[0].GROUP_NAME
    self.portal_picker.SceneGraph.value = self.ACTIVE_SCENE
    self.USER_HEAD.Children.value.append(self.portal_picker.Ray.value)
    self.PickedPortals.connect_from(self.portal_picker.Results)

  ## delete a specific GroupName in the GroupNames property of each protal in the PORTALS list
  def delete_portal_group_name(self, GROUPNAME):
    for p in self.PORTALS:
      p.geometry.GroupNames.value.remove(GROUPNAME)

  ## hides all portal cubes that must not be seen
  def hide_invisible_portal_cubes(self):
    for p_cube in self.PORTAL_CUBES:
      if p_cube != self.visible_cube:
        for c_portal in p_cube.Portals:
            portal = next((p for p in self.PORTALS if c_portal.NAME == p.NAME), None)
            if portal in self.active_portals:
              self.active_portals.remove(portal)
              portal.pre_pipe.Enabled.value = False
            if "do_not_display_group" not in portal.geometry.GroupNames.value:
              portal.geometry.GroupNames.value.append("do_not_display_group")
              portal.geometry.Transform.value = portal.geometry.Transform.value * \
                                                  avango.gua.make_trans_mat(0.0,0.0,0.5) * \
                                                  avango.gua.make_scale_mat(0.5,0.5,0.5)

## Helper class to determine whether a user intersects a portal 
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

## Helper class to update the view rendered onto a portal texture
#
# It calculates the relation of a viewing position to the portal geometry.
# This can then be connected to the relative Transformation of the eye used to 
# specify the camera rendering the displayed pipeline. 
class UpdatePortalTransform(avango.script.Script):

  PortalTransformIn     = avango.gua.SFMatrix4()
  ViewTransformIn       = avango.gua.SFMatrix4()
  ViewTransformOut      = avango.gua.SFMatrix4()

  def __init__(self):
    self.super(UpdatePortalTransform).__init__()
    self.NAME = ""
    
  def my_constructor(self, NAME):
    self.NAME = NAME

  def evaluate(self):
    self.ViewTransformOut.value = avango.gua.make_inverse_mat(self.PortalTransformIn.value) * \
                                    self.ViewTransformIn.value


