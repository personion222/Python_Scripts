import cv2
from PIL import Image, ImageDraw
import numpy as np
from statistics import fmean, median_low
from pynput.mouse import Controller


def join_imgs_h(img1, img2):
    new_image = Image.new("RGB", (img1.width + img2.width, max((img1.height, img2.height))))
    new_image.paste(img1, (0, 0))
    new_image.paste(img2, (img1.width, 0))

    return new_image


cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
mouse_controller = Controller()

prev_frame = None
pos = (0, 0)
min_point_count = 5
denoise_window_size = 10

prev_x_poses = []
prev_y_poses = []

while True:
    ret, frame = cap.read()

    if not ret:
        print("Something went wrong. Exiting.")
        break

    pil_frame = Image.fromarray(cv2.resize(frame, None, fx=0.25, fy=0.25))
    dif_frame = Image.new("1", pil_frame.size)
    dif_draw = ImageDraw.Draw(dif_frame)

    x_poses = []
    y_poses = []

    if prev_frame is not None:
        for x in range(dif_frame.width):
            for y in range(dif_frame.height):
                old_pix = fmean(prev_frame.getpixel((x, y)))
                new_pix = fmean(pil_frame.getpixel((x, y)))
                if abs(old_pix - new_pix) >= 50:
                    dif_frame.putpixel((x, y), 1)
                    x_poses.append(x)
                    y_poses.append(y)

                else:
                    dif_frame.putpixel((x, y), 0)

    dif_frame = dif_frame.convert("RGB")
    dif_draw = ImageDraw.Draw(dif_frame)

    if len(x_poses) >= min_point_count:
        prev_x_poses.append(median_low(x_poses))
        prev_y_poses.append(median_low(y_poses))

        if len(prev_x_poses) >= denoise_window_size:
            prev_x_poses.pop(0)
            prev_y_poses.pop(0)

        pos = (median_low(prev_x_poses), median_low(prev_y_poses))

        dif_draw.rectangle((pos[0] - 10, pos[1] - 10, pos[0] + 10, pos[1] + 10), fill=(255, 140, 30))
        mouse_controller.position = (1920 - pos[0] * 4 * 3, pos[1] * 4 * 3)

    prev_frame = pil_frame

    cv2.imshow('what the camera sees', np.asarray(join_imgs_h(dif_frame, pil_frame)))

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
