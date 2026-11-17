import sys

from config_parser import parse_config
from mazegen import MazeGenerator 
# > MazeGenerator -> lab create class
from solver import bfs, path_to_directions
from output_writer import write_maze_output

if __name__ == "__main__":
    try:
        # Require exactly one config file argument
        if len(sys.argv) != 2:
            raise ValueError(
                "Usage: python3 a_maze_ing.py <config_file>"
            )

        # Read and validate configuration values
        config = parse_config(sys.argv[1])

        # Generate a maze using the validated values
        maze = MazeGenerator(
            width=config.width,
            height=config.height,
            entry=config.entry,
            exit=config.exit_position,
            perfect=config.perfect,
            seed=config.seed,
        )

        print("Maze generated successfully!")
        print(f"Seed: {maze.get_seed()}")
        # Find a shortest path through the generated maze
        path = bfs(maze.neighbors, config.entry, config.exit_position)

        # Display the result
        if path is None:
            print("No path found.")
        else:
            print(f"Solution path: {path}")
            print(f"Number of moves: {len(path) - 1}")
            # Convert the solution path into direction letters
            directions = path_to_directions(path)
            print(f"Directions: {directions}")
                        # Save the maze and its solution to the output file
            write_maze_output(
                output_file=config.output_file,
                grid=maze.get_grid(),
                entry=config.entry,
                exit_position=config.exit_position,
                directions=directions,
            )

            print(f"Maze saved to: {config.output_file}")

    # Handle configuration, generation and file access errors
    except (ValueError, OSError) as error:
        print(f"Error: {error}")