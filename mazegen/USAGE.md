# mazegen — Usage

`mazegen` provides a reusable maze generator and a BFS shortest-path solver. It requires Python 3.10 or later and uses only the Python standard library. Configuration parsing, terminal rendering and the main application are separate from this package.

## Installation

Install the distribution file using the Python interpreter of your chosen environment:

```bash
python3 -m pip install ./mazegen-1.0.0-py3-none-any.whl
```

Alternatively, install the source distribution:

```bash
python3 -m pip install ./mazegen-1.0.0.tar.gz
```

## Basic example

```python
from mazegen import MazeGenerator
from mazegen.solver import path_to_directions

maze = MazeGenerator(
    width=20,
    height=15,
    perfect=True,
    seed=42,
    entry=(0, 0),
    exit=(19, 14),
)

# The constructor generates the maze automatically.
grid = maze.get_grid()
print("Actual seed:", maze.get_seed())

path = maze.solve((0, 0), (19, 14))
if path is None:
    print("No path found.")
else:
    print("Coordinate path:", path)
    print("Number of moves:", len(path) - 1)
    print("Directions:", path_to_directions(path))
```

There is no separate `generate()` method. Create another instance to generate another maze. Use `seed=None` to select a fresh random seed, or reuse the same seed and parameters to reproduce a maze.

## Constructor parameters

| Parameter | Default | Description |
| --- | --- | --- |
| `width` | Required | Positive integer; number of columns. |
| `height` | Required | Positive integer; number of rows. |
| `perfect` | `False` | `True` creates a connected, cycle-free maze. `False` adds cycles and reduces dead-ends. |
| `seed` | `None` | Integer seed, or `None` to select one automatically. |
| `entry` | `None` | Optional `(x, y)` integer tuple inside the maze; protected from the "42" pattern. |
| `exit` | `None` | Optional `(x, y)` integer tuple inside the maze; protected from the "42" pattern. |

When both endpoints are provided to the constructor, they must differ. Passing them is recommended when solving: endpoints omitted during construction are not protected from the pattern.

In non-perfect mode, the four corners and centre remain available as corridors, at least two independent cycles are required, and at most two dead-ends are accepted. Completely open 3×3 areas are prevented. Impossible generation settings raise `ValueError`.

## Accessing the maze

```python
grid = maze.get_grid()
blocked_cells = maze.get_blocked_cells()
seed = maze.get_seed()
accessible_neighbors = maze.neighbors((0, 0))
```

- Coordinates use `(x, y)`; grid access is `grid[y][x]`.
- Increasing `x` moves east; increasing `y` moves south.
- `get_grid()` returns a copy of the integer wall grid.
- `get_blocked_cells()` returns a copy of the set of fully closed "42" cell coordinates.
- `get_seed()` returns the actual seed, including an automatically selected seed.
- `neighbors(cell)` returns accessible neighbours in north, east, south, west order.

Each grid integer encodes closed walls:

| Direction | Value |
| --- | --- |
| North | 1 |
| East | 2 |
| South | 4 |
| West | 8 |

A set bit means a closed wall. For example, `cell & 2` is nonzero when the east wall is closed. A value of `15` means all four walls are closed. This in-memory representation uses integers, not hexadecimal strings.

The generator preserves exterior walls and matching walls between neighbouring cells. If the "42" pattern cannot be placed under the implemented constraints, a warning is printed and generation proceeds without it.

## Accessing a solution

```python
path = maze.solve((0, 0), (19, 14))
```

The result is a shortest path as a list of coordinate tuples, including both endpoints. If a route is unavailable, including when an endpoint is part of the closed pattern, the result is `None`. Out-of-bounds solution endpoints raise `ValueError`.

Convert a path to compass directions with:

```python
from mazegen.solver import path_to_directions

if path is not None:
    directions = path_to_directions(path)
```

`N`, `E`, `S` and `W` represent one-cell moves. The number of moves is `len(path) - 1`. Consecutive coordinates must be cardinally adjacent; otherwise conversion raises `ValueError`.

## Error handling

For user-supplied generation parameters, catch `ValueError` at the application boundary:

```python
try:
    maze = MazeGenerator(width=20, height=15, perfect=True, seed=42)
except ValueError as error:
    print(f"Generation failed: {error}")
```

## License

MIT. See the license included in the distribution and `LICENSE.md` in the source repository.
