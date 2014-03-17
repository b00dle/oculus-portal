#!/usr/bin/python

## @file
# guacamole daemon to initialize tracking and device stations.

import avango.daemon
import os
import sys

## Initializes PST tracking.
def init_pst_tracking():

  # create instance of DTrack
  pst = avango.daemon.DTrack()
  pst.port = "5020" # PST port
  
  pst.stations[1] = avango.daemon.Station('tracking-pst-head')
  pst.stations[2] = avango.daemon.Station('tracking-pst-torch')
  
  device_list.append(pst)
  
  print "PST Tracking started!"

## Initializes AR Track on LCD wall.
def init_lcd_wall_tracking():

  # create instance of DTrack
  _dtrack = avango.daemon.DTrack()
  _dtrack.port = "5000" # ART port at LCD wall
  
  _dtrack.stations[17] = avango.daemon.Station('tracking-oculus-front') # oculus rift tracking
  _dtrack.stations[16] = avango.daemon.Station('tracking-oculus-stag')  # oculus rift tracking

  _dtrack.stations[4] = avango.daemon.Station('tracking-glasses-1')    # glasses powerwall user one
  _dtrack.stations[3] = avango.daemon.Station('tracking-glasses-2')    # glasses powerwall user two

  _dtrack.stations[1] = avango.daemon.Station('tracking-pointer-blue')  # blue pointer   
  _dtrack.stations[13] = avango.daemon.Station('tracking-pointer-green') # green pointer

  _dtrack.stations[7] = avango.daemon.Station('tracking-old-spheron')      # old spheron device

  device_list.append(_dtrack)
  print "ART Tracking started at LCD WALL"

## Initializes AR Track on LED wall.
def init_led_wall_tracking():

  # create instance of DTrack
  _dtrack = avango.daemon.DTrack()
  _dtrack.port = "5002" # ART port at LED wall
  
  _dtrack.stations[27] = avango.daemon.Station('tracking-oculus-front') # tracking-oculus-back
  _dtrack.stations[15] = avango.daemon.Station('tracking-pointer-green')  # blue pointer 
  _dtrack.stations[16] = avango.daemon.Station('tracking-pointer-blue') # green pointer

  device_list.append(_dtrack)
  print "ART Tracking started at LED WALL"


## Initializes pointers
def init_pointer(NAME):

  _string = os.popen("./list-ev -s | grep \"" + NAME + "\"| sed -e \'s/\"//g\'  | cut -d\" \" -f4").read()
  
  #if len(_string) == 0:
  #  _string = os.popen("./list-ev -s | grep \"2.4G Presenter\" | sed -e \'s/\"//g\'  | cut -d\" \" -f4").read() # search for other pointer

  #if len(_string) == 0:
  #  _string = os.popen("./list-ev -s | grep \"MOSART Semi. Input Device\" | sed -e \'s/\"//g\'  | cut -d\" \" -f4").read() # search for other pointer

  _string = _string.split()
  if len(_string) > 0:

    _string = _string[0]

    _pointer = avango.daemon.HIDInput()
    _pointer.station = avango.daemon.Station('device-pointer_' + NAME)
    _pointer.device = _string

    _pointer.buttons[0] = "EV_KEY::KEY_PAGEUP"
    _pointer.buttons[1] = "EV_KEY::KEY_PAGEDOWN"
    _pointer.buttons[2] = "EV_KEY::KEY_F5"
    _pointer.buttons[3] = "EV_KEY::KEY_RIGHT"
    _pointer.buttons[4] = "EV_KEY::KEY_LEFT"
    _pointer.buttons[5] = "EV_KEY::KEY_B"

    device_list.append(_pointer)
    print "Pointer started at:", _string

  else:
    print "Pointer NOT found !"


## Initializes a spacemouse for navigation.
def init_spacemouse():

  _string = os.popen("/opt/avango/vr_application_lib/tools/list-ev -s | grep \"3Dconnexion SpaceNavigator\" | sed -e \'s/\"//g\'  | cut -d\" \" -f4").read()

  if len(_string) == 0:
    _string = os.popen("/opt/avango/vr_application_lib/tools/list-ev -s | grep \"3Dconnexion SpaceTraveler USB\" | sed -e \'s/\"//g\'  | cut -d\" \" -f4").read()

  _string = _string.split()
  if len(_string) > 0:  

    _string = _string[0]
  
    _spacemouse = avango.daemon.HIDInput()
    _spacemouse.station = avango.daemon.Station('device-spacemouse') # create a station to propagate the input events
    _spacemouse.device = _string

    # map incoming spacemouse events to station values
    _spacemouse.values[0] = "EV_ABS::ABS_X"   # trans X
    _spacemouse.values[1] = "EV_ABS::ABS_Z"   # trans Y
    _spacemouse.values[2] = "EV_ABS::ABS_Y"   # trans Z
    _spacemouse.values[3] = "EV_ABS::ABS_RX"  # rotate X
    _spacemouse.values[4] = "EV_ABS::ABS_RZ"  # rotate Y
    _spacemouse.values[5] = "EV_ABS::ABS_RY"  # rotate Z

    # buttons
    _spacemouse.buttons[0] = "EV_KEY::BTN_0" # left button
    _spacemouse.buttons[1] = "EV_KEY::BTN_1" # right button

    device_list.append(_spacemouse)
    print "SpaceMouse started at:", _string

  else:
    print "SpaceMouse NOT found !"

## Initializes an old spheron for navigation.
def init_old_spheron():

  _string = os.popen("./list-ev -s | grep \"BUWEIMAR RAPID DEVEL DEVICE\" | sed -e \'s/\"//g\'  | cut -d\" \" -f4").read()
  
  _string = _string.split()
  if len(_string) > 0:
  
    _string = _string[0]
    _spheron = avango.daemon.HIDInput()
    _spheron.station = avango.daemon.Station("device-old-spheron") # create a station to propagate the input events
    _spheron.device = _string
    
    # map incoming spheron events to station values
    _spheron.values[0] = "EV_ABS::ABS_X"   # trans X    
    _spheron.values[1] = "EV_ABS::ABS_Y"   # trans Y
    _spheron.values[2] = "EV_ABS::ABS_Z"   # trans Z
    _spheron.values[3] = "EV_ABS::ABS_RX"  # rotate X
    _spheron.values[4] = "EV_ABS::ABS_RY"  # rotate Y
    _spheron.values[5] = "EV_ABS::ABS_RZ"  # rotate Z
    
    device_list.append(_spheron)
    
    print 'Old Spheron started at:', _string
    
  else:
    print "Old Spheron NOT found !"
    
  _string = os.popen("./list-ev -s | grep \"PIXART USB OPTICAL MOUSE\" | sed -e \'s/\"//g\'  | cut -d\" \" -f4").read()
  
  _string = _string.split()
  if len(_string) > 0:
  
    _string = _string[0]
    
    _spheron_buttons = avango.daemon.HIDInput()
    _spheron_buttons.station = avango.daemon.Station("device-old-spheron-buttons") # create a station to propagate the input events
    _spheron_buttons.device = _string
    
    # map buttons
    _spheron_buttons.buttons[0] = "EV_KEY::BTN_LEFT" # right
    _spheron_buttons.buttons[1] = "EV_KEY::BTN_MIDDLE" # left 
    _spheron_buttons.buttons[2] = "EV_KEY::BTN_RIGHT" # middle
    
    device_list.append(_spheron_buttons)
    print 'Old Spheron Buttons started at:', _string
    
  else:
    print "Old Spheron ButTons NOT found !"

## Initalizes a mouse for navigation.
def init_mouse():

  mouse_name = os.popen("ls /dev/input/by-id | grep \"-event-mouse\" | sed -e \'s/\"//g\'  | cut -d\" \" -f4").read()

  mouse_name = mouse_name.split()
  if len(mouse_name) > 0:

    mouse_name = mouse_name[0]

    mouse = avango.daemon.HIDInput()
    mouse.station = avango.daemon.Station('device-mouse')
    mouse.device = "/dev/input/by-id/" + mouse_name

    mouse.values[0] = "EV_REL::REL_X"
    mouse.values[1] = "EV_REL::REL_Y"

    mouse.buttons[0] = "EV_KEY::BTN_LEFT"
    mouse.buttons[1] = "EV_KEY::BTN_MIDDLE"
    mouse.buttons[2] = "EV_KEY::BTN_RIGHT"


    device_list.append(mouse)
    print "Mouse started at:", mouse_name

  else:
    print "Mouse NOT found !"

## Initializes a keyboard for navigation.
def init_keyboard():

  keyboard_name = os.popen("ls /dev/input/by-id | grep \"-event-kbd\" | sed -e \'s/\"//g\'  | cut -d\" \" -f4").read()

  keyboard_name = keyboard_name.split()

  for i, name in enumerate(keyboard_name):

    keyboard = avango.daemon.HIDInput()
    keyboard.station = avango.daemon.Station('device-keyboard' + str(i))
    keyboard.device = "/dev/input/by-id/" + name


    keyboard.buttons[0] = "EV_KEY::KEY_Q"
    keyboard.buttons[1] = "EV_KEY::KEY_W"
    keyboard.buttons[2] = "EV_KEY::KEY_E"
    keyboard.buttons[3] = "EV_KEY::KEY_R"
    keyboard.buttons[4] = "EV_KEY::KEY_T"
    keyboard.buttons[5] = "EV_KEY::KEY_Z"
    keyboard.buttons[6] = "EV_KEY::KEY_U"
    keyboard.buttons[7] = "EV_KEY::KEY_I"
    keyboard.buttons[8] = "EV_KEY::KEY_O"
    keyboard.buttons[9] = "EV_KEY::KEY_P"
    keyboard.buttons[10] = "EV_KEY::KEY_A"
    keyboard.buttons[11] = "EV_KEY::KEY_S"
    keyboard.buttons[12] = "EV_KEY::KEY_D"
    keyboard.buttons[13] = "EV_KEY::KEY_F"
    keyboard.buttons[14] = "EV_KEY::KEY_G"
    keyboard.buttons[15] = "EV_KEY::KEY_H"
    keyboard.buttons[16] = "EV_KEY::KEY_J"
    keyboard.buttons[17] = "EV_KEY::KEY_K"
    keyboard.buttons[18] = "EV_KEY::KEY_L"
    keyboard.buttons[19] = "EV_KEY::KEY_Y"
    keyboard.buttons[20] = "EV_KEY::KEY_X"
    keyboard.buttons[21] = "EV_KEY::KEY_C"
    keyboard.buttons[22] = "EV_KEY::KEY_V"
    keyboard.buttons[23] = "EV_KEY::KEY_B"
    keyboard.buttons[24] = "EV_KEY::KEY_N"
    keyboard.buttons[25] = "EV_KEY::KEY_M"

    keyboard.buttons[26] = "EV_KEY::KEY_1"
    keyboard.buttons[27] = "EV_KEY::KEY_2"
    keyboard.buttons[28] = "EV_KEY::KEY_3"
    keyboard.buttons[29] = "EV_KEY::KEY_6"

    keyboard.buttons[30] = "EV_KEY::KEY_UP"
    keyboard.buttons[31] = "EV_KEY::KEY_DOWN"


    device_list.append(keyboard)
    print "Keyboard " + str(i) + " started at:", name

## Initializes a X-Box controller for navigation.
# @param PLAYER_NUMBER A number from 1 to 4 indicating which of the four possible inputs to use.
def xbox_controller(PLAYER_NUMBER):

  _query = "./list-ev -s | grep \"Xbox 360 Wireless Receiver\" | sed -e \'s/\"//g\'  | cut -d\" \" -f4"
  
  # Grab one of the four controllers according to PLAYER_NUMBER  
  for i in range(1, PLAYER_NUMBER):
    _query = _query + " | sed -n \'1!p\'"

  _string = os.popen(_query).read()
  _string = _string.split()

  if len(_string) > 0:
    _string = _string[0]
    
    _xbox = avango.daemon.HIDInput()
    _xbox.station = avango.daemon.Station('device-xbox-' + str(PLAYER_NUMBER))
    _xbox.device = _string
    
    _xbox.values[0] = "EV_ABS::ABS_X" # left joystick
    _xbox.values[1] = "EV_ABS::ABS_Y" # left joystick
    _xbox.values[2] = "EV_ABS::ABS_RX" # right joystick
    _xbox.values[3] = "EV_ABS::ABS_RY" # right joystick

    _xbox.values[4] = "EV_ABS::ABS_Z"   # left bumper
    _xbox.values[5] = "EV_ABS::ABS_RZ"  # right bumper

    _xbox.buttons[0] = "EV_KEY::BTN_X" # Button X
    _xbox.buttons[1] = "EV_KEY::BTN_B" # Button B
    _xbox.buttons[2] = "EV_KEY::BTN_A" # Button A
    _xbox.buttons[3] = "EV_KEY::BTN_Y" # Button Y

    _xbox.buttons[4] = "EV_KEY::BTN_START" # Start button
    _xbox.buttons[5] = "EV_KEY::BTN_SELECT" # Select button

    device_list.append(_xbox)
    
    print "XBox Controller " + str(PLAYER_NUMBER) + " started at:", _string
    
  else:
    print "XBox Controller NOT found !"

## @var device_list
# List of devices to be handled by daemon.
device_list = []


#init_lcd_wall_tracking()
init_led_wall_tracking()

xbox_controller(1)
xbox_controller(2)
#xbox_controller(3)
#xbox_controller(4)

init_old_spheron()

init_keyboard()
init_mouse()
init_spacemouse()
#init_pointer("MOUSE USB MOUSE")
init_pointer("2.4G Presenter")
init_pointer("MOSART Semi. Input Device")

'''
init_pst_tracking()
'''



avango.daemon.run(device_list)
