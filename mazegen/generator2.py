"""Yeniden kullanılabilir labirent üretici arayüzü."""

import random
from typing import List, Optional, Set, Tuple
from .builder import MazeBuilder
from .solver import bfs


class MazeGenerator:
    """Bir labirent üretiyoruz koordinatlar (x, y), ızgara erişimi grid[y][x].

    Config'teki entry ve exit değerleri verilirse 42 bu hücreleri kapatmaz.
    Aynı parametreler ve seed aynı sonucu üretir. Non-perfect modda yeterli
    Döngü oluşturulamayan ayarlar hata verir; desen yerleştirilemezse
    veya non-perfect modun çıkmaz sınırıyla uyumsuzsa uyarı verilir ve
    üretim desensiz sürer.
    """

    def __init__(self, width: int, height: int, perfect: bool = False,
                 seed: Optional[int] = None,
                 entry: Optional[Tuple[int, int]] = None,
                 exit: Optional[Tuple[int, int]] = None) -> None:
        """Ayarları doğrular ve labirenti oluşturur."""
        if (type(width) is not int or type(height) is not int
                or width <= 0 or height <= 0):
            raise ValueError("width ve height pozitif tam sayı olmalıdır.")
        if type(perfect) is not bool:
            raise ValueError("perfect True veya False olmalıdır.")
        if seed is not None and type(seed) is not int:
            raise ValueError("seed tam sayı veya None olmalıdır.")
        for name, cell in (("entry", entry), ("exit", exit)):
            if cell is not None and (
                not isinstance(cell, tuple) or len(cell) != 2
                or any(type(v) is not int for v in cell)
                or not (0 <= cell[0] < width and 0 <= cell[1] < height)
            ):
                raise ValueError(
                    f"{name} labirent içindeki bir (x, y) çifti olmalıdır.")
        if entry is not None and entry == exit:
            raise ValueError("entry ve exit farklı hücreler olmalıdır.")
        self.width, self.height, self.perfect = width, height, perfect
        self.seed = random.randrange(2**32) if seed is None else seed
        reserved = {cell for cell in (entry, exit) if cell is not None}
        self._builder = MazeBuilder(
            width, height, perfect, random.Random(self.seed), reserved)

    def neighbors(self, cell: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Açık komşuları kuzey, doğu, güney ve batı sırasıyla döndürür."""
        x, y = cell
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise ValueError("Hücre labirent sınırları dışında.")
        return [neighbor for neighbor, bit in self._builder._adjacent(cell)
                if not self._builder.grid[y][x] & bit]

    def get_grid(self) -> List[List[int]]:
        """Duvar ızgarasının bağımsız bir kopyasını döndürür."""
        return [row.copy() for row in self._builder.grid]

    def get_blocked_cells(self) -> Set[Tuple[int, int]]:
        """42 desenindeki hücrelerin bağımsız bir kopyasını döndürür."""
        return self._builder.blocked_cells.copy()

    def get_seed(self) -> int:
        """Üretimde kullanılan seed değerini döndürür."""
        return self.seed

    def solve(
        self,
        entry: tuple[int, int],
        exit_position: tuple[int, int],
    ) -> list[tuple[int, int]] | None:
        """Return a shortest path between two maze cells."""

        # Reject coordinates outside the maze
        for x, y in (entry, exit_position):
            if not (0 <= x < self.width and 0 <= y < self.height):
                raise ValueError("Solution endpoints must be inside the maze")

        # A solution cannot start or end inside the 42 pattern
        blocked_cells = self.get_blocked_cells()
        if entry in blocked_cells or exit_position in blocked_cells:
            return None

        # Find the path using this maze's accessible neighbors
        return bfs(self.neighbors, entry, exit_position)
