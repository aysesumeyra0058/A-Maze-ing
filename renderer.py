"""Render the maze in the terminal."""

WALL = "█"
PASSAGE = " "

def render_maze(grid: list[list[int]]) -> None:
    """Display the maze in the terminal."""

    # Get the maze dimensions
    height = len(grid)
    width = len(grid[0])