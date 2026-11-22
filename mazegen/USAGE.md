# mazegen — Usage

`mazegen` is a reusable maze generator and shortest-path solver.
Python 3.10 or later is required.

## Installation

Run the following command from the directory containing the wheel:

```bash
python3 -m pip install ./mazegen-1.0.0-py3-none-any.whl
```

This installs `mazegen` into the Python environment selected by `python3`.
You do not need the original project directory or a separate build step.

Alternatively, install the source distribution:

```bash
python3 -m pip install ./mazegen-1.0.0.tar.gz
```

Choose one distribution format; installing both is unnecessary.

## Create a maze

```python
from mazegen import MazeGenerator

maze = MazeGenerator(
    width=20,
    height=15,
    perfect=True,
    seed=42,
    entry=(0, 0),
    exit=(19, 14),
)
```

The constructor generates the maze automatically. No separate `generate()`
call is needed.

### Parameters

| Parameter | Description | Default |
| --- | --- | --- |
| `width` | Positive integer: number of columns. | Required |
| `height` | Positive integer: number of rows. | Required |
| `perfect` | `True` creates a cycle-free maze. `False` creates a board with alternative routes and few dead-ends. | `False` |
| `seed` | Integer for reproducible generation. `None` selects a seed automatically. | `None` |
| `entry` | Optional `(x, y)` coordinates protected from the "42" pattern. | `None` |
| `exit` | Optional `(x, y)` coordinates protected from the "42" pattern. | `None` |

Coordinates must be inside the maze. When both endpoints are supplied,
they must differ.

Use identical parameters and seed to reproduce the same maze. To generate
another maze, create another instance with a different seed or `seed=None`.

## Access the maze structure

```python
grid = maze.get_grid()
blocked_cells = maze.get_blocked_cells()
actual_seed = maze.get_seed()
neighbors = maze.neighbors((0, 0))
```

- `get_grid()` returns an independent copy of the integer wall grid.
- `get_blocked_cells()` returns the coordinates forming the closed "42" pattern.
- `get_seed()` returns the actual seed used.
- `neighbors(cell)` returns accessible neighbouring cells.

Coordinates use `(x, y)`, while grid access uses `grid[y][x]`.
Increasing `x` moves east; increasing `y` moves south.

Each grid integer encodes the cell's closed walls:

| Direction | Value |
| --- | --- |
| North | 1 |
| East | 2 |
| South | 4 |
| West | 8 |

A set bit means a closed wall. For example:

```python
cell = grid[0][0]

if cell & 2:
    print("The east wall is closed.")
```

A value of `15` means all four walls are closed.

## Find a shortest path

```python
path = maze.solve((0, 0), (19, 14))

if path is None:
    print("No path found.")
else:
    print("Path:", path)
    print("Moves:", len(path) - 1)
```

`solve()` uses BFS and returns a shortest path as a list of `(x, y)`
coordinates, including entry and exit. It returns `None` if no route exists.

Provide the intended endpoints when constructing the maze so the "42"
pattern cannot cover them.

### Convert the path to directions

```python
from mazegen.solver import path_to_directions

if path is not None:
    directions = path_to_directions(path)
    print(directions)
```

The result uses `N`, `E`, `S` and `W` for north, east, south and west.
For example, `[(0, 0), (1, 0), (1, 1)]` becomes `"ES"`.

## Error handling

Invalid generation parameters or settings that cannot satisfy the
generation constraints raise `ValueError`.

```python
try:
    maze = MazeGenerator(width=20, height=15, perfect=True, seed=42)
except ValueError as error:
    print(f"Generation failed: {error}")
```

The package provides maze data and solutions. Terminal rendering,
configuration parsing and output-file creation belong to the separate
application.

## License

MIT. See the license included in the distribution.