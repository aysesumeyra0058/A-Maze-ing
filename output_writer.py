def write_maze_output(
    output_file: str,
    grid: list[list[int]],
    entry: tuple[int, int],
    exit_position: tuple[int, int],
    directions: str,
) -> None:
    """Write the maze, entry, exit and solution to a file."""