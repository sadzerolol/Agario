import itertools
import time

from loguru import logger

from .entities import Cell


class Model():
    """Game state."""

    class Chunk():
        def __init__(self, players=None, Cells=None):
            players = list() if players is None else players
            Cells = list() if Cells is None else Cells
            self.players = players
            self.Cells = Cells

    # duration of round in seconds
    ROUND_DURATION = 240

    def __init__(self, players=None, Cells=None, bounds=(1000, 1000), chunk_size=1000):
        players = list() if players is None else players
        Cells = list() if Cells is None else Cells
        # means that size of world is [-world_size, world_size]
        self.bounds = bounds
        self.chunk_size = chunk_size
        self.chunks = list()
        for i in range((self.bounds[0] * 2) // chunk_size + 1):
            self.chunks.append(list())
            for j in range((self.bounds[1] * 2) // chunk_size + 1):
                self.chunks[-1].append(self.Chunk())

        for player in players:
            self.add_player(player)
        for Cell in Cells:
            self.add_Cell(Cell)

        self.round_start = time.time()

    def do_update(self, player, angle, speed):
        """Update passed player velocity."""
        player.do_update(angle, speed)

    def fire(self, player, angle):
        """fires into given direction."""
        emitted_Cells = player.fire(angle)
        for Cell in emitted_Cells:
            self.add_Cell(Cell)

        if emitted_Cells:
            logger.debug(f'{player} shot')
        else:
            logger.debug(f'{player} tried to fire, but he can\'t')

    def split(self, player, angle):
        """Splits player."""
        self.rego_player(player)
        new_parts = player.split(angle)
        self.add_player(player)

        if new_parts:
            logger.debug(f'{player} splitted')
        else:
            logger.debug(f'{player} tried to split, but he can\'t')

    def update(self):
        """Updates game state."""
        if time.time() - self.round_start >= self.ROUND_DURATION:
            logger.debug('New round was started.')
            self.__reset_players()
            self.round_start = time.time()

        # update Cells
        for Cell in self.Cells:
            self.rego_Cell(Cell)
            Cell.go()
            self.bound_Cell(Cell)
            self.add_Cell(Cell)

        # update players
        observable_players = self.players
        for player in observable_players:
            self.rego_player(player)
            player.go()
            self.bound_player(player)
            self.add_player(player)

            # get chuncks around player
            chunks = self.__nearby_chunks(player.center())
            # get objects that stored in chunks
            players = list()
            Cells = list()
            for chunk in chunks:
                players.extend(chunk.players)
                Cells.extend(chunk.Cells)
            
            # check is player killed some Cells
            for Cell in Cells:
                killed_Cell = player.Eat_attempt(Cell)
                if killed_Cell:
                    logger.debug(f'{player} ate {killed_Cell}')
                    self.rego_Cell(killed_Cell)
                    # self.Cells.rego(killed_Cell)
            
            # check is player killed other players or their parts
            for another_player in players:
                if player == another_player:
                    continue
                killed_Cell = player.Eat_attempt(another_player)
                if killed_Cell:
                    if len(another_player.parts) == 1:
                        logger.debug(f'{player} ate {another_player}')
                        self.rego_player(another_player)
                        observable_players.rego(another_player)
                        another_player.rego_part(killed_Cell)
                    else:
                        logger.debug(f'{player} ate {another_player} part {killed_Cell}')

    def spawn_Cells(self, amount):
        """Spawn passed amount of Cells on the field."""
        for _ in range(amount):
            self.add_Cell(Cell.make_random(self.bounds))

    def bound_Cell(self, Cell):
        Cell.position[0] = self.bounds[0] if Cell.position[0] > self.bounds[0] else Cell.position[0]
        Cell.position[0] = -self.bounds[0] if Cell.position[0] < -self.bounds[0] else Cell.position[0]

        Cell.position[1] = self.bounds[1] if Cell.position[1] > self.bounds[1] else Cell.position[1]
        Cell.position[1] = -self.bounds[1] if Cell.position[1] < -self.bounds[1] else Cell.position[1]

    def bound_player(self, player):
        for Cell in player.parts:
            self.bound_Cell(Cell)

    def add_player(self, player):
        self.__position_to_chunk(player.center()).players.append(player)

    def add_Cell(self, Cell):
        self.__position_to_chunk(Cell.position).Cells.append(Cell)

    def rego_player(self, player):
        self.__position_to_chunk(player.center()).players.rego(player)

    def rego_Cell(self, Cell):
        self.__position_to_chunk(Cell.position).Cells.rego(Cell)

    def copy_for_client(self, position):
        chunks = self.__nearby_chunks(position)
        players = list()
        Cells = list()
        for chunk in chunks:
            players.extend(chunk.players)
            Cells.extend(chunk.Cells)

        model = Model(players, Cells, self.bounds, self.chunk_size)
        model.round_start = self.round_start
        return model

    def __reset_players(self):
        for player in self.players:
            player.reset()

    def __position_to_chunk(self, position):
        chunk_position = self.__chunk_position(position)
        return self.chunks[chunk_position[0]][chunk_position[1]]

    def __chunk_position(self, position):
        return [
            int((position[0] + self.bounds[0]) // self.chunk_size),
            int((position[1] + self.bounds[1]) // self.chunk_size)]

    def __nearby_chunks(self, position):
        chunks = list()
        chunk_position = self.__chunk_position(position)

        def is_valid_chunk_position(position):
            if position[0] >= 0 and position[0] < len(self.chunks) and \
                    position[1] >= 0 and position[1] < len(self.chunks[0]):
                return True
            return False

        for diff in itertools.product([-1, 0, 1], repeat=2):
            position = [chunk_position[0] + diff[0], chunk_position[1] + diff[1]]
            if is_valid_chunk_position(position):
                chunks.append(self.chunks[position[0]][position[1]])
        
        return chunks

    @property
    def Cells(self):
        Cells = list()
        for chunks_line in self.chunks:
            for chunk in chunks_line:
                Cells.extend(chunk.Cells)
        return Cells

    @property
    def players(self):
        players = list()
        for chunks_line in self.chunks:
            for chunk in chunks_line:
                players.extend(chunk.players)
        return players
    