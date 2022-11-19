from PIL import Image, ImageDraw
import cv2
import numpy as np
from statistics import fmean, StatisticsError, median_low
from time import time, sleep
from math import dist


def get_color_dist(col1: tuple, col2: tuple, thresh: int):
    col_dist = sum((abs(col1[0] - col2[0]), abs(col1[1] - col2[1]), abs(col1[2] - col2[2])))

    if col_dist <= thresh:
        return True

    return False


COLOR = (92, 132, 224)
SRC_COLOR = (280, 140, 120)
WAVE_COLOR = (15, 35, 64)
DETECT_DIST = 50
DRAW_R = 5
AVG_WIN_SIZE = 4
SOUND_SPEED = 12
WAVELENGTH = 3
MAX_FPS = 15

video_cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

pos = (0, 0)
avg_pos = (0, 0)
poses_x = [0]
poses_y = [0]
waves = dict()
ret, frame = video_cap.read()
screen_diag = dist((0, 0), Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).resize((Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).width // 2, Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).height // 2)).size)

frame_iterator = 0

while True:
    start = time()
    ret, frame = video_cap.read()

    if not ret:
        break

    pil_frame = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).resize((Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).width // 2, Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).height // 2))
    det_image = Image.new("RGB", pil_frame.size)
    draw_image = pil_frame.copy()
    drawer = ImageDraw.Draw(draw_image)

    pix_x = list()
    pix_y = list()

    for x in range(pil_frame.width):
        for y in range(pil_frame.height):
            sel_pix = pil_frame.getpixel((x, y))

            if get_color_dist(sel_pix, COLOR, DETECT_DIST):
                det_image.putpixel((x, y), COLOR)
                pix_x.append(x)
                pix_y.append(y)

    try:
        pos = (median_low(pix_x), median_low(pix_y))

    except StatisticsError:
        pass

    poses_x.append(pos[0])
    poses_y.append(pos[1])

    if len(poses_x) > AVG_WIN_SIZE:
        poses_x.pop(0)
        poses_y.pop(0)

    avg_pos = (fmean(poses_x), fmean(poses_y))

    if frame_iterator % WAVELENGTH == 0:
        waves.update({frame_iterator // WAVELENGTH: [avg_pos, 0]})

    del_waves = list()

    for wave in waves.keys():
        waves[wave][1] += SOUND_SPEED
        drawer.ellipse((waves[wave][0][0] - waves[wave][1], waves[wave][0][1] - waves[wave][1], waves[wave][0][0] + waves[wave][1], waves[wave][0][1] + waves[wave][1]), outline=WAVE_COLOR, width=2)

        if waves[wave][1] > screen_diag:
            del_waves.append(wave)

    for del_wave in del_waves:
        del waves[del_wave]

    drawer.ellipse((avg_pos[0] - DRAW_R, avg_pos[1] - DRAW_R, avg_pos[0] + DRAW_R, avg_pos[1] + DRAW_R), fill=SRC_COLOR)

    cv2.imshow('video', cv2.cvtColor(np.array(draw_image.resize((pil_frame.width * 2, pil_frame.height * 2), resample=Image.Resampling.BOX)), cv2.COLOR_RGB2BGR))

    frame_iterator += 1

    if cv2.waitKey(1) == ord('q'):
        break

    sleep(max((0, (1 / MAX_FPS) - (time() - start))))

video_cap.release()
cv2.destroyAllWindows()
