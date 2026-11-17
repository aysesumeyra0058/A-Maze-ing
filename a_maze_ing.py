import sys

from config_parser import parse_config
from mazegen import MazeGenerator 
# > MazeGenerator -> lab create class

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

    # Handle configuration, generation and file access errors
    except (ValueError, OSError) as error:
        print(f"Error: {error}")