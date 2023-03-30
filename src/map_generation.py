import numpy as np
from perlin_noise import PerlinNoise
import matplotlib.pyplot as plt


FIELD_WIDTH: int = 400
FIELD_HEIGHT: int = 300
WINDOW_WIDTH_IN_INCHES: int = 20
WINDOW_HEIHGT_IN_INCHES: int = 10
DEFAULT_CONCENTRATION: int = -1
NOISE_OCTAVES: int = 2
MAP_VALUE_SCALE_FACTOR: int = 800
SUBPLOT_ARRANGEMENT: int = 111
DEFAULT_POINT: np.array = np.array([0, 0])


class MapPoint:
    def __init__(self, point: np.array = DEFAULT_POINT, concentration: int = DEFAULT_CONCENTRATION):
        self.point: np.array = np.array(point).astype(int)
        self.concentration: int = concentration

    def update(self, map_point) -> None:
        self.point = map_point.point
        self.concentration = map_point.concentration


def generate_map(seed: int) -> np.array:
    print("Using seed", seed)
    noise = PerlinNoise(octaves=NOISE_OCTAVES, seed=seed)
    noise_map = np.zeros((FIELD_HEIGHT, FIELD_WIDTH))

    for y in range(FIELD_HEIGHT):
        for x in range(FIELD_WIDTH):
            noise_map[y][x] = np.abs(
                int(MAP_VALUE_SCALE_FACTOR * noise([x / FIELD_WIDTH, y / FIELD_HEIGHT])))

    return noise_map


def create_map_plot(map: np.array, explored_points: np.array):
    figure = plt.figure(
        figsize=(WINDOW_WIDTH_IN_INCHES, WINDOW_HEIHGT_IN_INCHES))
    ax = figure.add_subplot(SUBPLOT_ARRANGEMENT)

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
