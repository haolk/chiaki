import zmq
from time import sleep, time
from struct import pack
import datetime
import numpy
import cv2
import pytesseract
import re

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
    sleep(.1)
    e.reset()
    socket.send(e.tobytes())
    sleep(.1)

def pressLeft():
    e = JSEvent()
    e.buttonLeft = True
    socket.send(e.tobytes())
    sleep(.1)
    e.reset()
    socket.send(e.tobytes())
    sleep(.1)

def pressRight():
    e = JSEvent()
    e.buttonRight = True
    socket.send(e.tobytes())
    sleep(.1)
    e.reset()
    socket.send(e.tobytes())
    sleep(.1)

def pressBack():
    e = JSEvent()
    e.buttonO = True
    socket.send(e.tobytes())
    sleep(.1)
    e.reset()
    socket.send(e.tobytes())
    sleep(.1)

amount = 0

def race():
    global amount
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
            img = numpy.frombuffer(msg, numpy.uint8, -1, 6)
            img.shape = (height, width, channel)
            img = img[:, :, ::-1].copy()

            ocv = img[655:675, 620:680]
            text = pytesseract.image_to_string(ocv).lower()
            if re.search('retry', text):
                print("menu found retry")
                print("press back")
                pressBack()
                sleep(0.1)
                print("press back")
                pressBack()
                sleep(0.1)
                print("press left")
                pressLeft()
                sleep(0.1)
                print("press X")
                pressX()
                sleep(1)
                end = time()
                elapsed = end - start
                print("time taken: %d'%d\"" % ((elapsed / 60), (elapsed % 60)))
                print("credits: %d" % amount)
                return
            else:
                rewards = img[310:370, 100:400]
                text = pytesseract.image_to_string(rewards)
                if re.search('REWARDS', text):
                    creds = img[280:320, 920:1180]
                    text = pytesseract.image_to_string(creds)
                    amount_text = re.search("[0-9,]+", text)
                    if amount_text != None:
                        a = int(amount_text.group(0).replace(',', ''))
                        if a > amount:
                            amount = a
                e.buttonX = True
                socket.send(e.tobytes())
                sleep(.1)
                e.buttonX = False
                socket.send(e.tobytes())
                sleep(0.3)

while True:

    print(datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S"))
    print("start")
    pressX()
    sleep(1)
    pressX()
    print("started racing")
    race()
    print("finished racing")
