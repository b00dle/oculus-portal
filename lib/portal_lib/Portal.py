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

## Internal representation of a Geometry displaying a specified view
#
# this class works as a container for relevant information about the scene it IS DISPLAYED IN
# and the scene IT DISPLAYS. It renders its own Pipeline and projects the rendering result onto
# a specified geometry. Nodes can also be appended to this geometry
class Portal(avango.script.Script):

    sf_portal_pos   = avango.gua.SFMatrix4()
    
    def __init__(self):
        self.super(Portal).__init__()
        
        self.NAME                   = ""
        self.ENTRY_SCENE            = avango.gua.nodes.SceneGraph()
        self.EXIT_SCENE             = avango.gua.nodes.SceneGraph()
        self.EXIT_POS               = avango.gua.Mat4()
        self.WIDTH                  = 0
        self.HEIGHT                 = 0
        self.DEPTH                  = 1
        self.GROUP_NAME             = ""
        self.EXCLUDE_GROUPS         = []

        self.pre_pipe               = avango.gua.nodes.Pipeline()
        self.geometry               = avango.gua.nodes.GeometryNode()
        self.default_geometry       = True
        self.head                   = ""
        self.timer                  = avango.nodes.TimeSensor()
        self.water_updater          = TimedMaterialUniformUpdate()

    ## Custom constructor
    #
    # NAME              !unique! name of a portal object
    # ENTRY_SCENE       Scenegraph to append the portal geometry to
    # EXIT_SCENE        SceneGraph being displayed on a portal texture
    # ENTRY_POS         WorldTransformation to be applied to the portal geometry
    # EXIT_POS          WorldTransformation used for the orientation of the camera in the scene being displayed
    # WIDTH             Property for aspect ratio
    # HEIGHT            Property for aspect ratio
    # GROUP_NAME        Name to apply to GroupName property of the GeoetryNode (used for Masking)
    # EXCLUDE_GROUPS    Extends the RenderMask of the camera rendering the view being displayed  
    def my_constructor(self, NAME, ENTRY_SCENE, EXIT_SCENE, ENTRY_POS, EXIT_POS, WIDTH, HEIGHT, GROUP_NAME, EXCLUDE_GROUPS, PICKABLE = True, GEOMETRY = None):
        self.NAME                   = NAME
        self.ENTRY_SCENE            = ENTRY_SCENE
        self.EXIT_SCENE             = EXIT_SCENE
        self.EXIT_POS               = EXIT_POS
        self.WIDTH                  = WIDTH
        self.HEIGHT                 = HEIGHT
        self.GROUP_NAME             = GROUP_NAME
        self.EXCLUDE_GROUPS         = EXCLUDE_GROUPS
        
        self.pre_pipe               = self.create_default_pipe()
        self.geometry               = self.create_geometry(ENTRY_POS, GEOMETRY, PICKABLE)
        self.head                   = "/" + self.NAME + "Screen/head"
    
    ## creates the pipeline which is used to render the texture displayed on a portal geometry
    def create_default_pipe(self):
        self.create_camera()

        width   = 640
        height  = int(width * 9.0 / 16.0)
        size    = avango.gua.Vec2ui(width, height)

        camera = avango.gua.nodes.Camera(LeftEye    = "/" + self.NAME + "Screen/head" + "/mono_eye",
                                        RightEye    = "/" + self.NAME + "Screen/head" + "/mono_eye",
                                        LeftScreen  = "/" + self.NAME + "Screen",
                                        RightScreen = "/" + self.NAME + "Screen",
                                        SceneGraph  = self.EXIT_SCENE.Name.value)

        camera.RenderMask.value = "!portal_display_exclude && !portal && !do_not_display_group"        

        for group in self.EXCLUDE_GROUPS:
            if group != self.GROUP_NAME:
                camera.RenderMask.value = camera.RenderMask.value + " && !" + group

        pre_pipe = avango.gua.nodes.Pipeline(Name               = self.NAME + "_pipe",
                                            Camera              = camera,
                                            OutputTextureName   = self.NAME + "Texture")

        pre_pipe.LeftResolution.value  = avango.gua.Vec2ui(width/2, height/2)
        pre_pipe.EnableStereo.value = False
        pre_pipe.BackgroundTexture.value = "data/textures/skybox.jpg"
        pre_pipe.EnableBackfaceCulling.value = True

        return pre_pipe

    ## creates the geometry to project a portal view onto
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
            geometry                    = GEOMETRY
            geometry.Name.value         = self.NAME + "Node"
            geometry.Material.value     = "Portal" + self.NAME
            geometry.Transform.value    = PORTALPOS *\
                                        geometry.Transform.value *\
                                        avango.gua.make_scale_mat(self.WIDTH, self.HEIGHT, self.DEPTH)
            
            self.sf_portal_pos.value    = PORTALPOS           
            self.default_geometry       = False

        geometry.GroupNames.value.append(self.GROUP_NAME)
        geometry.GroupNames.value.append("portal")

        avango.gua.set_material_uniform(  "Portal" + self.NAME,
                                          "portal_texture",
                                          self.NAME + "Texture")

        self.water_updater.MaterialName.value   = "Portal" + self.NAME
        self.water_updater.UniformName.value    = "time"
        self.water_updater.TimeIn.connect_from(self.timer.Time)

        self.ENTRY_SCENE.Root.value.Children.value.append(geometry)
        
        return geometry

    ## creates the camera used for rendering the view into the portal pipeline
    def create_camera(self):
        screen = avango.gua.nodes.ScreenNode(Name   = self.NAME + "Screen", 
                                            Width   = self.WIDTH,
                                            Height  = self.HEIGHT)

        screen.Transform.value = self.EXIT_POS

        head                    = avango.gua.nodes.TransformNode(Name = "head")
        head.Transform.value    = avango.gua.make_trans_mat(0.0, 0.0, 1.7)

        mono_eye = avango.gua.nodes.TransformNode(Name = "mono_eye")

        left_eye                    = avango.gua.nodes.TransformNode(Name = "left_eye")
        left_eye.Transform.value    = avango.gua.make_trans_mat(-0.05, 0.0, 0.0)

        right_eye                   = avango.gua.nodes.TransformNode(Name = "right_eye")
        right_eye.Transform.value   = avango.gua.make_trans_mat(0.05, 0.0, 0.0)


        head.Children.value = [mono_eye, left_eye, right_eye]

        screen.Children.value.append(head)
        self.EXIT_SCENE.Root.value.Children.value.append(screen)

    ## changes a portal Geometry
    def change_geometry(self, GEOMETRY):
        self.geometry.Geometry.value  = GEOMETRY.Geometry.value
        self.geometry.Transform.value = PORTALPOS *\
                                        avango.gua.make_rot_mat(GEOMETRY.Transform.value.get_rotate()) *\
                                        avango.gua.make_scale_mat(self.WIDTH, self.HEIGHT, self.DEPTH)

    ## resizes both, the screen of the camera in the displayed scene and the portal geometry 
    def resize(self, WIDTH, HEIGHT, DEPTH):
        if self.default_geometry == True:
            self.geometry.Transform.value = self.geometry.Transform.value * \
                                            avango.gua.make_scale_mat(1/self.WIDTH, 1/self.DEPTH, 1/self.HEIGHT)
        else:
            self.geometry.Transform.value = self.geometry.Transform.value * \
                                            avango.gua.make_scale_mat(1/self.WIDTH, 1/self.HEIGHT, 1/self.DEPTH)
        
        self.WIDTH  = WIDTH
        self.HEIGHT = HEIGHT
        self.DEPTH  = DEPTH
        self.EXIT_SCENE["/" + self.NAME + "Screen"].Width.value  = self.WIDTH
        self.EXIT_SCENE["/" + self.NAME + "Screen"].Height.value = self.HEIGHT
        
        if self.default_geometry == True:
            self.geometry.Transform.value = self.geometry.Transform.value * \
                                            avango.gua.make_scale_mat(self.WIDTH, self.DEPTH, self.HEIGHT)
        else:
            self.geometry.Transform.value = self.geometry.Transform.value * \
                                            avango.gua.make_scale_mat(self.WIDTH, self.HEIGHT, self.DEPTH)
            
    ## appends a Childnode to the portal geometry
    def append_node(self, NODE):
        NODE.Transform.value =  avango.gua.make_inverse_mat(self.geometry.Transform.value) * \
                                avango.gua.make_trans_mat(self.geometry.Transform.value.get_translate())  * \
                                NODE.Transform.value
        self.geometry.Children.value.append(NODE)

## Helper class to update material values with respect to the current time.
class TimedMaterialUniformUpdate(avango.script.Script):

  TimeIn        = avango.SFFloat()
  MaterialName  = avango.SFString()
  UniformName   = avango.SFString()
  
  @field_has_changed(TimeIn)
  def update(self):
    avango.gua.set_material_uniform(self.MaterialName.value,
                                    self.UniformName.value,
                                    self.TimeIn.value)


