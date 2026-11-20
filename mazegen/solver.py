from collections import deque
from collections.abc import Callable


def bfs(
    get_neighbors: Callable[
        [tuple[int, int]], list[tuple[int, int]]
    ],
    entry: tuple[int, int],
    exit_cell: tuple[int, int],
) -> list[tuple[int, int]] | None:
    """Find a shortest path between two cells."""

    # Add the entry cell to the queue
    queue: deque[tuple[int, int]] = deque([entry])

    # Mark the entry cell as discovered
    visited: set[tuple[int, int]] = {entry}

    # Store which cell we came from; the entry has no previous cell
    previous: dict[
        tuple[int, int], tuple[int, int] | None
    ] = {entry: None}

    while queue:
        # Remove the first cell from the queue and assign it to current
        current = queue.popleft()

        if current == exit_cell:
            break

        for neighbor in get_neighbors(current):
            if neighbor not in visited:
                # Mark the neighbor as discovered
                visited.add(neighbor)

                # Record which cell we reached the neighbor from
                previous[neighbor] = current

                # Add the neighbor to the queue for later examination
                queue.append(neighbor)

    # Stop if the exit was not discovered
    if exit_cell not in visited:
        return None

    # Build the path backwards, starting from the exit
    path: list[tuple[int, int]] = []
    step: tuple[int, int] | None = exit_cell

    while step is not None:
        path.append(step)
        step = previous[step]

    # Reverse the path into entry-to-exit order
    path.reverse()
    return path


# [(0, 0), (1, 0), (1, 1)] → "ES"
# Convert the path found by BFS into N, E, S, W direction letters.
def path_to_directions(path: list[tuple[int, int]]) -> str:
    """Convert a coordinate path into compass directions."""
    directions = ""

    for i in range(1, len(path)):
        previous_x, previous_y = path[i - 1]
        current_x, current_y = path[i]

        dx = current_x - previous_x
        dy = current_y - previous_y

        # Identify the direction between consecutive cells
        if dx == 1 and dy == 0:
            directions += "E"
        elif dx == -1 and dy == 0:
            directions += "W"
        elif dx == 0 and dy == 1:
            directions += "S"
        elif dx == 0 and dy == -1:
            directions += "N"
        else:
            raise ValueError("Path contains a non-adjacent move")

    return directions


if __name__ == "__main__":
    neighbors = {
        (0, 0): [(1, 0), (0, 1)],
        (1, 0): [(0, 0), (1, 1)],
        (0, 1): [(0, 0)],
        (1, 1): [(1, 0)],
    }

    def get_neighbors(
        cell: tuple[int, int],
    ) -> list[tuple[int, int]]:
        """Return the neighbors of a cell."""
        return neighbors[cell]

    result = bfs(get_neighbors, (0, 1), (1, 1))

    if result is None:
        print("Çıkışa ulaşılamadı.")
    else:
        print(f"Çözüm yolu: {result}")
