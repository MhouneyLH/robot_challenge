import map_generation as mg
import rover_simulation_base as rsb
import numpy as np

MAXIMUM_LOOP_COUNT: int = 10


def stop(bot: rsb.SimulatedRover) -> None:
    print("Highest found point")
    mg.print_map_points([bot.highest_concentration_map_point])

    bot.stop()
    exit(0)


def has_higher_concentration(point_1: mg.MapPoint, point_2: mg.MapPoint) -> bool:
    return point_1.concentration > point_2.concentration


def get_ascended_sorted_list(triangle_points: list[mg.MapPoint]) -> list[mg.MapPoint]:
    return sorted(triangle_points, key=lambda attribute: attribute.concentration, reverse=True)


def get_in_bound_point(point: np.array) -> np.array:
    x = point[0]
    y = point[1]

    if (x < 0):
        x = 0
    elif (x > mg.FIELD_WIDTH):
        x = mg.FIELD_WIDTH
    if (y < 0):
        y = 0
    elif (y > mg.FIELD_HEIGHT):
        y = mg.FIELD_HEIGHT

    result = [x, y]
    return result


def measure_concentration_at_point_and_check_highest_concentration(bot: rsb.SimulatedRover, map_points: list[mg.MapPoint], point: np.array) -> int:
    in_bound_point: np.array = get_in_bound_point(point)
    bot.move_to(in_bound_point)
    bot.current_concentration = bot.get_concentration_of_current_position(
        map_points)

    if bot.current_concentration > bot.highest_concentration_map_point.concentration:
        new_point: mg.MapPoint = mg.MapPoint(
            point=bot.position, concentration=bot.current_concentration)
        bot.highest_concentration_map_point.update(new_point)

    return bot.current_concentration
