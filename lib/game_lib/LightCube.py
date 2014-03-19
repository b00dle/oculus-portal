#!/usr/bin/python

## @file
# Contains classes Navigation, Interface, LineCreator.

# import guacamole libraries
import avango
import avango.gua
import avango.script

# import python libraries
import time

# import framework libraries
from ..Navigation import *
from ..interface_lib.Interface import *
from ..LineCreator import *

class LightCube(avango.script.Script):
  sf_rot_up         = avango.SFBool()
  sf_rot_down       = avango.SFBool()
  sf_rot_left       = avango.SFBool()
  sf_rot_right      = avango.SFBool()

  sf_portal_button        = avango.SFBool()

  mf_pick_results_plus_x  = avango.gua.MFPickResult()
  mf_pick_results_minus_x = avango.gua.MFPickResult()

  mf_pick_results_plus_y  = avango.gua.MFPickResult()
  mf_pick_results_minus_y = avango.gua.MFPickResult()

  mf_pick_results_plus_z  = avango.gua.MFPickResult()
  mf_pick_results_minus_z = avango.gua.MFPickResult()

  sf_visible = avango.SFBool()

  def __init__(self):
    self.super(LightCube).__init__()
    self.always_evaluate(True)
    
    self.NAME       = "default_cube"
    self.HAS_LIGHT  = False
    self.IS_EMITTER = False
    self.LIGHT_EXITS = []


    self.activated  = False
    self.cube = avango.gua.nodes.GeometryNode()

    self.rot_up_button    = ConsoleButton()
    self.rot_down_button  = ConsoleButton()
    self.rot_left_button  = ConsoleButton()
    self.rot_right_button = ConsoleButton()

    self.pick_transforms_appended = False
    self.timer = avango.nodes.TimeSensor()
    self.animation_flag = False
    self.animation_time = 0.5


  def my_constructor(self, NAME, SCENEGRAPH, ROOM_NODE, ACTIV, LIGHT_EXITS, CONSOLE_NODE, COLOR):
    # init light cube

    self.NAME           = NAME
    self.HAS_LIGHT      = ACTIV
    self.IS_EMITTER     = ACTIV
    self.LIGHT_EXITS     = LIGHT_EXITS
    self.SCENEGRAPH     = SCENEGRAPH
    self.ROOM_NODE       = ROOM_NODE
    self.CONSOLE_NODE   = CONSOLE_NODE
    self.PORTAL_BUTTONS = []

    self.cube_transform = avango.gua.nodes.TransformNode(Name = "cube_transform")
    self.cube_transform.Transform.value = avango.gua.make_trans_mat(0,1.5,0)
    self.cube_rotate = avango.gua.nodes.TransformNode(Name = "cube_rotate")

    self.loader         = avango.gua.nodes.GeometryLoader()
    self.cube = self.loader.create_geometry_from_file(NAME + "_cube",
                                                      'data/objects/lightcube.obj',
                                                      "PhongWhite",
                                                      avango.gua.LoaderFlags.DEFAULTS | avango.gua.LoaderFlags.MAKE_PICKABLE)
    self.cube.Transform.value = avango.gua.make_scale_mat(0.1, 0.1, 0.1)
    self.cube.GroupNames.value  = ["interactiv"]
    self.cube.add_and_init_field(avango.script.SFObject(),
                                 "LightCube",
                                 self)

    self.ROOM_NODE.Children.value.append(self.cube_transform)
  
    self.cube_transform.Children.value.append(self.cube_rotate)
    self.cube_rotate.Children.value.append(self.cube)

    # init menu
    self.init_console()
    self.enable_console(self.ROOM_NODE)

    self.init_lightexits(COLOR)

    self.init_pickers()


  def evaluate(self):
    # Animation
    if (self.animation_flag == True ):
      _current_time = self.timer.Time.value
      _slerp_ratio = (_current_time - self.animation_start_time) / self.animation_time

      if _slerp_ratio > 1:
        _slerp_ratio = 1
        self.animation_flag = False
        self.cube_rotate.Transform.value = avango.gua.make_rot_mat(self.animation_end_pos)
        return
      
      _transformed_quat = self.animation_start_pos.slerp_to(self.animation_end_pos, _slerp_ratio)
      rotation_mat = avango.gua.make_rot_mat(_transformed_quat)
      self.cube_rotate.Transform.value = rotation_mat


    if self.activated == False:
      self.remove_ray_nodes()
      for button in self.PORTAL_BUTTONS: 
        button.sf_visible.value = False

    if self.IS_EMITTER:
      self.activate_light()

    if self.activated:
      self.HAS_LIGHT = True
      self.activated = False
    elif (self.activated == False):
      self.HAS_LIGHT = False


    # Update the visualization of the light KOENNTE VORHER NOCH UEBER LIGHT_EXITS ITERIEREN
    self.update_ray_visual(self.ray_visual_plus_x, self.mf_pick_results_plus_x)
    self.update_ray_visual(self.ray_visual_minus_x, self.mf_pick_results_minus_x)

    self.update_ray_visual(self.ray_visual_plus_y, self.mf_pick_results_plus_y)
    self.update_ray_visual(self.ray_visual_minus_y, self.mf_pick_results_minus_y)

    self.update_ray_visual(self.ray_visual_plus_z, self.mf_pick_results_plus_z)
    self.update_ray_visual(self.ray_visual_minus_z, self.mf_pick_results_minus_z)


  def check_pick_results(self, mf_pick_results):
    if len(mf_pick_results.value) > 0:
      _picked = mf_pick_results.value[0].Object.value

      if _picked.has_field("LightCube"):
        for button in self.PORTAL_BUTTONS: 
          if _picked.LightCube.value.NAME == button.NAME:
            button.sf_visible.value = True

      if _picked.has_field("LightCube") and _picked.LightCube.value.activated == False:
        _picked.LightCube.value.activate_light()

  def activate_light(self):
    # Set activated Flag
    self.activated = True
    # Append Rays and Ray-Visualizations
    self.append_all_rays()

    for button in self.PORTAL_BUTTONS: 
      button.sf_visible.value = False

    for l in self.LIGHT_EXITS:
      if (l == 1):
        self.check_pick_results(self.mf_pick_results_plus_x)
      elif (l == 2):
        self.check_pick_results(self.mf_pick_results_minus_x)
      elif (l == 3):
        self.check_pick_results(self.mf_pick_results_plus_y)
      elif (l == 4):
        self.check_pick_results(self.mf_pick_results_minus_y)
      elif (l == 5):
        self.check_pick_results(self.mf_pick_results_plus_z)
      elif (l == 6):
        self.check_pick_results(self.mf_pick_results_minus_z)

    button_ = next((b for b in self.PORTAL_BUTTONS if b.state_changed), None)
    if button_ != None:
      for b in self.PORTAL_BUTTONS:
        if b.NAME != button_.NAME and not b.sf_portal_active.value:
          b.sf_portal_active.value = False
      button_.state_changed = False



  def update_ray_visual(self, RAY_VISUAL, mf_pick_results):
    if len(mf_pick_results.value) > 0:
      RAY_VISUAL.Transform.value =  avango.gua.make_trans_mat(0,0,-(mf_pick_results.value[0].Distance.value)/2) *\
                                    avango.gua.make_scale_mat(1,1,(mf_pick_results.value[0].Distance.value)/2)
    else:
      RAY_VISUAL.Transform.value =  avango.gua.make_trans_mat(0,0,-0.5) *\
                                    avango.gua.make_scale_mat(1,1,0.5)


  def append_ray(self, RAY_VISUAL_TRANS, RAY_VISUAL, PICK_TRANSFORM, mf_pick_results):
    RAY_VISUAL_TRANS.Transform.value = avango.gua.make_trans_mat(0.0, 0.0, 0) *\
                                       avango.gua.make_scale_mat(0.01, 0.01, 7.5-0.15)
    self.cube_rotate.Children.value.append(PICK_TRANSFORM)

    if len(mf_pick_results.value) > 0:
      RAY_VISUAL.Transform.value =  avango.gua.make_trans_mat(0,0,-(mf_pick_results.value[0].Distance.value)/2) *\
                                    avango.gua.make_scale_mat(1,1,(mf_pick_results.value[0].Distance.value)/2)
      PICK_TRANSFORM.Children.value.append(RAY_VISUAL_TRANS)
      RAY_VISUAL_TRANS.Children.value.append(RAY_VISUAL)

    else:
      RAY_VISUAL.Transform.value =  avango.gua.make_trans_mat(0,0,-0.5) *\
                                    avango.gua.make_scale_mat(1,1,0.5)
      PICK_TRANSFORM.Children.value.append(RAY_VISUAL_TRANS)
      RAY_VISUAL_TRANS.Children.value.append(RAY_VISUAL)


  def append_all_rays(self):
    if (self.pick_transforms_appended == False):
      for l in self.LIGHT_EXITS:
        if (l == 1):
          self.append_ray(self.ray_visual_trans_plus_x, 
                               self.ray_visual_plus_x, 
                               self.pick_transform_plus_x, 
                               self.mf_pick_results_plus_x)
        elif (l == 2):
          self.append_ray(self.ray_visual_trans_minus_x, 
                               self.ray_visual_minus_x, 
                               self.pick_transform_minus_x, 
                               self.mf_pick_results_minus_x)
        elif (l == 3):
          self.append_ray(self.ray_visual_trans_plus_y, 
                               self.ray_visual_plus_y, 
                               self.pick_transform_plus_y, 
                               self.mf_pick_results_plus_y)
        elif (l == 4):
          self.append_ray(self.ray_visual_trans_minus_y, 
                               self.ray_visual_minus_y, 
                               self.pick_transform_minus_y, 
                               self.mf_pick_results_minus_y)
        elif (l == 5):
          self.append_ray(self.ray_visual_trans_plus_z, 
                               self.ray_visual_plus_z, 
                               self.pick_transform_plus_z, 
                               self.mf_pick_results_plus_z)
        elif (l == 6):
          self.append_ray(self.ray_visual_trans_minus_z, 
                               self.ray_visual_minus_z, 
                               self.pick_transform_minus_z, 
                               self.mf_pick_results_minus_z)
        
        self.pick_transforms_appended = True

  def remove_ray_nodes(self):
    if (self.pick_transforms_appended == True):
      for l in self.LIGHT_EXITS:
        if (l == 1):
          self.remove_ray(self.ray_visual_trans_plus_x, self.ray_visual_plus_x, self.pick_transform_plus_x)
        elif (l == 2):
          self.remove_ray(self.ray_visual_trans_minus_x, self.ray_visual_minus_x, self.pick_transform_minus_x)
        elif (l == 3):
          self.remove_ray(self.ray_visual_trans_plus_y, self.ray_visual_plus_y, self.pick_transform_plus_y)
        elif (l == 4):
          self.remove_ray(self.ray_visual_trans_minus_y, self.ray_visual_minus_y, self.pick_transform_minus_y)
        elif (l == 5):
          self.remove_ray(self.ray_visual_trans_plus_z, self.ray_visual_plus_z, self.pick_transform_plus_z)
        elif (l == 6):
          self.remove_ray(self.ray_visual_trans_minus_z, self.ray_visual_minus_z, self.pick_transform_minus_z)

        self.pick_transforms_appended = False

  def remove_ray(self, RAY_VISUAL_TRANS, RAY_VISUAL, PICK_TRANSFORM):
    RAY_VISUAL_TRANS.Children.value.remove(RAY_VISUAL)
    PICK_TRANSFORM.Children.value.remove(RAY_VISUAL_TRANS)
    self.cube_rotate.Children.value.remove(PICK_TRANSFORM)

  def enable_console(self, MENU_LOCATION):
      MENU_LOCATION.Children.value.append(self.CONSOLE_NODE)


  @field_has_changed(sf_rot_up)
  def rotate_up(self):
    if (self.sf_rot_up.value == True and self.animation_flag == False):
      self.animation_flag       = True
      self.animation_start_time = self.timer.Time.value
      self.animation_start_pos  = self.cube_rotate.Transform.value.get_rotate()
      self.animation_end_pos    = (avango.gua.make_rot_mat(-90.0, 1, 0, 0) * self.cube_rotate.Transform.value).get_rotate()

      self.rot_up_button.just_rotated = True

  @field_has_changed(sf_rot_down)
  def rotate_down(self):
    if (self.sf_rot_down.value == True and self.animation_flag == False):
      self.animation_flag       = True
      self.animation_start_time = self.timer.Time.value
      self.animation_start_pos  = self.cube_rotate.Transform.value.get_rotate()
      self.animation_end_pos    = (avango.gua.make_rot_mat(90.0, 1, 0, 0) * self.cube_rotate.Transform.value).get_rotate()
      self.rot_down_button.just_rotated = True

  @field_has_changed(sf_rot_left)
  def rotate_left(self):
    if (self.sf_rot_left.value == True and self.animation_flag == False):
      self.animation_flag       = True
      self.animation_start_time = self.timer.Time.value
      self.animation_start_pos  = self.cube_rotate.Transform.value.get_rotate()
      self.animation_end_pos    = (avango.gua.make_rot_mat(-90.0, 0, 1, 0) * self.cube_rotate.Transform.value).get_rotate()
      self.rot_left_button.just_rotated = True

  @field_has_changed(sf_rot_right)
  def rotate_right(self):
    if (self.sf_rot_right.value == True and self.animation_flag == False):
      self.animation_flag       = True
      self.animation_start_time = self.timer.Time.value
      self.animation_start_pos  = self.cube_rotate.Transform.value.get_rotate()
      self.animation_end_pos    = (avango.gua.make_rot_mat(90.0, 0, 1, 0) * self.cube_rotate.Transform.value).get_rotate()
      self.rot_right_button.just_rotated = True

  @field_has_changed(sf_portal_button)
  def portal_switch(self):
    if self.sf_portal_button.value:
      self.sf_visible.value = not self.sf_visible.value


  def init_pick_transform(self, PICK_TRANSFORM, PICKER):
    _ray = avango.gua.nodes.RayNode(Name = "pick_ray_")
    _ray_trans = avango.gua.nodes.TransformNode(Name = "ray_transform")
    _ray_trans.Transform.value = avango.gua.make_trans_mat(0.0, 0.0, -0.14) * avango.gua.make_scale_mat(1.0, 1.0, 7.5-0.15)
                                       
    # set picker values
    PICKER.SceneGraph = self.SCENEGRAPH
    PICKER.Ray.value  = _ray
    PICKER.Mask.value = "light_emitter || obsticale"
    _ray_trans.Children.value.append(_ray)
    PICK_TRANSFORM.Children.value.append(_ray_trans)


  def init_console(self):
    self.rot_up_button.my_constructor("rot_up_" + self.NAME,
                                      avango.gua.make_trans_mat(0.0, 0.0, 0.0),
                                      self.CONSOLE_NODE,
                                      "Grey",
                                      "up")
    self.sf_rot_up.connect_from(self.rot_up_button.sf_bool_button)

    self.rot_down_button.my_constructor("rot_down_" + self.NAME,
                                        avango.gua.make_trans_mat(0.0, 0.0, 0),
                                        self.CONSOLE_NODE,
                                        "Grey",
                                        "down")
    self.sf_rot_down.connect_from(self.rot_down_button.sf_bool_button)

    self.rot_left_button.my_constructor("rot_left_" + self.NAME,
                                        avango.gua.make_trans_mat(0, 0.0, 0.0),
                                        self.CONSOLE_NODE,
                                        "Grey",
                                        "left")
    self.sf_rot_left.connect_from(self.rot_left_button.sf_bool_button)

    self.rot_right_button.my_constructor("rot_right_" + self.NAME,
                                         avango.gua.make_trans_mat(0, 0.0, 0.0),
                                         self.CONSOLE_NODE,
                                         "Grey",
                                         "right")
    self.sf_rot_right.connect_from(self.rot_right_button.sf_bool_button)



  def init_lightexits(self, COLOR):
    for l in self.LIGHT_EXITS:
      if (l == 1):
        exit_plus_x = self.loader.create_geometry_from_file('light_exit_plus_x',
                                                            'data/objects/lightreceptor.obj',
                                                            COLOR,
                                                            avango.gua.LoaderFlags.DEFAULTS |\
                                                            avango.gua.LoaderFlags.MAKE_PICKABLE)
        exit_plus_x.GroupNames.value = ["light_emitter"]
        exit_plus_x.add_and_init_field(avango.script.SFObject(), "LightCube", self)
        exit_plus_x.Transform.value = avango.gua.make_trans_mat(1.05,0,0) *\
                                      avango.gua.make_scale_mat(0.8,0.8,0.8) *\
                                      avango.gua.make_rot_mat(90,0,1,0)
        self.cube.Children.value.append(exit_plus_x)
      elif (l == 2):
        exit_minus_x = self.loader.create_geometry_from_file('light_exit_minus_x',
                                                             'data/objects/lightreceptor.obj',
                                                             COLOR,
                                                             avango.gua.LoaderFlags.DEFAULTS |\
                                                             avango.gua.LoaderFlags.MAKE_PICKABLE)
        exit_minus_x.Transform.value = avango.gua.make_trans_mat(-1.05,0,0) *\
                                       avango.gua.make_scale_mat(0.8,0.8,0.8) *\
                                       avango.gua.make_rot_mat(-90,0,1,0)
        exit_minus_x.GroupNames.value = ["light_emitter"]
        exit_minus_x.add_and_init_field(avango.script.SFObject(), "LightCube", self)
        self.cube.Children.value.append(exit_minus_x)
      elif (l == 3):
        exit_plus_y = self.loader.create_geometry_from_file('light_exit_plus_y',
                                                            'data/objects/lightreceptor.obj',
                                                            COLOR,
                                                            avango.gua.LoaderFlags.DEFAULTS |\
                                                            avango.gua.LoaderFlags.MAKE_PICKABLE)
        exit_plus_y.GroupNames.value = ["light_emitter"]
        exit_plus_y.add_and_init_field(avango.script.SFObject(), "LightCube", self)
        exit_plus_y.Transform.value = avango.gua.make_trans_mat(0,1.05,0) *\
                                      avango.gua.make_scale_mat(0.8,0.8,0.8)*\
                                      avango.gua.make_rot_mat(-90,1,0,0)
        self.cube.Children.value.append(exit_plus_y)
      elif (l == 4):
        exit_minus_y = self.loader.create_geometry_from_file('light_exit_plus_z',
                                                             'data/objects/lightreceptor.obj',
                                                             COLOR, 
                                                             avango.gua.LoaderFlags.DEFAULTS |\
                                                             avango.gua.LoaderFlags.MAKE_PICKABLE)
        exit_minus_y.GroupNames.value = ["light_emitter"]
        exit_minus_y.add_and_init_field(avango.script.SFObject(), "LightCube", self)
        exit_minus_y.Transform.value = avango.gua.make_trans_mat(0,-1.05,0) *\
                                       avango.gua.make_scale_mat(0.8,0.8,0.8) *\
                                       avango.gua.make_rot_mat(90,1,0,0)
        self.cube.Children.value.append(exit_minus_y)
      elif (l == 5):
        exit_plus_z = self.loader.create_geometry_from_file('light_exit_plus_z',
                                                            'data/objects/lightreceptor.obj',
                                                            COLOR,
                                                            avango.gua.LoaderFlags.DEFAULTS |\
                                                            avango.gua.LoaderFlags.MAKE_PICKABLE)
        exit_plus_z.GroupNames.value = ["light_emitter"]
        exit_plus_z.add_and_init_field(avango.script.SFObject(), "LightCube", self)
        exit_plus_z.Transform.value = avango.gua.make_trans_mat(0,0,1.05) * avango.gua.make_scale_mat(0.8,0.8,0.8)
        self.cube.Children.value.append(exit_plus_z)
      elif (l == 6):
        exit_minus_z = self.loader.create_geometry_from_file('light_exit_plus_z',
                                                             'data/objects/lightreceptor.obj',
                                                             COLOR, 
                                                             avango.gua.LoaderFlags.DEFAULTS |\
                                                             avango.gua.LoaderFlags.MAKE_PICKABLE)
        exit_minus_z.GroupNames.value = ["light_emitter"]
        exit_minus_z.add_and_init_field(avango.script.SFObject(), "LightCube", self)
        exit_minus_z.Transform.value = avango.gua.make_trans_mat(0,0,-1.05) *\
                                       avango.gua.make_scale_mat(0.8,0.8,0.8) *\
                                       avango.gua.make_rot_mat(180,0,1,0)
        self.cube.Children.value.append(exit_minus_z)

  def init_pickers(self):
    # One Pick_Transform for every side of the cube
    # Each Pick_Transform holds a Ray and a Visual representation
    self.picker_plus_x         = LightRayPicker()
    self.pick_transform_plus_x = avango.gua.nodes.TransformNode(Name = "pick_transform_plus_x")
    self.pick_transform_plus_x.Transform.value = avango.gua.make_rot_mat(-90, 0, 1, 0)
    self.ray_visual_trans_plus_x = avango.gua.nodes.TransformNode(Name = "ray_visual_trans_plus_x")
    self.init_pick_transform(self.pick_transform_plus_x, self.picker_plus_x)

    self.picker_minus_x         = LightRayPicker()
    self.pick_transform_minus_x = avango.gua.nodes.TransformNode(Name = "pick_transform_minus_x")
    self.pick_transform_minus_x.Transform.value = avango.gua.make_rot_mat(90, 0, 1, 0)
    self.ray_visual_trans_minus_x = avango.gua.nodes.TransformNode(Name = "ray_visual_trans_minus_x")
    self.init_pick_transform(self.pick_transform_minus_x, self.picker_minus_x)

    self.picker_plus_y         = LightRayPicker()
    self.pick_transform_plus_y = avango.gua.nodes.TransformNode(Name = "pick_transform_plus_y")
    self.pick_transform_plus_y.Transform.value = avango.gua.make_rot_mat(90, 1, 0, 0)
    self.ray_visual_trans_plus_y = avango.gua.nodes.TransformNode(Name = "ray_visual_trans_plus_y")
    self.init_pick_transform(self.pick_transform_plus_y, self.picker_plus_y)
    
    self.picker_minus_y         = LightRayPicker()
    self.pick_transform_minus_y = avango.gua.nodes.TransformNode(Name = "pick_transform_minus_y")
    self.pick_transform_minus_y.Transform.value = avango.gua.make_rot_mat(-90, 1, 0, 0)
    self.ray_visual_trans_minus_y = avango.gua.nodes.TransformNode(Name = "ray_visual_trans_minus_y")
    self.init_pick_transform(self.pick_transform_minus_y, self.picker_minus_y)
    
    self.picker_plus_z         = LightRayPicker()
    self.pick_transform_plus_z = avango.gua.nodes.TransformNode(Name = "pick_transform_plus_z")
    self.pick_transform_plus_z.Transform.value = avango.gua.make_rot_mat(180, 1, 0, 0)
    self.ray_visual_trans_plus_z = avango.gua.nodes.TransformNode(Name = "ray_visual_trans_plus_z")
    self.init_pick_transform(self.pick_transform_plus_z, self.picker_plus_z)

    self.picker_minus_z         = LightRayPicker()
    self.pick_transform_minus_z = avango.gua.nodes.TransformNode(Name = "pick_transform_minus_z")
    self.ray_visual_trans_minus_z = avango.gua.nodes.TransformNode(Name = "ray_visual_trans_minus_z")
    self.init_pick_transform(self.pick_transform_minus_z, self.picker_minus_z)

    # Ray Visualizations
    self.ray_visual_plus_x  = self.loader.create_geometry_from_file('ray', 'data/objects/cube.obj', 'Ray', avango.gua.LoaderFlags.DEFAULTS)
    self.ray_visual_minus_x = self.loader.create_geometry_from_file('ray', 'data/objects/cube.obj', 'Ray', avango.gua.LoaderFlags.DEFAULTS)

    self.ray_visual_plus_y  = self.loader.create_geometry_from_file('ray', 'data/objects/cube.obj', 'Ray', avango.gua.LoaderFlags.DEFAULTS)
    self.ray_visual_minus_y = self.loader.create_geometry_from_file('ray', 'data/objects/cube.obj', 'Ray', avango.gua.LoaderFlags.DEFAULTS)

    self.ray_visual_plus_z  = self.loader.create_geometry_from_file('ray', 'data/objects/cube.obj', 'Ray', avango.gua.LoaderFlags.DEFAULTS)
    self.ray_visual_minus_z = self.loader.create_geometry_from_file('ray', 'data/objects/cube.obj', 'Ray', avango.gua.LoaderFlags.DEFAULTS)

    # Field Connections for the pick results
    self.mf_pick_results_plus_x.connect_from(self.picker_plus_x.Results)
    self.mf_pick_results_minus_x.connect_from(self.picker_minus_x.Results)

    self.mf_pick_results_plus_y.connect_from(self.picker_plus_y.Results)
    self.mf_pick_results_minus_y.connect_from(self.picker_minus_y.Results)

    self.mf_pick_results_plus_z.connect_from(self.picker_plus_z.Results)
    self.mf_pick_results_minus_z.connect_from(self.picker_minus_z.Results)


class LightRayPicker(avango.script.Script):
  Ray        = avango.gua.SFRayNode()
  Options    = avango.SFInt()
  Mask       = avango.SFString()
  Results    = avango.gua.MFPickResult()

  def __init__(self):
    self.super(LightRayPicker).__init__()
    self.always_evaluate(True)

    self.SceneGraph = avango.gua.nodes.SceneGraph()
    self.Ray.value  = avango.gua.nodes.RayNode()
    self.Options.value = avango.gua.PickingOptions.PICK_ONLY_FIRST_OBJECT \
                         | avango.gua.PickingOptions.PICK_ONLY_FIRST_FACE\
                         | avango.gua.PickingOptions.GET_POSITIONS
    self.Mask.value = ""
    
  def evaluate(self):
    results = self.SceneGraph.ray_test(self.Ray.value,
                                             self.Options.value,
                                             self.Mask.value)
    self.Results.value = results.value