import zmq
import numpy
import cv2
import pytesseract
import re

fcontext = zmq.Context()
fsocket = fcontext.socket(zmq.REQ)
fsocket.connect("tcp://localhost:5555")

fsocket.send_string('0')
msg = fsocket.recv()
if  len(msg) != 0:
    height = int.from_bytes(msg[0:2], byteorder='little')
    width = int.from_bytes(msg[2:4], byteorder='little')
    channel = int.from_bytes(msg[4:6], byteorder='little')
    img = numpy.frombuffer(msg, numpy.uint8, -1, 6)
    img.shape = (height, width, channel)
    img = img[:, :, ::-1].copy()
    img = img[655:675, 620:680]
    text = pytesseract.image_to_string(img).lower()
    if re.search('retry', text):
        print("found")
    cv2.imshow('img', img)
    cv2.waitKey(0)