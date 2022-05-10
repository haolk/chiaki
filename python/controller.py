import zmq
import numpy
import cv2
import pytesseract
import re
from struct import pack, unpack

class ControllerState:
    def __init__(self, cross=False, moon=False, box=False, pyramid=False, dleft=False, dright=False, dup=False, ddown=False, l1=False, r1=False, l3=False, r3=False, options=False, share=False, touchpad=False, ps=False, l2=0, r2=0, leftx = 0, lefty = 0, rightx = 0, righty = 0, ignore = False):
        self.cross = cross
        self.moon = moon
        self.box = box
        self.pyramid = pyramid
        self.dleft = dleft
        self.dright = dright
        self.dup = dup
        self.ddown = ddown
        self.l1 = l1
        self.r1 = r1
        self.l3 = l3
        self.r3 = r3
        self.options = options
        self.share = share
        self.touchpad = touchpad
        self.ps = ps
        self.l2 = l2
        self.r2 = r2
        self.leftx = leftx
        self.lefty = lefty
        self.rightx = rightx
        self.righty = righty
        self.press = 0
        self.ignore = ignore

    def stringify(self):
        s = "xobplrudlrlrostp"
        b = [ self.cross, self.moon, self.box, self.pyramid, self.dleft, self.dright, self.dup, self.ddown, self.l1, self.r1, self.l3, self.r3, self.options, self.share, self.touchpad, self.ps ]
        r = ""
        for x in b:
            if x:
                r += str(s[0]).upper()
            else:
                r += str(s[0])
            s = s[1:]
        return r

    def serialize(self):
        buttons = self.cross << 0 | self.moon << 1 | self.box << 2 | self.pyramid << 3 | self.dleft << 4 | self.dright << 5 | self.dup << 6 | self.ddown << 7 | self.l1 << 8 | self.r1 << 9 | self.l3 << 10 | self.r3 << 11 | self.options << 12 | self.share << 13 | self.touchpad << 14 | self.ps << 15

        return pack('!LBBBBhhhh', buttons, 0, self.ignore, self.l2, self.r2, self.leftx, self.lefty, self.rightx, self.righty)

    @classmethod
    def deserialize(cls, msg):
        (buttons, dummy, ignore, l2, r2, leftx, lefty, rightx, righty) = unpack('!LBBBBhhhh', msg[0:16])
        return ControllerState(
            cross = bool(buttons & (1 << 0)),
            moon = bool(buttons & (1 << 1)),
            box = bool(buttons & (1 << 2)),
            pyramid = bool(buttons & (1 << 3)),
            dleft = bool(buttons & (1 << 4)),
            dright = bool(buttons & (1 << 5)),
            dup = bool(buttons & (1 << 6)),
            ddown = bool(buttons & (1 << 7)),
            l1 = bool(buttons & (1 << 8)),
            r1 = bool(buttons & (1 << 9)),
            l3 = bool(buttons & (1 << 10)),
            r3 = bool(buttons & (1 << 11)),
            options = bool(buttons & (1 << 12)),
            share = bool(buttons & (1 << 13)),
            touchpad = bool(buttons & (1 << 14)),
            ps = bool(buttons & (1 << 15)),
            l2 = l2,
            r2 = r2,
            leftx = leftx,
            lefty = lefty,
            rightx = rightx,
            righty = righty,
            ignore = ignore)



fcontext = zmq.Context()
fsocket = fcontext.socket(zmq.REQ)
fsocket.connect("tcp://localhost:5553")

while True:
    state = ControllerState()
    state.ignore = True
    fsocket.send(state.serialize())
    msg = fsocket.recv()
    if  len(msg) != 0:
        state = ControllerState.deserialize(msg)
        print(state.stringify())
        msg = fsocket.recv()
        height = int.from_bytes(msg[0:2], byteorder='little')
        width = int.from_bytes(msg[2:4], byteorder='little')
        channel = int.from_bytes(msg[4:6], byteorder='little')
        img = numpy.frombuffer(msg, numpy.uint8, -1, 6)
        img.shape = (height, width, channel)
        img = img[:, :, ::-1].copy()
        cv2.imshow('img', img)
        cv2.waitKey(10)