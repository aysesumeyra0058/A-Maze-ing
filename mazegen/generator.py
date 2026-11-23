"""Public maze interface."""

import random
from typing import List, Optional, Set, Tuple
from .builder import MazeBuilder
from .solver import bfs


class MazeGenerator:
    """Generate and solve mazes."""

    def __init__(self, width: int, height: int, perfect: bool = False,
                 seed: Optional[int] = None,
                 entry: Optional[Tuple[int, int]] = None,
                 exit: Optional[Tuple[int, int]] = None) -> None:
        """Check inputs and generate."""
        if (type(width) is not int or type(height) is not int
                or width <= 0 or height <= 0):
            raise ValueError("width and height must be positive integers.")
        if type(perfect) is not bool:
            raise ValueError("perfect must be True or False.")
        if seed is not None and type(seed) is not int:
            raise ValueError("seed must be an integer or None.")
        for name, cell in (("entry", entry), ("exit", exit)):
            if cell is None:
                continue

            valid_cell = tuple in type(cell).__mro__
            if valid_cell and len(cell) != 2:
                valid_cell = False
            if valid_cell:
                for value in cell:
                    if type(value) is not int:
                        valid_cell = False
                        break
            if valid_cell and not (
                0 <= cell[0] < width and 0 <= cell[1] < height
            ):
                valid_cell = False
            if not valid_cell:
                raise ValueError(
                    f"{name} must be an (x, y) pair inside the maze.")
        if entry is not None and entry == exit:
            raise ValueError("entry and exit must differ.")
        self.width, self.height, self.perfect = width, height, perfect
        # Save the seed.
        self.seed = random.getrandbits(32) if seed is None else seed
        reserved = {cell for cell in (entry, exit) if cell is not None}
        self._builder = MazeBuilder(
            width, height, perfect, random.Random(self.seed), reserved)

    def neighbors(self, cell: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Return open neighbors."""
        x, y = cell
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise ValueError("Cell is outside the maze.")
        return [neighbor for neighbor, bit in self._builder._neighbour(cell)
                if not self._builder.grid[y][x] & bit]

    def get_grid(self) -> List[List[int]]:
        """Return a grid copy."""
        return [row.copy() for row in self._builder.grid]

    def get_blocked_cells(self) -> Set[Tuple[int, int]]:
        """Return pattern cells."""
        return self._builder.blocked_cells.copy()

    def get_seed(self) -> int:
        """Return the seed."""
        return self.seed

    def solve(
        self,
        entry: tuple[int, int],
        exit_position: tuple[int, int],
    ) -> list[tuple[int, int]] | None:
        """Return the shortest path."""

        for x, y in (entry, exit_position):
            if not (0 <= x < self.width and 0 <= y < self.height):
                raise ValueError("Solution endpoints must be inside the maze")

        blocked_cells = self.get_blocked_cells()
        if entry in blocked_cells or exit_position in blocked_cells:
            return None

        return bfs(self.neighbors, entry, exit_position)
