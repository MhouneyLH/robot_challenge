from rover_base import Rover
from getkey import getkey, keys
import time

SPEED = 70
TURNING_DURATION = 3
TURNING_SPEED = 70
MEASUREMENT_DEFAULT_VALUE = -1


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


bot = Rover()
bot.beep()

remote_control(bot)

bot.set_motor_speed(0, 0)

print(bot.position)
print(bot.acceleration)
print(bot.status)
