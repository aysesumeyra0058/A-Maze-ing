"""Render the maze in the terminal."""

WALL = "█"
PASSAGE = " "

def render_maze(grid: list[list[int]]) -> None:
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

            canvas[canvas_y][canvas_x] = PASSAGE