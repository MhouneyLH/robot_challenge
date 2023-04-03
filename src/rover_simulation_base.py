import numpy as np
import map_generation as mg

DEFAULT_STARTING_POSITION: np.array = [0, 0]
DEFAULT_SPEED: int = 10
FINISH_VALUE: int = 220


class SimulatedRover:
    def __init__(self,
                 starting_position: np.array = DEFAULT_STARTING_POSITION,
                 speed: int = DEFAULT_SPEED,
                 current_concentration: int = mg.DEFAULT_CONCENTRATION,
                 highest_concentration_map_point: mg.MapPoint = mg.MapPoint(),
                 explored_points: np.array = [],):
        self.position: np.array = starting_position
        self.speed: int = speed
        self.current_concentration: int = current_concentration
        self.highest_concentration_map_point: mg.MapPoint = highest_concentration_map_point
        self.explored_points: np.array = explored_points

    def stop(self) -> None:
        print("Highest found point")
        mg.print_map_points([self.highest_concentration_map_point])
        print(self.position)

        self.position = DEFAULT_STARTING_POSITION
        self.current_concentration = mg.DEFAULT_CONCENTRATION
        self.speed = DEFAULT_SPEED
        self.explored_points = []
        self.highest_concentration_map_point = mg.MapPoint()

    def is_finished(self) -> bool:
        return self.highest_concentration_map_point.concentration > FINISH_VALUE

    def move_to(self, point: np.array):
        self.position = point
        self.explored_points.append(point)

    def get_concentration_at_point(self, map_points: list[mg.MapPoint], target_point: np.array) -> int:
        for item in map_points:
            if np.array_equal(item.point, target_point):
                return item.concentration
        return mg.DEFAULT_CONCENTRATION

    def get_concentration_of_current_position(self, map_points: list[mg.MapPoint]) -> int:
        result: int = self.get_concentration_at_point(
            map_points, self.position)
        self.current_concentration = result
        return result
