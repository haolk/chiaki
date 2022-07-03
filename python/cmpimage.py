import zmq
import numpy
import cv2
from time import sleep, time
import re

fcontext = zmq.Context()
fsocket = fcontext.socket(zmq.REQ)
fsocket.connect("tcp://localhost:5555")

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

images = {}

def loadimg(name):
    global images
    with open(name, 'rb') as file:
        msg = file.read()
        img = msgtoimg(msg)
        m = re.match('([^-]+)-(\d+)-(\d+)-(\d+)-(\d+)\\.cv', name)
        if m is not None:
            images[m[1]] = {
                'img': img,
                'xy': (int(m[2]), int(m[3]), int(m[4]), int(m[5])),
                'cimg': img[int(m[2]):int(m[3]), int(m[4]):int(m[5])]
            }
        return img

def diffname(name, img):
    global images
    i = images[name]
    if i == None:
        print("repeat X %s not found" % name)
        return False
    src = i['img']
    (sx, ex, sy, ey) = i['xy']
    simg = src[sx:ex, sy:ey]
    dimg = img[sx:ex, sy:ey]
    return diffimg(simg, dimg)

garageimg = loadimg("garage-74-116-17-130.cv")
mainmenuimg = loadimg("mainmenu-74-121-1162-1259.cv")
giftsimg = loadimg("gifts-23-73-29-139.cv")
nogiftsimg = loadimg("nogifts-341-410-583-675.cv")
rotaryimg = loadimg("rotary-294-426-419-894.cv")
toyota86img = loadimg("./toyota86-300-424-453-837.cv")
cafeimg = loadimg("cafe-574-626-905-961.cv")
cafealtimg = loadimg("cafealt-561-606-531-557.cv")
img = loadimg("reject.cv")
print(diffname("cafealt", img))
cv2.imshow("1", cafealtimg)
cv2.imshow("2", img)
cv2.imshow("3", images['cafealt']['cimg'])


cv2.waitKey(0)
