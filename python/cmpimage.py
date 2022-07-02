import zmq
import numpy
import cv2
from time import sleep, time

fcontext = zmq.Context()
fsocket = fcontext.socket(zmq.REQ)
fsocket.connect("tcp://localhost:5555")

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
rotaryimg = loadimg("rotary-294-426-419-894.cv")
img = loadimg("cafe-574-626-905-961.cv")
print(diffimg(img[294:426, 419:894], rotaryimg[294:426, 419:894]))
cv2.imshow("1", rotaryimg)
cv2.imshow("2", img)
cv2.imshow("3", rotaryimg[294:426, 419:894])
cv2.imshow("4", img[294:426, 419:894])

cv2.waitKey(0)

def X():
    print("waiting for main menu")
    print(waitforimg(mainmenuimg, 74, 121, 1162, 1259, 60))
    print("waiting for not main menu")
    print(waitfornotimg(mainmenuimg, 74, 121, 1162, 1259, 60))
    print("waiting for cafe")
    print(waitforimg(cafeimg, 562, 625, 584, 688, 60))
    print("waiting for not cafe")
    print(waitfornotimg(cafeimg, 562, 625, 584, 688, 60))
    print("waiting for main menu")
    print(waitforimg(mainmenuimg, 74, 121, 1162, 1259, 60))
    print("waiting for not main menu")
    print(waitfornotimg(mainmenuimg, 74, 121, 1162, 1259, 60))
    print("waiting for garage")
    print(waitforimg(garageimg, 74, 116, 17, 130, 60))
    print("waiting for not garage")
    print(waitfornotimg(garageimg, 74, 116, 17, 130, 60))
    print("waiting for gifts 1")
    print(waitforimg(giftsimg, 23, 73, 29, 139, 60))
    print("waiting for not gifts 1")
    print(waitfornotimg(giftsimg, 23, 73, 29, 139, 60))
    print("waiting for gifts 2")
    print(waitforimg(giftsimg, 23, 73, 29, 139, 60))
    print("waiting for not gifts 2")
    print(waitfornotimg(giftsimg, 23, 73, 29, 139, 60))
    print("waiting for garage")
    print(waitforimg(garageimg, 74, 116, 17, 130, 60))
    print("waiting for not garage")
    print(waitfornotimg(garageimg, 74, 116, 17, 130, 60))