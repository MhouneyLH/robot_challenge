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
POINT_LIST = [
    (100, 100),
    [100, 900],
    [1000, 500],
    [1900, 900],
    [1900, 100],
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


bot = Rover()
bot.beep()

# x, y, z = generate_terrain(0.5)
# drawColorPlot(x, y, z)

remote_control(bot)
# for i in range(0, len(POINT_LIST)):
#     bot.move_to(POINT_LIST[i])
#     time.sleep(0.5)
#     measure(bot)
#     print(bot.measurement)

bot.set_motor_speed(0, 0)
time.sleep(1)
bot.set_leds(0, 0, 0)

print(bot.position)
print(bot.acceleration)
print(bot.status)
