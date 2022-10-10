import cv2
import numpy as np
from PIL import Image, ImageFilter


def concat_v(im1, im2):
    dst = Image.new('RGB', (im1.width, im1.height + im2.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (0, im1.height))
    return dst


cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)

filter_strength = 2
in_denoise = 3
out_denoise = 3
prev_img = None

while True:
    ret, frame = cam.read()

    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    pil_img = Image.fromarray(cv2.resize(img, dsize=None, fx=1 / 4, fy=1 / 4)).filter(ImageFilter.MedianFilter(size=in_denoise))

    dif_img = Image.new("RGB", pil_img.size)

    if prev_img is not None:
        for x in range(pil_img.width):
            for y in range(pil_img.height):
                og_pix = prev_img.getpixel((x, y))
                pix = pil_img.getpixel((x, y))

                new_pix = ((round((pix[0] - og_pix[0]) * filter_strength) + pix[0]), round(((pix[1] - og_pix[1]) * filter_strength) + pix[1]), round(((pix[2] - og_pix[2]) * filter_strength) + pix[2]))
                dif_img.putpixel((x, y), new_pix)

    cv2.imshow('video', cv2.resize(cv2.cvtColor(np.asarray(concat_v(pil_img, dif_img.filter(ImageFilter.MedianFilter(size=out_denoise)))), cv2.COLOR_BGR2RGB), dsize=None, fx=4, fy=4))

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    prev_img = pil_img.copy()

cam.release()
cv2.destroyAllWindows()
