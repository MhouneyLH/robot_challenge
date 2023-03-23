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
DEFAULT_THRESHOLD = 50
FINISH_VALUE = 235


highest_point = [-1, -1, MEASUREMENT_DEFAULT_VALUE]

######################################
# REMOTE_CONTROL
######################################


def turn_right(bot: Rover):
    bot.set_motor_speed(TURNING_SPEED, -TURNING_SPEED)


def turn_left(bot: Rover):
    bot.set_motor_speed(-TURNING_SPEED, TURNING_SPEED)


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

######################################
# HELPER_FUNCTIONS
######################################


def measure(bot):
    bot.measurement = MEASUREMENT_DEFAULT_VALUE
    bot.cheat()

    while bot.measurement == MEASUREMENT_DEFAULT_VALUE:
        time.sleep(1)

    return bot.measurement


def get_random_points_in_field(point_count):
    random_point_array = np.random.randint(
        low=FIELD_BOUNDARY, high=FIELD_WIDTH-FIELD_BOUNDARY + 1, size=(point_count, 1))
    random_point_array = np.hstack(
        (random_point_array, np.random.randint(low=FIELD_BOUNDARY, high=FIELD_HEIGHT-FIELD_BOUNDARY + 1, size=(point_count, 1))))

    return random_point_array


def explore_points_and_get_list_with_concentration(bot: Rover, point_list):
    result_list = []
    for point in point_list:
        bot.move_to(point, threshold=DEFAULT_THRESHOLD)
        measure(bot)
        result_list.append(
            [bot.position['x'], bot.position['y'], bot.measurement])

    return result_list


def isNewHighestPoint(point):
    global highest_point
    return has_higher_concentration(point, highest_point)


def get_point_with_highest_concentration(points_list):
    result = [-1, -1, MEASUREMENT_DEFAULT_VALUE]
    for point in points_list:
        concentration = point[2]
        if (concentration <= result[2]):
            continue

        result = point

    return result


def stop(bot: Rover):
    bot.set_motor_speed(0, 0)
    time.sleep(1)
    bot.set_leds(0, 0, 0)

    print(bot.position)
    print(bot.acceleration)
    print(bot.status)

    bot.beep()

    bot.disconnect()


def get_real_values(bot: Rover, point):
    bot.move_to(point, threshold=DEFAULT_THRESHOLD)
    time.sleep(1)
    measure(bot)

    result = [bot.position["x"], bot.position["y"], bot.measurement]
    if (not isNewHighestPoint(result)):
        return result

    highest_point = result
    if has_higher_concentration(highest_point, FINISH_VALUE):
        stop(bot)
        exit()


def get_ascended_sorted_list(points_list):
    return sorted(points_list, key=lambda tupel: tupel[2], reverse=True)


def get_middle_point(p1, p2):
    result = [(p1[0] + p2[0]) / 2, (p1[1] + p2[1]) /
              2, MEASUREMENT_DEFAULT_VALUE]
    return result


def calculate_special_point(p1, p2, constant):
    result = [p1[0] + constant * (p1[0] - p2[0]),
              p1[1] + constant * (p1[1] - p2[1]), MEASUREMENT_DEFAULT_VALUE]
    return result


def has_higher_concentration(p1, p2):
    result = p1[2] > p2[2]
    return result


def calculate_contraction_point(p1, p2, constant):
    result = [p1[0] + constant * (p2[0] - p1[0]),
              p1[1] + constant * (p2[1] - p1[1]), MEASUREMENT_DEFAULT_VALUE]
    return result


def simplex(bot: Rover, p1):
    global highest_point

    ALPHA = 1.3
    BETA = 0.75
    GAMMA = 1.25
    DELTA = 0.5

    exact_p2 = [p1[0] + 300, p1[1], MEASUREMENT_DEFAULT_VALUE]
    exact_p3 = [p1[0] + 150, p1[1] + 150, MEASUREMENT_DEFAULT_VALUE]

    p2 = get_real_values(bot, exact_p2)
    p3 = get_real_values(bot, exact_p3)

    point_list = [p1, p2, p3]
    print("point_list", point_list)

    while True:
        print("Highest Point", str(highest_point))

        sorted_list = get_ascended_sorted_list(point_list)
        print("sorted_list ", sorted_list)

        best_point = sorted_list[0]
        second_best = sorted_list[1]
        worst_point = sorted_list[2]

        middle_point_of_2_best_points = get_middle_point(
            best_point, second_best)
        print("middle_point_of_2_best_points ", middle_point_of_2_best_points)

        exact_reflection_point = calculate_special_point(
            middle_point_of_2_best_points, worst_point, ALPHA)
        reflection_point = get_real_values(bot, exact_reflection_point)
        print("reflection_point", reflection_point)

        if has_higher_concentration(reflection_point, best_point):
            exact_expand_point = calculate_special_point(
                reflection_point, middle_point_of_2_best_points, GAMMA)
            expand_point = get_real_values(bot, exact_expand_point)
            print("expand_point", expand_point)

            if has_higher_concentration(expand_point, reflection_point):
                worst_point = expand_point
                continue

            worst_point = reflection_point
            continue
        elif has_higher_concentration(reflection_point, second_best):
            worst_point = reflection_point
            continue

        h = reflection_point if has_higher_concentration(
            reflection_point, worst_point) else worst_point
        exact_contracting_point = calculate_contraction_point(
            h, middle_point_of_2_best_points, BETA)
        contracting_point = get_real_values(bot, exact_contracting_point)
        print("contracting_point", contracting_point)

        if has_higher_concentration(contracting_point, worst_point):
            worst_point = contracting_point
            continue

        # for item in sorted_list:
        #     DELTA = 0.5
        #     item += DELTA * ( best_point - item)


######################################
# MAIN_SCRIPT
######################################
bot = Rover()
bot.beep()

bot.set_leds(0, 0, 30)

# remote_control(bot)
# point_list = get_random_points_in_field(2)
# print("Generated Points:" + str(point_list))

# explored_points_list = explore_points_and_get_list_with_concentration(
#     bot, point_list)
# print("Explored Points:" + str(explored_points_list))

# explored_point = [1105, 452, 101]
explored_point = [967, 493, 84]
# max_point = get_point_with_highest_concentration(explored_points_list)
# print(max_point)
time.sleep(1)
simplex(bot, explored_point)

bot.set_leds(0, 0, 0)
stop(bot)
