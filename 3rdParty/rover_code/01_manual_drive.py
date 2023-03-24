from rover_base import Rover
from getkey import getkey
import time
import numpy as np

SPEED = 70
TURNING_DURATION = 3
TURNING_SPEED = 70
MEASUREMENT_DEFAULT_VALUE = -1
FIELD_WIDTH = 1900
FIELD_HEIGHT = 1000
FIELD_BOUNDARY = 200
DEFAULT_THRESHOLD = 50
FINISH_VALUE = 239
MAXIMUM_LOOP_COUNT = 5
SERVO_UP = 145
SERVO_DOWN = 0


highest_point = [-1, -1, MEASUREMENT_DEFAULT_VALUE]
# TARGET_POINTS = [
#     [FIELD_WIDTH / 2, FIELD_HEIGHT / 2, MEASUREMENT_DEFAULT_VALUE],
#     [FIELD_BOUNDARY, FIELD_HEIGHT - FIELD_BOUNDARY, MEASUREMENT_DEFAULT_VALUE],
#     [FIELD_WIDTH - FIELD_BOUNDARY, FIELD_HEIGHT -
#         FIELD_BOUNDARY, MEASUREMENT_DEFAULT_VALUE],
#     [FIELD_BOUNDARY, FIELD_BOUNDARY, MEASUREMENT_DEFAULT_VALUE],
#     [FIELD_WIDTH - FIELD_BOUNDARY, FIELD_BOUNDARY, MEASUREMENT_DEFAULT_VALUE],
# ]
TARGET_POINTS = [
    [2 * FIELD_BOUNDARY, FIELD_HEIGHT - 2 *
        FIELD_BOUNDARY, MEASUREMENT_DEFAULT_VALUE],  # left up
    [2 * FIELD_BOUNDARY, 2 * FIELD_BOUNDARY,
        MEASUREMENT_DEFAULT_VALUE],  # left down
    [FIELD_WIDTH - 2 * FIELD_BOUNDARY, FIELD_HEIGHT / \
        2, MEASUREMENT_DEFAULT_VALUE],  # mid right
]

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
#     bot.measurement = MEASUREMENT_DEFAULT_VALUE
#     bot.cheat()

#     i = 0
#     while bot.measurement == MEASUREMENT_DEFAULT_VALUE:
#         i += 1
#         if i % 5 == 0:
#             bot.set_motor_speed(SPEED, SPEED)
#             time.sleep(0.2)
#             bot.set_motor_speed(0, 0)
            # time.sleep(0.5)
#             bot.cheat()
#         time.sleep(1)

#     return bot.measurement


def measure(bot):
    bot.measurement = MEASUREMENT_DEFAULT_VALUE
    bot.set_servo1_pos(SERVO_DOWN)
    i = 0
    while bot.measurement == MEASUREMENT_DEFAULT_VALUE:
        i += 1
        # jeder 5. Wiederholung wird versucht nochmal zu messen
        if i % 5 == 0:
            bot.set_servo1_pos(SERVO_UP)
            bot.set_motor_speed(SPEED, SPEED)
            time.sleep(0.2)
            bot.set_motor_speed(0, 0)
            time.sleep(0.5)
            bot.set_servo1_pos(SERVO_DOWN)
        time.sleep(1)
    bot.set_servo1_pos(SERVO_UP)
    return bot.measurement


def isNewHighestPoint(point):
    global highest_point
    return has_higher_concentration(point, highest_point)


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


def get_real_values(bot: Rover, point):
    global highest_point

    # keep the robo in predefined boundaries
    checked_point = get_boundary_checked_point(point)
    print("checked_point", checked_point)

    bot.move_to(checked_point, speed=SPEED, threshold=DEFAULT_THRESHOLD)
    time.sleep(1)
    measure(bot)

    result = [bot.position["x"], bot.position["y"], bot.measurement]
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


def calculate_point_formula_1(p1, p2, constant):
    result = [p1[0] + constant * (p1[0] - p2[0]),
              p1[1] + constant * (p1[1] - p2[1]), MEASUREMENT_DEFAULT_VALUE]
    return result


def has_higher_concentration(p1, p2):
    result = p1[2] > p2[2]
    return result


def calculate_point_formula_2(p1, p2, constant):
    result = [p1[0] + constant * (p2[0] - p1[0]),
              p1[1] + constant * (p2[1] - p1[1]), MEASUREMENT_DEFAULT_VALUE]
    return result


def simplex(bot: Rover, p1):
    global highest_point

    ALPHA = 1.3
    BETA = 0.75
    GAMMA = 1.25
    DELTA = 0.5

    # define starting points
    exact_p2 = [p1[0] + 300, p1[1], MEASUREMENT_DEFAULT_VALUE]
    exact_p3 = [p1[0] + 150, p1[1] + 150, MEASUREMENT_DEFAULT_VALUE]

    p2 = get_real_values(bot, exact_p2)
    p3 = get_real_values(bot, exact_p3)

    current_list = [p1, p2, p3]
    print("current_list", current_list)

    current_maximum_loop_count = MAXIMUM_LOOP_COUNT
    for i in range(0, current_maximum_loop_count):
        if has_higher_concentration(highest_point, [-1, -1, FINISH_VALUE - 30]):
            current_maximum_loop_count = MAXIMUM_LOOP_COUNT * 2

        print("Highest Point", str(highest_point))

        sorted_list = get_ascended_sorted_list(current_list)
        print("sorted_list ", sorted_list)

        best_point = sorted_list[0]
        second_best = sorted_list[1]
        worst_point = sorted_list[2]

        # MIDDLE-POINT
        middle_point_of_2_best_points = get_middle_point(
            best_point, second_best)
        print("middle_point_of_2_best_points ", middle_point_of_2_best_points)

        # REFLECTION-POINT
        exact_reflection_point = calculate_point_formula_1(
            middle_point_of_2_best_points, worst_point, ALPHA)
        reflection_point = get_real_values(bot, exact_reflection_point)
        print("reflection_point", reflection_point)

        if has_higher_concentration(reflection_point, best_point):
            # EXPANDING-POINT
            exact_expand_point = calculate_point_formula_1(
                reflection_point, middle_point_of_2_best_points, GAMMA)
            expand_point = get_real_values(bot, exact_expand_point)
            print("expand_point", expand_point)

            # exchange worst-point
            if has_higher_concentration(expand_point, reflection_point):
                worst_point = expand_point
                continue

            worst_point = reflection_point
            continue
        # exchange worst-point
        elif has_higher_concentration(reflection_point, second_best):
            worst_point = reflection_point
            continue

        # CONTRACTION-POINT
        h = reflection_point if has_higher_concentration(
            reflection_point, worst_point) else worst_point
        exact_contracting_point = calculate_point_formula_2(
            h, middle_point_of_2_best_points, BETA)
        contracting_point = get_real_values(bot, exact_contracting_point)
        print("contracting_point", contracting_point)

        # exchange worst-point
        if has_higher_concentration(contracting_point, worst_point):
            worst_point = contracting_point
            continue


######################################
# MAIN_SCRIPT
######################################
bot = Rover()
bot.beep()

start(bot)
# remote_control(bot)

for point in TARGET_POINTS:
    simplex(bot, point)

bot.move_to(highest_point, speed=SPEED, threshold=DEFAULT_THRESHOLD)
stop(bot)
