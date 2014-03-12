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
  def __init__(self):
    self.super(LightCube).__init__()
    self.NAME = "default_cube"
    self.HAS_LIGHT = False

    self.console_node            = avango.gua.nodes.TransformNode(Name = "menu_node")
    self.cube      = avango.gua.nodes.GeometryNode()
    self.sf_color_red.value        = 0.5
    self.sf_color_green.value      = 0.5
    self.sf_color_blue.value       = 0.5
    self.LIGHTEXITS = []

    self.rot_up_button = Button()
    self.rot_down_button = Button()
    self.rot_left_button = Button()
    self.rot_right_button = Button()

  def my_constructor(self, NAME, PARENT_NODE, ACTIV, LIGHTEXITS):
    # init light cube
    self.loader = avango.gua.nodes.GeometryLoader()
    self.NAME = NAME
    self.HAS_LIGHT = ACTIV
    self.LIGHTEXITS = LIGHTEXITS

    self.cube = self.loader.create_geometry_from_file( NAME + "_cube" , 'data/objects/cube.obj', "lightcube",
                  avango.gua.LoaderFlags.DEFAULTS | avango.gua.LoaderFlags.MAKE_PICKABLE)
    self.cube.GroupNames.value  = ["interactiv"]
    self.cube.Transform.value = avango.gua.make_trans_mat(0,1.5,0) * avango.gua.make_scale_mat(0.2, 0.2, 0.2)
    self.cube.add_and_init_field(avango.script.SFObject(), "LightCube", self)
    PARENT_NODE.Children.value.append(self.cube)

    # init menu
    self.initalize_console()
    self.console_node.Transform.value = avango.gua.make_trans_mat(0.0, 1.0, 0.0) * avango.gua.make_rot_mat(90, 1, 0, 0)
    self.enable_console(PARENT_NODE)

    self.init_lightexits()

  def initalize_console(self):
    self.rot_up_button.my_constructor("rot_up_" + self.NAME, avango.gua.make_trans_mat(0.0, 0.0, -0.5) * avango.gua.make_rot_mat(90, 0, 1, 0),self.console_node)
    self.sf_rot_up.connect_from(self.rot_up_button.sf_bool_button)
    self.rot_down_button.my_constructor("rot_down_" + self.NAME, avango.gua.make_trans_mat(0.0, 0.0, 0.5) * avango.gua.make_rot_mat(90, 0, 1, 0),self.console_node)
    self.rot_left_button.my_constructor("rot_left_" + self.NAME, avango.gua.make_trans_mat(-0.5, 0.0, 0.0),self.console_node)
    self.rot_right_button.my_constructor("rot_right_" + self.NAME, avango.gua.make_trans_mat(0.5, 0.0, 0.0),self.console_node)


  def init_lightexits(self):
    for l in self.LIGHTEXITS:
      if (l == 1):
        exit_top = self.loader.create_geometry_from_file('light_exit_top', 'data/objects/cube.obj',
                                                        'AvatarGrey', avango.gua.LoaderFlags.DEFAULTS | avango.gua.LoaderFlags.MAKE_PICKABLE)
        exit_top.Transform.value = avango.gua.make_trans_mat(0,0.75,0) * avango.gua.make_scale_mat(0.5,0.5,0.5)
        self.cube.Children.value.append(exit_top)
      elif (l == 2):
        pass
      elif (l == 3):
        pass
      elif (l == 4):
        pass
      elif (l == 5):
        pass
      elif (l == 6):
        pass


  def enable_console(self, MENU_LOCATION):
      MENU_LOCATION.Children.value.append(self.console_node)

  def disable_menu(self, MENU_LOCATION):
    MENU_LOCATION.Children.value.remove(self.console_node)

  @field_has_changed(sf_rot_up)
  def rotate_up(self):
    if (self.sf_rot_up.value == True):
      self.cube.Transform.value *= 
      self.rot_up_button.just_rotated = True



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