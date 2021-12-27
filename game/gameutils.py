import math
import random
from operator import add, sub


def polar_to_cartesian(angle, val):
    """to cartesian."""
    return [val * math.cos(angle), val * math.sin(angle)]


def cartesian_to_polar(x, y):
    """Cto polar."""
    return [math.atan2(y, x), math.sqrt(x**2 + y**2)]


def random_safe_colour():
    """Returns random safe colour.

    Two random values of three RGB is 7 and 255
    and last is in range [0 - 255]
    """
    lights = (7, 255, random.randint(0, 255))
    return random.sample(lights, 3)


def make_border_colour(colour):
    """Creates border colour from passed colour.

    Simply maps 255 to 229 and 7 to 6.
    Third light is multiply by 0.9
    (255 -> 229, 7 -> 6, other -> 0.9*other)
    """
    mapper = lambda l: 229 if (l == 255) else 6 if (l == 7) else int(0.9*l)
    return list(map(mapper, colour))


def random_position(size):
    """Returns random position in within given size."""
    return [random.randint(-size[0], size[1]), 
        random.randint(-size[1], size[1])]


def velocity_relative_to_position(vec_position, angle, speed, position):
    """Returns new velocity that points in position."""
    # get catesian vector
    vec = polar_to_cartesian(angle, speed*500)
    # get vector end positionition
    vec_end = list(map(add, vec_position, vec))
    # get vector with start in center of Cell and ends in vec_end positionition
    rel_vec = list(map(sub, vec_end, position))
    # converts to polar
    rel_vec = cartesian_to_polar(*rel_vec)
    # normalize speed
    rel_vec[1] = speed
    return rel_vec


def apply(iter_obj, func):
    """Apply given function to given sequence."""
    for x in iter_obj:
        func(iter_obj)