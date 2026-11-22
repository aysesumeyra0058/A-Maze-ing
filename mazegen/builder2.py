"""Seed kontrollü, duvarları bit maskesiyle tutulan labirent üreticisi."""

import random
from collections import deque
from itertools import islice
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
        self.grid: List[List[int]] = [[15] * width for _  in range(height)]
        self.blocked_cells: Set[Cell] = set()
        self._reserved = set(reserved or ())
        if not perfect:
            self._reserved.update({
                (0, 0), (width - 1, 0), (0, height - 1),
                (width - 1, height - 1), (width // 2, height // 2),
            })
        rejected = False

        def eligible_patterns() -> Iterator[Set[Cell]]:
            nonlocal rejected
            for cells in self._pattern_candidates():
                if not perfect and self._forced_dead_ends(cells) > 2:
                    rejected = True
                    continue
                yield cells

        candidates = list(islice(eligible_patterns(), 1 if perfect else 32))
        if not candidates:
            if rejected:
                print("Warning: the 42 pattern would exceed the non-perfect "
                      "maze's two-dead-end limit; pattern skipped.")
            candidates = [set()]

        if perfect:
            self.blocked_cells = candidates[0]
            self._generate_perfect_maze()
            return

        # Try a bounded number of deterministic attempts for each placement.
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
            "Non-perfect labirent denenen desen yerleşimleri ve "
            "üretim denemeleriyle oluşturulamadı.")

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

    def _forced_dead_ends(self, blocked: Set[Cell]) -> int:
        """Boş alanda yalnızca bir komşusu olan hücreleri sayar."""
        return sum(
            sum(neighbor not in blocked for neighbor, _ in self._adjacent(cell)) == 1
            for y in range(self.height)
            for x in range(self.width)
            if (cell := (x, y)) not in blocked
        )

    def _pattern_candidates(self) -> Iterator[Set[Cell]]:
        """Uygun 42 yerleşimlerini öncelik sırasıyla döndürür."""

        # 1. Adım: Olası tüm sol-üst köşe koordinatlarını (ox, oy) toplayalım

        # !!!!! burdan değişiklik başladı !!!

        # Get the dimensions of the 42 pattern
        pattern_height = len(self.LOGO)
        pattern_width = len(self.LOGO[0])

        # Skip the pattern if the maze is too small
        if (
            self.width < pattern_width
            or self.height < pattern_height
        ):
            print("Warning: maze too small for the 42 pattern; skipped.")
            return

        # Collect starting positions where the entire pattern fits
        positions: list[Cell] = []
        max_y = self.height - pattern_height
        max_x = self.width - pattern_width

        for oy in range(max_y + 1):
            for ox in range(max_x + 1):
                positions.append((ox, oy))

        # !!! buraya kadar olan kısım değiştirildi !!

        # 2. Adım: Pozisyonları sıralayacağız (Lambda kullanmadan, klasik
        # döngüyle veya net bir mantıkla)
        # Önce merkeze en yakın olanları ve labirentin kenar taşmalarını
        # engelleyenleri seçmek istiyoruz.
        # Bunun için Python'ın klasik sorted fonksiyonuna düz bir normal
        # fonksiyon (helper) verelim:
        def position_score(pos):
            ox, oy = pos
            # Kenarda mı kalıyor yoksa içeride mi? (0: içeride ve ideal, 1:
            # kenara çok yakın/taşma riski)
            is_edge_risk = not (0 < ox and ox + 7 <
                                self.width and 0 < oy and oy + 5 < self.height)

            # Merkeze olan uzaklık hesaplaması
            center_distance = abs(2 * ox + 7 - self.width) + \
                abs(2 * oy + 5 - self.height)

            return (is_edge_risk, center_distance, oy, ox)

        positions.sort(key=position_score)

        # 3. Adım: Pozisyonları tek tek deneme sırasına koyalım
        fits_without_reservations = False
        found = False

        for ox, oy in positions:
            # 42 logosunun '1' olan piksellerini hücre kümesine dönüştürelim
            # (enumerate yerine satır-sütun sayacıyla)
            cells = set()
            for row_index, row in enumerate(self.LOGO):
                for col_index, value in enumerate(row):
                    if value == "1":
                        cells.add((ox + col_index, oy + row_index))

            # Bu hücreleri engellediğimizde labirentin geri kalanı hâlâ
            # bağlanabiliyor mu?
            if self._connected_without(cells):
                fits_without_reservations = True
                # Eğer ayrılmış (reserved) özel hücrelerle çakışmıyorsa burası
                # mükemmeldir!
                if not cells.intersection(self._reserved):
                    found = True
                    yield cells

        if found:
            return

        # Skip the pattern if it cannot fit around protected cells
        if fits_without_reservations:
            print(
                "Warning: the 42 pattern cannot be placed while "
                "preserving protected cells; pattern skipped."
            )
            return

        print((
            'Uyarı: 42 deseni bu boyutta bağlantı korunarak '
            'yerleştirilemedi; desen atlandı.'
        ))

    def _knock_down_wall(self, a: Cell, b: Cell) -> None:
        """İki komşu hücrenin ortak duvarını iki taraftan açar."""
        x, y = a
        nx, ny = b

        for neighbor, bit in self._adjacent(a):
            if neighbor == b:
                # 1. Kendi hücremizin duvarını açalım
                existing_walls = self.grid[y][x]
                self.grid[y][x] = existing_walls & ~bit

                # Eğer bizim açtığımız yön Kuzeyse (1)
                if bit == self.MASK_NORTH:
                    # Karşı komşunun açılacak duvarı Güney'dir (4)
                    opposite_bit = self.MASK_SOUTH
                # Eğer bizim açtığımız yön Güneyse (4)
                elif bit == self.MASK_SOUTH:
                    # Karşı komşunun açılacak duvarı Kuzey'dir (1)
                    opposite_bit = self.MASK_NORTH
                # Eğer bizim açtığımız yön Doğuyorsa (2)
                elif bit == self.MASK_EAST:
                    # Karşı komşunun açılacak duvarı Batı'dır (8)
                    opposite_bit = self.MASK_WEST
                # Durum geriye bir tek Batı kalıyor (8)
                else:
                    # Karşı komşunun açılacak duvarı Doğu'dur (2)
                    opposite_bit = self.MASK_EAST

                # 3. Komşu hücrenin o duvarını da açalım
                neighbor_walls = self.grid[ny][nx]
                self.grid[ny][nx] = neighbor_walls & ~opposite_bit

                return

        raise ValueError("Duvar yalnızca komşu hücreler arasında açılabilir.")

    def _generate_perfect_maze(self) -> None:
        """İteratif rastgele DFS ile bağlı ve döngüsüz bir yapı üretir."""

        # 1. Adım: Başlangıç hücresini rastgele seç (engellenmiş 42 hücreleri
        # hariç)
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

        # 2. Adım: Ziyaret edilenler kümesini ve Stacki oluştur
        # 42 hücrelerini de ziyaret edilmiş kabul ediyoruz ki duvarlala
        # oynanmasın duvar olarak kalabilsinler
        visited = {start} | self.blocked_cells
        # Adımlarımızı kaydettiğimiz stack
        stack = [start]

        # 3. Adım: Stack boşalana kadar labirenti örmeye devam et
        while stack:
            # Şu an üzerinde bulunduğumuz hücre (Stack'in en üstü)
            current = stack[-1]

            # Etrafımızdaki komşulardan henüz ZİYARET EDİLMEMİŞ olanları
            # bulalım
            candidates = []
            for cell, bit_value in self._adjacent(current):
                if cell not in visited:
                    candidates.append(cell)
            if candidates:  # Eğer gidilmemiş en az bir komşu varsa
                # Rastgele bir komşu seç
                neighbor = self._rng.choice(candidates)

                # Aradaki duvarı yık (hem bizim hücrenin hem komşunun duvarı
                # açılır)
                self._knock_down_wall(current, neighbor)

                # Komşuyu ziyaret edildi olarak işaretle
                visited.add(neighbor)

                # Stacke ekle (artık yeni bulunduğumuz yer burası oldu)
                stack.append(neighbor)

            # Eğer etrafta gidecek hiç ham yol kalmadıysa (Çıkmaz sokak!):
            else:
                # Son adımı yığından çıkararak bir adım geriye (önceki hücreye)
                # sar!
                stack.pop()

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
