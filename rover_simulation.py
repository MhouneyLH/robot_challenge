import math
from matplotlib.animation import FuncAnimation
import time
import numpy as np
import matplotlib.pyplot as plt
from perlin_noise import PerlinNoise

FIELD_WIDTH = 200
FIELD_HEIGHT = 100
DEFAULT_STARTING_POSITION: np.array = [0, 0]
DEFAULT_CONCENTRATION: int = -1
DEFAULT_SPEED: int = 10


class MapPoint:
    def __init__(self, point: np.array, concentration: float):
        self.point = point
        self.concentration = concentration


class SimulatedRover:
    def __init__(self, starting_position: np.array = DEFAULT_STARTING_POSITION, current_concentration: float = DEFAULT_CONCENTRATION, speed: int = DEFAULT_SPEED):
        self.position = starting_position
        self.current_concentration = current_concentration
        self.speed = speed

    def get_concentration_at_point(self, map_points: list[MapPoint], point: np.array) -> float:
        for point in map_points:
            if point.point == point:
                return point.concentration
        return DEFAULT_CONCENTRATION

    def get_concentration_of_current_position(self, map_points: list[MapPoint]):
        result = self.get_concentration_at_point(self.position)
        return result


def generate_map(seed: int) -> np.array:
    noise = PerlinNoise(octaves=2, seed=seed)
    noise_map = np.zeros((FIELD_HEIGHT, FIELD_WIDTH))

    for y in range(FIELD_HEIGHT):
        for x in range(FIELD_WIDTH):
            noise_map[y][x] = np.abs(
                int(255 * 2.5 * noise([x / FIELD_WIDTH, y / FIELD_HEIGHT])))

    return noise_map


def create_map_plot(map: np.array):
    figure, ax = plt.subplots()
    ax.imshow(map, cmap='hot', origin='lower', extent=[
              0, FIELD_WIDTH, 0, FIELD_HEIGHT])
    ax.set_title('Generated Map')

    for i in range(0, 100):
        ax.plot(i, i, 'x', markersize=2, color='green')
    plt.show()


def convert_to_map_points(map: np.array) -> list[MapPoint]:
    point_list: list[MapPoint] = []
    for x in range(FIELD_WIDTH):
        for y in range(FIELD_HEIGHT):
            point: np.array = [x, y]
            point_list.append(MapPoint(point=point, concentration=map[y][x]))

    return point_list


def print_map_points(map_points: list[MapPoint]):
    for point in map_points:
        print(point.point, point.concentration)


def simplex(bot: SimulatedRover, map_points: list[MapPoint], plotted_map: np.array):
    print("simplex")
    create_map_plot(plotted_map)


explored_points: list[MapPoint] = []
bot: SimulatedRover = SimulatedRover()

map: np.array = generate_map(1)
map_points = convert_to_map_points(map)
# print_map_points(map_points)

simplex(bot, map_points, map)
