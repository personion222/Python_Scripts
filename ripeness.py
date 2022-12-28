import cv2
from PIL import Image, ImageFilter
import numpy as np
from shapely import geometry
from math import dist
from statistics import fmean


def click_event(event, x, y, _, __):
    global polygon
    global inside_pixels
    global banana_clear_edges
    global clicking
    global frame_iter
    global banana_rect

    if event == cv2.EVENT_LBUTTONDOWN:
        clicking = True
        closest = (dist(banana_clear_edges[0], (x, y)), (x, y))
        for edge in banana_clear_edges:
            if dist(edge, (x, y)) < closest[0]:
                closest = (dist(edge, (x, y)), edge)

        if closest[0] < 25:
            polygon.append(closest[1])

        else:
            polygon.append((x, y))

    if clicking and frame_iter % 2 == 0:
        closest = (dist(banana_clear_edges[0], (x, y)), (x, y))
        for edge in banana_clear_edges:
            if dist(edge, (x, y)) < closest[0]:
                closest = (dist(edge, (x, y)), edge)

        if closest[0] < 25:
            if closest[1] not in polygon:
                polygon.append(closest[1])

        else:
            if (x, y) not in polygon:
                polygon.append((x, y))

        if banana_rect == [None, None]:
            banana_rect = [list(polygon[-1]), list(polygon[-1])]

        else:
            if polygon[-1][0] < banana_rect[0][0]:
                banana_rect[0][0] = polygon[-1][0]

            if polygon[-1][1] < banana_rect[0][1]:
                banana_rect[0][1] = polygon[-1][1]

            if polygon[-1][0] > banana_rect[1][0]:
                banana_rect[1][0] = polygon[-1][0]

            if polygon[-1][1] > banana_rect[1][1]:
                banana_rect[1][1] = polygon[-1][1]

    if event == cv2.EVENT_LBUTTONUP:
        clicking = False

    if event == cv2.EVENT_RBUTTONDOWN:
        polygon = list()
        inside_pixels = list()
        banana_rect = [None, None]


def get_ripeness(color, ideal, weights):
    hue_dif = (ideal[0] - color[0]) * weights[0]
    sat_dif = (ideal[1] - color[1]) * weights[1]
    val_dif = (ideal[2] - color[2]) * weights[2]

    return sum((hue_dif, sat_dif, val_dif))


def pix_dist(pix1, pix2):
    return int(sum((abs(pix1[0] - pix2[0]), abs(pix1[1] - pix2[1]), abs(pix1[2] - pix2[2]))) / 3)


def score_to_percent(score):
    # -11249
    if score <= 0:
        return max((round(0.25 * score) + 100, 0))

    return round(0.00888967908 * score) + 100


clicking = False
polygon = list()
inside_pixels = list()
vid_cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
banana_picture = Image.fromarray(vid_cap.read()[1])
# banana_picture = banana_picture.resize((banana_picture.width // 2, banana_picture.height // 2))
banana_hsv = banana_picture.convert("HSV")
# banana_edges = banana_picture.filter(ImageFilter.FIND_EDGES).convert("L")
banana_clear_edges = list()
bar_img = Image.open("bar.png")
bar_point_img = Image.open("bar_point.png")

'''for x in range(banana_edges.width):
    for y in range(banana_edges.height):
        if banana_edges.getpixel((x, y)) > 35:
            banana_clear_edges.append((x, y))'''

blurred = banana_picture.filter(ImageFilter.BoxBlur(1))

for x in range(0, blurred.width, 4):
    for y in range(0, blurred.height, 4):
        pil_pix = banana_picture.getpixel((x, y))
        cur_pix_dist = pix_dist(pil_pix, blurred.getpixel((x, y)))

        if cur_pix_dist > 3:
            banana_clear_edges.append((x, y))

avg_color = (255, 255, 255)
point_space = banana_picture.width * banana_picture.height // 25000
frame_iter = 0
banana_rect = [None, None]
ripeness_prev_vals = [0]
ripeness_percent_to_x_pos = 0.6
ripeness_avg_win_size = 32

while True:
    banana_picture = Image.fromarray(cv2.cvtColor(vid_cap.read()[1], cv2.COLOR_RGB2BGR))
    banana_hsv = banana_picture.convert("HSV")
    banana_clear_edges = list()

    blurred = banana_picture.filter(ImageFilter.BoxBlur(1))

    for x in range(0, blurred.width, 4):
        for y in range(0, blurred.height, 4):
            pil_pix = banana_picture.getpixel((x, y))
            cur_pix_dist = pix_dist(pil_pix, blurred.getpixel((x, y)))

            if cur_pix_dist > 3:
                banana_clear_edges.append((x, y))

    if len(polygon) >= 3:
        inside_pixels = list()
        outside_pixels = list()

        inside_hue_sum = 0
        inside_sat_sum = 0
        inside_val_sum = 0
        inside_count = 0

        shapely_poly = geometry.Polygon(polygon)
        for x in range(banana_rect[0][0], banana_rect[1][0], point_space):
            for y in range(banana_rect[0][1], banana_rect[1][1], point_space):
                pixel_point = geometry.Point(x, y)

                if shapely_poly.contains(pixel_point):
                    pixel = banana_hsv.getpixel((x, y))
                    inside_pixels.append((x, y))
                    inside_hue_sum += pixel[0]
                    inside_sat_sum += pixel[1]
                    inside_val_sum += pixel[2]
                    inside_count += 1

        if inside_count != 0:
            avg_color = (round(inside_hue_sum / inside_count), round(inside_sat_sum / inside_count), round(inside_val_sum / inside_count))
            '''print(round(inside_hue_sum / inside_count), end=" ")
            print(round(inside_sat_sum / inside_count), end=" ")
            print(round(inside_val_sum / inside_count))'''

    # print(get_ripeness(avg_color, (32, 212, 227), (50, 1, 2)), score_to_percent(get_ripeness(avg_color, (32, 212, 227), (50, 1, 2))))
    ripeness_percent = score_to_percent(get_ripeness(avg_color, (32, 212, 227), (50, 1, 2)))
    ripeness_prev_vals.append(ripeness_percent)
    print(ripeness_percent)

    if len(ripeness_prev_vals) >= ripeness_avg_win_size:
        ripeness_prev_vals.pop(0)

    # print(banana_rect)
    # print(len(polygon))
    pil_draw_img = banana_picture.copy()
    pil_draw_img.paste(bar_img, (32, 32), bar_img.convert("RGBA"))
    point_pos = (round(38 + fmean(ripeness_prev_vals) * ripeness_percent_to_x_pos), 38)
    pil_draw_img.paste(bar_point_img, point_pos, bar_point_img.convert("RGBA"))

    cv_image = cv2.polylines(cv2.cvtColor(np.array(pil_draw_img), cv2.COLOR_RGB2BGR), [np.asarray(polygon)], True, (255, 140, 30), 5)

    '''for pixel in inside_pixels:
        cv_image = cv2.circle(cv_image, pixel, 0, (140, 255, 30), 3)'''

    cv2.imshow('video', cv_image)
    cv2.setMouseCallback("video", click_event)

    if cv2.waitKey(1) == ord('q'):
        break

    frame_iter += 1

cv2.destroyAllWindows()
vid_cap.release()
