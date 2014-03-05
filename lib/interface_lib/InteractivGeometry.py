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
  sf_enabled = avango.SFBool()
  sf_resize = avango.SFFloat()
  sf_color_red = avango.SFFloat()
  sf_color_green = avango.SFFloat()
  sf_color_blue = avango.SFFloat()

  def __init__(self):
    self.super(InteractivGeometry).__init__()
    self.NAME                 = ""  
    self.geometry             = avango.gua.nodes.GeometryNode()
    self.menu_enabled         = False
    self.menu_node            = avango.gua.nodes.TransformNode(Name = "menu_node")

  def my_constructor(self, NAME, PATH, MATERIAL, PARENT_NODE, CHANGE_OPTIONS):
    # init interactiv geometry
    loader = avango.gua.nodes.GeometryLoader()
    self.geometry = loader.create_geometry_from_file(NAME, PATH, MATERIAL,
                  avango.gua.LoaderFlags.DEFAULTS | avango.gua.LoaderFlags.MAKE_PICKABLE)
    self.geometry.GroupNames.value  = ["interactiv"]
    self.geometry.add_and_init_field(avango.script.SFObject(), "InteractivGeometry", self)
    PARENT_NODE.Children.value.append(self.geometry)

    # init menu
    self.initalize_menu(CHANGE_OPTIONS)

  def initalize_menu(self, CHANGE_OPTIONS):
    element_counter = 0
    self.menu_node.Transform.value = avango.gua.make_rot_mat(-90,1,0,0) * avango.gua.make_scale_mat(0.25,0.25,0.25)
    for option in CHANGE_OPTIONS:
      # Slider to change size
      if(option == "size"):
        size_slider = Slider()
        size_slider.my_constructor(option, avango.gua.make_trans_mat(0.0, (element_counter * 0.4), 0.0), self.menu_node)
        size_slider.slider_geometry.GroupNames.value = ["interface_element"]
        self.sf_resize.connect_from(size_slider.sf_float_output)
        element_counter += 1
        print option, "created"
      # Slider to change red color
      elif(option == "red"):
        red_slider = Slider()
        red_slider.my_constructor(option, avango.gua.make_trans_mat(0.0, (element_counter * 0.4), 0.0), self.menu_node)
        red_slider.slider_geometry.GroupNames.value = ["interface_element"]
        self.sf_color_red.connect_from(red_slider.sf_float_output)
        element_counter += 1
        print option, "created"
      # Slider to change green color
      elif(option == "green"):
        green_slider = Slider()
        green_slider.my_constructor(option, avango.gua.make_trans_mat(0.0, (element_counter * 0.4), 0.0), self.menu_node)
        green_slider.slider_geometry.GroupNames.value = ["interface_element"]
        self.sf_color_green.connect_from(green_slider.sf_float_output)
        element_counter += 1
        print option, "created"
      # Slider to change blue color
      elif(option == "blue"):
        blue_slider = Slider()
        blue_slider.my_constructor(option, avango.gua.make_trans_mat(0.0, (element_counter * 0.4), 0.0), self.menu_node)
        blue_slider.slider_geometry.GroupNames.value = ["interface_element"]
        self.sf_color_blue.connect_from(blue_slider.sf_float_output)
        element_counter += 1
        print option, "created"
      # Switch to enable something
      #elif(option == "enable"):
      #  switch = Switch()
      #  slider.my_constructor(option, avango.gua.make_trans_mat(0.0, 0.0, 0.0), self.menu_node)
      #
      #  element_counter += 1
      #  print option, "created"
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



# @field_has_changed(sf_resize)
#  def resize_geometry(self):
#   self.GEOMETRY.Transform.value = avango.gua.make_scale_mat(self.sf_resize.value * factor_size,
#                                                             self.sf_resize.value,
 #                                                            self.sf_resize.value)




#interactiv = InteractivGeometry()
#interactiv.my_constructor(GeometryNode, size, on_off)

#interactiv2 = InteractivGeometry()
#interactiv2.my_constructor(GeometryNode, size, factor_size, on_off, color)




'''
    self.menu_node.Transform.value  = avango.gua.make_rot_mat(-90,1,0,0) * avango.gua.make_scale_mat(0.25,0.25,0.25)
    self.size_slider.my_constructor("size", avango.gua.make_trans_mat(0.0, 0.0, 0.0), self.menu_node, self.loader)
    self.size_slider.
'''