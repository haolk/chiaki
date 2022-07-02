import zmq
import numpy
import cv2
import pytesseract
import re

#
# img-1-world-circuits.cv [280:320, 250:360] 'america'
# img-2-change-car.cv [620:670, 610:700] 'change car'
# img-3-pan-america-race-1.cv [660:690, 630:680] 'next' [300:390, 530:780] 'blue moon bay'
# img-4-start-pan-america-race-1.cv [80:110, 150:560] 'pan-american championship race 1' [630:650, 330:380] 'start'
# img-5-racing.cv [20:50, 80:320] 'position'
# img=6-finished-racing.cv ???
# img-7-leaderboard.cv [660:710, 630:680] 'next' [50:75, 540:930] 'pan-american championship race 1'
# img-8-results.cv [670:755, 640:690] 'next' [630:655, 930:1030] 'prize money'
# img-9-standings.cv [80:115, 30:180] 'end of round 1' [640:670, 1190:1240] 'next' x2
# img-10-rewards.cv [650:705, 630:690] 'next' [275:375, 100:400] 'rewards'
# img-11-blank-replay.cv [650:780, 1040:1220] 'gran turismo'
# img-11b-replay-exit.cv [620:648, 1170:1230] 'exit'
# img-12-to-next-race.cv [650:680, 680:800] 'to next race'
# img-13-pan-america-race-2.cv [660:690, 630:680] 'next' [330:380, 530:780] 'international speedway'
# img-14-start-pan-america-race-2.cv [80:110, 150:560] 'pan-american championship race 2' [630:650, 330:380] 'start'
# img-15-exit-pan-america-race-2.cv [300:360, 430:870] 'are you sure you want to retire from the championship'

sx = 0
sy = 0
ex = 0
ey = 0
clicked = False
drawn = False

def mouse(event, x, y, flags, params):
    global sx, sy, ex, ey
    if event == cv2.EVENT_LBUTTONDOWN:
        sx = ex = x
        sy = ey = y
    elif event == cv2.EVENT_LBUTTONUP:
        ex = x
        ey = y
    
    i = img.copy()
    if sx > ex:
        tx = sx
        sx = ex
        ex = tx
    if sy > ey:
        ty = sy
        sy = ey
        ey = ty

    cv2.rectangle(i, (sx, sy), (ex, ey), (0, 255, 0), 2)
    cv2.imshow("Image", i)

cv2.namedWindow("Image")
cv2.setMouseCallback("Image", mouse)

with open('img.cv', 'rb') as file:
    global img
    msg = file.read()

    height = int.from_bytes(msg[0:2], byteorder='little')
    width = int.from_bytes(msg[2:4], byteorder='little')
    channel = int.from_bytes(msg[4:6], byteorder='little')
    img = numpy.frombuffer(msg, numpy.uint8, -1, 6)
    img.shape = (height, width, channel)
    img = img[:, :, ::-1].copy()
    cv2.imshow("Image", img)
    cv2.waitKey(0)
    i = img[sy:ey, sx:ex]
    cv2.imshow("Foo", i)
    cv2.waitKey(0)
    print("img[%d:%d, %d:%d]" % (sy, ey, sx, ex))