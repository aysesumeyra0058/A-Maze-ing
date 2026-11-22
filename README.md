*This project has been created as part of the 42 curriculum by aykesim, dilkayma.*

# A-Maze-ing

## Description

A-Maze-ing generates a maze from a configuration file, finds a shortest path with BFS, saves the result using hexadecimal wall encoding, and displays it in the terminal.

It supports reproducible generation with a seed, perfect and non-perfect modes, a blue "42" pattern, and an interactive menu. No bonus features are claimed.

## Instructions

### Requirements and execution

Python 3.10 or later is required. The application uses only the Python standard library. A terminal supporting ANSI colours and the Unicode block character `█` is needed for the intended display.

On Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
make install
make run
```

The direct command is:

```bash
python3 a_maze_ing.py config.txt
```

On Windows, use `py a_maze_ing.py config.txt`. Exactly one configuration file argument is required.

### Makefile

| Rule | Purpose |
| --- | --- |
| `install` | Install flake8, mypy and build. |
| `run` | Run the application with `config.txt`. |
| `debug` | Run the application with the Python debugger, pdb. |
| `clean` | Remove Python caches, package metadata directories and `build/`. |
| `lint` | Run flake8 and mypy with the subject's required flags. |
| `build` | Build both distribution formats and copy them to the repository root. |

A different configuration can be selected with `make run CONFIG=other_config.txt`.

### Interactive commands

Type a command and press Enter:

| Command | Action |
| --- | --- |
| `s` | Show or hide the shortest path. |
| `c` | Cycle through wall colours. |
| `r` | Generate a new maze with a fresh seed, solve it and update the output file. |
| `q` | Quit. |

The display uses `S` for entry, `E` for exit, dots for the solution, blocks for walls and empty spaces for passages. The "42" pattern stays blue when other wall colours change. Regeneration retains the size, endpoints and mode loaded at startup.

## Configuration file

Use one `KEY=VALUE` pair per line. Empty lines and lines whose first non-whitespace character is `#` are ignored. Leading and trailing whitespace is removed. Keys are uppercase; `PERFECT` accepts exactly `True` or `False`.

```text
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=True
SEED=42
```

| Key | Meaning and constraints |
| --- | --- |
| `WIDTH` | Positive integer: number of columns. |
| `HEIGHT` | Positive integer: number of rows. |
| `ENTRY` | Two integers in `x,y` format, inside the maze. |
| `EXIT` | Two integers in `x,y` format, inside the maze and different from entry. |
| `OUTPUT_FILE` | Non-empty output file path; its parent directory must exist. |
| `PERFECT` | `True` for a perfect maze; `False` for a non-perfect board. Required. |
| `SEED` | Optional integer. If omitted, a seed is selected and printed. |

All keys except `SEED` are mandatory. Unknown or duplicate keys, missing values, malformed lines, invalid numbers or coordinates, and file access errors are reported. Impossible generation parameters produce an error message. With identical parameters and seed, generation is reproducible.

Coordinates are `(x, y)` and grid access is `grid[y][x]`; increasing `y` moves south.

## Algorithms and maze rules

### Generation: iterative randomized DFS

The generator starts with all walls closed. It uses a stack and opens a passage to a randomly selected unvisited neighbour. When no unvisited neighbour remains, it backtracks. This builds a connected, cycle-free maze, excluding the fully closed "42" cells.

We chose DFS because it is straightforward to understand, creates a spanning tree for perfect mode, and works with a seeded random generator. The iterative implementation avoids recursive call-depth limits.

For non-perfect mode, the generator removes additional walls to reduce dead-ends and create at least two independent cycles. It accepts at most two dead-ends and keeps the four corners and centre available as corridors. Before opening an extra wall, it checks that the change will not create a completely open 3×3 area. Generation uses bounded retries and reports failure if the requested constraints cannot be met.

Shared walls are updated on both cells and exterior walls remain closed. The "42" uses a 7×5 pattern of fully closed cells; its placement preserves connectivity and protected cells. If no suitable placement is available, the program prints a warning and continues without the pattern.

### Solution: BFS

Breadth-first search explores accessible neighbours using a FIFO queue. A visited set prevents repeated discovery, and a predecessor dictionary reconstructs the route. Since each move has equal cost, BFS returns a shortest path. That same path is used for display and output.

## Output file format

The file contains `HEIGHT` rows of `WIDTH` hexadecimal digits, an empty line, entry coordinates, exit coordinates, and the shortest path as `N`, `E`, `S`, `W` letters. Each line ends with a newline.

Each digit represents the closed walls of one cell:

| Direction | Bit | Value |
| --- | --- | --- |
| North | 0 | 1 |
| East | 1 | 2 |
| South | 2 | 4 |
| West | 3 | 8 |

A set bit means a closed wall; a cleared bit means an open passage. For example, `A` (10) means east and west are closed; `F` (15) means all four walls are closed. The hexadecimal digit encodes walls, not the cell's position.

## Reusable module

The public class is `mazegen.MazeGenerator`. The `mazegen/` package contains generation and solving logic and does not depend on configuration parsing or terminal rendering.

### Build and install

From the repository root, in a build environment:

```bash
python3 -m pip install build
make build
```

This creates `dist/mazegen-1.0.0.tar.gz` and `dist/mazegen-1.0.0-py3-none-any.whl`, and copies both files to the repository root. The source archive contains the code and build configuration; the wheel is ready for installation.

For a separate installation test, from the repository root:

```bash
python3 -m venv ../mazegen-test-env
../mazegen-test-env/bin/python -m pip install ./mazegen-1.0.0-py3-none-any.whl
../mazegen-test-env/bin/python -I -c "from mazegen import MazeGenerator; print('Import OK')"
```

On Windows, the environment's interpreter is `..\mazegen-test-env\Scripts\python.exe`. To test the complete application against the installed package, copy `a_maze_ing.py`, `config_parser.py`, `renderer.py`, `output_writer.py` and `config.txt` to another directory without the source `mazegen/` folder, then run the application there using the test environment's interpreter.

### Basic usage

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

# Construction generates the maze; no separate generate() call is needed.
grid = maze.get_grid()
path = maze.solve((0, 0), (19, 14))

if path is not None:
    print(path)
    print(path_to_directions(path))
```

`width` and `height` are required. Constructor defaults are `perfect=False`, `seed=None`, `entry=None` and `exit=None`. Providing entry and exit protects them from the "42" pattern.

| Method | Result |
| --- | --- |
| `get_grid()` | Independent copy of the integer wall grid. |
| `get_blocked_cells()` | Copy of the set of "42" cell coordinates. |
| `get_seed()` | Actual seed used for generation. |
| `neighbors(cell)` | Accessible neighbours in north, east, south, west order. |
| `solve(entry, exit_position)` | Shortest coordinate path including both endpoints, or `None` if unreachable. |

`path_to_directions(path)` converts the coordinate path into a direction string. Reuse and distribution are permitted under the MIT license in `LICENSE.md`.

## Team and project management

### Roles

- **dilkayma:** maze generation, wall structure, pattern placement and generation constraints.
- **aykesim:** configuration parsing, BFS, output writing, terminal rendering and interactive application flow, testing.
- **Shared:** interface decisions, integration, packaging and documentation review.

### Initial plan and changes

We planned to separate generation from input, solving and display. We agreed on `(x, y)` coordinates and integer wall masks so both parts could be developed independently. The solver was first tested with manually defined neighbours, then connected to the generator's neighbour method. Display work followed integration. Edge-case testing led to refinements in pattern placement and error handling; packaging was completed after the main application worked.

### What worked well and what could improve

A shared coordinate and wall convention made integration easier. Separating the parser, generator, solver, writer and renderer also helped us study and test each part. We could improve the process by testing package installation earlier and updating documentation alongside API changes.

### Tools

Python, VS Code, Git/GitHub, venv, pip, setuptools, build, flake8, mypy, the supplied `maze_analyzer.py`, and an AI assistant were used during development and review.

## Resources

- [Python documentation](https://docs.python.org/3/): random, collections, typing and file handling.
- [Maze generation algorithms](https://en.wikipedia.org/wiki/Maze_generation_algorithm).
- [Breadth-first search](https://en.wikipedia.org/wiki/Breadth-first_search).
- [Python Packaging User Guide](https://packaging.python.org/).
- [PEP 257](https://peps.python.org/pep-0257/): docstrings.

### AI use

AI was used as a **guide and learning support**, not as a replacement for our own work. We only kept what we understood and could explain.

- **Understanding the subject:** through interactive question-and-answer exchanges, we used AI to better understand what the module and the subject expected from us (output format, validity rules, reusable package requirements).
- **Testing phase:** AI helped us to define test ideas and edge cases (invalid configurations, small mazes, seed reproducibility, wall coherence between neighbouring cells), and to run checks. We then ran, reviewed and discussed the results together.

## License

MIT — see [LICENSE.md](LICENSE.md).
