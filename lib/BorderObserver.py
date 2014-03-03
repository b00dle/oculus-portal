#!/usr/bin/python

## @file
# Contains class BorderObserver.

# import avango-guacamole
import avango
import avango.gua
import avango.script

# import framework libraries
from User            import *
from PowerWallUser   import *
from OVRUser         import *
from Platform        import *

## Class to check whether users on a platform are close to platform borders.
#
# If one of the observed users is close to a platform border, the corresponding
# border plane is made visible.

class BorderObserver(avango.script.Script):

  ## @var warning_tolerance
  # Distance to a border when the warning plane should be displayed
  warning_tolerance = 0.7

  ## Default constructor
  def __init__(self):
    self.super(BorderObserver).__init__()

  ## Custom constructor
  # @param CHECKED_BORDERS A list of four booleans about which borders of the platform should be observed. 
  # [display_left_border, display_right_border, display_front_border, display_back_border]
  # @param USER_INSTANCE The first user to be observed.
  # @param PLATFORM_INSTANCE The platform on which the observed users are.
  def my_constructor(self, CHECKED_BORDERS, USER_INSTANCE, PLATFORM_INSTANCE):

    ## @var PLATFORM_INSTANCE
    # Reference to the platform on which the observed users stand.
    self.PLATFORM_INSTANCE = PLATFORM_INSTANCE

    ## @var platform_width
    # Physical width of the platform in meters.
    self.platform_width = self.PLATFORM_INSTANCE.width

    ## @var platform_depth
    # Physical depth of the platform in meters.
    self.platform_depth = self.PLATFORM_INSTANCE.depth

    ## @var checked_borders
    # A list of four booleans about which borders of the platform should be observed. [left, right, front, back].
    self.checked_borders = CHECKED_BORDERS                       

    ## @var user_list
    # A list of users to be observed.
    self.user_list = [USER_INSTANCE]

    self.always_evaluate(True)

  ## Adds a user to the list of observed ones.
  # @param USER_INSTANCE The user to be added.
  def add_user(self, USER_INSTANCE):
    self.user_list.append(USER_INSTANCE)

  ## Evaluated every frame.
  def evaluate(self):
    _left_plane_visible = False
    _right_plane_visible = False
    _front_plane_visible = False
    _back_plane_visible = False

    for _user in self.user_list:
      _pos = _user.head_transform.Transform.value.get_translate()

      if self.checked_borders[0]:
        # toggle left border visibility
        if _pos.x < -self.platform_width/2 + self.warning_tolerance:
          _left_plane_visible = True

      if self.checked_borders[1]:
        # toggle right border visibility
        if _pos.x > self.platform_width/2 - self.warning_tolerance:
          _right_plane_visible = True
   
      if self.checked_borders[2]:
        # toggle front border visibility
        if _pos.z < 0.0 + self.warning_tolerance:
          _front_plane_visible = True

      if self.checked_borders[3]:
        # toggle back border visibility
        if _pos.z > self.platform_depth - self.warning_tolerance:
          _back_plane_visible = True


    if _left_plane_visible == False:
      self.PLATFORM_INSTANCE.display_left_border(False)
    else:
      self.PLATFORM_INSTANCE.display_left_border(True)

    if _right_plane_visible == False:
      self.PLATFORM_INSTANCE.display_right_border(False)
    else:
      self.PLATFORM_INSTANCE.display_right_border(True)

    if _front_plane_visible == False:
      self.PLATFORM_INSTANCE.display_front_border(False)
    else:
      self.PLATFORM_INSTANCE.display_front_border(True)

    if _back_plane_visible == False:
      self.PLATFORM_INSTANCE.display_back_border(False)
    else:
      self.PLATFORM_INSTANCE.display_back_border(True)
