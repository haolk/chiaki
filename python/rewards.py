from time import sleep
from PIL import Image
import numpy
import cv2
import pytesseract
import re

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

ocv = cv2.imread("../../scratch/REWARDS.png")
rewards = ocv[310:370, 100:400]
text = pytesseract.image_to_string(rewards)
print(text)

credits = ocv[280:320, 920:1180]
text = pytesseract.image_to_string(credits)
print(text)
amount_text = re.search("[0-9,]+", text)
print(amount_text)
amount = 0
if amount_text != None:
    amount = int(amount_text.group(0).replace(',', ''))
print(amount)
cv2.imshow('image', credits)
cv2.waitKey(0)
