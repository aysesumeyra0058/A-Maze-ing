def write_maze_output(
    output_file: str,
    grid: list[list[int]],
    entry: tuple[int, int],
    exit_position: tuple[int, int],
    directions: str,
) -> None:
    """Write the maze, entry, exit and solution to a file."""

    # Open the output file for writing
    with open(output_file, "w", encoding="utf-8") as file:
        # Write each maze row as hexadecimal digits
        for row in grid:
            for cell in row:
                file.write(f"{cell:X}")
            file.write("\n")

        # Separate the maze from the coordinates and solution
        file.write("\n")

        # Write entry and exit coordinates in x,y format
        file.write(f"{entry[0]},{entry[1]}\n")
        file.write(f"{exit_position[0]},{exit_position[1]}\n")

        # Write the solution as direction letters
        file.write(f"{directions}\n")