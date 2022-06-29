import zmq
from time import sleep, time
from struct import pack
import datetime
import numpy
import cv2
import pytesseract
import re

delayTime = 1
pressTime = 0.2

class JSEvent:
    def __init__(self, buttonX=False, buttonO=False, buttonS=False, buttonT=False,
                       buttonLeft=False, buttonRight=False, buttonUp=False, buttonDown=False,
                       buttonL1=False, buttonR1=False, buttonL3=False, buttonR3=False,
                       buttonStart=False, buttonSelect=False, buttonGuide=False, #_dummy,
                       buttonL2=False, buttonR2=False,
                       axisLeftX=0, axisLeftY=0, axisRightX=0, axisRightY=0):
        self.buttonX = buttonX # Cross
        self.buttonO = buttonO # Circle
        self.buttonS = buttonS # Square
        self.buttonT = buttonT
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
        return pack('??????????????????hhhh', self.buttonX, self.buttonO, self.buttonS, self.buttonT,
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

context = zmq.Context()
socket = context.socket(zmq.PUSH)
socket.connect("tcp://localhost:5554")

fcontext = zmq.Context()
fsocket = fcontext.socket(zmq.REQ)
fsocket.connect("tcp://localhost:5555")

def pressX():
    e = JSEvent()
    e.buttonX = True
    socket.send(e.tobytes())
    sleep(pressTime)
    e.reset()
    socket.send(e.tobytes())
    sleep(delayTime)

def pressLeft():
    e = JSEvent()
    e.buttonLeft = True
    socket.send(e.tobytes())
    sleep(pressTime)
    e.reset()
    socket.send(e.tobytes())
    sleep(delayTime)

def pressRight():
    e = JSEvent()
    e.buttonRight = True
    socket.send(e.tobytes())
    sleep(pressTime)
    e.reset()
    socket.send(e.tobytes())
    sleep(delayTime)

def pressDown():
    e = JSEvent()
    e.buttonDown = True
    socket.send(e.tobytes())
    sleep(pressTime)
    e.reset()
    socket.send(e.tobytes())
    sleep(delayTime)

def pressUp():
    e = JSEvent()
    e.buttonUp = True
    socket.send(e.tobytes())
    sleep(pressTime)
    e.reset()
    socket.send(e.tobytes())
    sleep(delayTime)

def pressBack():
    e = JSEvent()
    e.buttonO = True
    socket.send(e.tobytes())
    sleep(pressTime)
    e.reset()
    socket.send(e.tobytes())
    sleep(delayTime)

amount = 0

def getimage():
    fsocket.send_string('0')
    msg = fsocket.recv()
    if  len(msg) != 0:
        height = int.from_bytes(msg[0:2], byteorder='little')
        width = int.from_bytes(msg[2:4], byteorder='little')
        channel = int.from_bytes(msg[4:6], byteorder='little')
        img = numpy.frombuffer(msg, numpy.uint8, -1, 6)
        img.shape = (height, width, channel)
        img = img[:, :, ::-1].copy() 
        return img
    else:
        print("error!")

def pressXrepeatedly(duration):
    start = time()
    while (time() < start+duration):
        pressX()

def maintoextra():
    print("start")
    pressLeft()
    pressX()
    print("cafe")
    sleep(4)
    pressLeft()
    pressX()
    print("my collections")
    pressDown()
    pressRight()
    pressX()
    print("extra menus")

def menutoclaim():
    sleep(1)
    pressX()
    sleep(3)
    pressBack()
    pressBack()
    pressBack()
    sleep(4)
    print("back to main")
    pressRight()
    pressX()
    sleep(6)
    print("garage")
    pressRight()
    pressRight()
    pressRight()
    pressX()
    print("gift")
    pressX()
    print("selected ticket")
    pressX()
    print("yes")
    pressX()
    print("repeating X")
    pressXrepeatedly(20)
    pressBack()
    pressBack()
    sleep(3)


def runloop1():
    print(datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S"))
    maintoextra()
    pressUp()
    pressX()
    print("Toyota 86")
    menutoclaim()

def runloop3():
    print(datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S"))
    maintoextra()
    pressUp()
    pressRight()
    pressRight()
    pressX()
    print("Rotary")
    menutoclaim()

while True:
    runloop1()
    sleep(3)
    runloop3()
    sleep(3)