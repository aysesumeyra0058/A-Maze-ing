"""Seed kontrollü, duvarları bit maskesiyle tutulan labirent üreticisi."""

import random
from collections import deque
from typing import Iterator, List, Optional, Set, Tuple

Cell = Tuple[int, int]


class MazeBuilder:
    """Duvar ızgarasını ve korunan 42 hücrelerini oluşturur."""

    MASK_NORTH, MASK_EAST, MASK_SOUTH, MASK_WEST = 1, 2, 4, 8
    DIRECTIONS = ((0, -1, 1), (1, 0, 2), (0, 1, 4), (-1, 0, 8))
    LOGO = ("1000111", "1000001", "1110111", "0010100", "0010111")

    def __init__(self, width: int, height: int, perfect: bool,
                 rng: random.Random,
                 reserved: Optional[Set[Cell]] = None) -> None:
        """Ayrılmış hücreleri koruyarak seçilen modda üretim yapar."""
        self.width, self.height, self.perfect = width, height, perfect
        self._rng = rng
        self.grid: List[List[int]] = [[15] * width for _ in range(height)]
        self.blocked_cells: Set[Cell] = set()
        self._reserved = set(reserved or ())
        if not perfect:
            self._reserved.update({
                (0, 0), (width - 1, 0), (0, height - 1),
                (width - 1, height - 1), (width // 2, height // 2),
            })
        self._place_42_pattern()
        self._generate_perfect_maze()
        if not perfect:
            self._generate_non_perfect_maze()

    def _adjacent(self, cell: Cell) -> Iterator[Tuple[Cell, int]]:
        """Sınırlar içindeki komşuları ve yön bitlerini döndürür."""
        x, y = cell
        for dx, dy, bit in self.DIRECTIONS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                yield (nx, ny), bit

    def _connected_without(self, blocked: Set[Cell]) -> bool:
        """Engelli hücreler dışındaki alanın bağlantısını denetler."""
        start = next(((x, y) for y in range(self.height)
                      for x in range(self.width) if (x, y) not in blocked),
                     None)
        if start is None:
            return False
        seen = {start}
        queue = deque([start])
        while queue:
            for neighbor, _ in self._adjacent(queue.popleft()):
                if neighbor not in blocked and neighbor not in seen:
                    seen.add(neighbor)
                    queue.append(neighbor)
        return len(seen) == self.width * self.height - len(blocked)

    def _place_42_pattern(self) -> None:
        """Uygun bir 42 yerleşimi seçer veya açıklayıcı uyarı verir."""
        positions = [(x, y) for y in range(max(0, self.height - 4))
                     for x in range(max(0, self.width - 6))]
        positions.sort(key=lambda p: (
            not (0 < p[0] and p[0] + 7 < self.width
                 and 0 < p[1] and p[1] + 5 < self.height),
            abs(2 * p[0] + 7 - self.width)
            + abs(2 * p[1] + 5 - self.height), p[1], p[0]))
        fits_without_reservations = False
        for ox, oy in positions:
            cells = {(ox + x, oy + y) for y, row in enumerate(self.LOGO)
                     for x, value in enumerate(row) if value == "1"}
            if self._connected_without(cells):
                fits_without_reservations = True
                if not cells.intersection(self._reserved):
                    self.blocked_cells = cells
                    return
        if fits_without_reservations:
            raise ValueError("42 deseni ayrılmış giriş, çıkış veya merkez "
                             "hücreleri korunarak yerleştirilemiyor.")
        print("Uyarı: 42 deseni bu boyutta bağlantı korunarak "
              "yerleştirilemedi; desen atlandı.")

    def _knock_down_wall(self, a: Cell, b: Cell) -> None:
        """İki komşu hücrenin ortak duvarını iki taraftan açar."""
        x, y = a
        nx, ny = b
        
        for neighbor, bit in self._adjacent(a):
            if neighbor == b:
                # 1. Kendi hücremizin duvarını açalım
                existing_walls = self.grid[y][x]
                self.grid[y][x] = existing_walls & ~bit

                if bit == self.MASK_NORTH:       # Eğer bizim açtığımız yön Kuzeyse (1)
                    opposite_bit = self.MASK_SOUTH  # Karşı komşunun açılacak duvarı Güney'dir (4)
                elif bit == self.MASK_SOUTH:     # Eğer bizim açtığımız yön Güneyse (4)
                    opposite_bit = self.MASK_NORTH  # Karşı komşunun açılacak duvarı Kuzey'dir (1)
                elif bit == self.MASK_EAST:      # Eğer bizim açtığımız yön Doğuyorsa (2)
                    opposite_bit = self.MASK_WEST   # Karşı komşunun açılacak duvarı Batı'dır (8)
                else:                            # Durum geriye bir tek Batı kalıyor (8)
                    opposite_bit = self.MASK_EAST   # Karşı komşunun açılacak duvarı Doğu'dur (2)
                                
                
                # 3. Komşu hücrenin o duvarını da açalım
                neighbor_walls = self.grid[ny][nx]
                self.grid[ny][nx] = neighbor_walls & ~opposite_bit
                
                return
                
        raise ValueError("Duvar yalnızca komşu hücreler arasında açılabilir.")
                
    def _generate_perfect_maze(self) -> None:
        """İteratif rastgele DFS ile bağlı ve döngüsüz bir yapı üretir."""
        
        # 1. Adım: Başlangıç hücresini rastgele seç (engellenmiş 42 hücreleri hariç)
        start = None
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) not in self.blocked_cells:
                    start = (x, y)
                    break
            if start is not None:
                break
        
        # 2. Adım: Ziyaret edilenler kümesini ve Stack'i (yığını) oluştur
        visited = {start} | self.blocked_cells  # 42 hücrelerini de ziyaret edilmiş kabul ediyoruz ki duvarları kazılmasın
        stack = [start]                         # Adımlarımızı kaydettiğimiz yığın
        
        # 3. Adım: Stack boşalana kadar labirenti örmeye devam et
        while stack:
            current = stack[-1]  # Şu an üzerinde bulunduğumuz hücre (Stack'in en üstü)
            
            # Etrafımızdaki komşulardan henüz ZİYARET EDİLMEMİŞ olanları bulalım
            candidates = []
            for cell, bit_value in self._adjacent(current):
                if cell not in visited:
                    candidates.append(cell)
            if candidates:  # Eğer gidilmemiş en az bir komşu varsa:
                # Rastgele bir komşu seç
                neighbor = self._rng.choice(candidates)
                
                # Aradaki duvarı yık (hem bizim hücrenin hem komşunun duvarı açılır)
                self._knock_down_wall(current, neighbor)
                
                # Komşuyu ziyaret edildi olarak işaretle
                visited.add(neighbor)
                
                # Stack'e ekle (artık yeni bulunduğumuz yer burası oldu)
                stack.append(neighbor)
                
            else:  # Eğer etrafta gidecek hiç ham yol kalmadıysa (Çıkmaz sokak!):
                stack.pop()  # Son adımı yığından çıkararak bir adım geriye (önceki hücreye) sar!

    def _would_open_square(self, a: Cell, b: Cell) -> bool:
        """Yeni duvarın açılmasıyla duvarsız 3x3 alan oluşmasını denetle."""
        ax, ay = a
        bx, by = b
        for y in range(max(0, max(ay, by) - 2),
                       min(ay, by, self.height - 3) + 1):
            for x in range(max(0, max(ax, bx) - 2),
                           min(ax, bx, self.width - 3) + 1):
                edges = [((x + i, y + j), (x + i + 1, y + j), 2)
                         for j in range(3) for i in range(2)]
                edges += [((x + i, y + j), (x + i, y + j + 1), 4)
                          for j in range(2) for i in range(3)]
                if all({u, v} == {a, b} or not (self.grid[u[1]][u[0]] & bit)
                       for u, v, bit in edges):
                    return True
        return False

    def _generate_non_perfect_maze(self) -> None:
        """Çıkmazları azaltır ve en az iki bağımsız döngü oluşturur."""
        # Önce çıkmazları azalt, sonra gerekirse iki bağımsız döngüye ulaş.
        cells = [(x, y) for y in range(self.height) for x in range(self.width)
                 if (x, y) not in self.blocked_cells]
        self._rng.shuffle(cells)
        loops = 0
        for cell in cells:
            x, y = cell
            if self.grid[y][x].bit_count() != 3:
                continue
            choices = [n for n, bit in self._adjacent(cell)
                       if n not in self.blocked_cells and self.grid[y][x] & bit
                       and not self._would_open_square(cell, n)]
            if choices:
                self._knock_down_wall(cell, self._rng.choice(choices))
                loops += 1
        if loops < 2:
            edges = [(cell, n) for cell in cells
                     for n, bit in self._adjacent(cell)
                     if n not in self.blocked_cells
                     and self.grid[cell[1]][cell[0]] & bit]
            self._rng.shuffle(edges)
            for a, b in edges:
                if loops >= 2:
                    break
                if (any(n == b and self.grid[a[1]][a[0]] & bit
                        for n, bit in self._adjacent(a))
                        and not self._would_open_square(a, b)):
                    self._knock_down_wall(a, b)
                    loops += 1
        if loops < 2:
            raise ValueError(
                "Bu boyutta en az iki döngülü non-perfect labirent "
                "üretilemez.")
        dead_ends = sum(self.grid[y][x].bit_count() == 3 for x, y in cells)
        if dead_ends > 2:
            raise ValueError(
                "Bu ayarlarla en fazla iki çıkmazlı non-perfect labirent "
                "üretilemedi.")
