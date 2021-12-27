import math
from operator import sub

from .. import gameutils as gu


class Circle():
    """Circle object"""

    def __init__(self, position, to_center):
        self.position = position
        self.to_center = to_center

    def is_intersects(self, circle):
        """True if it is
           False returns none"""
        if self.distance_to(circle) < self.to_center + circle.to_center:
            return True
        return False

    def distance_to(self, circle):
        """distance to target"""
        diff = tuple(map(sub, self.position, circle.position))
        return math.hypot(*diff)

    def area(self):
        """Returns circle area."""
        return math.pi * self.to_center**2