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

    return bot.measurement


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
        bot.move_to(point, threshold=DEFAULT_THRESHOLD)
        measure(bot)
        result_list.append(
            [bot.position['x'], bot.position['y'], bot.measurement])

    return result_list


def measure_and_update_values(bot: Rover):
    time.sleep(1)
    measure(bot)

    result = [bot.position["x"], bot.position["y"], bot.measurement]
    return result


highest_point = [-1, -1, -1]


def update_highest_point(new_point):
    global highest_point
    if new_point[2] > highest_point[2]:
        highest_point = new_point


def simplex(bot: Rover, p1):
    global highest_point

    p2 = [p1[0] + 300, p1[1], -1]
    p3 = [p1[0] + 150, p1[1] + 150, -1]

    bot.move_to(p2, threshold=DEFAULT_THRESHOLD)
    p2 = measure_and_update_values(bot)
    bot.move_to(p3, threshold=DEFAULT_THRESHOLD)
    p3 = measure_and_update_values(bot)

def get_point_with_highest_concentration(points_list):
    result = [-1, -1, -1]
    for point in points_list:
        concentration = point[2]
        if (concentration <= result[2]):
            continue

        result = point

    return result


def simplex(p1, p2, p3):
    point_list = [p1, p2, p3]
    print("point_list", point_list)

    while highest_point[2] < 250:
        print("Highest Point", str(highest_point))
        # sortieren der Punkte
        sorted_list = sorted(
            point_list, key=lambda tupel: tupel[2], reverse=True)
        print("sorted_list ", sorted_list)

        update_highest_point(sorted_list[0])

        # Mittelpunkt der zwei besten Werte
        best_point = sorted_list[0]
        second_best = sorted_list[1]
        worst_point = sorted_list[2]
        middle_point_of_2_best_points = [(best_point[0] + second_best[0]) / 2,
                                         (best_point[1] + second_best[1]) / 2,]
        print("middle_point_of_2_best_points ", middle_point_of_2_best_points)

        # reflexion
        alpha = 1.25
        reflection_point = [middle_point_of_2_best_points[0] + alpha *
                            (middle_point_of_2_best_points[0] -
                             worst_point[0]),
                            middle_point_of_2_best_points[1] + alpha *
                            (middle_point_of_2_best_points[1] -
                             worst_point[1]), -1
                            ]
        bot.move_to(reflection_point, threshold=DEFAULT_THRESHOLD)
        reflection_point = measure_and_update_values(bot)
        print("reflection_point", reflection_point)
        update_highest_point(reflection_point)

        if reflection_point[2] > best_point[2]:
            gamma = 1.25
            expand_point = [reflection_point[0] + gamma * (reflection_point[0] - middle_point_of_2_best_points[0]),
                            reflection_point[1] + gamma *
                            (reflection_point[1] -
                             middle_point_of_2_best_points[1]),
                            -1]
            bot.move_to(expand_point, threshold=DEFAULT_THRESHOLD)
            expand_point = measure_and_update_values(bot)
            print("expand_point", expand_point)
            update_highest_point(expand_point)

            if expand_point[2] > reflection_point[2]:
                worst_point = expand_point
            else:
                worst_point = reflection_point
            continue
        elif reflection_point[2] > second_best[2]:
            worst_point = reflection_point
            continue

        beta = 0.75
        h = reflection_point if reflection_point[2] > worst_point[2] else worst_point
        contracting_point = [h[0] + beta * (middle_point_of_2_best_points[0] - h[0]),
                             h[1] + beta * (middle_point_of_2_best_points[1] - h[1]), -1]
        bot.move_to(contracting_point, threshold=DEFAULT_THRESHOLD)
        contracting_point = measure_and_update_values(bot)
        print("contracting_point", contracting_point)
        update_highest_point(contracting_point)

        if contracting_point[2] > worst_point[2]:
            worst_point = contracting_point
            continue

        # for item in sorted_list:
        #     delta = 0.5
        #     item += delta * ( best_point - item)


bot = Rover()
bot.beep()

# remote_control(bot)
point_list = get_random_points_in_field(2)
print("Generated Points:" + str(point_list))

explored_points_list = explore_points_and_get_list_with_concentration(
    bot, point_list)
print("Explored Points:" + str(explored_points_list))

explored_point = (1105, 452, 101)
max_point = get_point_with_highest_concentration(explored_points_list)
print(max_point)
# simplex(max_point)

bot.move_to(explored_point)
time.sleep(1)
simplex(bot, explored_point)


bot.set_motor_speed(0, 0)
time.sleep(1)
bot.set_leds(0, 0, 0)

# print(bot.position)
# print(bot.acceleration)
# print(bot.status)
