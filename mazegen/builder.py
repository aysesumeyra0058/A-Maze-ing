import random
from typing import List, Optional, Set, Tuple

from .pattern import PatternMixin

Cell = Tuple[int, int]


class MazeBuilder(PatternMixin):
    """Build a maze."""

    MASK_NORTH, MASK_EAST, MASK_SOUTH, MASK_WEST = 1, 2, 4, 8
    DIRECTIONS = ((0, -1, 1), (1, 0, 2), (0, 1, 4), (-1, 0, 8))

    def __init__(self, width: int, height: int, perfect: bool,
                 rng: random.Random,
                 reserved: Optional[Set[Cell]] = None) -> None:
        """Set up the maze."""
        self.width, self.height, self.perfect = width, height, perfect
        self._rng = rng
        # Close all walls.
        self.grid: List[List[int]] = [[15] * width for _ in range(height)]
        self.blocked_cells: Set[Cell] = set()
        self._reserved = set(reserved or ())
        if not perfect:
            self._reserved.update({
                (0, 0), (width - 1, 0), (0, height - 1),
                (width - 1, height - 1), (width // 2, height // 2),
            })
        rejected = False
        # Find pattern positions.
        candidates: List[Set[Cell]] = []
        for cells in self._pattern_candidates():
            if not perfect and self._forced_dead_ends(cells) > 2:
                rejected = True
                continue
            candidates.append(cells)
            if perfect or len(candidates) == 32:
                break
        if not candidates:
            if rejected:
                print("Warning: the 42 pattern would exceed the non-perfect "
                      "maze's two-dead-end limit; pattern skipped.")
            candidates = [set()]

        if perfect:
            self.blocked_cells = candidates[0]
            self._generate_perfect_maze()
            return

        for cells in candidates:
            for _ in range(4):
                self.grid = [[15] * width for _ in range(height)]
                self.blocked_cells = cells
                self._generate_perfect_maze()
                try:
                    self._generate_non_perfect_maze()
                    return
                except ValueError:
                    continue
        raise ValueError(
            "Non-perfect maze generation failed after "
            "all placement attempts.")

    def _generate_perfect_maze(self) -> None:
        """Create a perfect maze."""

        start = None
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) not in self.blocked_cells:
                    start = (x, y)
                    break
            if start is not None:
                break

        if start is None:
            raise ValueError("No available starting cell for maze generation")

        # Track visited cells.
        visited = {start} | self.blocked_cells

        stack = [start]

        while stack:

            current = stack[-1]

            candidates = []
            for cell, bit_value in self._neighbour(current):
                if cell not in visited:
                    candidates.append(cell)
            if candidates:

                neighbor = self._rng.choice(candidates)

                self._knock_down_wall(current, neighbor)

                visited.add(neighbor)

                stack.append(neighbor)

            else:

                stack.pop()

    def _generate_non_perfect_maze(self) -> None:
        """Add paths and loops."""

        cells = [(x, y) for y in range(self.height) for x in range(self.width)
                 if (x, y) not in self.blocked_cells]
        self._rng.shuffle(cells)
        # Count new loops.
        loops = 0
        for cell in cells:
            x, y = cell
            closed_walls = 0
            for wall_bit in (1, 2, 4, 8):
                if self.grid[y][x] & wall_bit:
                    closed_walls += 1
            if closed_walls != 3:
                continue
            choices = [n for n, bit in self._neighbour(cell)
                       if n not in self.blocked_cells and self.grid[y][x] & bit
                       and not self._would_open_square(cell, n)]
            if choices:
                self._knock_down_wall(cell, self._rng.choice(choices))
                loops += 1
        if loops < 2:
            edges = [(cell, n) for cell in cells
                     for n, bit in self._neighbour(cell)
                     if n not in self.blocked_cells
                     and self.grid[cell[1]][cell[0]] & bit]
            self._rng.shuffle(edges)
            for a, b in edges:
                if loops >= 2:
                    break

                wall_closed = False
                for neighbor, bit in self._neighbour(a):
                    if neighbor == b and self.grid[a[1]][a[0]] & bit:
                        wall_closed = True
                        break
                if wall_closed and not self._would_open_square(a, b):
                    self._knock_down_wall(a, b)
                    loops += 1
        if loops < 2:
            raise ValueError(
                "Cannot create a non-perfect maze with "
                "at least two loops.")
        dead_ends = 0
        for x, y in cells:
            closed_walls = 0
            for wall_bit in (1, 2, 4, 8):
                if self.grid[y][x] & wall_bit:
                    closed_walls += 1
            if closed_walls == 3:
                dead_ends += 1
        if dead_ends > 2:
            raise ValueError(
                "Cannot create a non-perfect maze with "
                "at most two dead ends.")
