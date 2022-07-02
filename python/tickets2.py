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

tickets = 0
restarts = 0

comparison = 0.5

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
    similarity = 1- error2 / (src.shape[0] * src.shape[1])
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
    global msg
    fsocket.send_string('0')
    msg = fsocket.recv()
    if  len(msg) != 0:
        return msgtoimg(msg)
    else:
        print("error!")

images = {}

def loadimg(name):
    global images
    with open(name, 'rb') as file:
        msg = file.read()
        img = msgtoimg(msg)
        m = re.match('([^-]+)-([0-9]+)-([0-9]+)-([0-9]+)-([0-9]+)\\.cv', name)
        if m is not None:
            images[m[1]] = {
                'img': img,
                'xy': (int(m[2]), int(m[3]), int(m[4]), int(m[5])),
                'cimg': img[int(m[2]):int(m[3]), int(m[4]):int(m[5])]
            }
        return img

garageimg = loadimg("garage-74-116-17-130.cv")
mainmenuimg = loadimg("mainmenu-74-121-1162-1259.cv")
giftsimg = loadimg("gifts-23-73-29-139.cv")
cafeimg = loadimg("cafe-574-626-905-961.cv")
cafealtimg = loadimg("cafealt-561-606-531-557.cv")
cafealt2img = loadimg("cafealt2-562-613-397-424.cv")
nogiftsimg = loadimg("nogifts-341-410-583-675.cv")
toyota86preimg = loadimg("toyota86pre-531-587-548-728.cv")
rotarypreimg = loadimg("rotarypre-537-591-526-754.cv")
toyota86img = loadimg("toyota86-300-424-453-837.cv")
rotaryimg = loadimg("rotary-294-426-419-894.cv")
titleimg = loadimg("title-125-293-406-894.cv")

def repeatX(name, duration):
    global images
    i = images[name]
    if i == None:
        print("repeat X %s not found" % name)
        return False
    src = i['img']
    (sx, ex, sy, ey) = i['xy']
    simg = src[sx:ex, sy:ey]
    start = time()
    print("   repeat X in %05.2f/%05.2f (% 2.5f) for %s" % (time() - start, duration, 0, name))
    while (time() < start+duration):
        pressX()
        dst = fetchimg()[sx:ex, sy:ey]
        s = diffimg(simg, dst)
        print("\033[A\033[0K   repeat X in %05.2f/%05.2f (% 2.5f) for %s" % (time() - start, duration, s, name))
        if s >= comparison:
            print("\033[A\033[0K   repeat X in %05.2f/%05.2f (% 2.5f) for %s" % (time() - start, duration, s, name))
            return True
    print("\033[A\033[0Kfail to find %s in %.2f seconds (%f - %d)" % (name, time() - start, s, duration))
    with open('reject.cv', 'wb') as file:
        file.write(msg)
    return False

def repeatBack(name, duration):
    global images
    i = images[name]
    if i == None:
        print("repeat Back %s not found" % name)
        return False
    src = i['img']
    (sx, ex, sy, ey) = i['xy']
    simg = src[sx:ex, sy:ey]
    start = time()
    print("repeat Back in %05.2f/%05.2f (% 2.5f) for %s" % (time() - start, duration, 0, name))
    while (time() < start+duration):
        pressBack()
        dst = fetchimg()[sx:ex, sy:ey]
        s = diffimg(simg, dst)
        print("\033[A\033[0Krepeat Back in %05.2f/%05.2f (% 2.5f) for %s" % (time() - start, duration, s, name))
        if s >= comparison:
            print("\033[A\033[0Krepeat Back in %05.2f/%05.2f (% 2.5f) for %s" % (time() - start, duration, s, name))
            return True
    print("\033[A\033[0Kfailed to find %s in %.2f seconds (%f - %d)" % (name, time() - start, s, duration))
    with open('reject.cv', 'wb') as file:
        file.write(msg)
    return False

def cmpimg(name):
    global images
    i = images[name]
    if i == None:
        print("cmpimg %s not found" % name)
        return False
    src = i['img']
    (sx, ex, sy, ey) = i['xy']
    simg = src[sx:ex, sy:ey]
    i = fetchimg()
    img = i[sx:ex, sy:ey]
    s = diffimg(simg, img)
    return s

def waitfor(name, duration):
    global images
    if (type(name) is str):
        name = [name]
    im = [images[x] for x in name]
    if None in im:
        print("waitfor %s not found" % name)
        return False
    start = time()
    print("    waiting in %05.2f/%05.2f (% 2.5f) for %s" % (time() - start, duration, 0, name))
    while (time() < start+duration):
        i = fetchimg()
        for x in im:
            simg = x['cimg']
            (sx, ex, sy, ey) = x['xy']
            img = i[sx:ex, sy:ey]
            s = diffimg(simg, img)
            print("\033[A\033[0K    waiting in %05.2f/%05.2f (% 2.5f) for %s" % (time() - start, duration, s, name))
            if (s > comparison):
                print("\033[A\033[0K      found in %05.2f/%05.2f (% 2.5f) for %s" % (time() - start, duration, s, name))
                return True
    print("\033[A\033[0Kfailed to find %s in %05.2f seconds (%f - %d)" % (name, time() - start, s, duration))
    with open('reject.cv', 'wb') as file:
        file.write(msg)
    return False

def waitfornot(name, duration):
    global images
    i = images[name]
    if i == None:
        print("waitfornot %s not found" % name)
        return False
    src = i['img']
    (sx, ex, sy, ey) = i['xy']
    simg = src[sx:ex, sy:ey]
    start = time()
    print("not waiting in %05.2f/%05.2f (% 2.5f) for %s" % (time() - start, duration, 0, name))
    while (time() < start+duration):
        i = fetchimg()
        img = i[sx:ex, sy:ey]
        s = diffimg(simg, img)
        print("\033[A\033[0Knot waiting in %05.2f/%05.2f (% 2.5f) for %s" % (time() - start, duration, s, name))
        if (s < comparison):
            print("\033[A\033[0K  not found in %05.2f/%05.2f (% 2.5f) for %s" % (time() - start, duration, s, name))
            return True
    print("\033[A\033[0Kfailed to not find %s in %02.02f seconds (%f - %d)" % (name, time() - start, s, duration))
    with open('reject.cv', 'wb') as file:
        file.write(msg)
    return False

def maintoextra():
    global tickets, restarts
    tickets += 1
    print("start: %d tickets (%d restarts)" % (tickets, restarts))
    if waitfor('mainmenu', 10) == False:
        return False
    sleep(0.2)
    pressLeft()
    pressX()
    if waitfor(['cafe', 'cafealt', 'cafealt2'], 10) == False:
        return False
    sleep(0.2)
    pressLeft()
    pressX()
    print("my collections")
    pressDown()
    pressRight()
    pressX()
    print("\033[A\033[0Kmy collections - extra menus\033[A")
    sleep(0.2)
    return True

def menutoclaim():
    sleep(0.5)
    pressBack()
    pressBack()
    pressBack()
    if waitfor('mainmenu', 10) == False:
        return False
    sleep(0.5)
    pressRight()
    pressX()
    if waitfor('garage', 10) == False:
        return False
    sleep(0.5)
    pressRight()
    pressRight()
    pressRight()
    pressX()
    if waitfor('gifts', 10) == False:
        return False
    pressX()
    print("selected ticket")
    pressX()
    df = cmpimg('nogifts')
    print("\033[A\033[0K          comparing images (% 2.5f) for %s" % (df, 'nogifts'))
    if cmpimg('nogifts') > 0.75:
        return False
    pressX()
    if repeatX('gifts', 35) == False:
        return False
    sleep(0.5)
    pressBack()
    sleep(0.2)
    if waitfornot('gifts', 20) == False:
        return False
    pressBack()
    return True

def runloop1():
    print(datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S"))
    if maintoextra() == False:
        return False
    pressUp()
    pressX()
    if waitfor('toyota86pre', 10) == False:
        return False
    pressX()
    if waitfor('toyota86', 4) == False:
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
    if waitfor('rotarypre', 10) == False:
        return False
    pressX()
    if waitfor('rotary', 4) == False:
        return False
    return menutoclaim()

def restartGame():
    global tickets, restarts
    tickets -= 1
    restarts += 1
    print("*** Restarting Game***")
    pressGuide()
    sleep(3)
    pressDown()
    pressX()
    sleep(3)
    print("opening options")
    pressStart()
    sleep(3)
    pressX()
    print("closed game")
    sleep(7)
    pressX()
    print("start game")
    sleep(10)
    repeatBack('title', 30)
    print("intro closed")
    sleep(7)
    pressX()
    sleep(2)
    pressRight()
    
while True:
    if runloop1() == False or runloop3() == False:
        restartGame()