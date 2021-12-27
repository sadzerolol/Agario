import math
import enum 
from operator import add, sub

from .. import gameutils as gu
from . import interfaces
from .Cell import Cell


class PlayerCell(Cell, interfaces.eater):
    """Represents player Cell(part of player) state."""

    width = 5
    speed_lim = 10
    # size of player
    size = (5,)
    size_cum = (1,)

    fireCell_cond_to_center = 40
    fireCell_to_center = 10
    fireCell_speed = Cell.speed_lim

    # min ratius to split
    SplitCell_cond_to_center = 40
    SplitCell_speed = 3
    # the time that must pass before сell can connect to another Cell
    timeout = 240

    def __init__(self, position, to_center, colour, angle=0, speed=0):
        super().__init__(position, to_center, colour, angle, speed)
        # time to connect
        self.split_timeout = self.SPLIT_TIMETOUT
        self.area_pool = 0

    def go(self):
        """Update Cell state and go with described velocity."""
        self.__split_timeout_tick()
        self.__add_area(self.__area_pool_give_out())
        super().go()

    def eat(self, Cell):
        """Increase current Cell area"""
        self.area_pool += Cell.area()
        self.__add_area(self.__area_pool_give_out())

    def __split_timeout_tick(self):
        """Simply changes timeout value by one."""
        if self.split_timeout > 0:
            self.split_timeout -= 1

    def __add_area(self, area):
        """Increase current Cell area with passed area."""
        self.to_center = math.sqrt((super().area() + area) / math.pi)

    def __area_pool_give_out(self, part=0.05):
        """Returns some part of food from area pool."""
        if self.area_pool > 0:
            area = self.area_pool * part
            self.area_pool *= 1 - part
        else:
            area = 0
        return area

    def spit_out(self, Cell):
        """Decrease current Cell"""
        self.to_center = math.sqrt((super().area() - Cell.area()) / math.pi)

    def able_to_emit(self, cond_to_center):
        """Checks if Cell able to emmit."""
        if self.to_center >= cond_to_center:
            return True
        return False

    def emit(self, angle, speed, to_center, ObjClass):
        """Returns emmited object.
        """
        # create emmited object at position [0, 0]
        obj = ObjClass(
            [0, 0], to_center, 
            self.colour, 
            angle, speed)
        # change current Cell to_center
        self.spit_out(obj)
        # find diff_xy to go spawn Cell on current circle border
        diff_xy = gu.polar_to_cartesian(angle, self.to_center + to_center)
        # go created object
        obj.position = list(map(add, self.position, diff_xy))
        return obj

    def Eat_attempt(self, target):
        """Try to eat."""
        return target.attempt_to_be_eaten(self)

    def fire(self, angle):
        """fire in the given angle.
        Returns the fired Cell.
        """
        return self.emit(
            angle, 
            self.fireCell_speed,
            self.fireCell_to_center,
            Cell)

    def able_to_fire(self):
        """Check if Cell able to fire."""
        return self.able_to_emit(self.fireCell_cond_to_center)

    def split(self, angle):
        """Split Cell in the given angle.
        """
        return self.emit(
            angle, 
            self.SPLITCell_speed,
            self.to_center/math.sqrt(2),
            PlayerCell)

    def able_to_split(self):
        """Checks if Cell able to split."""
        return self.able_to_emit(self.SPLITCell_cond_to_center)

    def regurgitate_from(self, Cell):
        """Pushing  Cell to edge of the passed Cell and get rid of the collision beetwen them.
        """
        # get vector that connects two centers, to determine direction
        centers_vec = list(map(
            sub,
            self.position,
            Cell.position))
        # get angle of contact
        angle = gu.cartesian_to_polar(*centers_vec)[0]
        # intersection length
        delta = self.to_center + Cell.to_center - self.distance_to(Cell)
        # get delta in cartesian coordinate system
        d_xy = gu.polar_to_cartesian(angle, delta)
        # go current Cell outside passed Cell
        self.position = list(map(
            add,
            self.position,
            d_xy))

    def area(self):
        """Returns full PlayerCell area"""
        return super().area() + self.area_pool
