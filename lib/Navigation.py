#!/usr/bin/python

## @file
# Contains class Navigation.

# import avango-guacamole
import avango
import avango.gua
import avango.script

from Device           import *
from GroundFollowing  import GroundFollowing
from InputMapping     import InputMapping
from Platform         import Platform

import Tools
import TraceLines

# import python libraries
import math

## Wrapper class to create an input Device, a GroundFollowing instance, an InputMapping and a Platform.
#
# Furthermore, this class reacts on the device's button inputs and toggles the 3-DOF (realistic) / 6-DOF (unrealistic) 
# navigation mode. When switching from unrealistic to realistic mode, an animation is triggered in which the platform
# is rotated back in an upright position (removal of pitch and roll angle).

class Navigation(avango.script.Script):

  ## Default constructor.
  def __init__(self):
    self.super(Navigation).__init__()

  ## Custom constructor.
  # @param SCENEGRAPH Reference to the scenegraph in which the navigation should take place.
  # @param PLATFORM_SIZE Physical size of the platform in meters. Passed in an two-element list: [width, depth]
  # @param STARTING_MATRIX Initial position matrix of the platform to be created.
  # @param NAVIGATION_LIST List of all navigations in the setup.
  # @param INPUT_SENSOR_TYPE String indicating the type of input device to be created, e.g. "XBoxController" or "Spheron"
  # @param INPUT_SENSOR_NAME Name of the input device sensor as chosen in daemon.
  # @param NO_TRACKING_MAT Matrix which should be applied if no tracking is available.
  # @param GF_SETTINGS Setting list for the GroundFollowing instance: [activated, ray_start_height]
  # @param ANIMATE_COUPLING Boolean indicating if an animation should be done when a coupling of navigations is initiated.
  # @param MOVEMENT_TRACES Boolean indicating if the device should leave traces behind.
  # @param TRACKING_TARGET_NAME Name of the device's tracking target name as chosen in daemon.
  def my_constructor(self, SCENEGRAPH, PLATFORM_SIZE, STARTING_MATRIX, NAVIGATION_LIST, INPUT_SENSOR_TYPE, INPUT_SENSOR_NAME, NO_TRACKING_MAT, GF_SETTINGS, ANIMATE_COUPLING, MOVEMENT_TRACES, TRACKING_TARGET_NAME = None):
    
    ## @var SCENEGRAPH
    # Reference to the scenegraph.
    self.SCENEGRAPH = SCENEGRAPH

    ## @var coupled_navigations
    # List of coupled Navigation instances to which this Navigation's changes are forwarded to.
    self.coupled_navigations = []

    ## @var input_sensor_type
    # String indicating the type of input device to be created, e.g. "XBoxController" or "Spheron"
    self.input_sensor_type = INPUT_SENSOR_TYPE

    ## @var start_matrix
    # Initial position matrix of the platform.
    self.start_matrix = STARTING_MATRIX
    
    # create device
    ## @var device
    # Device instance handling relative inputs of physical device.
    if self.input_sensor_type == "Spheron":
      self.device = OldSpheronDevice()
      self.device.my_constructor(INPUT_SENSOR_NAME, TRACKING_TARGET_NAME, NO_TRACKING_MAT)
    elif self.input_sensor_type == "XBoxController":
      self.device = XBoxDevice()
      self.device.my_constructor(INPUT_SENSOR_NAME, TRACKING_TARGET_NAME, NO_TRACKING_MAT)
    elif self.input_sensor_type == "KeyboardMouse":
      self.device = KeyboardMouseDevice()
      self.device.my_constructor()
    elif self.input_sensor_type == "Spacemouse":
      self.device = SpacemouseDevice()
      self.device.my_constructor(INPUT_SENSOR_NAME)
    
    # create ground following
    ## @var groundfollowing
    # GroundFollowing instance to correct the absolute matrices with respect to gravity.
    self.groundfollowing = GroundFollowing()
    self.groundfollowing.my_constructor(self.SCENEGRAPH, self.device.sf_station_mat, GF_SETTINGS)

    # create input mapping
    ## @var inputmapping
    # InputMapping instance to process and map relative device inputs to an absolute matrix.
    self.inputmapping = InputMapping()
    self.inputmapping.my_constructor(self, self.device, self.groundfollowing, STARTING_MATRIX)
    self.inputmapping.set_input_factors(self.device.translation_factor, self.device.rotation_factor)
    
    # create platform
    ## @var platform
    # Platform instance that is controlled by the Device.
    self.platform = Platform()
    self.platform.my_constructor(self.SCENEGRAPH, PLATFORM_SIZE, self.inputmapping, len(NAVIGATION_LIST))

    ## @var NAVIGATION_LIST
    # Reference to a list containing all Navigation instances in the setup.
    self.NAVIGATION_LIST = NAVIGATION_LIST

    # attributes
    ## @var in_dofchange_animation
    # Boolean variable to indicate if a movement animation for a DOF change (realistic/unrealistic) is in progress.
    self.in_dofchange_animation = False

    ## @var frames_since_last_dofchange
    # Framecount to make realistic/unrealistic switch on one button. Switching again is possible after x frames.
    self.frames_since_last_dofchange = 0

    ## @var frames_since_last_coupling
    # Framecount since the last coupling / decoupling operation was done. Used to make functionality on one button.
    self.frames_since_last_coupling = 0

    ## @var in_coupling_animation
    # Boolean variable to indicate if a movement animation for coupling is in progress.
    self.in_coupling_animation = False

    ## @var timer
    # Instance of TimeSensor to handle the duration of animations.
    self.timer = avango.nodes.TimeSensor()

    ## @var ANIMATE_COUPLING
    # Boolean indicating if an animation should be done when a coupling of navigations is initiated.
    self.ANIMATE_COUPLING = ANIMATE_COUPLING

    ## @var movement_traces
    # Boolean indicating if the movement traces should be visualized by line segments.
    self.movement_traces = MOVEMENT_TRACES

    ## @var trace
    # The trace class that handles the line segment updating.
    self.trace = None
      

    # evaluate every frame
    self.always_evaluate(True)

  ## Resets the platform's matrix to the initial value.
  def reset(self):
    self.inputmapping.set_abs_mat(self.start_matrix)

  ## Sets platform to new start position
  def set_to_pos(self, NEWPOS):
    self.start_matrix = NEWPOS
    self.reset()

  ## Activates 3-DOF (realistic) navigation mode.
  def activate_realistic_mode(self):

    # remove pitch and roll from current orientation
    _current_mat = self.platform.sf_abs_mat.value
    _current_trans = _current_mat.get_translate()
    _current_yaw = Tools.get_yaw(_current_mat)

    ## @var start_rot
    # Quaternion representing the start rotation of the animation
    self.start_rot = self.platform.sf_abs_mat.value.get_rotate()

    ## @var target_rot
    # Quaternion representing the target rotation of the animation
    self.target_rot = avango.gua.make_rot_mat(math.degrees(_current_yaw), 0, 1, 0).get_rotate()

    ## @var animation_time
    # Time of the rotation animation in relation to the rotation distance.
    self.animation_time = 2 * math.sqrt(math.pow(self.start_rot.x - self.target_rot.x, 2) +\
                           math.pow(self.start_rot.y - self.target_rot.y, 2) + math.pow(self.start_rot.z -\
                           self.target_rot.z, 2) + math.pow(self.start_rot.w - self.target_rot.w, 2))
   
    # if no animation is needed, set animation time to a minimum value to avoid division by zero
    if self.animation_time == 0.0:
      self.animation_time = 0.01

    ## @var start_trans
    # Starting translation vector of the animation.
    self.start_trans = _current_trans

    ## @var animation_start_time
    # Point in time where the animation started.
    self.animation_start_time = self.timer.Time.value
 
    self.in_dofchange_animation = True                       
  
  ## Animates the removal of pitch and roll angles when switching from 6-DOF (unrealistic) to 3-DOF (realistic) navigation mode.
  def animate_dofchange(self):

    _current_time = self.timer.Time.value
    _slerp_ratio = (_current_time - self.animation_start_time) / self.animation_time

    if _slerp_ratio > 1:
      _slerp_ratio = 1
      self.in_dofchange_animation = False
      self.inputmapping.activate_realistic_mode()
      self.frames_since_last_dofchange = 0

    _transformed_quat = self.start_rot.slerp_to(self.target_rot, _slerp_ratio)

    _position_yaw_mat = avango.gua.make_trans_mat(self.start_trans.x, self.start_trans.y, self.start_trans.z) * \
                        avango.gua.make_rot_mat(_transformed_quat)

    self.inputmapping.set_abs_mat(_position_yaw_mat)

  ## Activates 6-DOF (unrealistic) navigation mode.
  def deactivate_realistic_mode(self):
    self.inputmapping.deactivate_realistic_mode()
    self.frames_since_last_dofchange = 0

  ## Bidirectional coupling of this and another navigation.
  # @param NAVIGATION The Navigation to be coupled.
  def couple_navigation(self, NAVIGATION):
    if not ((NAVIGATION in self.coupled_navigations) or (self in NAVIGATION.coupled_navigations)):
      for _nav in self.coupled_navigations:
        if not (NAVIGATION in _nav.coupled_navigations):
          _nav.coupled_navigations.append(NAVIGATION)
        if not (_nav in NAVIGATION.coupled_navigations):
          NAVIGATION.coupled_navigations.append(_nav)
      for _nav in NAVIGATION.coupled_navigations:
        if not (self in _nav.coupled_navigations):
          _nav.coupled_navigations.append(self)
        if not (_nav in self.coupled_navigations):
          self.coupled_navigations.append(_nav)
      self.coupled_navigations.append(NAVIGATION)
      NAVIGATION.coupled_navigations.append(self)

  ## Bidirectional decoupling of this and another navigation.
  # @param NAVIGATION The Navigation to be decoupled.
  def decouple_navigation(self, NAVIGATION):
    if NAVIGATION in self.coupled_navigations:
      self.coupled_navigations.remove(NAVIGATION)
      NAVIGATION.coupled_navigations.remove(self)

  ## Triggers the coupling mechanism.
  # When other platforms are close enough, they are coupled to each other.
  def trigger_coupling(self):

    self.frames_since_last_coupling = 0
    
    # list containing the navigataions close enough to couple
    _close_navs = []

    # threshold when two navigations should be considered for coupling (distance in meter)
    _threshold = 7.0
    
    # compute center position of own platform
    _position_self = (self.platform.sf_abs_mat.value * self.device.sf_station_mat.value).get_translate()

    # check for all navigations in the setup
    for _nav in self.NAVIGATION_LIST:
      
      # compute center position of currently iterated platform
      _position_nav = (_nav.platform.sf_abs_mat.value * _nav.device.sf_station_mat.value).get_translate()

      # append navigation to the list of close ones if distance is smaller than a threshold
      if _nav != self and Tools.euclidean_distance(_position_self, _position_nav) < _threshold:
        _close_navs.append(_nav)

    # sort list of close navs, highest distance first
    _close_navs.sort(key = lambda _nav: Tools.euclidean_distance(_position_self, (_nav.platform.sf_abs_mat.value * _nav.device.sf_station_mat.value).get_translate()), reverse = True)

    if len(_close_navs) > 0:
      # couple the close navigations
      for _nav in _close_navs:
        self.couple_navigation(_nav)

      if self.ANIMATE_COUPLING:
        # do an animation to closest navigation if this functionality is switched on
        _nav_animation_target = _close_navs[-1]
        
        self.set_coupling_animation_settings(_nav_animation_target)
   
        for i in range(len(_close_navs) - 1):
          _close_navs[i].set_coupling_animation_settings(_nav_animation_target)

      print "Coupling of platform " + str(self.platform.platform_id) + " successfully initiated."

    else:
      #print "No platform in range for coupling."
      self.frames_since_last_coupling = 0
  
  ## Sets all the necessary attributes to perform a lerp and slerp animation to another navigation.
  # @param TARGET_NAVIGATION The Navigation instance to animate to.
  def set_coupling_animation_settings(self, TARGET_NAVIGATION):
    self.start_rot = self.platform.sf_abs_mat.value.get_rotate()
    self.start_trans = self.platform.sf_abs_mat.value.get_translate()

    _start_rot_center_mat = self.platform.sf_abs_mat.value * self.device.sf_station_mat.value
    _target_rot_center_mat = TARGET_NAVIGATION.platform.sf_abs_mat.value * TARGET_NAVIGATION.device.sf_station_mat.value

    _difference_vector = _target_rot_center_mat.get_translate() - _start_rot_center_mat.get_translate()
    _difference_vector.y = 0.0

    self.target_rot = self.start_rot
    #self.target_rot = avango.gua.make_rot_mat(math.degrees(Tools.get_yaw(_target_rot_center_mat)), 0, 1, 0).get_rotate()
    self.target_trans = self.start_trans + _difference_vector

    self.animation_time = 0.5 * math.sqrt(math.pow(self.start_trans.x - self.target_trans.x, 2) + math.pow(self.start_trans.y - self.target_trans.y, 2) + math.pow(self.start_trans.z - self.target_trans.z, 2)) + \
                          math.sqrt(math.pow(self.start_rot.x - self.target_rot.x, 2) + math.pow(self.start_rot.y - self.target_rot.y, 2) + math.pow(self.start_rot.z - self.target_rot.z, 2) + math.pow(self.start_rot.w - self.target_rot.w, 2))

    # if no animation is needed, set animation time to a minimum value to avoid division by zero
    if self.animation_time == 0.0:
      self.animation_time = 0.01

    self.animation_start_time = self.timer.Time.value
    self.in_coupling_animation = True

  ## Animates the movement to another platform during the coupling process.
  def animate_coupling(self):
    
    _current_time = self.timer.Time.value
    _animation_ratio = (_current_time - self.animation_start_time) / self.animation_time

    if _animation_ratio > 1:
      _animation_ratio = 1
      self.in_coupling_animation = False
      self.frames_since_last_coupling = 0

    _transformed_quat = self.start_rot.slerp_to(self.target_rot, _animation_ratio)
    _transformed_vec = self.start_trans.lerp_to(self.target_trans, _animation_ratio)

    _animation_mat = avango.gua.make_trans_mat(_transformed_vec.x, _transformed_vec.y, _transformed_vec.z) * \
                     avango.gua.make_rot_mat(_transformed_quat)

    self.inputmapping.set_abs_mat(_animation_mat)
  
  ## Decouples this Navigation from all coupled Navigations.
  def clear_couplings(self):

    if len(self.coupled_navigations) > 0:
      # create hard copy of coupled navigations
      _couplings = list(self.coupled_navigations)

      # iterate over all navigations and clear the coupling
      for _nav in _couplings:
        _nav.decouple_navigation(self)

      self.coupled_navigations = []
      self.frames_since_last_coupling = 0

      print "Cleared couplings of platform " + str(self.platform.platform_id)

  ## Switches from realistic to unrealistic or from unrealistic to realistic mode on this
  # and all other coupled instances.
  def trigger_dofchange(self):

    # if in realistic mode, switch to unrealistic mode
    if self.inputmapping.realistic == True:
      self.deactivate_realistic_mode()
      for _navigation in self.coupled_navigations:
        _navigation.deactivate_realistic_mode()
    
    # if in unrealistic mode, switch to realistic mode
    else:
      self.activate_realistic_mode()
      for _navigation in self.coupled_navigations:
        _navigation.activate_realistic_mode()

  
  ## Evaluated every frame.
  def evaluate(self):

    # increase frame counters
    self.frames_since_last_dofchange = self.frames_since_last_dofchange + 1
    self.frames_since_last_coupling = self.frames_since_last_coupling + 1

    # handle visibilities
    self.platform.platform_transform_node.GroupNames.value = []
    for _nav in self.coupled_navigations:
      self.platform.platform_transform_node.GroupNames.value.append("couple_group_" + str(_nav.platform.platform_id))


    # handle button inputs

    if self.input_sensor_type == "Spheron" or self.input_sensor_type == "KeyboardMouse":

      # left mouse button (Spheron) or R-key (KeyboardMouse) resets platform
      if self.device.mf_buttons.value[1] == True:
        self.reset()
        for _navigation in self.coupled_navigations:
            _navigation.reset()

      # right mouse button (Spheron) or H-key (KeyboardMouse) triggers switch between 
      # realistic (3 DOF) and unrealistic (6 DOF) mode
      if self.device.mf_buttons.value[0] == True:
        if self.frames_since_last_dofchange > 100:        # at least 100 frames must lie between two dofchanges
           self.trigger_dofchange()

      # middle mouse button (Spheron) or G-key (KeyboardMouse) triggers coupling
      if self.device.mf_buttons.value[2] == True:
        if self.frames_since_last_coupling > 100:        # at least 100 frames must lie between two coupling actions
          if len(self.coupled_navigations) == 0:
            self.trigger_coupling()
          else:
            self.clear_couplings()               
    

    elif self.input_sensor_type == "XBoxController":
      # X Button resets platform
      if self.device.mf_buttons.value[2] == True:
        self.reset()
        for _navigation in self.coupled_navigations:
            _navigation.reset()
      
      # A Button triggers switch between realistic (3 DOF) and unrealistic (6 DOF) mode
      if self.device.mf_buttons.value[0] == True:
        if self.frames_since_last_dofchange > 100:        # at least 100 frames must lie between two dofchanges
           self.trigger_dofchange()

      # B Button triggers coupling
      if self.device.mf_buttons.value[1] == True:
        if self.frames_since_last_coupling > 100:        # at least 100 frames must lie between two coupling actions
          if len(self.coupled_navigations) == 0:
            self.trigger_coupling()
          else:
            self.clear_couplings()


    elif self.input_sensor_type == "Spacemouse":
      
      # left button triggers switch between realistic (3 DOF) and unrealistic (6 DOF) mode
      if self.device.mf_buttons.value[0] == True:
        if self.frames_since_last_dofchange > 100:       # at least 100 frames must lie between two dofchanges
          self.trigger_dofchange()

      # right button triggers coupling
      if self.device.mf_buttons.value[1] == True:
        if self.frames_since_last_coupling > 100:        # at least 100 frames must lie between two coupling actions
          if len(self.coupled_navigations) == 0:
            self.trigger_coupling()
          else:
            self.clear_couplings()

          
    # handle dofchange animation
    if self.in_dofchange_animation:
      self.animate_dofchange()

    # handle coupling animation
    elif self.in_coupling_animation:
      self.animate_coupling()

    # draw the traces if enabled
    #if self.movement_traces:
    #  _station_trans = self.device.sf_station_mat.value.get_translate()
    #  _mat = self.platform.sf_abs_mat.value * avango.gua.make_trans_mat(_station_trans.x, 0, _station_trans.z)
    #  if self.trace == None:
    #    self.trace = TraceLines.Trace(self.SCENEGRAPH.Root.value, self.platform.platform_id, 20, _mat)  
      
    #  self.trace.update(_mat)