import random
from operator import add, sub

from .. import gameutils as gu
from . import interfaces
from .circle import Circle


class Cell(Circle, interfaces.target):
    
    width= 2
    speed_lim = 4
    size = (4, 6, 10)
    cum_size = (50, 16, 12)

    @classmethod
    def make_random(cls, bounds):
        """do random Cell."""
        position = gu.random_position(bounds)
        to_center = random.choices(cls.size, cls.size_CUM)[0]
        colour = gu.random_safe_colour()
        return cls(position, to_center, colour)

    def __init__(self, position, to_center, colour, angle=0, speed=0):
        super().__init__(position, to_center)
        # rgb colour
        self.colour = colour
        # rad angle speed
        self.angle = angle
        # coef value
        self.speed = speed

    def go(self):
        if self.speed < 0:
            self.speed = 0
        # get cartesian vector
        diff_xy = gu.polar_to_cartesian(self.angle, self.speed*self.speed_lim)
        # change positionition
        self.position = list(map(add, self.position, diff_xy))

    def do_update(self, angle, speed):
        """update velocity"""
        # to cart
        before_speed = self.speed
        v1 = gu.polar_to_cartesian(angle, speed)
        v2 = gu.polar_to_cartesian(self.angle, self.speed)
        # add 
        v3 = list(map(add, v1, v2))
        # to polar
        self.angle, self.speed = gu.cartesian_to_polar(*v3)
        # norm of speed vel
        if before_speed <= 1 and self.speed > 1:
            self.speed = 1
        elif before_speed > 1 and self.speed > before_speed:
            self.speed = before_speed

    def attempt_to_be_eaten(self, eater):
        if 2*self.area() <= eater.area() and self.distance_to(eater) <= eater.to_center - self.to_center:
            return self
        return None

    def __repr__(self):
        return '<{} position={} to_center={}>'.format(
            self.__class__.__name__,
            list(map(int, self.position)),
            int(self.to_center))