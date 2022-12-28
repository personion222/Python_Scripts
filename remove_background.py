import cv2
from PIL import Image, ImageFilter, ImageEnhance
import numpy as np


def concat_img(img1, img2):
    concat = Image.new('RGB', (img1.width + img2.width, img1.height))
    concat.paste(img1, (0, 0))
    concat.paste(img2, (img1.width, 0))
    return concat


def pix_dist(pix0, pix1):
    return sum((abs(pix0[0] - pix1[0]), abs(pix0[1] - pix1[1]), abs(pix0[2] - pix1[2])))


background = Image.open("background.jpg").resize((160, 120), resample=Image.Resampling.LANCZOS)

max_dist = 50

vid_cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
ret, background_frame = vid_cap.read()
background_frame = Image.fromarray(cv2.cvtColor(background_frame, cv2.COLOR_RGB2BGR)).resize((160, 120), resample=Image.Resampling.LANCZOS).filter(ImageFilter.MedianFilter(size=3))

while True:
    ret, frame = vid_cap.read()

    if not ret:
        print("Something happened.")
        break

    pil_frame = Image.fromarray(cv2.resize(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), dsize=None, fx=0.25, fy=0.25, interpolation=cv2.INTER_LINEAR)).filter(ImageFilter.MedianFilter(size=3))

    replaced_frame = background.copy()

    for x in range(pil_frame.width):
        for y in range(pil_frame.height):
            if pix_dist(pil_frame.getpixel((x, y)), background_frame.getpixel((x, y))) < max_dist:
                replaced_frame.putpixel((x, y), background.getpixel((x, y)))

            else:
                replaced_frame.putpixel((x, y), pil_frame.getpixel((x, y)))

    cv2.imshow("Background Replaced", cv2.resize(cv2.cvtColor(np.asarray(concat_img(replaced_frame, pil_frame)), cv2.COLOR_RGB2BGR), dsize=None, fx=4, fy=4, interpolation=cv2.INTER_LINEAR))

    if cv2.waitKey(1) == ord('q'):
        break

vid_cap.release()
cv2.destroyAllWindows()
