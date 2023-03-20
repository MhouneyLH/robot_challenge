"""
First steps with the rover

Learn, how the LEDs, motors, servos, and the horn are controlled.
Also, learn, how to read out important values like the position of the rover, or its current acceleration.
"""

from rover_base import Rover
import time

bot = Rover()

print("Hello World!")

bot.beep()

bot.set_leds(20,20,20)
time.sleep(1)
bot.set_leds(130,130,130)

bot.set_motor_speed(30,-30)
time.sleep(2)
bot.set_motor_speed(-30,30)
time.sleep(2)
bot.set_motor_speed(0,0) # don't forget to turn off the motors, when you're done!
time.sleep(1)

bot.set_servo1_pos(30)
bot.set_servo1_pos(70)

print(bot.position)
print(bot.acceleration)
print(bot.status)