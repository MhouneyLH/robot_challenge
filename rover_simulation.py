import time
import numpy as np
import matplotlib.pyplot as plt
from perlin_noise import PerlinNoise


class MapPoint:
    def __init__(self, point: np.array, concentration: float):
        self.point = point
        self.concentration = concentration


def generate_map(seed: int) -> np.array:
    width = 100
    height = 100
    shape = (width, height)
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
    ax.imshow(map, origin='lower', extent=[0, width, 0, height])
    ax.set_title('Generated Map')

    plt.show()


def drawColoredPlot(x, y, z):
    fig = plt.Figure()
    plt.contourf(x*10, y*10, z, 70, cmap="hot")
    plt.colorbar()
    plt.show()


map: np.array = generate_map(1)
create_map_plot(map)
