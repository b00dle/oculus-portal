
import avango
import avango.gua
import avango.script
from avango.script import field_has_changed
import avango.oculus

import math

class Manipulator(avango.script.Script)


	def __init__(self):
    self.super(Manipulator).__init__()
    self.Keyboard = KeyboardDevice()
    self.LeftPointer = PointerDevice()
    #self.LeftPicker  = Picker()
    self.RightPointer = PointerDevice()
    #self.RightPicker  = Picker()


    self.always_evaluate(True)