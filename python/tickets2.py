import zmq
from time import sleep, time
from struct import pack
import datetime
import numpy
import cv2
import pytesseract
import re

delayTime = 0.2 # 0.5 0.3
pressTime = 0.025 # 0.2 0.15

tickets = 0
restarts = 0

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

def diffimg(src, dst):
    error2 = cv2.norm(src, dst, cv2.NORM_L2)
    similarity = 1- error2 / (60 * 60)
    return similarity

def msgtoimg(msg):
    height = int.from_bytes(msg[0:2], byteorder='little')
    width = int.from_bytes(msg[2:4], byteorder='little')
    channel = int.from_bytes(msg[4:6], byteorder='little')
    img = numpy.frombuffer(msg, numpy.uint8, -1, 6)
    img.shape = (height, width, channel)
    img = img[:, :, ::-1].copy()
    return img

def fetchimg():
    fsocket.send_string('0')
    msg = fsocket.recv()
    if  len(msg) != 0:
        return msgtoimg(msg)
    else:
        print("error!")

def waitforimg(src, sx, ex, sy, ey, duration):
    simg = src[sx:ex, sy:ey]
    start = time()
    while (time() < start+duration):
        img = fetchimg()[sx:ex, sy:ey]
        if (diffimg(simg, img) > 0.8):
            return True
    return False

def waitfornotimg(src, sx, ex, sy, ey, duration):
    simg = src[sx:ex, sy:ey]
    start = time()
    while (time() < start+duration):
        img = fetchimg()[sx:ex, sy:ey]
        if (diffimg(simg, img) < 0.8):
            return True
    return False

def loadimg(name):
    with open(name, 'rb') as file:
        msg = file.read()
        return msgtoimg(msg)

garageimg = loadimg("garage-74-116-17-130.cv")
mainmenuimg = loadimg("mainmenu-74-121-1162-1259.cv")
giftsimg = loadimg("gifts-23-73-29-139.cv")
cafeimg = loadimg("cafe-574-626-905-961.cv")
nogiftsimg = loadimg("nogifts-341-410-583-675.cv")
toyota86img = loadimg("toyota86pre-531-587-548-728.cv")
rotaryimg = loadimg("rotarypre-537-591-526-754.cv")

def pressXrepeatedly(img, sx, ex, sy, ey, duration):
    start = time()
    src = img[sx:ex, sy:ey]
    while (time() < start+duration):
        pressX()
        dst = fetchimg()[sx:ex, sy:ey]
        s = diffimg(src, dst)
        if s >= 0.8:
            return True
    return False

def waitformainmenu(duration):
    global mainmenuimg
    return waitforimg(mainmenuimg, 74, 121, 1162, 1259, duration)

def waitfornotmainmenu(duration):
    global mainmenuimg
    return waitfornotimg(mainmenuimg, 74, 121, 1162, 1259, duration)

def waitforcafe(duration):
    global cafeimg
    return waitforimg(cafeimg, 574, 626, 905, 961, duration)

def waitfornotcafe(duration):
    global cafeimg
    return waitfornotimg(cafeimg, 574, 626, 905, 961, duration)

def waitforgarage(duration):
    return waitforimg(garageimg, 74, 116, 17, 130, duration)

def waitfornotgarage(duration):
    return waitfornotimg(garageimg, 74, 116, 17, 130, duration)

def waitforgifts(duration):
    return waitforimg(giftsimg, 23, 73, 29, 139, duration)

def waitfornotgifts(duration):
    return waitfornotimg(giftsimg, 23, 73, 29, 139, duration)

def waitfortoyota86(duration):
    return waitforimg(toyota86img, 531, 587, 548, 728, duration)

def waitforrotary(duration):
    return waitforimg(rotaryimg, 537, 591, 526, 754, duration)

def maintoextra():
    global tickets, restarts
    tickets += 1
    print("start: %d tickets (%d restarts)" % (tickets, restarts))
    if waitformainmenu(10) == False:
        return False
    pressLeft()
    pressX()
    print("wait for cafe")
    if waitforcafe(10) == False:
        return False
    print("cafe")
    sleep(0.1)
    pressLeft()
    pressX()
    print("my collections")
    pressDown()
    pressRight()
    pressX()
    print("extra menus")
    return True

def menutoclaim():
    pressX()
    sleep(3)
    pressBack()
    pressBack()
    pressBack()
    print("wait for main")
    if waitformainmenu(10) == False:
        return False
    print("back to main")
    sleep(0.5)
    pressRight()
    pressX()
    print("wait for garage")
    if waitforgarage(10) == False:
        return False
    print("garage")
    sleep(0.2)
    pressRight()
    pressRight()
    pressRight()
    pressX()
    print("wait for gift")
    if waitforgifts(10) == False:
        return False
    print("gift")
    sleep(0.2)
    if diffimg(nogiftsimg[341:410, 583:675], fetchimg()[341:410, 583:675]) > 0.75:
        return False
    pressX()
    print("selected ticket")
    pressX()
    print("yes")
    pressX()
    print("repeating X")
    if pressXrepeatedly(giftsimg, 23, 73, 29, 139, 60) == False:
        return False
    print("exiting")
    sleep(0.5)
    pressBack()
    print("waiting for not gifts")
    if waitfornotgifts(10) == False:
        return False
    pressBack()
    print("back to main")
    return True

def runloop1():
    print(datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S"))
    if maintoextra() == False:
        return False
    pressUp()
    pressX()
    print("Toyota 86")
    if waitfortoyota86(10) == False:
        return False
    return menutoclaim()

def runloop3():
    print(datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S"))
    if maintoextra() == False:
        return False
    pressUp()
    pressRight()
    pressRight()
    pressX()
    print("Rotary")
    if waitforrotary(10) == False:
        return False
    return menutoclaim()

def pressBackRepeatedly(duration):
    start = time()
    while (time() < start+duration):
        pressBack()

def restartGame():
    global tickets, restarts
    tickets -= 1
    restarts += 1
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
    
while True:
    if runloop1() == False or runloop3() == False:
        restartGame()