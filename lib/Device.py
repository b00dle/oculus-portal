#!/usr/bin/python

## @file
# Contains classes MultiDofDevice, XBoxDevice and OldSpheronDevice.

# import avango-guacamole
import avango
import avango.gua
import avango.script
import avango.daemon

from TrackingReader import *

## Base class for the representation of an input device.
#
# This class should not be instantiated, but concrete device reading
# classed will inherit from this one.
class MultiDofDevice(avango.script.Script):

  # output fields
  ## @var mf_dof
  # The input values of the input device.
  mf_dof = avango.MFFloat()
  mf_dof.value = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0] # init 8 channels

  ## @var mf_buttons
  # The button values of the input device.
  mf_buttons = avango.MFBool()
  mf_buttons.value = [False, False, False, False, False, False, False] # init 7 buttons

  ## @var sf_station_mat
  # Tracking position and rotation.
  sf_station_mat = avango.gua.SFMatrix4()
  sf_station_mat.value = avango.gua.make_identity_mat()

  
  # factors for amplifying
  ## @var translation_factor
  # Factor to modify the device's translation input.
  translation_factor = 1.0

  ## @var rotation_factor
  # Factor to modify the device's rotation input.
  rotation_factor = 1.0

  ## Default constructor.
  def __init__(self):
    self.super(MultiDofDevice).__init__()


  ## Initializes a tracking reader for the device's position and rotation
  # @param TRACKING_TARGET_NAME The tracking name as chosen in daemon, None if no tracking is available.
  # @param NO_TRACKING_MAT Tracking matrix to be used if no tracking is available.

  def init_station_tracking(self, TRACKING_TARGET_NAME, NO_TRACKING_MAT):
    
    ## @var tracking_reader
    # Tracking Reader to process the tracking input of the device.
    if TRACKING_TARGET_NAME != None:
      self.tracking_reader = TrackingTargetReader()
      self.tracking_reader.my_constructor(TRACKING_TARGET_NAME)
      self.sf_station_mat.connect_from(self.tracking_reader.sf_abs_mat)
    else:
      self.tracking_reader = TrackingDefaultReader()
      self.tracking_reader.set_no_tracking_matrix(NO_TRACKING_MAT)
      self.sf_station_mat.connect_from(self.tracking_reader.sf_abs_mat)

  ## Map an input value to a certain interval.
  # @param VALUE The value to be mapped.
  # @param OFFSET The offset to be applied to VALUE, MIN and MAX
  # @param MIN The minimum value of the new interval.
  # @param MAX The maximum value of the old interval.
  # @param NEG_THRESHOLD The negative threshold to be used.
  # @param POS_THRESHOLD The positive threshold to be used.
  def filter_channel(self, VALUE, OFFSET, MIN, MAX, NEG_THRESHOLD, POS_THRESHOLD):

    VALUE = VALUE - OFFSET
    MIN = MIN - OFFSET
    MAX = MAX - OFFSET

    #print "+", VALUE, MAX, POS_THRESHOLD
    #print "-", VALUE, MIN, NEG_THRESHOLD

    if VALUE > 0:
      _pos = MAX * POS_THRESHOLD * 0.01

      if VALUE > _pos: # above positive threshold
        VALUE = min( (VALUE - _pos) / (MAX - _pos), 1.0) # normalize interval

      else: # beneath positive threshold
        VALUE = 0

    elif VALUE < 0:
      _neg = MIN * NEG_THRESHOLD * 0.01

      if VALUE < _neg:
        VALUE = max( (VALUE - _neg) / abs(MIN - _neg), -1.0)

      else: # above negative threshold
        VALUE = 0
      
    return VALUE

## Internal representation and reader for a spacemouse device.
class SpacemouseDevice(MultiDofDevice):

  ## @var translation_factor
  # Factor to modify the device's translation input.
  translation_factor  = 0.5

  ## @var rotation_factor
  # Factor to modify the device's rotation input.
  rotation_factor     = 1.0

  ## Custom constructor.
  # @param DEVICE_STATION The name of the input device as chosen in daemon.
  def my_constructor(self, DEVICE_STATION):
  
    # init sensor
    ## @var device_sensor
    # Device sensor for the device's inputs.
    self.device_sensor = avango.daemon.nodes.DeviceSensor(DeviceService = avango.daemon.DeviceService())
    self.device_sensor.Station.value = DEVICE_STATION

    # init trigger callback
    ## @var frame_trigger
    # Triggers framewise evaluation of frame_callback method
    self.frame_trigger = avango.script.nodes.Update(Callback = self.frame_callback, Active = True)

    self.init_station_tracking(None, avango.gua.make_trans_mat(0, 1.2, 1.5))

  ## Callback: evaluated every frame
  def frame_callback(self):
    
    # button input
    _button1 = self.device_sensor.Button0.value
    _button2 = self.device_sensor.Button1.value
    
    #print _button1, _button2
    
    _flag = False
    _buttons = self.mf_buttons.value
    
    if _button1 != _buttons[0]: # trigger changes
      _flag = True

    if _button2 != _buttons[1]: # trigger changes
      _flag = True

    if _flag == True: # forward input once per frame (unless there is no input at all)
      self.mf_buttons.value = [_button1, _button2, False, False, False, False, False, False]
      
    _x = self.device_sensor.Value0.value
    _y = self.device_sensor.Value1.value * -1.0
    _z = self.device_sensor.Value2.value
    _rx = self.device_sensor.Value3.value
    _ry = self.device_sensor.Value4.value * -1.0
    _rz = self.device_sensor.Value5.value

    #print _x, _y, _z, _rx, _ry, _rz
    
    if _x != 0.0:
      _x = self.filter_channel(_x, 0.0, -0.76, 0.82, 3, 3)
    
    if _y != 0.0:
      _y = self.filter_channel(_y, 0.0, -0.7, 0.6, 3, 3)
      
    if _z != 0.0:
      _z = self.filter_channel(_z, 0.0, -0.95, 0.8, 3, 3)
        
    if _rx != 0.0:
      _rx = self.filter_channel(_rx, 0.0, -0.82, 0.8, 12, 12)
     
    if _ry != 0.0:
      _ry = self.filter_channel(_ry, 0.0, -0.5, 0.6, 12, 12)
    
    if _rz != 0.0:
      _rz = self.filter_channel(_rz, 0.0, -0.86, 0.77, 12, 12)
     
    self.mf_dof.value = [_x,_y,_z,_rx,_ry,_rz,0.0]


## Internal representation and reader for a keyboard and mouse setup.
class KeyboardMouseDevice(MultiDofDevice):

  ## @var translation_factor
  # Factor to modify the device's translation input.
  translation_factor  = 0.3

  ## @var rotation_factor
  # Factor to modify the device's rotation input.
  rotation_factor     = 0.1

  ## Custom constructor.
  def my_constructor(self):

    ## @var mouse_device_sensor
    # Input sensor referencing the mouse connected to the computer.
    self.mouse_device_sensor = avango.daemon.nodes.DeviceSensor(DeviceService = avango.daemon.DeviceService())
    self.mouse_device_sensor.Station.value = "device-mouse"

    ## @var keyboard_device_sensor
    # Input sensor referencing the keyboard connected to the computer.
    self.keyboard_device_sensor = avango.daemon.nodes.DeviceSensor(DeviceService = avango.daemon.DeviceService())
    self.keyboard_device_sensor.Station.value = "device-keyboard0"

    ## @var frame_trigger
    # Triggers framewise evaluation of frame_callback method
    self.frame_trigger = avango.script.nodes.Update(Callback = self.frame_callback, Active = True)

    self.init_station_tracking(None, avango.gua.make_trans_mat(0, 1.2, 1.5))


  ## Callback: evaluated every frame
  def frame_callback(self):
    # get rotation values from mouse
    _rx = 0.0
    _ry = 0.0

    _rel_x = self.mouse_device_sensor.Value0.value
    if _rel_x >= 2 or _rel_x <= -2:
      _ry = -_rel_x

    _rel_y = self.mouse_device_sensor.Value1.value
    if _rel_y >= 2 or _rel_y <= -2:
      _rx = -_rel_y

    # get position values from keyboard
    _w = self.keyboard_device_sensor.Button1.value
    _a = self.keyboard_device_sensor.Button10.value
    _s = self.keyboard_device_sensor.Button11.value
    _d = self.keyboard_device_sensor.Button12.value
    _up   = self.keyboard_device_sensor.Button30.value
    _down = self.keyboard_device_sensor.Button31.value

    _movement = avango.gua.Vec3(0.0, 0.0, 0.0)
    if _w:
      _movement.z -= 1.0
    if _s:
      _movement.z += 1.0
    if _a:
      _movement.x -= 1.0
    if _d:
      _movement.x += 1.0
    if _up:
      _movement.y += 1.0
    if _down:
      _movement.y -= 1.0
    
    # to provide equally fast movement event when
    # moving diagonally
    if _movement.length() != 0:
      _movement.normalize()
    
    self.mf_dof.value = [_movement.x, _movement.y, _movement.z, _rx, _ry, 0.0, 0.0, 0.0]
    
    # keys
    _h    = self.keyboard_device_sensor.Button15.value
    _r    = self.keyboard_device_sensor.Button3.value
    _g    = self.keyboard_device_sensor.Button14.value
    
    self.mf_buttons.value = [_h, _r, _g, False, False, False, False]

## Internal representation and reader for a X-Box controller
class XBoxDevice(MultiDofDevice):
 
  # amplification factors

  ## @var translation_factor
  # Factor to modify the device's translation input.
  translation_factor  = 0.3

  ## @var rotation_factor
  # Factor to modify the device's rotation input.
  rotation_factor     = 2.0

  ## Custom constructor.
  # @param DEVICE_STATION The name of the input device as chosen in daemon.
  # @param TRACKING_TARGET_NAME The tracking name as chosen in daemon, None if no tracking is available.
  # @param NO_TRACKING_MAT Tracking matrix to be used if no tracking is available.
  def my_constructor(self, DEVICE_STATION, TRACKING_TARGET_NAME, NO_TRACKING_MAT):

    self.init_station_tracking(TRACKING_TARGET_NAME, NO_TRACKING_MAT)
  
    # init sensor
    ## @var device_sensor
    # Device sensor for the device's inputs.
    self.device_sensor = avango.daemon.nodes.DeviceSensor(DeviceService = avango.daemon.DeviceService())
    self.device_sensor.Station.value = DEVICE_STATION

    # init trigger callback
    ## @var frame_trigger
    # Triggers framewise evaluation of frame_callback method
    self.frame_trigger = avango.script.nodes.Update(Callback = self.frame_callback, Active = True)
  
  ## Callback: Evaluated every frame.
  def frame_callback(self):

    # button input
    _buttonX = self.device_sensor.Button0.value
    _buttonB = self.device_sensor.Button1.value
    _buttonA = self.device_sensor.Button2.value
    _buttonY = self.device_sensor.Button3.value

    _buttonStart = self.device_sensor.Button4.value
    _buttonSelect = self.device_sensor.Button5.value

    _flagBu = False
    _buttons = self.mf_buttons.value
    
    if _buttonX != _buttons[0]: # trigger changes
      _flagBu = True

    if _buttonB != _buttons[1]: # trigger changes
      _flagBu = True

    if _buttonA != _buttons[2]: # trigger changes
      _flagBu = True

    if _buttonY != _buttons[3]: # trigger changes
      _flagBu = True

    if _buttonStart != _buttons[4]: # trigger changes
      _flagBu = True

    if _buttonSelect != _buttons[5]: # trigger changes
      _flagBu = True

    if _flagBu == True: # forward input once per frame (unless there is no input at all)
      self.mf_buttons.value = [_buttonA, _buttonB, _buttonX, _buttonY, _buttonStart, _buttonSelect, False]

      
    _x = self.device_sensor.Value0.value
    _y = 0.0
    _z = self.device_sensor.Value1.value
    _rx = self.device_sensor.Value3.value
    _ry = self.device_sensor.Value2.value * -1.0
    _rz = 0.0


    if _x != 0.0:
      _x = self.filter_channel(_x, 0.0, -1.0, 1.0, 20, 20)

    if _z != 0.0:
      _z = self.filter_channel(_z, 0.0, -1.0, 1.0, 20, 20)
        
    if _rx != 0.0:
      _rx = self.filter_channel(_rx, 0.0, -1.0, 1.0, 20, 20)
     
    if _ry != 0.0:
      _ry = self.filter_channel(_ry, 0.0, -1.0, 1.0, 20, 20)

    _rx *= 0.5
    _ry *= 0.5


    _bumperLeft = self.device_sensor.Value4.value
    _bumperRight = self.device_sensor.Value5.value

    _bumperLeft = (_bumperLeft + 1)/2
    _bumperRight = (_bumperRight + 1)/2

    _flagBumperLeft = False
    _flagBumperRight = False

    if _bumperLeft != 0.5:
      _flagBumperLeft = True
    
    if _bumperRight != 0.5:
      _flagBumperRight = True

    if _flagBumperLeft:
      _y -= _bumperLeft

    if _flagBumperRight:
      _y += _bumperRight

    #if _x != self.mf_dof.value[0] or _y != self.mf_dof.value[1] or _z != self.mf_dof.value[2] or _rx != self.mf_dof.value[3] or _ry != self.mf_dof.value[4]:
    #  self.mf_dof.value = [_x, _y, _z, _rx, _ry, 0.0, 0.0]
    
    self.mf_dof.value = [_x, _y, _z, _rx, _ry, 0.0, 0.0]

  

## Internal representation and reader for an old spheron
class OldSpheronDevice(MultiDofDevice):

  # amplification factors
  ## @var translation_factor
  # Factor to modify the device's translation input.
  translation_factor  = 0.5

  ## @var rotation_factor
  # Factor to modify the device's rotation input.
  rotation_factor     = 1.4
  

  ## Custom constructor.
  # @param DEVICE_STATION The name of the input device as chosen in daemon.
  # @param TRACKING_TARGET_NAME The tracking name as chosen in daemon, None if no tracking is available.
  # @param NO_TRACKING_MAT Tracking matrix to be used if no tracking is available.
  def my_constructor(self, DEVICE_STATION, TRACKING_TARGET_NAME, NO_TRACKING_MAT):
    self.init_station_tracking(TRACKING_TARGET_NAME, NO_TRACKING_MAT)

    # init sensor
    ## @var device_sensor
    # Device sensor for the device's inputs.
    self.device_sensor = avango.daemon.nodes.DeviceSensor(DeviceService = avango.daemon.DeviceService())
    self.device_sensor.Station.value = DEVICE_STATION
 
    ## @var button_sensor
    # Device sensor for the device's button inputs.
    self.button_sensor = avango.daemon.nodes.DeviceSensor(DeviceService = avango.daemon.DeviceService())
    self.button_sensor.Station.value = "device-old-spheron-buttons"
 
    # init trigger callback
    ## @var frame_trigger
    # Triggers framewise evaluation of frame_callback method
    self.frame_trigger = avango.script.nodes.Update(Callback = self.frame_callback, Active = True)
 
     
  ## Callback: Evaluated every frame.
  def frame_callback(self): # evaluated every frame
     
    # button input
    _button1 = self.button_sensor.Button0.value
    _button2 = self.button_sensor.Button1.value
    _button3 = self.button_sensor.Button2.value
     
    _flag = False
    _buttons = self.mf_buttons.value
     
    if _button1 != _buttons[0]: # trigger changes
      _flag = True
 
    if _button2 != _buttons[1]: # trigger changes
      _flag = True
 
    if _button3 != _buttons[2]: # trigger changes
      _flag = True
      
    if _flag == True: # forward input once per frame (unless there is no input change)
      self.mf_buttons.value = [_button3, _button1, _button2, False, False, False, False]
       
    _x = self.device_sensor.Value0.value
    _y = self.device_sensor.Value1.value
    _z = self.device_sensor.Value2.value
    _rx = self.device_sensor.Value3.value
    _ry = self.device_sensor.Value4.value * -1.0
    _rz = self.device_sensor.Value5.value
   
     
    if _x != 0.0:
      _x = self.filter_channel(_x, -0.00787377543747, -0.0134, 0.003, 5, 5)
     
    if _y != 0.0:
      _y = self.filter_channel(_y, -0.00787377543747, -0.0115, -0.003, 20, 20)
       
    if _z != 0.0:
      _z = self.filter_channel(_z, -0.00787377543747, -0.015, 0.0, 5, 5)
    
    if _rx != 0.0:
      _rx = self.filter_channel(_rx, -0.00787377543747, -0.0095, -0.006, 0, 0)
      _rx = round(_rx,6)
      #_rx *= -0.1
  
    if _ry != 0.0:
      _ry = self.filter_channel(_ry, 0.00787377543747, 0.00622577592731, 0.00912503432482, 0, 0)
      _ry = round(_ry,6)
      _ry *= -1.0

    if _rz != 0.0:
      _rz = self.filter_channel(_rz, -0.00787377543747, -0.0095, -0.006, 0, 0)
      _rz = round(_rz,6)
      #_rz *= -0.1
     
     
    self.mf_dof.value = [_x, _y, _z, _rx, _ry, _rz, 0.0]



class PointerDevice(avango.script.Script):

  sf_key_pageup = avango.SFBool()
  sf_key_pagedown = avango.SFBool()

  def __init__(self):
    self.super(PointerDevice).__init__()

  def my_constructor(self,NAME):

    self.device_sensor = avango.daemon.nodes.DeviceSensor(DeviceService = avango.daemon.DeviceService())
    self.device_sensor.Station.value = "device-pointer_" + NAME

    if (NAME =="MOUSE USB MOUSE"):
      self.sf_key_pageup.connect_from(self.device_sensor.Button0)
      self.sf_key_pagedown.connect_from(self.device_sensor.Button1)

    if (NAME == "2.4G Presenter"):
      self.sf_key_pageup.connect_from(self.device_sensor.Button3)
      self.sf_key_pagedown.connect_from(self.device_sensor.Button4)

'''
  @field_has_changed(sf_key_pageup)
  def sf_key_pageup_changed(self):

    print "Up: " , self.sf_key_pageup.value

  @field_has_changed(sf_key_pagedown)
  def sf_key_pagedown_changed(self):

    print "Down: " , self.sf_key_pagedown.value
'''    