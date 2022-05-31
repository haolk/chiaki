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

def pressDown():
    e = JSEvent()
    e.buttonDown = True
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

def race():
    global amount
    start = time()
    e = JSEvent()
    e.buttonUp = True
    e.buttonDown = True
    socket.send(e.tobytes())

    while True:
        img = getimage()[655:775, 630:680]
        text = pytesseract.image_to_string(img).lower()
        if re.search('next', text):
            print("race finished (next) found")
            print("press next")

            while True:
                img = getimage()
                rewards = pytesseract.image_to_string(img[275:375, 100:400]).lower()
                nextrace = pytesseract.image_to_string(img[655:680, 680:780]).lower()
                if re.search('rewards', rewards):
                    text = pytesseract.image_to_string(img[280:320, 920:1180])
                    amount_text = re.search("[0-9,]+", text)
                    if amount_text != None:
                        try:
                            a = int(amount_text.group(0).replace(',', ''))
                            if a > amount:
                                amount = a
                        except:
                            pass
                    pressX()
                    sleep(0.2)

                elif re.search('to next race', nextrace):
                    print("found to next race")

                    pressBack()
                    pressBack()
                    pressRight()

                    while True:
                        img = getimage()[630:650, 920:980]
                        ex = pytesseract.image_to_string(img).lower()
                        if re.search('exit', ex):
                            print("found exit")

                            pressBack()
                            pressBack()
                            pressX()
                            pressX()

                            while True:
                                img = getimage()[280:320, 250:360]
                                americas = pytesseract.image_to_string(img).lower()
                                if re.search('americas', americas):
                                    print("found americas")

                                    pressDown()
                                    pressRight()
                                    pressRight()
                                    pressRight()
                                    pressRight()
                                    pressRight()
                                    pressRight()
                                    
                                    while True:
                                        img = getimage()[625:650, 320:380]
                                        st = pytesseract.image_to_string(img).lower()
                                        if re.search('start', st):
                                            print("found start")

                                            end = time()
                                            elapsed = end - start
                                            print("time taken: %d'%d\"" % ((elapsed / 60), (elapsed % 60)))
                                            print("credits: %d" % amount)
                                            return
                                        else:
                                            pressX()
                                            sleep(1)


                        else:
                            pressX()
                            sleep(1)

                else:
                    pressX()
                    sleep(0.2)

        else:
            e.buttonRight = True
            socket.send(e.tobytes())
            sleep(0.5)
            e.buttonRight = False
            socket.send(e.tobytes())
            sleep(0.5)

while True:

    print(datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S"))
    print("start")
    pressX()
    sleep(1)
    pressX()
    print("started racing")
    race()
    print("finished racing")
