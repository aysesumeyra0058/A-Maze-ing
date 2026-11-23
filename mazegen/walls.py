"""Maze wall operations."""

from typing import Iterator, Tuple

Cell = Tuple[int, int]


class WallMixin:
    """Handle cells and walls."""

    width: int
    height: int
    grid: list[list[int]]
    DIRECTIONS: tuple[tuple[int, int, int], ...]
    MASK_NORTH: int
    MASK_EAST: int
    MASK_SOUTH: int
    MASK_WEST: int

    def _neighbour(self, cell: Cell) -> Iterator[Tuple[Cell, int]]:
        """Find nearby cells."""
        x, y = cell
        for dx, dy, bit in self.DIRECTIONS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                yield (nx, ny), bit

    def _knock_down_wall(self, a: Cell, b: Cell) -> None:
        """Open a shared wall."""
        x, y = a
        nx, ny = b

        # Open both sides.
        for neighbor, bit in self._neighbour(a):
            if neighbor == b:

                existing_walls = self.grid[y][x]
                self.grid[y][x] = existing_walls & ~bit

                if bit == self.MASK_NORTH:

                    opposite_bit = self.MASK_SOUTH

                elif bit == self.MASK_SOUTH:

                    opposite_bit = self.MASK_NORTH

                elif bit == self.MASK_EAST:

                    opposite_bit = self.MASK_WEST

                else:

                    opposite_bit = self.MASK_EAST

                neighbor_walls = self.grid[ny][nx]
                self.grid[ny][nx] = neighbor_walls & ~opposite_bit

                return

        raise ValueError("Walls can only be opened between neighbors.")

    def _would_open_square(self, cell_a: Cell, cell_b: Cell) -> bool:
        """Check for open squares."""
        ax, ay = cell_a
        bx, by = cell_b

        if ay > by:
            min_y = ay
        else:
            min_y = by
        min_y -= 2
        if min_y < 0:
            min_y = 0
        if ay < by:
            max_y = ay
        else:
            max_y = by
        if max_y > self.height - 3:
            max_y = self.height - 3
        if ax > bx:
            min_x = ax
        else:
            min_x = bx
        min_x -= 2
        if min_x < 0:
            min_x = 0
        if ax < bx:
            max_x = ax
        else:
            max_x = bx
        if max_x > self.width - 3:
            max_x = self.width - 3

        target_edge = {cell_a, cell_b}
        east_bit = self.MASK_EAST
        south_bit = self.MASK_SOUTH

        for top_y in range(min_y, max_y + 1):
            for top_x in range(min_x, max_x + 1):
                inner_walls: list[Tuple[Cell, Cell, int]] = []
                for row in range(3):
                    for col in range(2):
                        first = (top_x + col, top_y + row)
                        second = (top_x + col + 1, top_y + row)
                        inner_walls.append((first, second, east_bit))
                for row in range(2):
                    for col in range(3):
                        first = (top_x + col, top_y + row)
                        second = (top_x + col, top_y + row + 1)
                        inner_walls.append((first, second, south_bit))

                # Check inner walls.
                all_open = True
                for first_cell, second_cell, wall_bit in inner_walls:
                    first_x, first_y = first_cell
                    is_target_wall = {first_cell, second_cell} == target_edge
                    if (not is_target_wall
                            and self.grid[first_y][first_x] & wall_bit):
                        all_open = False
                        break
                if all_open:
                    return True

        return False
