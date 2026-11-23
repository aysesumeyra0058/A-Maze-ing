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
        if entry is not None:
            valid_entry = type(entry) is tuple
            if valid_entry and len(entry) != 2:
                valid_entry = False
            if valid_entry:
                for value in entry:
                    if type(value) is not int:
                        valid_entry = False
                        break
            if valid_entry and not (
                0 <= entry[0] < width and 0 <= entry[1] < height
            ):
                valid_entry = False
            if not valid_entry:
                raise ValueError(
                    "entry must be an (x, y) pair inside the maze.")
        if exit is not None:
            valid_exit = type(exit) is tuple
            if valid_exit and len(exit) != 2:
                valid_exit = False
            if valid_exit:
                for value in exit:
                    if type(value) is not int:
                        valid_exit = False
                        break
            if valid_exit and not (
                0 <= exit[0] < width and 0 <= exit[1] < height
            ):
                valid_exit = False
            if not valid_exit:
                raise ValueError(
                    "exit must be an (x, y) pair inside the maze.")
        if entry is not None and entry == exit:
            raise ValueError("entry and exit must differ.")
        self.width, self.height, self.perfect = width, height, perfect
        # Save the seed.
        if seed is None:
            self.seed = random.randint(0, 999999)
        else:
            self.seed = seed
        reserved: Set[Tuple[int, int]] = set()
        if entry is not None:
            reserved.add(entry)
        if exit is not None:
            reserved.add(exit)
        self._builder = MazeBuilder(
            width, height, perfect, random.Random(self.seed), reserved)

    def neighbors(self, cell: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Return open neighbors."""
        x, y = cell
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise ValueError("Cell is outside the maze.")
        open_neighbors: List[Tuple[int, int]] = []
        for neighbor, bit in self._builder._neighbour(cell):
            if not self._builder.grid[y][x] & bit:
                open_neighbors.append(neighbor)
        return open_neighbors

    def get_grid(self) -> List[List[int]]:
        """Return a grid copy."""
        grid_copy: List[List[int]] = []
        for row in self._builder.grid:
            grid_copy.append(row.copy())
        return grid_copy

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

        entry_x, entry_y = entry
        if not (0 <= entry_x < self.width and 0 <= entry_y < self.height):
            raise ValueError("Solution endpoints must be inside the maze")
        exit_x, exit_y = exit_position
        if not (0 <= exit_x < self.width and 0 <= exit_y < self.height):
            raise ValueError("Solution endpoints must be inside the maze")

        blocked_cells = self.get_blocked_cells()
        if entry in blocked_cells or exit_position in blocked_cells:
            return None

        return bfs(self.neighbors, entry, exit_position)
