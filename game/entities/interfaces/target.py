from abc import ABC, abstractmethod


class target(ABC):
    """Target interface"""

    @abstractmethod
    def attempt_to_be_eaten(self, eater):
        """Gets objects that tries to eat
        True returns eater object
        False returns none
        """ 
        pass
        