import zmq
from time import sleep, time
from struct import *
from PIL import Image
import numpy
import cv2
import pytesseract
import re

def hsl(rgb):
    red = rgb[0]/255
    green = rgb[1]/255
    blue = rgb[2]/255
    xmin = min(min(red, green), blue)
    xmax = max(max(red, green), blue)
    if (xmin == xmax):
        return (0, 0, 0)
    if (xmax == red):
        hue = (green - blue) / (xmax - xmin)
    elif (xmax == green):
        hue = 2.0 + (blue - red) / (xmax - xmin)
    else:
        hue = 4.0 + (red - green) / (xmax - xmin)
    hue = hue * 60
    if (hue < 0):
        hue = hue + 360
    light = (xmax + xmin)/2
    saturation = (xmax - xmin)/(1-abs(2*light-1))
    return (hue, light, saturation)

def ispurple(img):
    c = hsl(numpy.average(img, axis=(0,1)))
    return (c[0] > 260 and c[0] < 315) and (c[2] > 0.4) and (c[1] > 0.1)


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
    sleep(.3)
    e.reset()
    socket.send(e.tobytes())
    sleep(.3)

def pressLeft():
    e = JSEvent()
    e.buttonLeft = True
    socket.send(e.tobytes())
    sleep(.3)
    e.reset()
    socket.send(e.tobytes())
    sleep(.3)

def pressRight():
    e = JSEvent()
    e.buttonRight = True
    socket.send(e.tobytes())
    sleep(.3)
    e.reset()
    socket.send(e.tobytes())
    sleep(.3)

def pressBack():
    e = JSEvent()
    e.buttonO = True
    socket.send(e.tobytes())
    sleep(.3)
    e.reset()
    socket.send(e.tobytes())
    sleep(.3)

def race():
    
    start = time()
    e = JSEvent()
    e.buttonUp = True
    e.buttonDown = True
    socket.send(e.tobytes())

    while True:
        fsocket.send_string('0')
        msg = fsocket.recv()
        if  len(msg) != 0:

            height = int.from_bytes(msg[0:2], byteorder='little')
            width = int.from_bytes(msg[2:4], byteorder='little')
            channel = int.from_bytes(msg[4:6], byteorder='little')
            i = Image.frombytes('RGB', (1280, 720), msg[6:])
            j = i.crop((320, 650, 900, 670))
            ocv = numpy.array(j)
            ocv = ocv[:, :, ::-1].copy()
            text = pytesseract.image_to_string(ocv).lower()
            if re.search('retry', text):
                print("menu found retry")
                pressBack()
                sleep(1)
                pressBack()
                sleep(1)
                pressLeft()
                sleep(1)
                pressX()
                sleep(1)
                end = time()
                elapsed = end - start
                print("time taken: %d'%d\"" % ((elapsed / 60), (elapsed % 60)))
                return
            else:
                e.buttonX = True
                socket.send(e.tobytes())
                sleep(.3)
                e.buttonX = False
                socket.send(e.tobytes())
                sleep(1)

while True:

    print("start")
    pressX()
    sleep(1)
    pressX()
    print("started racing")
    race()
    print("finished racing")
