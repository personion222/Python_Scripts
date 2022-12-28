import cv2
from PIL import Image
import numpy as np
from statistics import fmean


vid_cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
face_cascade_model = cv2.CascadeClassifier("face_detect.xml")

avg_win_size = 8

prev_tops = list()
prev_downs = list()
prev_lefts = list()
prev_rights = list()

while True:
    cam_img = vid_cap.read()[1]

    cam_gray = cv2.cvtColor(cam_img, cv2.COLOR_BGR2GRAY)
    faces = list(face_cascade_model.detectMultiScale(cam_gray, 1.25, 4))

    if len(faces) != 0:
        face = list(faces[0])
        image_draw = cam_img.copy()
        cv2.rectangle(image_draw, (face[0], face[1]), (face[0] + face[2], face[1] + face[3]), (255, 140, 30), 5)
        prev_tops.append(face[1])
        prev_downs.append(face[1] + face[3])
        prev_lefts.append(face[0])
        prev_rights.append(face[0] + face[2])

        if len(prev_tops) >= avg_win_size:
            prev_tops.pop(0)
            prev_downs.pop(0)
            prev_lefts.pop(0)
            prev_rights.pop(0)

        image_cropped = Image.fromarray(cam_img).crop((round(fmean(prev_lefts) - 50),
                                                       round(fmean(prev_tops) - 50),
                                                       round(fmean(prev_rights) + 50),
                                                       round(fmean(prev_downs) + 50)))

        cv2.imshow("video", np.asarray(image_cropped.resize((1024, 1024))))

    else:
        image_cropped = Image.fromarray(cam_img).crop((round(fmean(prev_lefts) - 50),
                                                       round(fmean(prev_tops) - 50),
                                                       round(fmean(prev_rights) + 50),
                                                       round(fmean(prev_downs) + 50)))

        cv2.imshow("video", np.asarray(image_cropped.resize((1024, 1024))))

    if cv2.waitKey(1) == ord('q'):
        image_cropped.resize((1024, 1024)).save("yes.png")
        break

cv2.destroyAllWindows()
vid_cap.release()
