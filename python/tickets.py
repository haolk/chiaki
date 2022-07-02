import zmq
from time import sleep, time
from struct import pack
import datetime
import numpy
import cv2
import pytesseract
import re

delayTime = 0.3 # 0.5 0.3
pressTime = 0.05 # 0.2 0.15

msg = open('gift.cv', 'rb').read()
height = int.from_bytes(msg[0:2], byteorder='little')
width = int.from_bytes(msg[2:4], byteorder='little')
channel = int.from_bytes(msg[4:6], byteorder='little')
img = numpy.frombuffer(msg, numpy.uint8, -1, 6)
img.shape = (height, width, channel)
img = img[:, :, ::-1].copy()
img = img[20:80, 80:140]

def diffimg(dst):
    error2 = cv2.norm(img, dst, cv2.NORM_L2)
    similarity = 1- error2 / (60 * 60)
    return similarity

tickets = 0

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

def pressButton(e):
    socket.send(e.tobytes())
    sleep(pressTime)
    e.reset()
    socket.send(e.tobytes())
    sleep(delayTime)

def pressX():
    pressButton(JSEvent(buttonX = True))

def pressLeft():
    pressButton(JSEvent(buttonLeft = True))

def pressRight():
    pressButton(JSEvent(buttonRight = True))
    
def pressDown():
    pressButton(JSEvent(buttonDown = True))
    
def pressUp():
    pressButton(JSEvent(buttonUp = True))
    
def pressBack():
    pressButton(JSEvent(buttonO = True))    

def pressSelect():
    pressButton(JSEvent(buttonSelect = True))    

def pressStart():
    pressButton(JSEvent(buttonStart = True))    

def pressGuide():
    pressButton(JSEvent(buttonGuide = True))  

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
        i = getimage()
        i = i[20:80, 80:140]
        s = diffimg(i)
        if s >= 0.8:
            return True
    return False

def maintoextra():
    global tickets
    tickets += 1
    print("start: %d tickets" % tickets)
    sleep(1)
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
    sleep(5)
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
    success = pressXrepeatedly(60)
    print("exiting")
    sleep(1)
    pressBack()
    pressBack()
    print("back to main")
    sleep(3)
    return success


def runloop1():
    print(datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S"))
    maintoextra()
    pressUp()
    pressX()
    print("Toyota 86")
    return menutoclaim()

def runloop3():
    print(datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S"))
    maintoextra()
    pressUp()
    pressRight()
    pressRight()
    pressX()
    print("Rotary")
    return menutoclaim()

def pressBackRepeatedly(duration):
    start = time()
    while (time() < start+duration):
        pressBack()

def restartGame():
    print("*** Restarting Game***")
    pressGuide()
    sleep(2)
    pressDown()
    pressX()
    sleep(2)
    print("opening options")
    pressStart()
    sleep(2)
    pressX()
    print("closed game")
    sleep(7)
    pressX()
    print("start game")
    sleep(7)
    print("repeatedly quit intro")
    pressBackRepeatedly(20)
    print("intro closed")
    sleep(2)
    pressX()
    sleep(2)
    pressRight()
    

restartGame()

while True:
    if runloop1() == False or runloop3() == False:
        restartGame()