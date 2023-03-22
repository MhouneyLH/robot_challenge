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
POINT_LIST = [
    [100, 100],
    [100, 900],
    [1000, 500],
    [1700, 800],
    [1700, 100],
]


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


def explore_points(bot: Rover, point_list):
    for point in point_list:
        bot.move_to(point)
        measure(bot)
        print(bot.measurement)


bot = Rover()
bot.beep()

# x, y, z = generate_terrain(0.5)
# drawColorPlot(x, y, z)

# remote_control(bot)
point_list = get_random_points_in_field(5)
print(point_list)
explore_points(bot, point_list)

bot.set_motor_speed(0, 0)
time.sleep(1)
bot.set_leds(0, 0, 0)

print(bot.position)
print(bot.acceleration)
print(bot.status)
