#!/usr/bin/python

## @file
# Contains class ViewingManager.

# import guacamole libraries
import avango
import avango.gua
import avango.daemon
from   examples_common.GuaVE import GuaVE

# import framework libraries
from   Navigation       import *
from   Platform         import *
from   User             import *
from   OVRUser          import *
from   PowerWallUser    import *
from   DesktopUser      import *
from   BorderObserver   import *
import Tools

## Class to manage all the classes and processes in the application.
#
# Creates Navigation, OVRUser, PowerWallUser and BorderObserver instances according to the preferences read in from a XML configuration file.

class ViewingManager():
  
  ## @var viewer
  # The guacamole viewer to be used for rendering.
  viewer = avango.gua.nodes.Viewer()

  ## @var shell
  # The GuaVE shell to be used when the application is running.
  shell = GuaVE()

  ## Custom constructor
  # @param SCENEGRAPHS Reference to all scenegraph used in the application.
  # @param CONFIG_FILE Path to the XML configuration file.
  def __init__(self, SCENEGRAPHS, CONFIG_FILE):
    
    # parameters
    ## @var background_texture
    # The skymap to be used for all pipelines.
    self.background_texture = "data/textures/sky.jpg"
    avango.gua.create_texture(self.background_texture)

    # references
    ## @var SCENEGRAPH
    # Reference to the scenegraph.
    self.SCENEGRAPH = SCENEGRAPHS[0]

    # variables
    ## @var powerwall_user_list
    # List of all created PowerWallUser instances.
    self.powerwall_user_list  = []

    ## @var ovr_user_list
    # List of all created OVRUser instances.
    self.ovr_user_list        = []

    ## @var desktop_user_list
    # List of all created DesktopUser instances.
    self.desktop_user_list        = []

    ## @var navigation_list
    # List of all created Navigation instances.
    self.navigation_list      = []

    ## @var border_observer_list
    # List of all created BorderObserver instances.
    self.border_observer_list = []

    # global settings (can be overwritten by config file)
    ## @var transmitter_offset
    # Transmitter offset to be read in from configuration file
    self.transmitter_offset = avango.gua.make_identity_mat()

    ## @var no_tracking_mat
    # Matrix to be used when no tracking is available to be read in from configuration file
    self.no_tracking_mat = avango.gua.make_identity_mat()

    ## @var ground_following_settings
    # Settings for the GroundFollowing instance to be read in from configuration file: [activated, ray_start_height]
    self.ground_following_settings = [False, 0.75]

    ## @var enable_coupling_animation
    # Boolean indicating if an animation should be done when a coupling of Navigations is initiated.
    self.enable_coupling_animation = False

    ## @var enable_movementtraces
    #  Boolean indicating if the movement of every platform should be visualized by line segments.
    self.enable_movementtraces = False

    # load configuration file
    self.parse_config_file(CONFIG_FILE)

    for i in range(0, len(SCENEGRAPHS)):
      self.viewer.SceneGraphs.value.append(SCENEGRAPHS[i])

  ## Creates a Navigation instance and adds it to the list of navigations.
  # @param INPUT_DEVICE_TYPE Type of the input device to be associated (e.g. XBoxController" or "Spheron")
  # @param INPUT_DEVICE_NAME Name of the input device values as chosen in daemon.
  # @param STARTING_MATRIX Initial platform matrix for the new device.
  # @param PLATFORM_SIZE Physical size of the platform in meters. [width, depth]
  # @param ANIMATE_COUPLING Boolean indicating if an animation should be done when a coupling of Navigations is initiated.
  # @param MOVEMENT_TRACES Boolean indicating if the platform should leave traces behind.
  # @param DEVICE_TRACKING_NAME Name of the device's tracking sensor as chosen in daemon if available.
  def create_navigation(self, INPUT_DEVICE_TYPE, INPUT_DEVICE_NAME, STARTING_MATRIX, PLATFORM_SIZE, ANIMATE_COUPLING, MOVEMENT_TRACES, DEVICE_TRACKING_NAME = None):
    _navigation = Navigation()
    _navigation.my_constructor(self.SCENEGRAPH, PLATFORM_SIZE, STARTING_MATRIX, self.navigation_list, INPUT_DEVICE_TYPE, INPUT_DEVICE_NAME, self.no_tracking_mat, self.ground_following_settings, ANIMATE_COUPLING, MOVEMENT_TRACES, DEVICE_TRACKING_NAME)
    self.navigation_list.append(_navigation)
    self.border_observer_list.append(None)

  ## Creates a OVRUser instance and adds it to the list of OVRUsers.
  # @param TRACKING_TARGET_NAME Name of the Oculus Rift's tracking target as chosen in daemon.py
  # @param INITIAL_PLATFORM_ID Platform to which the user should be appended to.
  # @param WARNINGS Boolean value to determine if the user should be appended to a BorderObserver (i.e. the user is shown warning planes when close to the platform borders)
  def create_ovr_user(self, TRACKING_TARGET_NAME, INITIAL_PLATFORM_ID, SCENEGRAPH, WARNINGS):

    _user = OVRUser(self, TRACKING_TARGET_NAME, len(self.ovr_user_list), INITIAL_PLATFORM_ID, self.no_tracking_mat, SCENEGRAPH)
    self.ovr_user_list.append(_user)
   
    # init border checker to warn user on platform
    if WARNINGS:
      if self.border_observer_list[INITIAL_PLATFORM_ID] == None:
        _checked_borders = [True, True, True, True]
        self.create_border_observer(_checked_borders, _user, self.navigation_list[INITIAL_PLATFORM_ID].platform)
      else:
        self.border_observer_list[INITIAL_PLATFORM_ID].add_user(_user)

  ## Creates a PowerWallUser instance and adds it to the list of PowerWallUsers.
  # @param TRACKING_TARGET_NAME Name of the glasses' tracking target as chosen in daemon.py
  # @param INITIAL_PLATFORM_ID Platform to which the user should be appended to.
  # @param TRANSMITTER_OFFSET The transmitter offset to be applied.
  # @param WARNINGS Boolean value to determine if the user should be appended to a BorderObserver (i.e. the user is shown warning planes when close to the platform borders)
  def create_powerwall_user(self, TRACKING_TARGET_NAME, INITIAL_PLATFORM_ID, TRANSMITTER_OFFSET, SCENEGRAPH, WARNINGS):

    _user = PowerWallUser(self, TRACKING_TARGET_NAME, len(self.powerwall_user_list), INITIAL_PLATFORM_ID, self.no_tracking_mat, TRANSMITTER_OFFSET, SCENEGRAPH)
    self.powerwall_user_list.append(_user)

    # init border checker to warn user on platform
    if WARNINGS:
      if self.border_observer_list[INITIAL_PLATFORM_ID] == None:
        _checked_borders = [False, False, True, False]
        self.create_border_observer(_checked_borders, _user, self.navigation_list[INITIAL_PLATFORM_ID].platform)
      else:
        self.border_observer_list[INITIAL_PLATFORM_ID].add_user(_user)

  ## Creates a DesktopUser instance and adds it to the list of DesktopUsers.
  # @param INITIAL_PLATFORM_ID Platform to which the user should be appended to.
  # @param WINDOW_SIZE Resolution of the window to be created on the display. [width, height]
  # @param SCREEN_SIZE Physical width of the screen space to be rendered on in meters. [width, height]
  def create_desktop_user(self, INITIAL_PLATFORM_ID, WINDOW_SIZE, SCREEN_SIZE, SCENEGRAPH):

    _user = DesktopUser(self, len(self.desktop_user_list), INITIAL_PLATFORM_ID, WINDOW_SIZE, SCREEN_SIZE, SCENEGRAPH)
    self.desktop_user_list.append(_user)
   

  ## Creates a BorderObserver instance for a Platform and adds a User to it.
  # @param CHECKED_BORDERS A list of four booleans to indicate which borders of the platform should be checked: 
  # [display_left_border, display_right_border, display_front_border, display_back_border]
  # @param USER_INSTANCE A first User to be appended to the new BorderObserver.
  # @param PLATFORM_INSTANCE The platform to which the BorderObserver should belong to.
  def create_border_observer(self, CHECKED_BORDERS, USER_INSTANCE, PLATFORM_INSTANCE):
    _border_observer = BorderObserver()
    _border_observer.my_constructor(CHECKED_BORDERS, USER_INSTANCE, PLATFORM_INSTANCE)
    self.border_observer_list[PLATFORM_INSTANCE.platform_id] = _border_observer


  ## Parses a XML configuration file, saves settings and creates navigations and users.
  # @param FILENAME The path of the configuration file to be read in.
  def parse_config_file(self, FILENAME):
    print "\n=============================================================================="
    print "Loading configuration file", FILENAME
    print "==============================================================================\n"

    _in_comment = False
    _in_global = False
    _in_device = False
    _device_attributes = [None, None, None, None, None, None, None]      # [type, inputsensor, trackingstation, startpos, platformpos (x,y,z), platformrot (yaw))]
    _platform_size = [1.0, 1.0]                                          # [width, depth]
    _in_user = False
    _user_attributes = [None, None, None, False]                         # [type, headtrackingstation, startplatform, warnings]
    _window_size = [1920, 1080]                                          # [width, height]
    _screen_size = [1.6, 1.0]                                            # [width, height]

    _config_file = open(FILENAME, 'r')
    _current_line = self.get_next_line_in_file(_config_file)

    while _current_line != "":
      
      # handle end of block comments
      if _in_comment and _current_line.rstrip().endswith("-->"):
        _in_comment = False
        _current_line = self.get_next_line_in_file(_config_file)
        continue
      elif _in_comment:
        _current_line = self.get_next_line_in_file(_config_file)
        continue

      # ignore one line comments
      if _current_line.startswith("<!--") and _current_line.rstrip().endswith("-->"):
        _current_line = self.get_next_line_in_file(_config_file)
        continue

      # handle start of block comments
      if _current_line.startswith("<!--"):
        _in_comment = True
        _current_line = self.get_next_line_in_file(_config_file)
        continue
      
      # ignore XML declaration
      if _current_line.startswith("<?xml"):
        _current_line = self.get_next_line_in_file(_config_file)
        continue
    
      # ignore doctype declaration
      if _current_line.startswith("<!DOCTYPE"):
        _current_line = self.get_next_line_in_file(_config_file)
        continue

      # ignore opening setup tag
      if _current_line.startswith("<setup>"):
        _current_line = self.get_next_line_in_file(_config_file)
        continue
      
      # detect end of configuration file
      if _current_line.startswith("</setup>"):
        break

      # detect start of global settings
      if _current_line.startswith("<global>"):
        _in_global = True
        _current_line = self.get_next_line_in_file(_config_file)
        continue

      if _in_global:
        # get transmitter offset values
        if _current_line.startswith("<transmitteroffset>"):
          _current_line = self.get_next_line_in_file(_config_file)
          _current_line = _current_line.replace("<x>", "")
          _current_line = _current_line.replace("</x>", "")
          _current_line = _current_line.rstrip()
          _transmitter_x = float(_current_line)
          _current_line = self.get_next_line_in_file(_config_file)
          _current_line = _current_line.replace("<y>", "")
          _current_line = _current_line.replace("</y>", "")
          _current_line = _current_line.rstrip()
          _transmitter_y = float(_current_line)
          _current_line = self.get_next_line_in_file(_config_file)
          _current_line = _current_line.replace("<z>", "")
          _current_line = _current_line.replace("</z>", "")
          _current_line = _current_line.rstrip()
          _transmitter_z = float(_current_line)
          self.transmitter_offset = avango.gua.make_trans_mat(_transmitter_x, _transmitter_y, _transmitter_z)

        # get end of transmitter offset values
        if _current_line.startswith("</transmitteroffset>"):
          _current_line = self.get_next_line_in_file(_config_file)
          continue

        # get no tracking position values
        if _current_line.startswith("<notrackingposition>"):
          _current_line = self.get_next_line_in_file(_config_file)
          _current_line = _current_line.replace("<x>", "")
          _current_line = _current_line.replace("</x>", "")
          _current_line = _current_line.rstrip()
          _no_tracking_x = float(_current_line)
          _current_line = self.get_next_line_in_file(_config_file)
          _current_line = _current_line.replace("<y>", "")
          _current_line = _current_line.replace("</y>", "")
          _current_line = _current_line.rstrip()
          _no_tracking_y = float(_current_line)
          _current_line = self.get_next_line_in_file(_config_file)
          _current_line = _current_line.replace("<z>", "")
          _current_line = _current_line.replace("</z>", "")
          _current_line = _current_line.rstrip()
          _no_tracking_z = float(_current_line)
          self.no_tracking_mat = avango.gua.make_trans_mat(_no_tracking_x, _no_tracking_y, _no_tracking_z)

        # get end of no tracking position values
        if _current_line.startswith("</notrackingposition>"):
          _current_line = self.get_next_line_in_file(_config_file)
          continue

        # get ground following attributes
        if _current_line.startswith("<groundfollowing>"):
          _current_line = self.get_next_line_in_file(_config_file)
          _current_line = _current_line.replace("<activated>", "")
          _current_line = _current_line.replace("</activated>", "")
          _current_line = _current_line.rstrip()
           
          if _current_line == "True":
            self.ground_following_settings[0] = True
          else:
            self.ground_following_settings[0] = False

          _current_line = self.get_next_line_in_file(_config_file)
          _current_line = _current_line.replace("<raystartheight>", "")
          _current_line = _current_line.replace("</raystartheight>", "")
          _current_line = _current_line.rstrip()
          self.ground_following_settings[1] = float(_current_line)
        
        # get end of ground following attributes
        if _current_line.startswith("</groundfollowing>"):
          _current_line = self.get_next_line_in_file(_config_file)
          continue

        # get coupling animation boolean
        if _current_line.startswith("<animatecoupling>"):
          _current_line = _current_line.replace("<animatecoupling>", "")
          _current_line = _current_line.replace("</animatecoupling>", "")
          _current_line = _current_line.rstrip()
          self.enable_coupling_animation = bool(_current_line)

        # get platformtraces boolean
        if _current_line.startswith("<movementtraces>"):
          _current_line = _current_line.replace("<movementtraces>", "")
          _current_line = _current_line.replace("</movementtraces>", "")
          _current_line = _current_line.rstrip()
          self.enable_movementtraces = bool(_current_line)

      # detect end of global settings
      if _current_line.startswith("</global>"):
        _in_global = False
        _current_line = self.get_next_line_in_file(_config_file)

        print "Global settings loaded:"
        print "------------------------"
        print "Transmitter Offset:", self.transmitter_offset.get_translate()
        print "No tracking position:", self.no_tracking_mat.get_translate()
        print "Ground Following settings:", self.ground_following_settings
        print "Coupling of Navigations animated:", self.enable_coupling_animation, "\n"

        continue

      # detect start of device declaration
      if _current_line.startswith("<device>"):
        _in_device = True
        _current_line = self.get_next_line_in_file(_config_file)
        continue

      # read device values
      if _in_device:
        # get device type
        if _current_line.startswith("<type>"):
          _current_line = _current_line.replace("<type>", "")
          _current_line = _current_line.replace("</type>", "")
          _current_line = _current_line.rstrip()
          _device_attributes[0] = _current_line
       
        # get inputsensor name
        if _current_line.startswith("<inputsensor>"):
          _current_line = _current_line.replace("<inputsensor>", "")
          _current_line = _current_line.replace("</inputsensor>", "")
          _current_line = _current_line.rstrip()
          _device_attributes[1] = _current_line
        
        # get trackingstation name
        if _current_line.startswith("<trackingstation>"):
          _current_line = _current_line.replace("<trackingstation>", "")
          _current_line = _current_line.replace("</trackingstation>", "")
          _current_line = _current_line.rstrip()
          if _current_line != "None":
            _device_attributes[2] = _current_line

        # get platform position values
        if _current_line.startswith("<platformpos>"):
          _current_line = self.get_next_line_in_file(_config_file)
          _current_line = _current_line.replace("<x>", "")
          _current_line = _current_line.replace("</x>", "")
          _current_line = _current_line.rstrip()
          _device_attributes[3] = float(_current_line)
          _current_line = self.get_next_line_in_file(_config_file)
          _current_line = _current_line.replace("<y>", "")
          _current_line = _current_line.replace("</y>", "")
          _current_line = _current_line.rstrip()
          _device_attributes[4] = float(_current_line)
          _current_line = self.get_next_line_in_file(_config_file)
          _current_line = _current_line.replace("<z>", "")
          _current_line = _current_line.replace("</z>", "")
          _current_line = _current_line.rstrip()
          _device_attributes[5] = float(_current_line)

        # get end of platform position
        if _current_line.startswith("</platformpos>"):
          _current_line = self.get_next_line_in_file(_config_file)
          continue

        # get platform size values
        if _current_line.startswith("<platformsize>"):
          _current_line = self.get_next_line_in_file(_config_file)
          _current_line = _current_line.replace("<width>", "")
          _current_line = _current_line.replace("</width>", "")
          _current_line = _current_line.rstrip()
          _platform_size[0] = float(_current_line)
          _current_line = self.get_next_line_in_file(_config_file)
          _current_line = _current_line.replace("<depth>", "")
          _current_line = _current_line.replace("</depth>", "")
          _current_line = _current_line.rstrip()
          _platform_size[1] = float(_current_line)

        # get end of platform size values
        if _current_line.startswith("</platformsize>"):
          _current_line = self.get_next_line_in_file(_config_file)
          continue

        # get platform rotation values
        if _current_line.startswith("<platformrot>"):
          _current_line = self.get_next_line_in_file(_config_file)
          _current_line = _current_line.replace("<yaw>", "")
          _current_line = _current_line.replace("</yaw>", "")
          _current_line = _current_line.rstrip()
          _device_attributes[6] = float(_current_line)

        # get end of platform rotation
        if _current_line.startswith("</platformrot>"):
          _current_line = self.get_next_line_in_file(_config_file)
          continue
      
      # detect end of device declaration
      if _current_line.startswith("</device>"):
        _in_device = False
        _starting_matrix = avango.gua.make_trans_mat(_device_attributes[3], _device_attributes[4], _device_attributes[5]) * \
                           avango.gua.make_rot_mat(_device_attributes[6], 0, 1, 0)
      
        self.create_navigation(_device_attributes[0], 
                               _device_attributes[1],
                               _starting_matrix,
                               _platform_size,
                               self.enable_coupling_animation,
                               self.enable_movementtraces,
                               _device_attributes[2]) 

        print "Navigation loaded and created:"
        print "------------------------------"
        print _device_attributes
        print "Platform size: ", _platform_size, "\n"

        _device_attributes = [None, None, None, None, None, None, None]
        _current_line = self.get_next_line_in_file(_config_file)
        continue
     
      # detect start of user declaration
      if _current_line.startswith("<user>"):
        _in_user = True
        _current_line = self.get_next_line_in_file(_config_file)
        continue

      # read user values
      if _in_user:
        # get user type
        if _current_line.startswith("<type>"):
          _current_line = _current_line.replace("<type>", "")
          _current_line = _current_line.replace("</type>", "")
          _current_line = _current_line.rstrip()
          _user_attributes[0] = _current_line
        
        # get headtracking station name
        if _current_line.startswith("<headtrackingstation>"):
          _current_line = _current_line.replace("<headtrackingstation>", "")
          _current_line = _current_line.replace("</headtrackingstation>", "")
          _current_line = _current_line.rstrip()
          if _current_line != "None":
            _user_attributes[1] = _current_line

        # get starting platform name
        if _current_line.startswith("<startplatform>"):
          _current_line = _current_line.replace("<startplatform>", "")
          _current_line = _current_line.replace("</startplatform>", "")
          _current_line = _current_line.rstrip()
          _user_attributes[2] = int(_current_line)

        # get window size values
        if _current_line.startswith("<windowsize>"):
          _current_line = self.get_next_line_in_file(_config_file)
          _current_line = _current_line.replace("<width>", "")
          _current_line = _current_line.replace("</width>", "")
          _current_line = _current_line.rstrip()
          _window_size[0] = int(_current_line)
          _current_line = self.get_next_line_in_file(_config_file)
          _current_line = _current_line.replace("<height>", "")
          _current_line = _current_line.replace("</height>", "")
          _current_line = _current_line.rstrip()
          _window_size[1] = int(_current_line)

        # get screen size values
        if _current_line.startswith("<screensize>"):
          _current_line = self.get_next_line_in_file(_config_file)
          _current_line = _current_line.replace("<width>", "")
          _current_line = _current_line.replace("</width>", "")
          _current_line = _current_line.rstrip()
          _screen_size[0] = float(_current_line)
          _current_line = self.get_next_line_in_file(_config_file)
          _current_line = _current_line.replace("<height>", "")
          _current_line = _current_line.replace("</height>", "")
          _current_line = _current_line.rstrip()
          _screen_size[1] = float(_current_line)

        # get boolean for warning borders
        if _current_line.startswith("<warnings>"):
          _current_line = _current_line.replace("<warnings>", "")
          _current_line = _current_line.replace("</warnings>", "")
          _current_line = _current_line.rstrip()
          
          if _current_line == "True":
            _user_attributes[3] = True

      # detect end of user declaration
      if _current_line.startswith("</user>"):
        _in_user = False

        if _user_attributes[0] == "PowerWallUser":
          self.create_powerwall_user(_user_attributes[1], _user_attributes[2], self.transmitter_offset, self.SCENEGRAPH, _user_attributes[3])
        elif _user_attributes[0] == "OVRUser":
          print "Oculus Rift Messages:"
          print "----------------------"
          self.create_ovr_user(_user_attributes[1], _user_attributes[2], self.SCENEGRAPH, _user_attributes[3])
        elif _user_attributes[0] == "DesktopUser":
          self.create_desktop_user(_user_attributes[2], _window_size, _screen_size, self.SCENEGRAPH)
        else:
          print "Unknown user type", _user_attributes[0]
          _current_line = self.get_next_line_in_file(_config_file)
          continue

        print "\nUser loaded and created:"
        print "-------------------------"
        print _user_attributes, "\n"

        if _user_attributes[0] == "DesktopUser":
          print "Window resolution:", _window_size[0], "x", _window_size[1]
          print "Screen size:", _screen_size[0], "x", _screen_size[1], "\n"
          # restore default values
          _window_size = [1920, 1080]
          _screen_size = [1.6, 1.0]

        _user_attributes = [None, None, None, False]
        _current_line = self.get_next_line_in_file(_config_file)
        continue

      # go to next line in file
      _current_line = self.get_next_line_in_file(_config_file)

    print "\n=============================================================================="
    print "Configuration file", FILENAME, "successfully loaded."
    print "=============================================================================="

  ## Gets the next line in the file. Thereby, empty lines are skipped.
  # @param FILE The opened file to get the line from.
  def get_next_line_in_file(self, FILE):
    _next_line = FILE.readline()
    _next_line = _next_line.replace(" ", "")

    # skip empty lines
    while _next_line == "\r\n":
      _next_line = FILE.readline()
      _next_line = _next_line.replace(" ", "")

    return _next_line

  ## Sets RenderMask for hiding portals not owned by user
  def setup_portal_render_masks(self):
    # extend render mask for oculus users
    for OVR_user in self.ovr_user_list:
      for other_OVR_user in self.ovr_user_list:
        if other_OVR_user.id != OVR_user.id:
          OVR_user.camera.RenderMask.value = OVR_user.camera.RenderMask.value + \
                                          " && !" + other_OVR_user.portal_controller.NAME + \
                                          "portals"
      for DESK_user in self.desktop_user_list:
        OVR_user.camera.RenderMask.value = OVR_user.camera.RenderMask.value + \
                                          " && !" + DESK_user.portal_controller.NAME + \
                                          "portals"
      for PW_user in self.powerwall_user_list:
        OVR_user.camera.RenderMask.value = OVR_user.camera.RenderMask.value + \
                                          " && !" + PW_user.portal_controller.NAME + \
                                          "portals"
      OVR_user.pipeline.Camera.value = OVR_user.camera
      OVR_user.portal_controller.PIPELINE = OVR_user.pipeline
      
    # extend render mask for oculus users
    for DESK_user in self.desktop_user_list:
      for other_DESK_user in self.desktop_user_list:
        if other_DESK_user.id != DESK_user.id:
          DESK_user.camera.RenderMask.value = DESK_user.camera.RenderMask.value + \
                                          " && !" + other_DESK_user.portal_controller.NAME + \
                                          "portals"
      for OVR_user in self.ovr_user_list:
        DESK_user.camera.RenderMask.value = DESK_user.camera.RenderMask.value + \
                                          " && !" + OVR_user.portal_controller.NAME + \
                                          "portals"
      for PW_user in self.powerwall_user_list:
        DESK_user.camera.RenderMask.value = DESK_user.camera.RenderMask.value + \
                                          " && !" + PW_user.portal_controller.NAME + \
                                          "portals"
      DESK_user.pipeline.Camera.value = DESK_user.camera
      DESK_user.portal_controller.PIPELINE = DESK_user.pipeline
      
    # extend render mask for oculus users
    for PW_user in self.powerwall_user_list:
      for other_PW_user in self.powerwall_user_list:
        if other_PW_user.id != PW_user.id:
          PW_user.camera.RenderMask.value = PW_user.camera.RenderMask.value + \
                                          " && !" + other_PW_user.portal_controller.NAME + \
                                          "portals"
      for DESK_user in self.desktop_user_list:
        PW_user.camera.RenderMask.value = PW_user.camera.RenderMask.value + \
                                          " && !" + DESK_user.portal_controller.NAME + \
                                          "portals"
      for OVR_user in self.ovr_user_list:
        PW_user.camera.RenderMask.value = PW_user.camera.RenderMask.value + \
                                          " && !" + OVR_user.portal_controller.NAME + \
                                          "portals" 
      PW_user.pipeline.Camera.value = PW_user.camera
      PW_user.portal_controller.PIPELINE = PW_user.pipeline
      
  ## Starts the shell and the viewer.
  # @param LOCALS Local variables.
  # @param GLOBALS Global variables.
  def run(self, LOCALS, GLOBALS):
    self.shell.start(LOCALS, GLOBALS)
    self.viewer.run()

  ## Lists the variables of the shell.
  def list_variables(self):
    self.shell.list_variables()


