import cv2
import mediapipe as mp
from pynput.mouse import Controller, Button
from statistics import fmean, multimode
from math import dist

mouse_con = Controller()

mp_holistic = mp.solutions.holistic
holistic_model = mp_holistic.Holistic(min_detection_confidence=0.01, min_tracking_confidence=0.01)

prev_mouse_poses_x = list()
prev_mouse_poses_y = list()
prev_clicks = list()
mouse_avg_win_len = 8
click_mode_win_len = 3
clicking = False

vid_cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

while vid_cap.isOpened():
    ret, frame = vid_cap.read()

    frame_size = list(frame.shape)
    camx_to_screenx = 1920 / frame_size[1]
    camy_to_screeny = 1080 / frame_size[0]

    if not ret:
        print("There was a fault with the camera. Quitting.")
        break

    # frame = cv2.cvtColor(cv2.flip(frame, 0), cv2.COLOR_BGR2RGB)

    results = holistic_model.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    # results = holistic_model.process(frame)

    right_landmarks = []
    left_landmarks = []

    if results.right_hand_landmarks is not None:
        for data_point in results.right_hand_landmarks.landmark:
            right_landmarks.append({
                'X': data_point.x * frame_size[1],
                'Y': data_point.y * frame_size[0],
                'Z': data_point.z,
                'Visibility': data_point.visibility,
             })

    if results.left_hand_landmarks is not None:
        for data_point in results.left_hand_landmarks.landmark:
            left_landmarks.append({
                 'X': data_point.x * frame_size[1],
                 'Y': data_point.y * frame_size[0],
                 'Z': data_point.z,
                 'Visibility': data_point.visibility,
             })

    for landmark in right_landmarks:
        cv2.circle(frame, (round(landmark["X"]), round(landmark["Y"])), 1, (255, 140, 30), 15)

    for landmark in left_landmarks:
        cv2.circle(frame, (round(landmark["X"]), round(landmark["Y"])), 1, (255, 140, 30), 15)

    if results.right_hand_landmarks is not None:
        if clicking:
            cv2.line(frame, (round(right_landmarks[12]["X"]), round(right_landmarks[12]["Y"])),
                            (round(right_landmarks[7]["X"]), round(right_landmarks[6]["Y"])), (140, 255, 30), 5)

        else:
            cv2.line(frame, (round(right_landmarks[12]["X"]), round(right_landmarks[12]["Y"])),
                             (round(right_landmarks[7]["X"]), round(right_landmarks[6]["Y"])), (30, 30, 255), 5)

        cv2.circle(frame, (round(right_landmarks[8]["X"]), round(right_landmarks[8]["Y"])), 1, (30, 140, 255), 15)
        cv2.circle(frame, (round(right_landmarks[12]["X"]), round(right_landmarks[12]["Y"])), 1, (30, 140, 255), 15)
        cv2.circle(frame, (round(right_landmarks[7]["X"]), round(right_landmarks[6]["Y"])), 1, (30, 140, 255), 15)

        if round(right_landmarks[12]["Y"]) > round(right_landmarks[6]["Y"]):
            prev_clicks.append(True)

        else:
            prev_clicks.append(False)

        if len(prev_clicks) >= click_mode_win_len:
            prev_clicks.pop(0)

        if multimode(prev_clicks)[0] and not clicking:
            mouse_con.press(Button.left)
            clicking = True
            print("pressing")

        if not multimode(prev_clicks)[0] and clicking:
            mouse_con.release(Button.left)
            clicking = False
            print("releasing")

        '''if results.left_hand_landmarks is not None:
            cv2.circle(frame, (round(left_landmarks[4]["X"]), round(left_landmarks[4]["Y"])), 1, (30, 140, 255), 15)
            cv2.circle(frame, (round(left_landmarks[5]["X"]), round(left_landmarks[5]["Y"])), 1, (30, 140, 255), 15)

            if round(left_landmarks[4]["Y"]) >= round(left_landmarks[5]["Y"]):
                prev_clicks.append(True)

            else:
                prev_clicks.append(False)

            if len(prev_clicks) >= click_mode_win_len:
                prev_clicks.pop(0)

            if multimode(prev_clicks)[0] and not clicking:
                mouse_con.press(Button.left)

            elif clicking:
                mouse_con.release(Button.left)'''

        prev_mouse_poses_x.append(1920 - right_landmarks[8]["X"] * camx_to_screenx)
        prev_mouse_poses_y.append(right_landmarks[8]["Y"] * camy_to_screeny)

        if len(prev_mouse_poses_x) >= mouse_avg_win_len:
            prev_mouse_poses_x.pop(0)
            prev_mouse_poses_y.pop(0)

        cv2.line(frame, (round((1920 - fmean(prev_mouse_poses_x)) / camx_to_screenx), round(fmean(prev_mouse_poses_y) / camy_to_screeny)),
                        (round(right_landmarks[8]["X"]), round(right_landmarks[8]["Y"])), (255, 140, 30), 5)

        cv2.circle(frame, (round((1920 - fmean(prev_mouse_poses_x)) / camx_to_screenx), round(fmean(prev_mouse_poses_y) / camy_to_screeny)), 1, (140, 255, 30), 15)

        if dist((prev_mouse_poses_x[0], prev_mouse_poses_y[0]), (prev_mouse_poses_x[-1], prev_mouse_poses_y[-1])) >= 16:
            mouse_con.position = (fmean(prev_mouse_poses_x), fmean(prev_mouse_poses_y))

    cv2.imshow("hand landmarks", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

vid_cap.release()
cv2.destroyAllWindows()
