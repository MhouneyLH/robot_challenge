from rover_base import Rover
import time

bot = Rover()
bot.beep()

bot.remote_control()

bot.set_motor_speed(0, 0)
time.sleep(1)

print(bot.position)
print(bot.acceleration)
print(bot.status)
