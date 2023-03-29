from matplotlib.animation import FuncAnimation
import numpy as np
import matplotlib.pyplot as plt
from perlin_noise import PerlinNoise
import random

FIELD_WIDTH: int = 500
FIELD_HEIGHT: int = 300
DEFAULT_STARTING_POSITION: np.array = [0, 0]
DEFAULT_CONCENTRATION: int = -1
DEFAULT_SPEED: int = 10
FINISH_VALUE: int = 200
WINDOW_WIDTH_IN_INCHES: int = 20
WINDOW_HEIHGT_IN_INCHES: int = 10
MAXIMUM_LOOP_COUNT: int = 10


class MapPoint:
    def __init__(self, point: np.array, concentration: int = DEFAULT_CONCENTRATION):
        self.point: np.array = np.array(point).astype(int)
        self.concentration: int = concentration

    def update(self, map_point) -> None:
        self.point = map_point.point
        self.concentration = map_point.concentration


class SimulatedRover:
    def __init__(self, starting_position: np.array = DEFAULT_STARTING_POSITION, current_concentration: int = DEFAULT_CONCENTRATION, speed: int = DEFAULT_SPEED, explored_points: np.array = [], highest_concentration: int = DEFAULT_CONCENTRATION):
        self.position: np.array = starting_position
        self.current_concentration: int = current_concentration
        self.speed: int = speed
        self.explored_points: np.array = explored_points
        self.highest_concentration: int = highest_concentration

    def stop(self) -> None:
        print("Highest found point", self.highest_concentration)
        print(self.position)

        self.position = DEFAULT_STARTING_POSITION
        self.current_concentration = DEFAULT_CONCENTRATION
        self.speed = DEFAULT_SPEED
        self.explored_points = []
        self.highest_concentration = DEFAULT_CONCENTRATION

    def get_concentration_at_point(self, map_points: list[MapPoint], target_point: np.array) -> float:
        for item in map_points:
            if np.array_equal(item.point, target_point):
                return item.concentration
        return DEFAULT_CONCENTRATION

    def get_concentration_of_current_position(self, map_points: list[MapPoint]) -> float:
        result = self.get_concentration_at_point(map_points, self.position)
        self.current_concentration = result
        return result

    def move_to(self, point: np.array):
        self.position = point
        self.explored_points.append(point)


def generate_map(seed: int) -> np.array:
    print("Using seed", seed)
    noise = PerlinNoise(octaves=1, seed=seed)
    noise_map = np.zeros((FIELD_HEIGHT, FIELD_WIDTH))

    for y in range(FIELD_HEIGHT):
        for x in range(FIELD_WIDTH):
            noise_map[y][x] = np.abs(
                int(800 * noise([x / FIELD_WIDTH, y / FIELD_HEIGHT])))

    return noise_map


def stop(bot: SimulatedRover) -> None:
    print("Highest found point", bot.highest_concentration)
    print(bot.position)
    create_map_plot(generated_map, bot.explored_points)
    bot.stop()

    exit(0)


def create_map_plot(map: np.array, explored_points: np.array):
    figure = plt.figure(
        figsize=(WINDOW_WIDTH_IN_INCHES, WINDOW_HEIHGT_IN_INCHES))
    ax = figure.add_subplot(111)

    ax.imshow(map, cmap='hot', origin='lower', extent=[
              0, FIELD_WIDTH, 0, FIELD_HEIGHT])
    ax.set_title('Generated Map')

    ax.plot(np.array(explored_points)[:, 0],
            np.array(explored_points)[:, 1], marker='o', linestyle='-')

    plt.show()


def convert_to_map_points(map: np.array) -> list[MapPoint]:
    point_list: list[MapPoint] = []
    for x in range(FIELD_WIDTH):
        for y in range(FIELD_HEIGHT):
            point: np.array = [x, y]
            point_list.append(MapPoint(point=point, concentration=map[y][x]))

    return point_list


def print_map_points(map_points: list[MapPoint]) -> None:
    for point in map_points:
        print(point.point, point.concentration)


def has_higher_concentration(point_1: MapPoint, point_2: MapPoint) -> bool:
    return point_1.concentration > point_2.concentration


def get_ascended_sorted_list(triangle_points: list[MapPoint]) -> list[MapPoint]:
    return sorted(triangle_points, key=lambda attribute: attribute.concentration, reverse=True)


def get_in_bound_point(point: np.array) -> np.array:
    x = point[0]
    y = point[1]

    if (x < 0):
        x = 0
    elif (x > FIELD_WIDTH):
        x = FIELD_WIDTH
    if (y < 0):
        y = 0
    elif (y > FIELD_HEIGHT):
        y = FIELD_HEIGHT

    result = [x, y]
    return result


def measure_concentration_at_point_and_check_highest_concencration(bot: SimulatedRover, map_points: list[MapPoint], point: np.array) -> int:
    in_bound_point = get_in_bound_point(point)
    bot.move_to(in_bound_point)
    bot.current_concentration = bot.get_concentration_of_current_position(
        map_points)

    if bot.current_concentration > bot.highest_concentration:
        bot.highest_concentration = bot.current_concentration

        if bot.highest_concentration > FINISH_VALUE:
            stop(bot)
    return bot.current_concentration


def simplex(bot: SimulatedRover, map_points: list[MapPoint]) -> None:
    ALPHA = 1.3
    BETA = 0.75
    GAMMA = 1.25
    DELTA = 0.5

    # define starting points
    starting_point_1: MapPoint = MapPoint(
        point=[FIELD_WIDTH / 2, FIELD_HEIGHT / 2],)
    starting_point_1.concentration = measure_concentration_at_point_and_check_highest_concencration(
        bot, map_points, starting_point_1.point)
    starting_point_2: MapPoint = MapPoint(
        point=[starting_point_1.point[0] + 100, starting_point_1.point[1]],)
    starting_point_2.concentration = measure_concentration_at_point_and_check_highest_concencration(
        bot, map_points, starting_point_2.point)
    starting_point_3: MapPoint = MapPoint(
        point=[starting_point_1.point[0] + 50, starting_point_1.point[1] + 40],)
    starting_point_3.concentration = measure_concentration_at_point_and_check_highest_concencration(
        bot, map_points, starting_point_3.point)

    triangle_points: list[MapPoint] = [
        starting_point_1, starting_point_2, starting_point_3,]
    print("triangle_points")
    print_map_points(triangle_points)

    for i in range(MAXIMUM_LOOP_COUNT):
        print("Highest Concentration so far:",
              bot.highest_concentration, bot.position)

        sorted_list: list[MapPoint] = get_ascended_sorted_list(triangle_points)
        # print("sorted_list")
        # print_map_points(sorted_list)

        best_point: MapPoint = sorted_list[0]
        second_best_point: MapPoint = sorted_list[1]
        worst_point: MapPoint = sorted_list[2]

        # MIDDLE-POINT
        middle_point_of_2_best_points: MapPoint = MapPoint(
            point=np.divide(best_point.point + second_best_point.point, 2))

        # REFLECTION-POINT
        reflection_point: MapPoint = MapPoint(
            point=middle_point_of_2_best_points.point + np.multiply(middle_point_of_2_best_points.point - worst_point.point, ALPHA))
        reflection_point.concentration = measure_concentration_at_point_and_check_highest_concencration(
            bot, map_points, reflection_point.point)

        if has_higher_concentration(reflection_point, best_point):
            # EXPANDING-POINT
            expand_point: MapPoint = MapPoint(
                point=reflection_point.point + np.multiply(reflection_point.point - middle_point_of_2_best_points.point, GAMMA))
            expand_point.concentration = measure_concentration_at_point_and_check_highest_concencration(
                bot, map_points, expand_point.point)

            # exchange worst-point
            if has_higher_concentration(expand_point, reflection_point):
                worst_point.update(expand_point)
                continue

            worst_point.update(reflection_point)
            continue
        # exchange worst-point
        elif has_higher_concentration(reflection_point, second_best_point):
            worst_point.update(reflection_point)
            continue

        # CONTRACTION-POINT
        h: MapPoint = reflection_point if has_higher_concentration(
            reflection_point, worst_point) else worst_point

        contracting_point: MapPoint = MapPoint(
            point=h.point + np.multiply(middle_point_of_2_best_points.point - h.point, BETA))
        contracting_point.concentration = measure_concentration_at_point_and_check_highest_concencration(
            bot, map_points, contracting_point.point)

        # exchange worst-point
        if has_higher_concentration(contracting_point, worst_point):
            worst_point.update(contracting_point)
            continue


bot: SimulatedRover = SimulatedRover()

seed: float = random.uniform(0, 10000)
generated_map: np.array = generate_map(seed)
map_points: list[MapPoint] = convert_to_map_points(generated_map)
# print_map_points(map_points)

simplex(bot, map_points)
stop(bot)
