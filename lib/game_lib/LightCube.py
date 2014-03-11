#!/usr/bin/python

import avango
import avango.gua
import avango.script

class LightCube(avango.script.Script):

	def __init__(self):
		self.super(LightCube).__init__()
		self.Name = "default_cube"
		self.TransformNode = avango.gua.TransformNode(Name = "cube_transform")