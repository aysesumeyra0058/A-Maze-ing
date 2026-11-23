"""42 pattern placement."""

from collections import deque
from typing import Iterator, Set, Tuple

from .walls import WallMixin

Cell = Tuple[int, int]


class PatternMixin(WallMixin):
    """Place the 42 pattern."""

    _reserved: Set[Cell]

    PATTERN_42 = ("1000111", "1000001", "1110111", "0010100", "0010111")

    def _connected_without(self, blocked: Set[Cell]) -> bool:
        """Check open cell connections."""

        start = None
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) not in blocked:
                    start = (x, y)
                    break
            if start is not None:
                break
        if start is None:
            return False
        seen = {start}
        queue = deque([start])
        while queue:
            for neighbor, _ in self._neighbour(queue.popleft()):
                if neighbor not in blocked and neighbor not in seen:
                    seen.add(neighbor)
                    queue.append(neighbor)
        return len(seen) == self.width * self.height - len(blocked)

    def _forced_dead_ends(self, blocked: Set[Cell]) -> int:
        """Count forced dead ends."""
        # Count blocked exits.
        dead_ends = 0
        for y in range(self.height):
            for x in range(self.width):
                cell = (x, y)
                if cell in blocked:
                    continue
                available = 0
                for neighbor, _ in self._neighbour(cell):
                    if neighbor not in blocked:
                        available += 1
                if available == 1:
                    dead_ends += 1
        return dead_ends

    def _pattern_candidates(self) -> Iterator[Set[Cell]]:
        """Find valid pattern positions."""

        pattern_height = len(self.PATTERN_42)
        pattern_width = len(self.PATTERN_42[0])

        if (
            self.width < pattern_width + 2
            or self.height < pattern_height + 2
        ):
            print("Warning: maze too small for the 42 pattern; skipped.")
            return

        max_y = self.height - pattern_height
        max_x = self.width - pattern_width
        # Rank pattern positions.
        ranked_positions = []
        for oy in range(max_y + 1):
            for ox in range(max_x + 1):
                edge_risk = not (
                    0 < ox and ox + pattern_width < self.width
                    and 0 < oy and oy + pattern_height < self.height
                )
                dx = 2 * ox + pattern_width - self.width
                dy = 2 * oy + pattern_height - self.height
                if dx < 0:
                    dx = -dx
                if dy < 0:
                    dy = -dy
                ranked_positions.append((edge_risk, dx + dy, oy, ox))
        ranked_positions.sort()

        fits_without_reservations = False
        found = False

        for _, _, oy, ox in ranked_positions:

            cells = set()
            for row_index in range(pattern_height):
                for col_index in range(pattern_width):
                    if self.PATTERN_42[row_index][col_index] == "1":
                        cells.add((ox + col_index, oy + row_index))

            if self._connected_without(cells):
                fits_without_reservations = True

                overlaps_reserved = False
                for cell in cells:
                    if cell in self._reserved:
                        overlaps_reserved = True
                        break
                if not overlaps_reserved:
                    found = True
                    yield cells

        if found:
            return

        if fits_without_reservations:
            print(
                "Warning: the 42 pattern cannot be placed while "
                "preserving protected cells; pattern skipped."
            )
            return

        print((
            'Warning: cannot place the 42 pattern while '
            'keeping all cells connected; pattern skipped.'
        ))
