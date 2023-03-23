from rover_base import Rover
from getkey import getkey
import time
import numpy as np

SPEED = 70
TURNING_DURATION = 3
TURNING_SPEED = 70
MEASUREMENT_DEFAULT_VALUE = -1
FIELD_WIDTH = 2000
FIELD_HEIGHT = 1000
FIELD_BOUNDARY = 200
DEFAULT_THRESHOLD = 50
FINISH_VALUE = 240
MAXIMUM_LOOP_COUNT = 5
SERVO_UP = 180
SERVO_DOWN = 0


highest_point = [-1, -1, MEASUREMENT_DEFAULT_VALUE]
GLOBAL_POINTS = [
    [FIELD_WIDTH / 2, FIELD_HEIGHT / 2, MEASUREMENT_DEFAULT_VALUE],
    [FIELD_BOUNDARY, FIELD_HEIGHT - FIELD_BOUNDARY, MEASUREMENT_DEFAULT_VALUE],
    [FIELD_WIDTH - FIELD_BOUNDARY, FIELD_HEIGHT -
        FIELD_BOUNDARY, MEASUREMENT_DEFAULT_VALUE],
    [FIELD_BOUNDARY, FIELD_BOUNDARY, MEASUREMENT_DEFAULT_VALUE],
    [FIELD_WIDTH - FIELD_BOUNDARY, FIELD_BOUNDARY, MEASUREMENT_DEFAULT_VALUE],
]
all_point_list = []

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
                print(measure(bot))

######################################
# HELPER_FUNCTIONS
######################################


# def measure(bot):
#    bot.measurement = MEASUREMENT_DEFAULT_VALUE
#    bot.cheat()
#
#    i = 0
#    while bot.measurement == MEASUREMENT_DEFAULT_VALUE:
#        i += 1
#        if i % 5 == 0:
#            bot.cheat()
#        time.sleep(1)
#
#    return bot.measurement


def measure(bot):
    bot.measurement = MEASUREMENT_DEFAULT_VALUE
    bot.set_servo1_pos(SERVO_DOWN)
    i = 0
    while bot.measurement == MEASUREMENT_DEFAULT_VALUE:
        i += 1
        if i % 5 == 0:
            bot.set_servo1_pos(SERVO_UP)
            bot.set_servo1_pos(SERVO_DOWN)
        time.sleep(1)
    bot.set_servo1_pos(SERVO_UP)
    return bot.measurement


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


def start(bot: Rover):
    bot.set_leds(0, 0, 30)
    bot.set_servo1_pos(SERVO_UP)


def stop(bot: Rover):
    global highest_point

    bot.set_motor_speed(0, 0)
    time.sleep(1)

    bot.beep()
    bot.set_leds(0, 0, 0)
    bot.set_servo1_pos(SERVO_UP)

    print("Highest found point", highest_point)
    print(bot.position)
    print(bot.acceleration)
    print(bot.status)

    bot.disconnect()


def get_boundary_checked_point(point):
    x = point[0]
    y = point[1]

    if (x < FIELD_BOUNDARY):
        x = FIELD_BOUNDARY
    elif (x > FIELD_WIDTH - FIELD_BOUNDARY):
        x = FIELD_WIDTH - FIELD_BOUNDARY
    if (y < FIELD_BOUNDARY):
        y = FIELD_BOUNDARY
    elif (y > FIELD_HEIGHT - FIELD_BOUNDARY):
        y = FIELD_HEIGHT - FIELD_BOUNDARY

    result = [x, y]
    return result


def point_is_already_in_database(point):
    point_x = point[0]
    point_y = point[1]

    threshold = DEFAULT_THRESHOLD / 2

    for item in all_point_list:
        item_x = item[0]
        item_y = item[1]
        # ähnlicher Punkt kann gefunden werden
        if (point_x >= item_x - threshold and point_x <= item_x + threshold) and \
                (point_y >= item_y - threshold and point_y <= item_y + threshold):
            return True, item

    return False, point


def get_real_values(bot: Rover, point):
    global all_point_list
    global highest_point

    checked_point = get_boundary_checked_point(point)
    print("checked_point", checked_point)

    test, test1 = point_is_already_in_database(checked_point)
    # if (test):
    if (False):
        print("Jetzt passierts----------------------")
        result = test1
    else:
        bot.move_to(checked_point, speed=SPEED, threshold=DEFAULT_THRESHOLD)
        time.sleep(1)
        measure(bot)

        result = [bot.position["x"], bot.position["y"], bot.measurement]
        all_point_list.append(result)

    if (isNewHighestPoint(result)):
        highest_point = result

        if has_higher_concentration(highest_point, [-1, -1, FINISH_VALUE]):
            stop(bot)
            exit()

    return result


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


def calculate_special_point2(p1, p2, constant):
    result = [p1[0] + constant * (p2[0] - p1[0]),
              p1[1] + constant * (p2[1] - p1[1]), MEASUREMENT_DEFAULT_VALUE]
    return result


temp_list = []


def simplex(bot: Rover, p1):
    global highest_point

    ALPHA = 1.5
    BETA = 0.5
    GAMMA = 1.25
    DELTA = 0.5

    exact_p2 = [p1[0] + 300, p1[1], MEASUREMENT_DEFAULT_VALUE]
    exact_p3 = [p1[0] + 150, p1[1] + 150, MEASUREMENT_DEFAULT_VALUE]

    p2 = get_real_values(bot, exact_p2)
    p3 = get_real_values(bot, exact_p3)

    current_list = [p1, p2, p3]
    print("current_list", current_list)

    test_loop_count = MAXIMUM_LOOP_COUNT
    for i in range(0, MAXIMUM_LOOP_COUNT):
        if (highest_point >= FINISH_VALUE - 20):
            test_loop_count = MAXIMUM_LOOP_COUNT * 2
        print("Highest Point", str(highest_point))

        sorted_list = get_ascended_sorted_list(current_list)
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
                # current_list = [best_point, second_best, worst_point]
                continue

            worst_point = reflection_point
            # current_list = [best_point, second_best, worst_point]
            continue
        elif has_higher_concentration(reflection_point, second_best):
            worst_point = reflection_point
            # current_list = [best_point, second_best, worst_point]
            continue

        h = reflection_point if has_higher_concentration(
            reflection_point, worst_point) else worst_point
        exact_contracting_point = calculate_special_point2(
            h, middle_point_of_2_best_points, BETA)
        contracting_point = get_real_values(bot, exact_contracting_point)
        print("contracting_point", contracting_point)

        if has_higher_concentration(contracting_point, worst_point):
            worst_point = contracting_point
            # current_list = [best_point, second_best, worst_point]
            continue

        # print(current_list)
        # for j in range(0, len(current_list)):
        #     current_list[j] = calculate_special_point2(
        #         current_list[j], best_point, DELTA)
        # print(current_list)


######################################
# MAIN_SCRIPT
######################################
bot = Rover()
bot.beep()

# start(bot)
bot.set_motor_speed(40, 40)
time.sleep(1)
# remote_control(bot)

# for point in GLOBAL_POINTS:
#     simplex(bot, point)

# bot.move_to(highest_point, speed=SPEED, threshold=DEFAULT_THRESHOLD)
stop(bot)

{'bat': 2805, 'FW': 0.55}
