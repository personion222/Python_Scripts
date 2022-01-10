from PIL import Image
from random import choices, randint
import cv2 as cv
import numpy as np
from time import time

Map = Image.open('map.png')
map_width, map_height = Map.size

print('Welcome to Slime, the Best / Only Slime Mold Simulator!')


def find_weight(pix):
    weight = pix[3] + pix[2] - (pix[1]*3)

    if pix == (38, 208, 124, 255) or (30, 144, 255, 255) or (200, 75, 75, 255) or (0, 0, 0, 255):
        weight = 2048

    elif weight <= 0:
        weight = 1

    return weight


class Agent:

    def __init__(self, x_start=128, y_start=128):
        self.location = {
            'x': x_start,
            'y': y_start
        }
        self.energy = 512

        self.speed = 0

    def move(self):
        x_offset = 0
        y_offset = 0

        directions = []
        pix_weights = []

        try:
            north_pix = Map.getpixel((self.location['x'], self.location['y']-1))
            directions.append('north')
            pix_weights.append(find_weight(north_pix))

        except IndexError:
            pass

        try:
            northwest_pix = Map.getpixel((self.location['x']-1, self.location['y']-1))
            directions.append('northwest')
            pix_weights.append(find_weight(northwest_pix))

        except IndexError:
            pass

        try:
            west_pix = Map.getpixel((self.location['x']-1, self.location['y']))
            directions.append('west')
            pix_weights.append(find_weight(west_pix))

        except IndexError:
            pass

        try:
            southwest_pix = Map.getpixel((self.location['x']-1, self.location['y']+1))
            directions.append('southwest')
            pix_weights.append(find_weight(southwest_pix))

        except IndexError:
            pass

        try:
            south_pix = Map.getpixel((self.location['x'], self.location['y']+1))
            directions.append('south')
            pix_weights.append(find_weight(south_pix))

        except IndexError:
            pass

        try:
            southeast_pix = Map.getpixel((self.location['x']+1, self.location['y']+1))
            directions.append('southeast')
            pix_weights.append(find_weight(southeast_pix))

        except IndexError:
            pass

        try:
            east_pix = Map.getpixel((self.location['x']+1, self.location['y']))
            directions.append('east')
            pix_weights.append(find_weight(east_pix))

        except IndexError:
            pass

        try:
            northeast_pix = Map.getpixel((self.location['x']+1, self.location['y']-1))
            directions.append('northeast')
            pix_weights.append(find_weight(northeast_pix))

        except IndexError:
            pass

        direction = choices(directions, pix_weights)[0]

        if direction == 'north':
            y_offset = -1

        elif direction == 'northwest':
            x_offset = -1
            y_offset = -1

        elif direction == 'west':
            x_offset = -1

        elif direction == 'southwest':
            x_offset = -1
            y_offset = 1

        elif direction == 'south':
            y_offset = 1

        elif direction == 'southeast':
            x_offset = 1
            y_offset = 1

        elif direction == 'east':
            x_offset = 1

        elif direction is None:
            pass

        else:
            x_offset = 1
            y_offset = -1

        self.location['x'] += x_offset
        self.location['y'] += y_offset
        Map.putpixel((self.location['x'], self.location['y']), (255, 255, 255))

        self.energy -= 1

        if self.speed > 0:
            self.speed -= 1

    def regen(self):
        self.energy += 256

    def regen_speed(self):
        self.speed = 32

    def teleport(self):
        self.location['x'] = randint(1, 256)
        self.location['y'] = randint(1, 256)


agent_count = 256

slime_types = ('line', 'growing dot', 'dots')

while True:
    slime_type = input('What type of slime would you like?(Line, Growing Dot or Dots)(Recommended: Growing Dot): ').lower()

    if slime_type in slime_types:
        break

    else:
        print('Please enter Line, Growing Dot or Dots.')

while True:

    if slime_type != 'line':
        try:
            agent_count = int(input('How many agents (Bits of slime) would you like?(Recommended: 512): '))
            break

        except ValueError:
            print('Please enter an integer.')

    else:
        break

while True:
    try:
        food_count = int(input('How much pieces of food would you like?(Recommended: 512): '))
        power_pellet_count = int(input('How much power pellets would you like?(Recommended: 256): '))
        teleport_count = int(input('How much teleport pads would you like?(Recommended: 256): '))
        break
    except ValueError:
        print('Please enter an integer.')

while True:
    HUD = input('Would you like to enable the HUD?(Please enter Yes or No): ').lower()

    if HUD == 'no' or 'yes':
        break

    else:
        print('Please enter Yes or No.')

agents = list()

print("Press 'q' to exit and save your slime!")

for i in range(agent_count):
    if slime_type == 'line':
        agents.append(Agent(i, 128))

    elif slime_type == 'growing dot':
        agents.append(Agent())

    else:
        agents.append(Agent(randint(1, 256), randint(1, 256)))

food_locs = []

for i in range(food_count):
    food_locs.append([randint(0, 255), randint(0, 255)])

power_pellet_locs = []

for i in range(power_pellet_count):
    power_pellet_locs.append([randint(0, 255), randint(0, 255)])

teleport_locs = []

for i in range(teleport_count):
    teleport_locs.append([randint(0, 255), randint(0, 255)])

frame = 0

sim_start = time()

while True:
    frame_start = time()
    frame += 1
    for agent in agents:
        if agent.speed > 0:
            for i in range(3):
                agent.move()

        else:
            agent.move()

        if [agent.location['x'], agent.location['y']] in food_locs:
            agent.regen()
            food_locs.remove([agent.location['x'], agent.location['y']])
            food_locs.append([randint(0, 255), randint(0, 255)])

        if [agent.location['x'], agent.location['y']] in power_pellet_locs:
            agent.regen_speed()
            agent.regen()
            power_pellet_locs.remove([agent.location['x'], agent.location['y']])
            power_pellet_locs.append([randint(0, 255), randint(0, 255)])

        if [agent.location['x'], agent.location['y']] in teleport_locs:
            agent.regen()
            teleport_locs.remove([agent.location['x'], agent.location['y']])
            agent.teleport()
            teleport_locs.append([randint(0, 255), randint(0, 255)])

        if agent.energy <= 0:
            agents.remove(agent)

    if len(agents) == 0:
        print('All of the slime is dead!')
        cv.imwrite(slime_type + ' slime' + ' taken at' + ' ' + str(round(time())) + '.png', cv2map)
        cv.destroyAllWindows()
        break

    for x in range(map_width):
        for y in range(map_height):
            pixel = Map.getpixel((x, y))

            Map.putpixel((x, y), (pixel[0]-3, pixel[1]-2, pixel[2]-1))

    for food in food_locs:
        Map.putpixel(food, (38, 204, 114))

    for power_pellet in power_pellet_locs:
        Map.putpixel(power_pellet, (30, 144, 255))

    for teleport in teleport_locs:
        Map.putpixel(teleport, (200, 75, 75))

    frame_end = time()
    SPF = frame_end - frame_start

    cv2map = np.asarray(Map)
    cv2map = cv.resize(cv2map, (720, 720), interpolation=cv.INTER_AREA)
    if HUD == 'yes':
        energies = []
        for agent in agents:
            energies.append(agent.energy)

        cv.putText(cv2map, 'FPS: ' + str(round(1 / SPF)), (0, 12), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255, 255), 1)
        cv.putText(cv2map, 'Agents Remaining: ' + str(len(agents)), (0, 32), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255, 255), 1)
        cv.putText(cv2map, 'Food Particles: ' + str(food_count), (0, 52), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255, 255), 1)
        cv.putText(cv2map, 'Power Pellets: ' + str(power_pellet_count), (0, 72), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255, 255), 1)
        cv.putText(cv2map, 'Teleport Particles: ' + str(teleport_count), (0, 92), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255, 255), 1)
        cv.putText(cv2map, 'AVG Energy Remaining: ' + str(round(sum(energies) / len(energies))), (0, 112), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255, 255), 1)
        cv.putText(cv2map, 'Iterations: ' + str(frame), (0, 132), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255, 255), 1)
        cv.putText(cv2map, 'Runtime: ' + str(int(round(time() - sim_start) / 60)) + ':' + str(round(time() - sim_start) - int((time() - sim_start) / 60) * 60), (0, 152), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255, 255), 1)

    cv2map = cv.cvtColor(cv2map, cv.COLOR_RGB2BGR)
    cv.imshow('Slime Sim', cv2map)

    if cv.waitKey(1) & 0xFF == ord('q'):
        break

cv.imwrite(slime_type+' slime'+' taken at'+' '+str(round(time()))+'.png', cv2map)
cv.destroyAllWindows()
