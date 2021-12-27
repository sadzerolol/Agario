from abc import ABC, abstractmethod


class Eater(ABC):
    """Interface of eater"""

    @abstractmethod
    def Eat_attempt(self, target):
        """Attempt to eat target.
        True returns scores
        False returns none"""
        pass
        