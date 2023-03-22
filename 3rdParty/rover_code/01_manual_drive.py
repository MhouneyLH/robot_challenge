from rover_base import Rover
from getkey import getkey, keys
from perlin_noise import PerlinNoise
import time
import numpy as np
import matplotlib.pyplot as plt

SPEED = 70
TURNING_DURATION = 3
TURNING_SPEED = 70
MEASUREMENT_DEFAULT_VALUE = -1
FIELD_WIDTH = 2000
FIELD_HEIGHT = 1000
FIELD_BOUNDARY = 100


def turn_right(bot: Rover):
    bot.set_motor_speed(TURNING_SPEED, -TURNING_SPEED)
    # time.sleep(TURNING_DURATION)


def turn_left(bot: Rover):
    bot.set_motor_speed(-TURNING_SPEED, TURNING_SPEED)
    # time.sleep(TURNING_DURATION)


def remote_control(bot: Rover):
    key = "0"
    while key != "b":
        key = getkey()

        match key:
            case "w":
                bot.set_motor_speed(SPEED, SPEED)
            case "s":
                bot.set_motor_speed(-SPEED, -SPEED)
            case "a":
                turn_left(bot)
            case "d":
                turn_right(bot)
            case "c":
                bot.set_motor_speed(0, 0)
            case "m":
                measure(bot)
                print(bot.measurement)


def measure(bot):
    bot.measurement = MEASUREMENT_DEFAULT_VALUE
    bot.cheat()

    while bot.measurement == MEASUREMENT_DEFAULT_VALUE:
        time.sleep(1)


def generate_terrain(seed: int):
    shape = (200, 200)
    noise = PerlinNoise(octaves=2, seed=seed)

    world = [[noise([i/shape[0], j/shape[1]])
              for j in range(shape[0])] for i in range(shape[1])]

    lin_x = np.linspace(0, 1, shape[0], endpoint=False)
    lin_y = np.linspace(0, 1, shape[1], endpoint=False)
    x, y = np.meshgrid(lin_x, lin_y)

    return (x, y, world)


def drawColorPlot(x, y, z):
    color_count = 70

    fig = plt.Figure()
    plt.contourf(x, y, z, color_count, cmap="hot")
    plt.colorbar()
    plt.show()


def get_random_points_in_field(point_count):
    random_point_array = np.random.randint(
        low=FIELD_BOUNDARY, high=FIELD_WIDTH-FIELD_BOUNDARY + 1, size=(point_count, 1))
    random_point_array = np.hstack(
        (random_point_array, np.random.randint(low=FIELD_BOUNDARY, high=FIELD_HEIGHT-FIELD_BOUNDARY + 1, size=(point_count, 1))))

    return random_point_array


def explore_points_and_get_list_with_concentration(bot: Rover, point_list):
    result_list = []
    for point in point_list:
        bot.move_to(point)
        measure(bot)
        result_list.append(
            [bot.position['x'], bot.position['y'], bot.measurement])

    return result_list


def simplex(p1, p2, p3):
    point_list = [p1, p2, p3]

    print(point_list)

    # sortieren der Punkte
    sorted_list = sorted(point_list, key=lambda tupel: tupel[2], reverse=True)
    print(sorted_list)

    # Mittelpunkt der zwei besten Werte
    m = (((sorted_list[0][0] + sorted_list[1][0])/2),
         ((sorted_list[0][1] + sorted_list[1][1])/2),)
    print("Mittelpunkt: ", m)


bot = Rover()
bot.beep()

# remote_control(bot)
point_list = get_random_points_in_field(5)
print("Generated Points:" + point_list)

explored_points_list = explore_points_and_get_list_with_concentration(
    bot, point_list)
print("Explored Points:" + explored_points_list)

simplex(explored_points_list[0],
        explored_points_list[1], explored_points_list[2])

bot.set_motor_speed(0, 0)
time.sleep(1)
bot.set_leds(0, 0, 0)

print(bot.position)
print(bot.acceleration)
print(bot.status)
