#!/usr/bin/python

import avango
import avango.gua
import avango.script


from ..interface_lib.Interface import *

class LightCube(avango.script.Script):
  sf_enabled        = avango.SFBool()
  sf_color_red      = avango.SFFloat()
  sf_color_green    = avango.SFFloat()
  sf_color_blue     = avango.SFFloat()
  sf_switch_enable  = avango.SFBool()

  sf_rot_up         = avango.SFBool()
  sf_rot_down       = avango.SFBool()
  sf_rot_left       = avango.SFBool()
  sf_rot_right      = avango.SFBool()

  mf_pick_results_plus_x  = avango.gua.MFPickResult()
  mf_pick_results_minus_x = avango.gua.MFPickResult()

  mf_pick_results_plus_y  = avango.gua.MFPickResult()
  mf_pick_results_minus_y = avango.gua.MFPickResult()

  mf_pick_results_plus_z  = avango.gua.MFPickResult()
  mf_pick_results_minus_z = avango.gua.MFPickResult()


  def __init__(self):
    self.super(LightCube).__init__()
    self.always_evaluate(True)
    self.timer = avango.nodes.TimeSensor()

    self.NAME = "default_cube"
    self.HAS_LIGHT    = False
    self.ALWAYS_LIGHT = False

    self.console_node            = avango.gua.nodes.TransformNode(Name = "menu_node")
    self.cube                    = avango.gua.nodes.GeometryNode()
    #self.cube.add_and_init_field(avango.script.SFObject(), "LightCube", self)
    self.sf_color_red.value        = 0.5
    self.sf_color_green.value      = 0.5
    self.sf_color_blue.value       = 0.5
    self.LIGHTEXITS = []

    self.rot_up_button    = Button()
    self.rot_down_button  = Button()
    self.rot_left_button  = Button()
    self.rot_right_button = Button()

    self.pick_transforms_appended = False

    self.picked_plus_x = avango.gua.nodes.GeometryNode()
    self.picked_minus_x = avango.gua.nodes.GeometryNode()

    self.picked_plus_y = avango.gua.nodes.GeometryNode()
    self.picked_minus_y = avango.gua.nodes.GeometryNode()

    self.picked_plus_z = avango.gua.nodes.GeometryNode()
    self.picked_minus_z = avango.gua.nodes.GeometryNode()

    self.animation_flag = False
    self.animation_time = 0.5
    #self.animation_start_pos = avango.g
    #self.animation_end_pos


  def my_constructor(self, NAME, SCENEGRAPH, ROOMNODE, ACTIV, LIGHTEXITS):
    # init light cube
    self.loader       = avango.gua.nodes.GeometryLoader()
    self.NAME         = NAME
    self.HAS_LIGHT    = ACTIV
    self.ALWAYS_LIGHT = ACTIV
    self.LIGHTEXITS   = LIGHTEXITS
    self.SCENEGRAPH   = SCENEGRAPH
    self.ROOMNODE     = ROOMNODE

    self.cube_transform = avango.gua.nodes.TransformNode()

    self.cube_transform.Transform.value = avango.gua.make_trans_mat(0,1.5,0)
    self.cube_rotate = avango.gua.nodes.TransformNode()


    self.cube = self.loader.create_geometry_from_file( NAME + "_cube" , 'data/objects/cube.obj', "lightcube",
                  avango.gua.LoaderFlags.DEFAULTS | avango.gua.LoaderFlags.MAKE_PICKABLE)
    self.cube.Transform.value = avango.gua.make_scale_mat(0.1, 0.1, 0.1)
    self.cube.GroupNames.value  = ["interactiv"]
    self.cube.add_and_init_field(avango.script.SFObject(), "LightCube", self)

    self.ROOMNODE.Children.value.append(self.cube_transform)
    
    self.cube_transform.Children.value.append(self.cube_rotate)
    self.cube_rotate.Children.value.append(self.cube)


    # init menu
    self.initalize_console()
    self.console_node.Transform.value = avango.gua.make_trans_mat(0.0, 1.5, -0.5) * avango.gua.make_rot_mat(90, 1, 0, 0)
    self.enable_console(self.ROOMNODE)

    self.init_lightexits()

    # One Pick_Transform for every side of the cube
    # Each Pick_Transform holds a Ray and a Visual representation
    self.picker_plus_x         = LightRayPicker()
    self.pick_transform_plus_x = avango.gua.nodes.TransformNode(Name = "pick_transform_plus_x")
    self.pick_transform_plus_x.Transform.value = avango.gua.make_rot_mat(-90, 0, 1, 0)
    self.initialize_pick_transform(self.pick_transform_plus_x, self.picker_plus_x)

    self.picker_minus_x         = LightRayPicker()
    self.pick_transform_minus_x = avango.gua.nodes.TransformNode(Name = "pick_transform_minus_x")
    self.pick_transform_minus_x.Transform.value = avango.gua.make_rot_mat(90, 0, 1, 0)
    self.initialize_pick_transform(self.pick_transform_minus_x, self.picker_minus_x)

    self.picker_plus_y         = LightRayPicker()
    self.pick_transform_plus_y = avango.gua.nodes.TransformNode(Name = "pick_transform_plus_y")
    self.pick_transform_plus_y.Transform.value = avango.gua.make_rot_mat(90, 1, 0, 0)
    self.initialize_pick_transform(self.pick_transform_plus_y, self.picker_plus_y)
    
    self.picker_minus_y         = LightRayPicker()
    self.pick_transform_minus_y = avango.gua.nodes.TransformNode(Name = "pick_transform_minus_y")
    self.pick_transform_minus_y.Transform.value = avango.gua.make_rot_mat(-90, 1, 0, 0)
    self.initialize_pick_transform(self.pick_transform_minus_y, self.picker_minus_y)
    
    self.picker_plus_z         = LightRayPicker()
    self.pick_transform_plus_z = avango.gua.nodes.TransformNode(Name = "pick_transform_plus_z")
    self.initialize_pick_transform(self.pick_transform_plus_z, self.picker_plus_z)

    self.picker_minus_z         = LightRayPicker()
    self.pick_transform_minus_z = avango.gua.nodes.TransformNode(Name = "pick_transform_minus_z")
    self.pick_transform_minus_z.Transform.value = avango.gua.make_rot_mat(180, 1, 0, 0)
    self.initialize_pick_transform(self.pick_transform_minus_z, self.picker_minus_z)

    # Field Connections for the pick results
    self.mf_pick_results_plus_x.connect_from(self.picker_plus_x.Results)
    self.mf_pick_results_minus_x.connect_from(self.picker_minus_x.Results)

    self.mf_pick_results_plus_y.connect_from(self.picker_plus_y.Results)
    self.mf_pick_results_minus_y.connect_from(self.picker_minus_y.Results)

    self.mf_pick_results_plus_z.connect_from(self.picker_plus_z.Results)
    self.mf_pick_results_minus_z.connect_from(self.picker_minus_z.Results)


  def evaluate(self):
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


    # check if lightexits emmit light and append lights and rays
    if self.HAS_LIGHT and not self.pick_transforms_appended:
      for l in self.LIGHTEXITS:
        if (l == 1):
          self.cube.Children.value.append(self.pick_transform_plus_x)
        elif (l == 2):
          self.cube.Children.value.append(self.pick_transform_minus_x)
        elif (l == 3):
          self.cube.Children.value.append(self.pick_transform_plus_y)
        elif (l == 4):
          self.cube.Children.value.append(self.pick_transform_minus_y)
        elif (l == 5):
          self.cube.Children.value.append(self.pick_transform_plus_z)
        elif (l == 6):
          self.cube.Children.value.append(self.pick_transform_minus_z)
        self.pick_transforms_appended = True

    # check if ray hits object
    if self.HAS_LIGHT and self.pick_transforms_appended:
      for l in self.LIGHTEXITS:
        
        if (l == 1):
          if len(self.mf_pick_results_plus_x.value) > 0:
            self.picked_plus_x = self.mf_pick_results_plus_x.value[0].Object.value
            if self.picked_plus_x.has_field("LightCube"):
              self.picked_plus_x.LightCube.value.HAS_LIGHT = True
          if len(self.mf_pick_results_plus_x.value) == 0:           
            if self.picked_plus_x.has_field("LightCube") and not self.picked_plus_x.LightCube.value.ALWAYS_LIGHT:
              self.picked_plus_x.LightCube.value.HAS_LIGHT = False

        elif (l == 2):
          if len(self.mf_pick_results_minus_x.value) > 0:
            self.picked_minus_x = self.mf_pick_results_minus_x.value[0].Object.value
            if self.picked_minus_x.has_field("LightCube"):
              self.picked_minus_x.LightCube.value.HAS_LIGHT = True
          if len(self.mf_pick_results_minus_x.value) == 0:           
            if self.picked_minus_x.has_field("LightCube") and not self.picked_minus_x.LightCube.value.ALWAYS_LIGHT:
              self.picked_minus_x.LightCube.value.HAS_LIGHT = False
        
        elif (l == 3):
          if len(self.mf_pick_results_plus_y.value) > 0:
            self.picked_plus_y = self.mf_pick_results_plus_y.value[0].Object.value
            if self.picked_plus_y.has_field("LightCube"):
              self.picked_plus_y.LightCube.value.HAS_LIGHT = True
          if len(self.mf_pick_results_plus_y.value) == 0:           
            if self.picked_plus_y.has_field("LightCube") and not self.picked_plus_y.LightCube.value.ALWAYS_LIGHT:
              self.picked_plus_y.LightCube.value.HAS_LIGHT = False
        
        elif (l == 4):
          if len(self.mf_pick_results_minus_y.value) > 0:
            self.picked_minus_y = self.mf_pick_results_minus_y.value[0].Object.value
            if self.picked_minus_y.has_field("LightCube"):
              self.picked_minus_y.LightCube.value.HAS_LIGHT = True
          if len(self.mf_pick_results_minus_y.value) == 0:           
            if self.picked_minus_y.has_field("LightCube") and not self.picked_minus_y.LightCube.value.ALWAYS_LIGHT:
              self.picked_minus_y.LightCube.value.HAS_LIGHT = False
        
        elif (l == 5):
          if len(self.mf_pick_results_plus_z.value) > 0:
            self.picked_plus_z = self.mf_pick_results_plus_z.value[0].Object.value
            if self.picked_plus_z.has_field("LightCube"):
              self.picked_plus_z.LightCube.value.HAS_LIGHT = True
          if len(self.mf_pick_results_plus_z.value) == 0:           
            if self.picked_plus_z.has_field("LightCube") and not self.picked_plus_z.LightCube.value.ALWAYS_LIGHT:
              self.picked_plus_z.LightCube.value.HAS_LIGHT = False
        
        elif (l == 6):
          if len(self.mf_pick_results_minus_z.value) > 0:
            self.picked_minus_z = self.mf_pick_results_minus_z.value[0].Object.value
            if self.picked_minus_z.has_field("LightCube"):
              self.picked_minus_z.LightCube.value.HAS_LIGHT = True
          if len(self.mf_pick_results_minus_z.value) == 0:           
            if self.picked_minus_z.has_field("LightCube") and not self.picked_minus_z.LightCube.value.ALWAYS_LIGHT:
              self.picked_minus_z.LightCube.value.HAS_LIGHT = False


    if not self.HAS_LIGHT and self.pick_transforms_appended:
      for l in self.LIGHTEXITS:
        if (l == 1):
          self.cube.Children.value.remove(self.pick_transform_plus_x)
        elif (l == 2):
          self.cube.Children.value.remove(self.pick_transform_minus_x)
        elif (l == 3):
          self.cube.Children.value.remove(self.pick_transform_plus_y)
        elif (l == 4):
          self.cube.Children.value.remove(self.pick_transform_minus_y)
        elif (l == 5):
          self.cube.Children.value.remove(self.pick_transform_plus_z)
        elif (l == 6):
          self.cube.Children.value.remove(self.pick_transform_minus_z)
        self.pick_transforms_appended = False



  def initalize_console(self):
    self.rot_up_button.my_constructor("rot_up_" + self.NAME, avango.gua.make_trans_mat(0.0, 0.0, -0.5) * avango.gua.make_rot_mat(90, 0, 1, 0),self.console_node)
    self.sf_rot_up.connect_from(self.rot_up_button.sf_bool_button)
    self.rot_down_button.my_constructor("rot_down_" + self.NAME, avango.gua.make_trans_mat(0.0, 0.0, 0.5) * avango.gua.make_rot_mat(90, 0, 1, 0),self.console_node)
    self.sf_rot_down.connect_from(self.rot_down_button.sf_bool_button)
    self.rot_left_button.my_constructor("rot_left_" + self.NAME, avango.gua.make_trans_mat(-0.5, 0.0, 0.0),self.console_node)
    self.sf_rot_left.connect_from(self.rot_left_button.sf_bool_button)
    self.rot_right_button.my_constructor("rot_right_" + self.NAME, avango.gua.make_trans_mat(0.5, 0.0, 0.0),self.console_node)
    self.sf_rot_right.connect_from(self.rot_right_button.sf_bool_button)


  def init_lightexits(self):
    for l in self.LIGHTEXITS:
      if (l == 1):
        exit_plus_x = self.loader.create_geometry_from_file('light_exit_plus_x', 'data/objects/cube.obj',
                                                        'AvatarGrey', avango.gua.LoaderFlags.DEFAULTS | avango.gua.LoaderFlags.MAKE_PICKABLE)
        exit_plus_x.GroupNames.value = ["light_emitter"]
        exit_plus_x.add_and_init_field(avango.script.SFObject(), "LightCube", self)
        exit_plus_x.Transform.value = avango.gua.make_trans_mat(0.75,0,0) * avango.gua.make_scale_mat(0.5,0.5,0.5)
        self.cube.Children.value.append(exit_plus_x)
      elif (l == 2):
        exit_minus_x = self.loader.create_geometry_from_file('light_exit_minus_x', 'data/objects/cube.obj',
                                                        'AvatarGrey', avango.gua.LoaderFlags.DEFAULTS | avango.gua.LoaderFlags.MAKE_PICKABLE)
        exit_minus_x.Transform.value = avango.gua.make_trans_mat(-0.75,0,0) * avango.gua.make_scale_mat(0.5,0.5,0.5)
        exit_minus_x.GroupNames.value = ["light_emitter"]
        exit_minus_x.add_and_init_field(avango.script.SFObject(), "LightCube", self)
        self.cube.Children.value.append(exit_minus_x)
      elif (l == 3):
        exit_plus_y = self.loader.create_geometry_from_file('light_exit_plus_y', 'data/objects/cube.obj',
                                                        'AvatarGrey', avango.gua.LoaderFlags.DEFAULTS | avango.gua.LoaderFlags.MAKE_PICKABLE)
        exit_plus_y.Transform.value = avango.gua.make_trans_mat(0,0.75,0) * avango.gua.make_scale_mat(0.5,0.5,0.5)
        self.cube.Children.value.append(exit_plus_y)
      elif (l == 4):
        exit_minus_y = self.loader.create_geometry_from_file('light_exit_plus_z', 'data/objects/cube.obj',
                                                        'AvatarGrey', avango.gua.LoaderFlags.DEFAULTS | avango.gua.LoaderFlags.MAKE_PICKABLE)
        exit_minus_y.Transform.value = avango.gua.make_trans_mat(0,-0.75,0) * avango.gua.make_scale_mat(0.5,0.5,0.5)
        self.cube.Children.value.append(exit_minus_y)
      elif (l == 5):
        exit_plus_z = self.loader.create_geometry_from_file('light_exit_plus_z', 'data/objects/cube.obj',
                                                        'AvatarGrey', avango.gua.LoaderFlags.DEFAULTS | avango.gua.LoaderFlags.MAKE_PICKABLE)
        exit_plus_z.Transform.value = avango.gua.make_trans_mat(0,0,0.75) * avango.gua.make_scale_mat(0.5,0.5,0.5)
        self.cube.Children.value.append(exit_plus_z)
      elif (l == 6):
        exit_minus_z = self.loader.create_geometry_from_file('light_exit_plus_z', 'data/objects/cube.obj',
                                                        'AvatarGrey', avango.gua.LoaderFlags.DEFAULTS | avango.gua.LoaderFlags.MAKE_PICKABLE)
        exit_minus_z.Transform.value = avango.gua.make_trans_mat(0,0,-0.75) * avango.gua.make_scale_mat(0.5,0.5,0.5)
        self.cube.Children.value.append(exit_minus_z)


  def enable_console(self, MENU_LOCATION):
      MENU_LOCATION.Children.value.append(self.console_node)


  @field_has_changed(sf_rot_up)
  def rotate_up(self):
    if (self.sf_rot_up.value == True and self.animation_flag == False):
      self.animation_flag = True
      self.animation_start_time = self.timer.Time.value
      self.animation_start_pos = self.cube_rotate.Transform.value.get_rotate()
      self.animation_end_pos = (avango.gua.make_rot_mat(-90.0, 1, 0, 0) * self.cube_rotate.Transform.value).get_rotate()

      self.rot_up_button.just_rotated = True

  @field_has_changed(sf_rot_down)
  def rotate_down(self):
    if (self.sf_rot_down.value == True and self.animation_flag == False):
      self.animation_flag = True
      self.animation_start_time = self.timer.Time.value
      self.animation_start_pos = self.cube_rotate.Transform.value.get_rotate()
      self.animation_end_pos = (avango.gua.make_rot_mat(90.0, 1, 0, 0) * self.cube_rotate.Transform.value).get_rotate()
      self.rot_down_button.just_rotated = True

  @field_has_changed(sf_rot_left)
  def rotate_left(self):
    if (self.sf_rot_left.value == True and self.animation_flag == False):
      self.animation_flag = True
      self.animation_start_time = self.timer.Time.value
      self.animation_start_pos = self.cube_rotate.Transform.value.get_rotate()
      self.animation_end_pos = (avango.gua.make_rot_mat(-90.0, 0, 1, 0) * self.cube_rotate.Transform.value).get_rotate()
      self.rot_left_button.just_rotated = True

  @field_has_changed(sf_rot_right)
  def rotate_right(self):
    if (self.sf_rot_right.value == True and self.animation_flag == False):
      self.animation_flag = True
      self.animation_start_time = self.timer.Time.value
      self.animation_start_pos = self.cube_rotate.Transform.value.get_rotate()
      self.animation_end_pos = (avango.gua.make_rot_mat(90.0, 0, 1, 0) * self.cube_rotate.Transform.value).get_rotate()
      self.rot_right_button.just_rotated = True

  def initialize_pick_transform(self, pick_transform, PICKER):

    _ray   = avango.gua.nodes.RayNode(Name = "pick_ray_right")

    _ray.Transform.value = avango.gua.make_trans_mat(0.0, 0.0, -1.5) * avango.gua.make_scale_mat(1.0, 1.0, 100.0)

    _ray_visual = self.loader.create_geometry_from_file('ray' , 'data/objects/cube.obj',
                                                    'White', avango.gua.LoaderFlags.DEFAULTS)
    
    _ray_visual.Transform.value = avango.gua.make_trans_mat(0.0, 0.0, -21.5) *\
                                       avango.gua.make_scale_mat(0.008, 0.008, 20)
    
    # set picker values
    PICKER.SceneGraph = self.SCENEGRAPH
    PICKER.Ray.value = _ray
    PICKER.Mask.value = "light_emitter"
    pick_transform.Children.value = [_ray, _ray_visual]

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


'''
  @field_has_changed(sf_color_red)
  def change_color_r(self):
    _new_color = avango.gua.Vec3(self.sf_color_red.value, self.sf_color_green.value, self.sf_color_blue.value)
    avango.gua.set_material_uniform(self.material, "diffuse_color", _new_color)

  @field_has_changed(sf_color_green)
  def change_color_g(self):
    _new_color = avango.gua.Vec3(self.sf_color_red.value, self.sf_color_green.value, self.sf_color_blue.value)
    avango.gua.set_material_uniform(self.material, "diffuse_color", _new_color)

  @field_has_changed(sf_color_blue)
  def change_color_b(self):
    _new_color = avango.gua.Vec3(self.sf_color_red.value, self.sf_color_green.value, self.sf_color_blue.value)
    avango.gua.set_material_uniform(self.material, "diffuse_color", _new_color)

  @field_has_changed(sf_switch_enable)
  def change_switch_enable(self):
    if self.sf_switch_enable.value:
      self.geometry.Material.value = "AvatarYellow"
    elif self.sf_switch_enable.value == False:
      self.geometry.Material.value = "Stone"
'''