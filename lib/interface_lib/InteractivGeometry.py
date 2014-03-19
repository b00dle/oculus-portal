#!/usr/bin/python

## @file
# Contains class Interface.

# import guacamole libraries
import avango
import avango.script
from avango.script import field_has_changed
import avango.gua

# import python libraries
import time
import math

# import framework libraries
from Interface import *


## Class that creates interactive geometrys. 
# An InteractivGemetry shows a specific interface, when it is selected by a User via the manipulator
class InteractivGeometry(avango.script.Script):

  ## @var sf_resize 
  # Float field which can be connected with a slider to resize the geometry
  sf_resize         = avango.SFFloat()

  ## @var sf_color_red
  # Float field which can be connected with a slider to change the color of the geometry
  sf_color_red      = avango.SFFloat()

  ## @var sf_color_green
  # Float field which can be connected with a slider to change the color of the geometry
  sf_color_green    = avango.SFFloat()

  ## @var sf_color_blue
  # Float field which can be connected with a slider to change the color of the geometry
  sf_color_blue     = avango.SFFloat()

  ## @var sf_switch_enabled
  # Bool field which can be connected with a switch to en-/disable the geometry
  sf_switch_enable  = avango.SFBool()

  ## @var sf_material
  # Field to change the color of the geometry
  sf_material = 'slider_mat_1'

  ## Default constructor.
  def __init__(self):
    self.super(InteractivGeometry).__init__()
    self.geometry             = avango.gua.nodes.GeometryNode()
    self.menu_enabled         = False
    self.menu_node            = avango.gua.nodes.TransformNode(Name = "menu_node")
    self.interface_elements   = []

    self.sf_color_red.value        = 0.5
    self.sf_color_green.value      = 0.5
    self.sf_color_blue.value       = 0.5

  ## Custom constructor
  # @param NAME The name of the InteractivGeometry.
  # @param PATH The filepath to the geometry (.obj).
  # @param MATERIAL The material of the geometry.
  # @param TRANSFORMATION The position of the geometry in world coordinates.
  # @param PARENT_NODE The node in the scenegraph to which the geometry is appended.
  # @param POSSIBLE_INTERACTIONS A list with strings, that defines the possible interactions with the geometry.
  def my_constructor(self, NAME, PATH, MATERIAL, TRANSFORMATION, PARENT_NODE, POSSIBLE_INTERACTIONS):
    loader = avango.gua.nodes.GeometryLoader()
    self.geometry = loader.create_geometry_from_file(NAME,
                                                     PATH,
                                                     MATERIAL,
                                                     avango.gua.LoaderFlags.DEFAULTS |\
                                                     avango.gua.LoaderFlags.MAKE_PICKABLE)
    self.geometry.GroupNames.value  = ["interactiv", "obsticale"]
    self.geometry.Transform.value = TRANSFORMATION
    self.geometry.add_and_init_field(avango.script.SFObject(),
                                     "InteractivGeometry",
                                     self)
    PARENT_NODE.Children.value.append(self.geometry)

    self.TRANSFORMATION   = TRANSFORMATION
    self.sf_resize.value  = 1

    self.init_menu(POSSIBLE_INTERACTIONS)

  ## Called whenever sf_color_red changes.
  # Applies a red color value to the geometry
  @field_has_changed(sf_color_red)
  def change_color_r(self):
    _new_color = avango.gua.Vec3(self.sf_color_red.value,
                                 self.sf_color_green.value,
                                 self.sf_color_blue.value)
    avango.gua.set_material_uniform(self.sf_material,
                                    "diffuse_color",
                                    _new_color)
  ## Called whenever sf_color_green changes.
  # Applies a green color value to the geometry
  @field_has_changed(sf_color_green)
  def change_color_g(self):
    _new_color = avango.gua.Vec3(self.sf_color_red.value,
                                 self.sf_color_green.value, 
                                 self.sf_color_blue.value)
    avango.gua.set_material_uniform(self.sf_material,
                                    "diffuse_color",
                                    _new_color)

  ## Called whenever sf_color_blue changes.
  # Applies a blue color value to the geometry
  @field_has_changed(sf_color_blue)
  def change_color_b(self):
    _new_color = avango.gua.Vec3(self.sf_color_red.value,
                                 self.sf_color_green.value,
                                 self.sf_color_blue.value)
    avango.gua.set_material_uniform(self.sf_material,
                                    "diffuse_color", 
                                    _new_color)

  ## Called whenever sf_switch_enable changes.
  # Applies a new material to the geometry
  @field_has_changed(sf_switch_enable)
  def change_switch_enable(self):
    if self.sf_switch_enable.value:
      self.geometry.Material.value = "CarPaintOrange"
    elif self.sf_switch_enable.value == False:
      self.geometry.Material.value = "CarPaintBlue"

  ## Called whenever sf_resize changes.
  # Applies a scaling to the geometry
  @field_has_changed(sf_resize)
  def change_size(self):
    self.geometry.Transform.value = self.TRANSFORMATION *\
                                    avango.gua.make_scale_mat(self.sf_resize.value,
                                                              self.sf_resize.value,
                                                              self.sf_resize.value)


  ## Initializes the menu with different interactions, depending in the possible interactions.
  # @param POSSIBLE_INTERACTIONS A list with strings, that defines the possible interactions with the geometry.
  def init_menu(self, POSSIBLE_INTERACTIONS):
    element_counter = 0
    self.menu_node.Transform.value = avango.gua.make_trans_mat(0, 0, -0.3) *\
                                     avango.gua.make_rot_mat(-90,1,0,0) *\
                                     avango.gua.make_scale_mat(0.25,0.25,0.25)
    for option in POSSIBLE_INTERACTIONS:
      
      # Slider to change size
      if(option == "size"):
        size_slider = Slider()
        size_slider.my_constructor(option,
                                   avango.gua.make_trans_mat(0.0, (element_counter * 0.4), 0.0),
                                   self.menu_node)
        size_slider.slider_geometry.GroupNames.value = ["interface_element"]
        self.sf_resize.connect_from(size_slider.sf_float_output)
        element_counter += 1

        self.interface_elements.append(size_slider)

      # Slider to change red color
      elif(option == "red"):
        red_slider = Slider()
        red_slider.my_constructor(option,
                                  avango.gua.make_trans_mat(0.0, (element_counter * 0.4), 0.0),
                                  self.menu_node)
        red_slider.slider_geometry.GroupNames.value = ["interface_element"]
        self.sf_color_red.connect_from(red_slider.sf_float_output)
        element_counter += 1

        self.interface_elements.append(red_slider)
      
      # Slider to change green color
      elif(option == "green"):
        green_slider = Slider()
        green_slider.my_constructor(option,
                                    avango.gua.make_trans_mat(0.0, (element_counter * 0.4), 0.0),
                                    self.menu_node)
        green_slider.slider_geometry.GroupNames.value = ["interface_element"]
        self.sf_color_green.connect_from(green_slider.sf_float_output)
        element_counter += 1

        self.interface_elements.append(green_slider)
      
      # Slider to change blue color
      elif(option == "blue"):
        blue_slider = Slider()
        blue_slider.my_constructor(option,
                                   avango.gua.make_trans_mat(0.0, (element_counter * 0.4), 0.0),
                                   self.menu_node)
        blue_slider.slider_geometry.GroupNames.value = ["interface_element"]
        self.sf_color_blue.connect_from(blue_slider.sf_float_output)
        element_counter += 1

        self.interface_elements.append(blue_slider)

      # Switch to enable something
      elif(option == "enable"):
        switch = Switch()
        switch.my_constructor(option,
                              avango.gua.make_trans_mat(0.0, (element_counter * 0.4), 0.0),
                              self.menu_node)
        element_counter += 1

        self.interface_elements.append(switch)
      
      else:
        print ("Error from InteractivGeometry: Wrong change option (", option, ")")


  ## Function that enables the menu-interface of the geometry
  # @param MENU_LOCATION The node in the scenegraph to which the menu is appended.
  def enable_menu(self, MENU_LOCATION):
    if self.menu_enabled == False:
      self.menu_enabled = True
      MENU_LOCATION.Children.value.append(self.menu_node)

  ## Function that disables the menu-interface of the geometry
  # @param MENU_LOCATION The node in the scenegraph to where the menu needs to be removed.
  def disable_menu(self, MENU_LOCATION):
    self.menu_enabled = False
    MENU_LOCATION.Children.value.remove(self.menu_node)

