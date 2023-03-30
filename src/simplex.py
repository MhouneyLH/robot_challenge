import numpy as np
import random
import map_generation as mg
import rover_simulation_base as rsb
import utils


def simplex(bot: rsb.SimulatedRover, map_points: list[mg.MapPoint]) -> None:
    ALPHA = 1.3
    BETA = 0.75
    GAMMA = 1.25
    DELTA = 0.5

    # define starting points
    starting_point_1: mg.MapPoint = mg.MapPoint(
        point=[mg.FIELD_WIDTH / 2, mg.FIELD_HEIGHT / 2],)
    starting_point_1.concentration = utils.measure_concentration_at_point_and_check_highest_concentration(
        bot, map_points, starting_point_1.point)
    if bot.is_finished():
        return
    starting_point_2: mg.MapPoint = mg.MapPoint(
        point=[starting_point_1.point[0] + 100, starting_point_1.point[1]],)
    starting_point_2.concentration = utils.measure_concentration_at_point_and_check_highest_concentration(
        bot, map_points, starting_point_2.point)
    if bot.is_finished():
        return
    starting_point_3: mg.MapPoint = mg.MapPoint(
        point=[starting_point_1.point[0] + 50, starting_point_1.point[1] + 40],)
    starting_point_3.concentration = utils.measure_concentration_at_point_and_check_highest_concentration(
        bot, map_points, starting_point_3.point)
    if bot.is_finished():
        return

    triangle_points: list[mg.MapPoint] = [
        starting_point_1, starting_point_2, starting_point_3,]
    print("triangle_points")
    mg.print_map_points(triangle_points)

    for i in range(utils.MAXIMUM_LOOP_COUNT):
        print("Highest Concentration so far:",
              bot.highest_concentration_map_point.concentration, bot.highest_concentration_map_point.point)

        sorted_list: list[mg.MapPoint] = utils.get_ascended_sorted_list(
            triangle_points)

        best_point: mg.MapPoint = sorted_list[0]
        second_best_point: mg.MapPoint = sorted_list[1]
        worst_point: mg.MapPoint = sorted_list[2]

        # MIDDLE-POINT
        middle_point_of_2_best_points: mg.MapPoint = mg.MapPoint(
            point=np.divide(best_point.point + second_best_point.point, 2))

        # REFLECTION-POINT
        reflection_point: mg.MapPoint = mg.MapPoint(
            point=middle_point_of_2_best_points.point + np.multiply(middle_point_of_2_best_points.point - worst_point.point, ALPHA))
        reflection_point.concentration = utils.measure_concentration_at_point_and_check_highest_concentration(
            bot, map_points, reflection_point.point)
        if bot.is_finished():
            return

        if utils.has_higher_concentration(reflection_point, best_point):
            # EXPANDING-POINT
            expand_point: mg.MapPoint = mg.MapPoint(
                point=reflection_point.point + np.multiply(reflection_point.point - middle_point_of_2_best_points.point, GAMMA))
            expand_point.concentration = utils.measure_concentration_at_point_and_check_highest_concentration(
                bot, map_points, expand_point.point)
            if bot.is_finished():
                return

            # exchange worst-point
            if utils.has_higher_concentration(expand_point, reflection_point):
                worst_point.update(expand_point)
                continue

            worst_point.update(reflection_point)
            continue
        # exchange worst-point
        elif utils.has_higher_concentration(reflection_point, second_best_point):
            worst_point.update(reflection_point)
            continue

        # CONTRACTION-POINT
        h: mg.MapPoint = reflection_point if utils.has_higher_concentration(
            reflection_point, worst_point) else worst_point

        contracting_point: mg.MapPoint = mg.MapPoint(
            point=h.point + np.multiply(middle_point_of_2_best_points.point - h.point, BETA))
        contracting_point.concentration = utils.measure_concentration_at_point_and_check_highest_concentration(
            bot, map_points, contracting_point.point)
        if bot.is_finished():
            return

        # exchange worst-point
        if utils.has_higher_concentration(contracting_point, worst_point):
            worst_point.update(contracting_point)
            continue


bot: rsb.SimulatedRover = rsb.SimulatedRover()

seed: float = random.uniform(0, 10000)
generated_map: np.array = mg.generate_map(seed)
map_points: list[mg.MapPoint] = mg.convert_to_map_points(generated_map)

simplex(bot, map_points)
mg.create_map_plot(generated_map, bot.explored_points)
utils.stop(bot)
