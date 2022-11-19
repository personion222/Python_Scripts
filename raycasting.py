import pygame
from math import sin, cos, radians
from PIL import Image, ImageEnhance
import cv2
import numpy as np


def check_point_in_bounds(point, width_height):
    if point[0] > width_height[0] or point[0] < 0 or point[1] > width_height[1] or point[1] < 0:
        return True

    return False


def raycast(starting_pos: list, angle: float, rects: list, screen_size: tuple, step_dist: int = 4, rads: bool = False):
    ray_pos = starting_pos.copy()
    colliding = False
    travel_dist = 0
    hit_wall = False

    while not colliding:

        if rads:
            ray_pos[0] += cos(angle) * step_dist
            ray_pos[1] += sin(angle) * step_dist

        else:
            ray_pos[0] += cos(radians(angle)) * step_dist
            ray_pos[1] += sin(radians(angle)) * step_dist

        travel_dist += step_dist

        if check_point_in_bounds(ray_pos, (screen_size[0], screen_size[1])):
            while check_point_in_bounds(ray_pos, (screen_size[0], screen_size[1])):
                if rads:
                    ray_pos[0] -= cos(angle)
                    ray_pos[1] -= sin(angle)

                else:
                    ray_pos[0] -= cos(radians(angle))
                    ray_pos[1] -= sin(radians(angle))

                travel_dist -= 1

            hit_wall = True
            colliding = True

        for rect in rects:
            if rect.collidepoint(ray_pos):
                while rect.collidepoint(ray_pos):
                    if rads:
                        ray_pos[0] -= cos(angle)
                        ray_pos[1] -= sin(angle)

                    else:
                        ray_pos[0] -= cos(radians(angle))
                        ray_pos[1] -= sin(radians(angle))

                    travel_dist -= 1

                colliding = True

    return ray_pos, travel_dist, hit_wall


WIDTH = 720
HEIGHT = 480
FPS = 15
AA_SAMPLES = 2
RAY_THICKNESS = 1
CIRCLE_RADIUS = 16
CIRCLE_THICKNESS = 0
OBSTACLE_THICKNESS = 16
OBSTACLE_ROUNDNESS = 32
RAYCASTS = 720
FOV = 120
LOOK_SPEED = 0.25
RAYCAST_DEGREE_CHANGE = FOV / RAYCASTS
RAY_JUMP = 4
COL_DIST_MULTIPLIER = 0.25
MOVE_SPEED = 0.25

BACKGROUND = (15, 82, 186)
OBSTACLE = (180, 200, 160)
BALL = (255, 130, 30)
RAY = (0, 41, 93)

scaled_obstacles = list()
obstacles = list()
looking_dir = 0

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
aa_samples = pygame.Surface((WIDTH * AA_SAMPLES, HEIGHT * AA_SAMPLES))
pygame.display.set_caption("Raycasting")
clock = pygame.time.Clock()

drag_start = (0, 0)
circle_pos = [WIDTH // 2, HEIGHT // 2]
dragging = False

running = True
while running:
    print(circle_pos)
    delta = clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                drag_start = pygame.mouse.get_pos()
                dragging = True

            if event.button == 2:
                obstacles = list()
                scaled_obstacles = list()

            if event.button == 3:
                for obstacle in obstacles:
                    if obstacle.collidepoint(pygame.mouse.get_pos()):
                        scaled_obstacles.pop(obstacles.index(obstacle))
                        obstacles.remove(obstacle)

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                scaled_obstacles.append(pygame.Rect(drag_start[0] * AA_SAMPLES, drag_start[1] * AA_SAMPLES, (pygame.mouse.get_pos()[0] - drag_start[0]) * AA_SAMPLES, (pygame.mouse.get_pos()[1] - drag_start[1]) * AA_SAMPLES))
                obstacles.append(pygame.Rect(drag_start, ((pygame.mouse.get_pos()[0] - drag_start[0]), (pygame.mouse.get_pos()[1] - drag_start[1]))))
                dragging = False

        if event.type == pygame.MOUSEWHEEL:
            looking_dir -= event.y * LOOK_SPEED * delta

    pressed_keys = pygame.key.get_pressed()

    if pressed_keys[pygame.K_a]:
        x = cos(radians(0 - looking_dir - FOV / 2 + 90)) * MOVE_SPEED
        y = sin(radians(0 - looking_dir - FOV / 2 + 90)) * MOVE_SPEED
        circle_pos[0] += x * delta
        circle_pos[1] -= y * delta

        if check_point_in_bounds(circle_pos, (WIDTH, HEIGHT)):
            circle_pos[0] -= x * delta
            circle_pos[1] += y * delta

        for obstacle in obstacles:
            if obstacle.collidepoint(circle_pos):
                circle_pos[0] -= x * delta
                circle_pos[1] += y * delta

    if pressed_keys[pygame.K_d]:
        x = cos(radians(0 - looking_dir - FOV / 2 - 90)) * MOVE_SPEED
        y = sin(radians(0 - looking_dir - FOV / 2 - 90)) * MOVE_SPEED
        circle_pos[0] += x * delta
        circle_pos[1] -= y * delta

        if check_point_in_bounds(circle_pos, (WIDTH, HEIGHT)):
            circle_pos[0] -= x * delta
            circle_pos[1] += y * delta

        for obstacle in obstacles:
            if obstacle.collidepoint(circle_pos):
                circle_pos[0] -= x * delta
                circle_pos[1] += y * delta

    if pressed_keys[pygame.K_w]:
        x = cos(radians(0 - looking_dir - FOV / 2)) * MOVE_SPEED
        y = sin(radians(0 - looking_dir - FOV / 2)) * MOVE_SPEED
        circle_pos[0] += x * delta
        circle_pos[1] -= y * delta

        if check_point_in_bounds(circle_pos, (WIDTH, HEIGHT)):
            circle_pos[0] -= x * delta
            circle_pos[1] += y * delta

        for obstacle in obstacles:
            if obstacle.collidepoint(circle_pos):
                circle_pos[0] -= x * delta
                circle_pos[1] += y * delta

    if pressed_keys[pygame.K_s]:
        x = cos(radians(0 - looking_dir - FOV / 2)) * MOVE_SPEED
        y = sin(radians(0 - looking_dir - FOV / 2)) * MOVE_SPEED
        circle_pos[0] -= x * delta
        circle_pos[1] += y * delta

        if check_point_in_bounds(circle_pos, (WIDTH, HEIGHT)):
            circle_pos[0] += x * delta
            circle_pos[1] -= y * delta

        for obstacle in obstacles:
            if obstacle.collidepoint(circle_pos):
                circle_pos[0] += x * delta
                circle_pos[1] -= y * delta

    if pressed_keys[pygame.K_q]:
        looking_dir -= MOVE_SPEED * delta

    if pressed_keys[pygame.K_e]:
        looking_dir += MOVE_SPEED * delta

    aa_samples.fill(BACKGROUND)

    dists = list()
    wall_hits = list()

    for raycast_deg in range(RAYCASTS):
        hit_pos, dist_traveled, if_hit_wall = raycast(circle_pos, (raycast_deg * RAYCAST_DEGREE_CHANGE) + looking_dir, obstacles, (WIDTH, HEIGHT), RAY_JUMP)

        dists.append(dist_traveled)
        wall_hits.append(if_hit_wall)

        hit_pos[0] *= AA_SAMPLES
        hit_pos[1] *= AA_SAMPLES

        pygame.draw.line(aa_samples, RAY, (circle_pos[0] * AA_SAMPLES, circle_pos[1] * AA_SAMPLES), hit_pos, RAY_THICKNESS * AA_SAMPLES)

    for obstacle in scaled_obstacles:
        pygame.draw.rect(aa_samples, OBSTACLE, obstacle, OBSTACLE_THICKNESS * AA_SAMPLES, OBSTACLE_ROUNDNESS * AA_SAMPLES)

    if dragging:
        pygame.draw.rect(aa_samples, OBSTACLE, pygame.Rect(drag_start[0] * AA_SAMPLES, drag_start[1] * AA_SAMPLES, (pygame.mouse.get_pos()[0] - drag_start[0]) * AA_SAMPLES, (pygame.mouse.get_pos()[1] - drag_start[1]) * AA_SAMPLES), OBSTACLE_THICKNESS * AA_SAMPLES, OBSTACLE_ROUNDNESS * AA_SAMPLES)

    pygame.draw.circle(aa_samples, BALL, (circle_pos[0] * AA_SAMPLES, circle_pos[1] * AA_SAMPLES), CIRCLE_RADIUS * AA_SAMPLES, CIRCLE_THICKNESS * AA_SAMPLES)

    screen.blit(pygame.transform.smoothscale(aa_samples, (WIDTH, HEIGHT)), (0, 0))

    pygame.display.flip()

    looking_image_scaled = Image.new("RGB", (RAYCASTS, 1), (0, 0, 0))

    cur_pix = 0
    for dist in dists:
        if wall_hits[cur_pix]:
            dist_col_num = 255 - int(dist * COL_DIST_MULTIPLIER)
            dist_col = [int(dist_col_num * (BACKGROUND[2] / 255)), int(dist_col_num * (BACKGROUND[1] / 255)), int(dist_col_num * (BACKGROUND[0] / 255))]

            if dist_col[0] > 255:
                dist_col[0] = 255

            if dist_col[1] > 255:
                dist_col[1] = 255

            if dist_col[2] > 255:
                dist_col[2] = 255

            looking_image_scaled.putpixel((cur_pix, 0), tuple(dist_col))

        else:
            dist_col_num = 255 - int(dist * COL_DIST_MULTIPLIER)
            dist_col = [int(dist_col_num * (OBSTACLE[2] / 255)), int(dist_col_num * (OBSTACLE[1] / 255)), int(dist_col_num * (OBSTACLE[0] / 255))]

            if dist_col[0] > 255:
                dist_col[0] = 255

            if dist_col[1] > 255:
                dist_col[1] = 255

            if dist_col[2] > 255:
                dist_col[2] = 255

            looking_image_scaled.putpixel((cur_pix, 0), tuple(dist_col))

        cur_pix += 1

    looking_image = looking_image_scaled.resize((WIDTH * 2, HEIGHT // 2), resample=Image.Resampling.BOX)

    enhancer = ImageEnhance.Contrast(looking_image)
    looking_image = enhancer.enhance(1.5)

    cv2_looking_image = np.asarray(looking_image)
    cv2.imshow("POV", cv2_looking_image)

pygame.quit()
cv2.destroyAllWindows()
