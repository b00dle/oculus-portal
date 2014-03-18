#!/usr/bin/python

import avango
import avango.script
from avango.script import field_has_changed
import avango.gua
import time
import math

import examples_common.navigator
from examples_common.GuaVE import GuaVE

from Interface import *

class InteractivGeometry(avango.script.Script):
  sf_enabled      = avango.SFBool()
  sf_resize       = avango.SFFloat()
  sf_color_red    = avango.SFFloat()
  sf_color_green  = avango.SFFloat()
  sf_color_blue   = avango.SFFloat()
  sf_switch_enable  = avango.SFBool()

  material = 'slider_mat_1'

  def __init__(self):
    self.super(InteractivGeometry).__init__()
    self.NAME                 = ""  
    self.geometry             = avango.gua.nodes.GeometryNode()
    self.menu_enabled         = False
    self.menu_node            = avango.gua.nodes.TransformNode(Name = "menu_node")
    self.interface_elements   = []

    self.sf_color_red.value        = 0.5
    self.sf_color_green.value      = 0.5
    self.sf_color_blue.value       = 0.5

    # test slider
    #self.size_slider = Slider()

  def my_constructor(self, NAME, PATH, MATERIAL, TRANSFORMATION, PARENT_NODE, CHANGE_OPTIONS):
    # init interactiv geometry
    loader = avango.gua.nodes.GeometryLoader()
    self.TRANSFORMATION = TRANSFORMATION
    self.geometry = loader.create_geometry_from_file(NAME, PATH, MATERIAL,
                  avango.gua.LoaderFlags.DEFAULTS | avango.gua.LoaderFlags.MAKE_PICKABLE)
    self.geometry.GroupNames.value  = ["interactiv", "obsticale"]
    self.geometry.Transform.value = self.TRANSFORMATION
    self.geometry.add_and_init_field(avango.script.SFObject(), "InteractivGeometry", self)
    PARENT_NODE.Children.value.append(self.geometry)

    self.material = MATERIAL
    self.sf_resize.value = 1
    # init menu
    self.initalize_menu(CHANGE_OPTIONS)

  def portal_constructor(self, NAME, GEOMETRY, CHANGE_OPTIONS, PORTAL):
    self.NAME = NAME
    self.geometry = GEOMETRY
    self.geometry.add_and_init_field(avango.script.SFObject(), "InteractivGeometry", self)
    self.PORTAL = PORTAL

    self.initalize_menu(CHANGE_OPTIONS)

  def initalize_menu(self, CHANGE_OPTIONS):
    element_counter = 0
    self.menu_node.Transform.value = avango.gua.make_trans_mat(0, 0, -0.3) * avango.gua.make_rot_mat(-90,1,0,0) * avango.gua.make_scale_mat(0.25,0.25,0.25)
    for option in CHANGE_OPTIONS:
      # Slider to change size
      if(option == "size"):
        size_slider = Slider()
        size_slider.my_constructor(option, avango.gua.make_trans_mat(0.0, (element_counter * 0.4), 0.0), self.menu_node)
        size_slider.slider_geometry.GroupNames.value = ["interface_element"]
        self.sf_resize.connect_from(size_slider.sf_float_output)
        element_counter += 1

        self.interface_elements.append(size_slider)
        print option, "created"
      # Slider to change y Position
      if(option == "x_pos"):
        x_pos_slider = Slider()
        x_pos_slider.my_constructor(option, avango.gua.make_trans_mat(0.0, (element_counter * 0.4), 0.0), self.menu_node)
        x_pos_slider.slider_geometry.GroupNames.value = ["interface_element"]
        self.sf_resize.connect_from(x_pos_slider.sf_float_output)
        element_counter += 1

        self.interface_elements.append(x_pos_slider)
        print option, "created"
      # Slider to change y Position
      if(option == "y_pos"):
        y_pos_slider = Slider()
        y_pos_slider.my_constructor(option, avango.gua.make_trans_mat(0.0, (element_counter * 0.4), 0.0), self.menu_node)
        y_pos_slider.slider_geometry.GroupNames.value = ["interface_element"]
        self.sf_resize.connect_from(y_pos_slider.sf_float_output)
        element_counter += 1

        self.interface_elements.append(y_pos_slider)
        print option, "created"
      # Slider to change z Position
      if(option == "z_pos"):
        z_pos_slider = Slider()
        z_pos_slider.my_constructor(option, avango.gua.make_trans_mat(0.0, (element_counter * 0.4), 0.0), self.menu_node)
        z_pos_slider.slider_geometry.GroupNames.value = ["interface_element"]
        self.sf_resize.connect_from(z_pos_slider.sf_float_output)
        element_counter += 1

        self.interface_elements.append(z_pos_slider)
        print option, "created"
      # Slider to change red color
      elif(option == "red"):
        red_slider = Slider()
        red_slider.my_constructor(option, avango.gua.make_trans_mat(0.0, (element_counter * 0.4), 0.0), self.menu_node)
        red_slider.slider_geometry.GroupNames.value = ["interface_element"]
        self.sf_color_red.connect_from(red_slider.sf_float_output)
        element_counter += 1

        self.interface_elements.append(red_slider)
        print option, "created"
      # Slider to change green color
      elif(option == "green"):
        green_slider = Slider()
        green_slider.my_constructor(option, avango.gua.make_trans_mat(0.0, (element_counter * 0.4), 0.0), self.menu_node)
        green_slider.slider_geometry.GroupNames.value = ["interface_element"]
        self.sf_color_green.connect_from(green_slider.sf_float_output)
        element_counter += 1

        self.interface_elements.append(green_slider)
        print option, "created"
      # Slider to change blue color
      elif(option == "blue"):
        blue_slider = Slider()
        blue_slider.my_constructor(option, avango.gua.make_trans_mat(0.0, (element_counter * 0.4), 0.0), self.menu_node)
        blue_slider.slider_geometry.GroupNames.value = ["interface_element"]
        self.sf_color_blue.connect_from(blue_slider.sf_float_output)
        element_counter += 1

        self.interface_elements.append(blue_slider)
        print option, "created"

      # Switch to enable something
      elif(option == "enable"):
        switch = Switch()
        switch.my_constructor(option, avango.gua.make_trans_mat(0.0, (element_counter * 0.4), 0.0), self.menu_node)
        element_counter += 1

        self.interface_elements.append(switch)
        print option, "created"
      
      else:
        print "Wrong change option"

  def enable_menu(self, MENU_LOCATION):
    if self.menu_enabled == False:
      self.menu_enabled = True
      MENU_LOCATION.Children.value.append(self.menu_node)
      #self.menu_node.GroupNames.value = ["interface_element"]

  def disable_menu(self, MENU_LOCATION):
    self.menu_enabled = False
    MENU_LOCATION.Children.value.remove(self.menu_node)

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

  @field_has_changed(sf_resize)
  def change_size(self):
    self.geometry.Transform.value = self.TRANSFORMATION *\
                                    avango.gua.make_scale_mat(self.sf_resize.value,
                                                              self.sf_resize.value,
                                                              self.sf_resize.value)
    print self.geometry.Transform.value