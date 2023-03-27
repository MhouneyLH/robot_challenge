import time
import numpy as np
import matplotlib.pyplot as plt
from perlin_noise import PerlinNoise


class MapPoint:
    def __init__(self, point: np.array, concentration: float):
        self.point = point
        self.concentration = concentration


def generate_map(seed: int) -> np.array:
    width = 200
    height = 100

    noise = PerlinNoise(octaves=2, seed=seed)
    noise_map = np.zeros((height, width))

    for y in range(height):
        for x in range(width):
            noise_map[y][x] = np.abs(
                int(255 * 2.5 * noise([x / width, y / height])))

    return noise_map


def create_map_plot(map: np.array):
    width = map.shape[1]
    height = map.shape[0]

    figure, ax = plt.subplots()
    ax.imshow(map, cmap='hot', origin='lower', extent=[0, width, 0, height])
    ax.set_title('Generated Map')

    plt.show()


def convert_to_map_points(map: np.array) -> list[MapPoint]:
    width = map.shape[1]
    height = map.shape[0]

    point_list: list[MapPoint] = []
    for x in range(width):
        for y in range(height):
            point: np.array = [x, y]
            point_list.append(MapPoint(point=point, concentration=map[y][x]))

    return point_list


def print_map_points(map_points: list[MapPoint]):
    for point in map_points:
        print(point.point, point.concentration)


map: np.array = generate_map(1)
map_points = convert_to_map_points(map)
# print_map_points(map_points)

create_map_plot(map)
