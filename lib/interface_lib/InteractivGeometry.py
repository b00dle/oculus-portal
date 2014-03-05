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
		self.NAME 								= ""	
		self.GEOMETRY 						= avango.gua.nodes.GeometryNode()
		self.menu_enabled 				= False
		self.size_slider					= Slider()
		self.menu_node 						= avango.gua.nodes.TransformNode(Name = "menu_node")

	def my_constructor(self, NAME, GEOMETRY_NODE, PARENT_NODE):
		# init interactiv geometry
		self.GEOMETRY 									= GEOMETRY_NODE
		self.GEOMETRY.GroupNames.value 	= ["interactiv"]
		self.GEOMETRY.add_and_init_field(avango.script.SFObject(), "InteractivGeometry", self)
		PARENT_NODE.Children.value.append(self.GEOMETRY)

		# init menu
    self.menu_node.Transform.value  = avango.gua.make_rot_mat(-90,1,0,0) * avango.gua.make_scale_mat(0.25,0.25,0.25)
		self.size_slider.my_constructor("size", avango.gua.make_trans_mat(0.0, 0.0, 0.0), self.menu_node, self.loader)


	def enable_menu(self, MENU_LOCATION):
		self.menu_enabled = True
		MENU_LOCATION.Children.value.append(self.menu_node)
		self.size_slider.GroupNames.value = [""]

	def close_menu()

	def size

	def on_off
	def color

	@field_has_changed(sf_resize)
  def resize_geometry(self):
  	self.GEOMETRY.Transform.value = avango.gua.make_scale_mat(self.sf_resize.value,
  																													  self.sf_resize.value,
  																													  self.sf_resize.value)




interactiv = InteractivGeometry()
interactiv.my_constructor(GeometryNode, size, on_off)

interactiv2 = InteractivGeometry()
interactiv2.my_constructor(GeometryNode, size, on_off, color)




