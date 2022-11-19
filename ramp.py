import cv2
from PIL import Image, ImageFilter
import numpy as np
from statistics import fmean
from random import randint


def color_multiply(color, fac):
    return round(color[0] * fac), round(color[1] * fac), round(color[2] * fac)


def color_add(color1, color2):
    return round(color1[0] + color2[0]), round(color1[1] + color2[1]), round(color1[2] + color2[2])


'''def avg_color(colors):
    rs = list()
    gs = list()
    bs = list()

    for color in colors:
        rs.append(color[0])
        gs.append(color[1])
        bs.append(color[2])

    return round(fmean(rs)), round(fmean(gs)), round(fmean(bs))


def ramp_color(color1, color2, idx, ramp_scale):
    colors = list()

    for i in range(round(ramp_scale * 255 - ramp_scale * idx)):
        colors.append(color1)

    for i in range(round(ramp_scale * idx)):
        colors.append(color2)

    return avg_color(colors)'''


def ramp_color(color1, color2, idx, step_size=1):
    idx = round(idx / step_size) * step_size
    return color_add(color_multiply(color1, (255 - idx) / 255), color_multiply(color2, idx / 255))


vid_cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

while True:
    ret, frame = vid_cap.read()

    if not ret:
        print("Something happened.")
        break

    pil_frame = Image.fromarray(cv2.resize(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), dsize=None, fx=0.25, fy=0.25, interpolation=cv2.INTER_NEAREST))

    ramped_frame = pil_frame.copy()

    for x in range(pil_frame.width):
        for y in range(pil_frame.height):
            pix = round(fmean(pil_frame.getpixel((x, y))))
            ramped_frame.putpixel((x, y), ramp_color((15, 35, 64), (30, 255, 140), pix, 32))

    cv2.imshow("Color Ramped", cv2.resize(cv2.cvtColor(np.asarray(ramped_frame), cv2.COLOR_RGB2BGR), dsize=None, fx=4, fy=4, interpolation=cv2.INTER_NEAREST))

    if cv2.waitKey(1) == ord('q'):
        break

vid_cap.release()
cv2.destroyAllWindows()
