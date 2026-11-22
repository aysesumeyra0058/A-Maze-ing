*This project has been created as part of the 42 curriculum by aykesim, dilkayma.*

# A-Maze-ing

## Description

**A-Maze-ing** is a maze generator written in Python 3.10+. The program reads a plain-text configuration file, generates a random (and reproducible, thanks to a seed) maze, writes it to a file using a hexadecimal wall encoding, and displays it in the terminal with an interactive menu.

Main features:

- Random maze generation with seed-based reproducibility.
- Two modes, selected with the `PERFECT` key:
  - `PERFECT=True`: a perfect maze (exactly one path between entry and exit, no loops).
  - `PERFECT=False` (default): a playable, Pac-Man-like board (full connectivity, open corners and centre, at least two independent routes, very few dead-ends).
- A visible **"42"** pattern made of fully closed cells (omitted with a console error message if the maze is too small).
- Shortest path computation from entry to exit using **BFS**.
- Output file with the hexadecimal wall representation, the entry, the exit and the shortest path (`N`, `E`, `S`, `W`).
- Terminal ASCII rendering with an interactive menu.
- A reusable maze generator packaged as a `mazegen-*` pip package.

## Instructions

### Requirements

- Python 3.10 or later
- `pip` (a virtual environment is recommended)

### Makefile rules

| Rule          | Description                                                           |
|---------------|-----------------------------------------------------------------------|
| `make install`| Install the project dependencies                                      |
| `make run`    | Run `a_maze_ing.py` with the default `config.txt`                     |
| `make debug`  | Run the main script with Python's debugger (`pdb`)                    |
| `make clean`  | Remove `__pycache__`, `.mypy_cache` and other temporary files         |
| `make lint`   | Run `flake8 .` and `mypy .` with the mandatory flags                  |
| `make lint-strict` | Run `flake8 .` and `mypy . --strict` (optional)                  |

### Execution

```bash
python3 a_maze_ing.py config.txt
```

`config.txt` is the only argument. A default configuration file is provided in the repository.

### Interactive menu

While the program is running, the following actions are available:

1. **Re-generate** a new maze and display it.
2. **Show / Hide** the shortest path from entry to exit.
3. **Change the wall colours.**
4. **Quit.**

### Building the reusable package

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install build
python3 -m build
```

This re-creates the `mazegen-*.tar.gz` and `mazegen-*.whl` files. To install the generated package in another environment:

```bash
pip install mazegen-*.whl
```

## Configuration file

The configuration file contains one `KEY=VALUE` pair per line. Lines starting with `#` are comments and are ignored. Empty lines are ignored.

| Key           | Description                         | Example            |
|---------------|-------------------------------------|--------------------|
| `WIDTH`       | Maze width (number of cells)        | `WIDTH=20`         |
| `HEIGHT`      | Maze height (number of cells)       | `HEIGHT=15`        |
| `ENTRY`       | Entry coordinates `x,y`             | `ENTRY=0,0`        |
| `EXIT`        | Exit coordinates `x,y`              | `EXIT=19,14`       |
| `OUTPUT_FILE` | Output filename                     | `OUTPUT_FILE=maze.txt` |
| `PERFECT`     | Perfect maze or playable board      | `PERFECT=True`     |

Optional keys:

| Key    | Description                                        | Example     |
|--------|----------------------------------------------------|-------------|
| `SEED` | Seed used for reproducible generation              | `SEED=42`   |

Example:

```
# Default configuration
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=True
```

Rules and error handling:

- All mandatory keys must be present.
- `WIDTH` and `HEIGHT` must be positive integers.
- `ENTRY` and `EXIT` must be two comma-separated integers, inside the maze bounds, and different from each other.
- `PERFECT` must be a boolean (`True` / `False`).
- Any invalid configuration (missing key, line without `=`, letters instead of numbers, wrong tuple format, file not found, ...) produces a clear error message and a clean exit, never a crash.

## Output file format

Each cell is written as one hexadecimal digit encoding its closed walls:

| Bit       | Direction |
|-----------|-----------|
| 0 (LSB)   | North     |
| 1         | East      |
| 2         | South     |
| 3         | West      |

A bit set to `1` means the wall is closed. Cells are written row by row, one row per line. After an empty line come three lines: the entry coordinates, the exit coordinates, and the shortest path from entry to exit using `N`, `E`, `S`, `W`. All lines end with `\n`.

## Maze generation algorithm

<!-- TODO (dilkayma): fill in the algorithm actually used -->
**Algorithm:** *(e.g. Recursive Backtracker / DFS, Prim, Kruskal ... — to be completed)*

**Why this algorithm:** *(to be completed: simplicity, produces perfect mazes as spanning trees, easy to extend to a braided / loop-based playable board by removing walls, easy seed-based reproducibility, ...)*

**Shortest path:** the solution is computed with a **Breadth-First Search (BFS)**, which guarantees the shortest path in an unweighted grid. The same path is used for the output file and for the terminal display.

## Reusable module

The maze generation logic lives in a single class (`MazeGenerator`) inside a standalone module, independent from the display and the configuration parsing. It is packaged as `mazegen-*` (`.whl` / `.tar.gz`) at the root of the repository.

### Basic example

```python
from mazegen import MazeGenerator

# Instantiate with custom parameters (size, seed, ...)
generator = MazeGenerator(width=20, height=15, seed=42)

# Generate the maze
generator.generate()

# Access the generated structure
maze = generator.maze            # grid of cells and their walls

# Access a solution (shortest path from entry to exit)
path = generator.solve()         # e.g. "ESEENE..."
```

<!-- TODO: adjust the import path, constructor arguments and attribute / method names to match the real API -->

### Custom parameters

- `width`, `height`: size of the maze.
- `seed`: same seed gives the same maze.
- entry / exit coordinates and the `perfect` flag can also be passed to the generator.

### Accessing the result

- The maze structure is available as a grid of cells; each cell knows which of its four walls (N, E, S, W) are closed. This format is not necessarily the same as the hexadecimal output file.
- The shortest path is available as a sequence of `N`, `E`, `S`, `W` moves.

### What is reusable

- The generator class (generation, seed handling, perfect / non-perfect modes, "42" pattern, solution).
- It has no dependency on the terminal rendering or on the configuration file, so it can be imported in any future project.
- The code is released under the license described in `LICENSE.md`.

## Team and project management

### Roles

- **dilkayma**: maze generator (generation logic and structure, reusable module).
- **aykesim**: BFS shortest-path solver, output file creation, terminal rendering and interactive menu, and other related parts (configuration parsing, error handling, ...).

<!-- TODO (aykesim): add anything else you handled -->

### Planning

<!-- TODO: write your initial planning and how it evolved, e.g. week-by-week -->
- **Anticipated planning:** *(to be completed)*
- **How it evolved:** *(to be completed)*

### What worked well / what could be improved

<!-- TODO: complete honestly with your own experience -->
- **Worked well:** *(e.g. clear split between generator and display/solver, early agreement on the maze data structure)*
- **Could be improved:** *(to be completed)*

### Tools used

- Python 3.10+, `flake8`, `mypy`, `pytest` / `unittest`
- Git and a shared repository
- `venv`, `build` (package building)
- `maze_analyzer.py` / `output_validator.py` (provided with the subject) to validate the output file
- AI assistant (see Resources)

## Resources

### References

- Wikipedia, *Maze generation algorithm*: https://en.wikipedia.org/wiki/Maze_generation_algorithm
- Wikipedia, *Breadth-first search*: https://en.wikipedia.org/wiki/Breadth-first_search
- Jamis Buck, *Mazes for Programmers* and his maze algorithm articles: https://weblog.jamisbuck.org/2011/2/7/maze-generation-algorithm-recap
- Python documentation: https://docs.python.org/3/ (`random`, `typing`, `collections`)
- PEP 8, PEP 257, flake8 and mypy documentation
- Python Packaging User Guide: https://packaging.python.org/

### How AI was used

AI was used as a **guide and learning support**, not as a replacement for our own work. We only kept what we understood and could explain.

- **Understanding the subject:** through interactive question-and-answer exchanges, we used AI to better understand what the module and the subject expected from us (output format, validity rules, reusable package requirements).
- **Testing phase:** AI helped us to define test ideas and edge cases (invalid configurations, small mazes, seed reproducibility, wall coherence between neighbouring cells), and to run checks. We then ran, reviewed and discussed the results together.
- **README:** AI helped us to structure this document and to make sure every requirement of the subject was covered. The content was reviewed and completed by us.

All AI suggestions were tested, reviewed and discussed between both team members before being used.

## License

See [`LICENSE.md`](LICENSE.md).
