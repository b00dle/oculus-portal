import avango
import avango.gua
from avango.script import field_has_changed
import avango.script

import math



class PortalButton(avango.script.Script):

  sf_bool_button   = avango.SFBool()
  sf_visible       = avango.SFBool()
  sf_portal_active = avango.SFBool()

  def __init__(self):
    self.super(PortalButton).__init__()
    self.always_evaluate(True)

    self.NAME = ""
    self.button_pos = avango.gua.Mat4()
    self.PARENT_NODE = avango.gua.nodes.TransformNode()
    self.button_geometry = avango.gua.nodes.GeometryNode()
    self.button_transform = avango.gua.nodes.TransformNode()

    self.button_scale = avango.gua.make_scale_mat(1, 1, 1)

    self.sf_bool_button.value = False
    self.sf_visible.value = False

    self.state_changed = False

  def my_constructor(self, NAME, PARENT_NODE, SIDE ):
    self.NAME = NAME
    self.PARENT_NODE = PARENT_NODE

    self.LOADER = avango.gua.nodes.GeometryLoader()
    self.button_geometry = self.LOADER.create_geometry_from_file('button_' + NAME, 'data/objects/arrow.obj',
                            "Yellow" , avango.gua.LoaderFlags.DEFAULTS | avango.gua.LoaderFlags.MAKE_PICKABLE)
    rot_mat = avango.gua.make_rot_mat(-90,0,1,0)

    if (SIDE == "left"):
      self.button_pos  = avango.gua.make_trans_mat(-1.5, 1.5, 0) * avango.gua.make_rot_mat(90,0,1,0) *\
                         rot_mat* avango.gua.make_scale_mat(0.08,0.08,0.08)
    elif (SIDE == "right"):
      self.button_pos  = avango.gua.make_trans_mat(1.5, 1.5, 0) * avango.gua.make_rot_mat(-90,0,1,0)* rot_mat* avango.gua.make_scale_mat(0.08,0.08,0.08)
    elif (SIDE == "up"):
      self.button_pos  = avango.gua.make_trans_mat(0, 3, 0) * avango.gua.make_rot_mat(90,1,0,0)* rot_mat* avango.gua.make_scale_mat(0.08,0.08,0.08)
    elif (SIDE == "down"):
      self.button_pos  = avango.gua.make_trans_mat(0, 0, 0) * avango.gua.make_rot_mat(-90,1,0,0)* rot_mat*avango.gua.make_scale_mat(0.08,0.08,0.08)
    elif (SIDE == "front"):
      self.button_pos  = avango.gua.make_trans_mat(0, 1.5, -1.5)* rot_mat*avango.gua.make_scale_mat(0.08,0.08,0.08)
    elif (SIDE == "back"):
      self.button_pos  = avango.gua.make_trans_mat(0, 1.5, 1.5) * avango.gua.make_rot_mat(180,0,1,0)*rot_mat  * avango.gua.make_scale_mat(0.08,0.08,0.08)

    #self.button_geometry = self.LOADER.create_geometry_from_file('button_' + NAME, 'data/objects/cube.obj',
     #                                                       'Blue' , avango.gua.LoaderFlags.DEFAULTS | avango.gua.LoaderFlags.MAKE_PICKABLE)
    self.button_geometry.GroupNames.value.append("console")
    self.button_geometry.add_and_init_field(avango.script.SFObject(), "Button", self)

    self.button_transform = avango.gua.nodes.TransformNode(Name = 'switch_' + NAME)
    self.button_transform.Transform.value = self.button_pos
    self.button_transform.Children.value.append(self.button_geometry)
    self.PARENT_NODE.Children.value.append(self.button_transform)

  def evaluate(self):
    if not self.sf_visible.value:
      if self.sf_portal_active.value:
        self.sf_portal_active.value = False
      if self.sf_bool_button.value:
        self.sf_bool_button.value = False
      if "do_not_display_group" not in self.button_geometry.GroupNames.value:
        self.button_geometry.GroupNames.value.append("do_not_display_group")
    else:
      if "do_not_display_group" in self.button_geometry.GroupNames.value:
        self.button_geometry.GroupNames.value.remove("do_not_display_group")

  @field_has_changed(sf_bool_button)
  def toggle_portal_active_field(self):
    if self.sf_bool_button.value and self.sf_visible.value:
      self.sf_portal_active.value = not self.sf_portal_active.value
      self.state_changed = True