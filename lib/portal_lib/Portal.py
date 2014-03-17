#!/usr/bin/python

import avango
import avango.script
from avango.script import field_has_changed
import avango.gua
import time
import math

import examples_common.navigator
from examples_common.GuaVE import GuaVE
from ..interface_lib.InteractivGeometry import *

## Helper class to update material values with respect to the current time.
class TimedMaterialUniformUpdate(avango.script.Script):

  ## @var TimeIn
  # Field containing the current time in milliseconds.
  TimeIn = avango.SFFloat()

  ## @var MaterialName
  # Field containing the name of the material to be updated
  MaterialName = avango.SFString()

  ## @var UniformName
  # Field containing the name of the uniform value to be updated
  UniformName = avango.SFString()

  ## Called whenever TimeIn changes.
  @field_has_changed(TimeIn)
  def update(self):
    avango.gua.set_material_uniform(self.MaterialName.value,
                                    self.UniformName.value,
                                    self.TimeIn.value)

class Portal(avango.script.Script):

    # init fields
    sf_portal_pos   = avango.gua.SFMatrix4()
   #sf_active       = avango.SFBool() 
    
    def __init__(self):
        self.super(Portal).__init__()
        self.timer                  = avango.nodes.TimeSensor()
        self.water_updater          = TimedMaterialUniformUpdate()
        self.NAME                   = ""
        self.ENTRYSCENE             = avango.gua.nodes.SceneGraph()
        self.EXITSCENE              = avango.gua.nodes.SceneGraph()
        self.EXITPOS                = avango.gua.Mat4()
        self.WIDTH                  = 0
        self.HEIGHT                 = 0
        self.DEPTH                  = 1
        self.PRE_PIPE               = avango.gua.nodes.Pipeline()
        self.GEOMETRY               = avango.gua.nodes.GeometryNode()
        self.default_geometry       = True
        self.HEAD                   = ""
        self.GROUPNAME              = ""
        self.EXCLUDEGROUPS          = []

    def my_constructor(self, NAME, ENTRYSCENE, EXITSCENE, ENTRYPOS, EXITPOS, WIDTH, HEIGHT, GROUPNAME, EXCLUDEGROUPS, PICKABLE = True, GEOMETRY = None):
        #self.sf_active.value        = True

        self.NAME                   = NAME
        self.ENTRYSCENE             = ENTRYSCENE
        self.EXITSCENE              = EXITSCENE
        self.EXITPOS                = EXITPOS
        self.WIDTH                  = WIDTH
        self.HEIGHT                 = HEIGHT
        self.GROUPNAME              = GROUPNAME
        self.EXCLUDEGROUPS          = EXCLUDEGROUPS
        self.PRE_PIPE               = self.create_default_pipe()
        self.GEOMETRY               = self.create_geometry(ENTRYPOS, GEOMETRY, PICKABLE)
        self.HEAD                   = "/" + self.NAME + "Screen/head"
    # @field_has_changed(sf_active)
    # def toggle_pipe_enabled_field(self):
    #     self.PRE_PIPE.Enabled.value = self.sf_active.value 

    def create_default_pipe(self):
        self.create_camera()

        width   = 1920
        height  = int(width * 9.0 / 16.0)
        size    = avango.gua.Vec2ui(width, height)

        camera = avango.gua.nodes.Camera(LeftEye    = "/" + self.NAME + "Screen/head" + "/mono_eye",
                                        RightEye    = "/" + self.NAME + "Screen/head" + "/mono_eye",
                                        LeftScreen  = "/" + self.NAME + "Screen",
                                        RightScreen = "/" + self.NAME + "Screen",
                                        SceneGraph  = self.EXITSCENE.Name.value)

        camera.RenderMask.value = "!portal_display_exclude && !portal && !do_not_display_group"        

        for group in self.EXCLUDEGROUPS:
            if group != self.GROUPNAME:
                camera.RenderMask.value = camera.RenderMask.value + " && !" + group

        pre_pipe = avango.gua.nodes.Pipeline(Name = self.NAME + "_pipe",
                                            Camera = camera,
                                            OutputTextureName = self.NAME + "Texture")

        pre_pipe.LeftResolution.value  = avango.gua.Vec2ui(width/2, height/2)
        pre_pipe.EnableStereo.value = False
        pre_pipe.BackgroundTexture.value = "data/textures/skybox.jpg"
        pre_pipe.EnableBackfaceCulling.value = True

        return pre_pipe

    def create_geometry(self, PORTALPOS, GEOMETRY, PICKABLE):
        loader = avango.gua.nodes.GeometryLoader()
        
        if(GEOMETRY == None):
            if PICKABLE:
                geometry = loader.create_geometry_from_file(self.NAME + "Node",
                                                        "data/objects/plane.obj",
                                                        "Portal" + self.NAME,
                                                        avango.gua.LoaderFlags.DEFAULTS | avango.gua.LoaderFlags.MAKE_PICKABLE)
            else:
                geometry = loader.create_geometry_from_file(self.NAME + "Node",
                                                        "data/objects/plane.obj",
                                                        "Portal" + self.NAME,
                                                        avango.gua.LoaderFlags.DEFAULTS)
            
            geometry.Transform.value = PORTALPOS *\
                                    avango.gua.make_rot_mat(90, 1.0, 0.0, 0.0) *\
                                    avango.gua.make_rot_mat(180, 0.0, 1.0, 0.0) *\
                                    avango.gua.make_scale_mat(self.WIDTH, self.DEPTH, self.HEIGHT)
            
            self.sf_portal_pos.value = PORTALPOS

        else:
            geometry                = GEOMETRY
            geometry.Name.value     = self.NAME + "Node"
            geometry.Material.value = "Portal" + self.NAME
            geometry.Transform.value = PORTALPOS *\
                                    GEOMETRY.Transform.value *\
                                    avango.gua.make_scale_mat(self.WIDTH, self.HEIGHT, self.DEPTH)
            
            self.sf_portal_pos.value = PORTALPOS           
            self.default_geometry   = False

        geometry.GroupNames.value.append(self.GROUPNAME)
        geometry.GroupNames.value.append("portal")

        avango.gua.set_material_uniform(  "Portal" + self.NAME,
                                          "portal_texture",
                                          self.NAME + "Texture")

        self.water_updater.MaterialName.value = "Portal" + self.NAME
        self.water_updater.UniformName.value = "time"
        self.water_updater.TimeIn.connect_from(self.timer.Time)

        # make interactive
        #geometry.GroupNames.value.append("interactiv")
        #interactiv_geometry = InteractivGeometry()
        #interactiv_geometry.portal_constructor("TestPortal", geometry, ["x_pos", "y_pos", "z_pos"], self)

        self.ENTRYSCENE.Root.value.Children.value.append(geometry)
        
        return geometry

    def create_camera(self):
        screen = avango.gua.nodes.ScreenNode(Name   = self.NAME + "Screen", 
                                            Width   = self.WIDTH,
                                            Height  = self.HEIGHT)

        screen.Transform.value = self.EXITPOS

        head = avango.gua.nodes.TransformNode(Name = "head")
        head.Transform.value = avango.gua.make_trans_mat(0.0, 0.0, 1.7)

        mono_eye = avango.gua.nodes.TransformNode(Name = "mono_eye")

        left_eye = avango.gua.nodes.TransformNode(Name = "left_eye")
        left_eye.Transform.value = avango.gua.make_trans_mat(-0.05, 0.0, 0.0)

        right_eye = avango.gua.nodes.TransformNode(Name = "right_eye")
        right_eye.Transform.value = avango.gua.make_trans_mat(0.05, 0.0, 0.0)


        head.Children.value = [mono_eye, left_eye, right_eye]

        screen.Children.value.append(head)
        self.EXITSCENE.Root.value.Children.value.append(screen)

    def change_geometry(self, GEOMETRY):
        self.GEOMETRY.Geometry.value  = GEOMETRY.Geometry.value
        self.GEOMETRY.Transform.value = PORTALPOS *\
                                        avango.gua.make_rot_mat(GEOMETRY.Transform.value.get_rotate()) *\
                                        avango.gua.make_scale_mat(self.WIDTH, self.HEIGHT, self.DEPTH)

    def resize(self, WIDTH, HEIGHT, DEPTH):
        if self.default_geometry == True:
            self.GEOMETRY.Transform.value = self.GEOMETRY.Transform.value * avango.gua.make_scale_mat(1/self.WIDTH, 1/self.DEPTH, 1/self.HEIGHT)
        else:
            self.GEOMETRY.Transform.value = self.GEOMETRY.Transform.value * avango.gua.make_scale_mat(1/self.WIDTH, 1/self.HEIGHT, 1/self.DEPTH)
        
        self.WIDTH  = WIDTH
        self.HEIGHT = HEIGHT
        self.DEPTH  = DEPTH
        self.EXITSCENE["/" + self.NAME + "Screen"].Width.value  = self.WIDTH
        self.EXITSCENE["/" + self.NAME + "Screen"].Height.value = self.HEIGHT
        
        if self.default_geometry == True:
            self.GEOMETRY.Transform.value = self.GEOMETRY.Transform.value * avango.gua.make_scale_mat(self.WIDTH, self.DEPTH, self.HEIGHT)
        else:
            self.GEOMETRY.Transform.value = self.GEOMETRY.Transform.value * avango.gua.make_scale_mat(self.WIDTH, self.HEIGHT, self.DEPTH)
            
    def translate(self, X, Y, Z):
        self.GEOMETRY.Transform.value  = self.GEOMETRY.Transform.value * avango.gua.make_trans_mat(X, Y, Z)
        self.sf_portal_pos.value = self.sf_portal_pos.value * avango.gua.make_trans_mat(X, Y, Z)
        self.EXITPOS = self.EXITPOS * avango.gua.make_trans_mat(X, Y, Z)

    def append_node(self, NODE):
        NODE.Transform.value =  avango.gua.make_inverse_mat(self.GEOMETRY.Transform.value) * \
                                avango.gua.make_trans_mat(self.GEOMETRY.Transform.value.get_translate())  * \
                                NODE.Transform.value
        self.GEOMETRY.Children.value.append(NODE)

