import cv2
from PIL import Image, ImageFilter
import numpy as np


def pix_dist(pix1, pix2):
    return int(sum((abs(pix1[0] - pix2[0]), abs(pix1[1] - pix2[1]), abs(pix1[2] - pix2[2]))) / 3)


vid_cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

while True:
    ret, frame = vid_cap.read()
    frame = cv2.resize(frame, dsize=None, fx=1, fy=1, interpolation=cv2.INTER_NEAREST)

    if not ret:
        print("Something happened.")
        break

    pil_frame = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    adjusted_frame = Image.new("L", (pil_frame.size))

    blurred = pil_frame.filter(ImageFilter.BoxBlur(1))

    for x in range(adjusted_frame.width):
        for y in range(adjusted_frame.height):
            pil_pix = pil_frame.getpixel((x, y))
            cur_pix_dist = pix_dist(pil_pix, blurred.getpixel((x, y)))

            if cur_pix_dist > 4:
                adjusted_frame.putpixel((x, y), 255)

            else:
                adjusted_frame.putpixel((x, y), 0)

    cv2.imshow('edges', cv2.resize(cv2.cvtColor(np.asarray(adjusted_frame.filter(ImageFilter.MedianFilter(3))), cv2.COLOR_RGB2BGR), dsize=None, fx=1, fy=1, interpolation=cv2.INTER_NEAREST))

    if cv2.waitKey(1) == ord('q'):
        break

vid_cap.release()
cv2.destroyAllWindows()
