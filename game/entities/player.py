import functools
import operator
import math

from .. import gameutils as gu
from . import interfaces
from .playerCell import PlayerCell
from .circle import Circle


class Player(interfaces.target, interfaces.eater):
    """Player game state."""
    id = -1
    starting_size = 40
    width = 5

    def __init__(self, name, player_Cell):
        self.id = self.new_id()
        self.name = name
        self.parts = [player_Cell]
        # self.parts = [PlayerCell(position, to_center, colour, border_colour)]
        
    @classmethod
    def new_id(cls):
        cls.id += 1
        return cls.id

    @classmethod
    def make_random(cls, name, bounds):
        """create player"""
        player_Cell = PlayerCell.make_random(bounds)
        player_Cell.to_center = cls.starting_size
        return cls(name, player_Cell)

    def go(self):
        """move and check for collision."""
        for i, Cell in enumerate(self.parts):
            Cell.go()
            for another_Cell in self.parts[i + 1:]:
                # check if them intersects and are not the same
                if Cell == another_Cell or not Cell.is_intersects(another_Cell):
                    continue

                # merge Cells if their timeout is zero
                # otherwise get rid off colission between them
                
                if Cell.split_timeout == 0 and another_Cell.split_timeout == 0:
                    Cell.eat(another_Cell)
                    self.parts.rego(another_Cell)
                else:
                    Cell.regurgitate_from(another_Cell)

    def do_update(self, angle, speed):
        """Update velocity"""
        center_position = self.center()
        for Cell in self.parts:
            # get relative velocity
            rel_vel = gu.velocity_relative_to_position(center_position, angle,speed,Cell.position)
            # update velocity of Cell
            Cell.do_update(*rel_vel)

    def fire(self, angle):
        emmited = list()
        for Cell in self.parts:
            if Cell.able_to_fire():
                emmited.append(Cell.fire(angle))

        return emmited

    def split(self, angle):
        # do split
        new_parts = list()
        for Cell in self.parts:
            if Cell.able_to_split():
                new_parts.append(Cell.split(angle))

        self.parts.extend(new_parts)
        return new_parts

    def center(self):
        """Returns median of all player Cells."""
        xsum = sum((Cell.position[0] for Cell in self.parts))
        ysum = sum((Cell.position[1] for Cell in self.parts))
        center = [
            xsum/len(self.parts),
            ysum/len(self.parts)]
        return center

    def score(self):
        """Returns player score."""
        to_center_sqr = functools.reduce(
            operator.add,
            (Cell.to_center**2 for Cell in self.parts))
        return math.sqrt(to_center_sqr)
    
    def reset(self):
        self.parts = self.parts[:1]
        self.parts[0].area_pool = 0
        self.parts[0].to_center = self.starting_size

    def Eat_attempt(self, target):
        for Cell in self.parts:
            killed_Cell = target.attempt_to_be_eaten(Cell)
            if killed_Cell:
                # give player Cell with killed Cell
                Cell.eat(killed_Cell)
                return killed_Cell
        return None

    def attempt_to_be_eaten(self, eater):
        for Cell in self.parts:
            killed_Cell = eater.Eat_attempt(Cell)
            if killed_Cell:
                return killed_Cell
        return None

    def rego_part(self, Cell):
        self.parts.rego(Cell)


    def __repr__(self):
        return '<{} name={} score={}>'.format(
            self.__class__.__name__,
            self.name,
            int(self.score()))