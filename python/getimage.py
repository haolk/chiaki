import zmq
from time import sleep
from struct import *
from PIL import Image
import numpy
import cv2
import pytesseract

fcontext = zmq.Context()
fsocket = fcontext.socket(zmq.REQ)
fsocket.connect("tcp://localhost:5555")

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
    c = hsl(numpy.average(j, axis=(0,1)))
    print(c)
    return (c[0] > 260 and c[0] < 315) and (c[2] > 0.4) and (c[1] > 0.1)

fsocket.send_string('0')
msg = fsocket.recv()
if  len(msg) != 0:
    height = int.from_bytes(msg[0:2], byteorder='little')
    width = int.from_bytes(msg[2:4], byteorder='little')
    channel = int.from_bytes(msg[4:6], byteorder='little')
    i = Image.frombytes('RGB', (1280, 720), msg[6:])
    i.show()
    ocv = numpy.array(i)
    ocv = ocv[:, :, ::-1].copy()
    text = pytesseract.image_to_string(ocv)
    print(text)