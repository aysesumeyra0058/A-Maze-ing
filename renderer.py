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
            # Read the wall information for this cell
            cell = grid[y][x]

            # Open the passage to the east if there is no wall
            if not (cell & 2):
                canvas[canvas_y][canvas_x + 1] = PASSAGE

            # Open the passage to the south if there is no wall
            if not (cell & 4):
                canvas[canvas_y + 1][canvas_x] = PASSAGE
    
    # Print each drawing row, doubling characters for better proportions
    for row in canvas:
        print("".join(character * 2 for character in row))