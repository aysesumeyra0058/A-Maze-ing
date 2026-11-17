"""Render the maze in the terminal."""

WALL = "█"
PASSAGE = " "
PATTERN = "P"
PATTERN_COLOR = "\033[34m"
RESET = "\033[0m"

def render_maze(
    grid: list[list[int]],
    blocked_cells: set[tuple[int, int]],
    entry: tuple[int, int],
    exit_position: tuple[int, int],
    path: list[tuple[int, int]],
) -> None:
    """Display the maze in the terminal."""

    # Get the maze dimensions
    height = len(grid)
    width = len(grid[0])
        # Calculate the drawing dimensions
    canvas_height = height * 2 + 1
    canvas_width = width * 2 + 1

    # Fill the drawing area with walls
    canvas: list[list[str]] = []
    for _ in range(canvas_height):
        row = [WALL] * canvas_width
        canvas.append(row)
    # Open the center of each maze cell
    for y in range(height):
        for x in range(width):
            canvas_y = y * 2 + 1
            canvas_x = x * 2 + 1

            # Keep the cells forming the 42 pattern filled with walls
            if (x, y) not in blocked_cells:
                canvas[canvas_y][canvas_x] = PASSAGE
            # Read the wall information for this cell
            cell = grid[y][x]

            # Open the passage to the east if there is no wall
            if not (cell & 2):
                canvas[canvas_y][canvas_x + 1] = PASSAGE

            # Open the passage to the south if there is no wall
            if not (cell & 4):
                canvas[canvas_y + 1][canvas_x] = PASSAGE

    # Mark the centers, walls and corners of the 42 cells
    for x, y in blocked_cells:
        center_y = y * 2 + 1
        center_x = x * 2 + 1

        for dy in range(-1, 2):
            for dx in range(-1, 2):
                canvas[center_y + dy][center_x + dx] = PATTERN

    # Mark the centers of cells along the solution path
    for x, y in path:
        canvas[y * 2 + 1][x * 2 + 1] = "."

    # Connect consecutive solution cells through their shared passage
    for i in range(1, len(path)):
        previous_x, previous_y = path[i - 1]
        current_x, current_y = path[i]

        passage_x = previous_x + current_x + 1
        passage_y = previous_y + current_y + 1

        canvas[passage_y][passage_x] = "."

    # Mark the entry and exit at their cell centers
    entry_x, entry_y = entry
    exit_x, exit_y = exit_position

    canvas[entry_y * 2 + 1][entry_x * 2 + 1] = "S"
    canvas[exit_y * 2 + 1][exit_x * 2 + 1] = "E"

    # Display the 42 pattern in blue
    for row in canvas:
        output = ""
        for character in row:
            if character == PATTERN:
                output += PATTERN_COLOR + WALL * 2 + RESET
            elif character in (".", "S", "E"):
                output += character + " "
            else:
                output += character * 2
        print(output)