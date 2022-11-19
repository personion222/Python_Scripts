from PIL import Image
import cv2
import numpy as np
from time import time, sleep

SWIPE_LEN = 5

video_cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

temp_img = Image.fromarray(video_cap.read()[1])

screen_dim = (temp_img.width // 8, temp_img.height // 8)
og_screen_dim = temp_img.size
swipe_image = Image.new("RGBA", screen_dim)

startest = time()

for x in range(screen_dim[0]):
    start = time()
    ret, frame = video_cap.read()

    if not ret:
        break

    pil_frame = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).resize(screen_dim, resample=Image.Resampling.NEAREST).convert("RGBA")

    for y in range(screen_dim[1]):
        swipe_image.putpixel((x, y), pil_frame.getpixel((x, y)))

    show_img = pil_frame.copy()
    show_img.paste(swipe_image)

    cv2.imshow('video', cv2.cvtColor(np.array(show_img.resize(og_screen_dim, resample=Image.Resampling.NEAREST)), cv2.COLOR_RGB2BGR))

    if cv2.waitKey(1) == ord('q'):
        break

    sleep(max((SWIPE_LEN / screen_dim[0] - (time() - start), 0)))

print(time() - startest)

swipe_image.resize(og_screen_dim, resample=Image.Resampling.NEAREST).save("camera_swipe.png")

video_cap.release()
cv2.destroyAllWindows()
