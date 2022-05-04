import zmq
from time import sleep
from struct import *

class JSEvent:
    def __init__(self, buttonA=False, buttonB=False, buttonX=False, buttonY=False,
                       buttonLeft=False, buttonRight=False, buttonUp=False, buttonDown=False,
                       buttonL1=False, buttonR1=False, buttonL3=False, buttonR3=False,
                       buttonStart=False, buttonSelect=False, buttonGuide=False, #_dummy,
                       buttonL2=False, buttonR2=False,
                       axisLeftX=0, axisLeftY=0, axisRightX=0, axisRightY=0):
        self.buttonA = buttonA
        self.buttonB = buttonB # Circle
        self.buttonX = buttonX # Square
        self.buttonY = buttonY
        self.buttonLeft = buttonLeft
        self.buttonRight = buttonRight
        self.buttonUp = buttonUp
        self.buttonDown = buttonDown
        self.buttonL1 = buttonL1
        self.buttonR1 = buttonR1
        self.buttonL3 = buttonL3
        self.buttonR3 = buttonR3
        self.buttonStart = buttonStart
        self.buttonSelect = buttonSelect
        self.buttonGuide = buttonGuide
        self._dummy = False # padding
        self.buttonL2 = buttonL2
        self.buttonR2 = buttonR2
        self.axisLeftX = axisLeftX
        self.axisLeftY = axisLeftY
        self.axisRightX = axisRightX
        self.axisRightY = axisRightY

    def tobytes(self):
        return pack('??????????????????hhhh', self.buttonA, self.buttonB, self.buttonX, self.buttonY,
                                                self.buttonLeft, self.buttonRight, self.buttonUp, self.buttonDown,
                                                self.buttonL1, self.buttonR1, self.buttonL3, self.buttonR3,
                                                self.buttonStart, self.buttonSelect, self.buttonGuide, self._dummy,
                                                self.buttonL2, self.buttonR2, self.axisLeftX, self.axisLeftY, self.axisRightX, self.axisRightY)

    def reset(self):
        for prop in self.__dict__.keys():
            if prop[:2] != '__':
                if type(self.__dict__[prop]) == bool:
                    self.__dict__[prop] = False
                else:
                    self.__dict__[prop] = 0

port = "5556"
context = zmq.Context()
socket = context.socket(zmq.PAIR)
socket.connect("tcp://localhost:%s" % port)

while True:
    e = JSEvent()
    e.buttonLeft = True
    msg = socket.send(e.tobytes())
    print("send")
    sleep(1)
    e.buttonLeft = False
    msg = socket.send(e.tobytes())
    sleep(1)

