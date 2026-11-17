import sys

from config_parser import parse_config
from mazegen import MazeGenerator
# > MazeGenerator -> lab create class
from solver import bfs, path_to_directions
from output_writer import write_maze_output
from renderer import render_maze

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
            # Display the maze and keep the 42 pattern filled
            # Display the maze with its entry and exit
            # Keep the current solution visibility

            show_solution = True
            # Available wall colors: white, green, cyan, magenta
            wall_colors = [
                "\033[37m",
                "\033[32m",
                "\033[36m",
                "\033[35m",
            ]
            color_index = 0

            # Display the maze and wait for user commands
            while True:
                render_maze(
                    grid=maze.get_grid(),
                    blocked_cells=maze.get_blocked_cells(),
                    entry=config.entry,
                    exit_position=config.exit_position,
                    path=path,
                    show_solution=show_solution,
                    wall_color=wall_colors[color_index],
                )

                try:
                    command = input(
                        "[s] Show/hide solution | "
                        "[c] Change wall color | "
                        "[r] Regenerate | [q] Quit: "
                    ).strip().lower()
                except (EOFError, KeyboardInterrupt):
                    print("\nExiting.")
                    break

                if command == "q":
                    break
                elif command == "s":
                    show_solution = not show_solution
                elif command == "c":
                    color_index = (color_index + 1) % len(wall_colors)
                elif command == "r":
                    try:
                        # Generate a new maze with a fresh random seed
                        new_maze = MazeGenerator(
                            width=config.width,
                            height=config.height,
                            entry=config.entry,
                            exit=config.exit_position,
                            perfect=config.perfect,
                            seed=None,
                        )

                        # Find a shortest path through the new maze
                        new_path = bfs(
                            new_maze.neighbors,
                            config.entry,
                            config.exit_position,
                        )

                        if new_path is None:
                            raise ValueError(
                                "No path found in the new maze"
                            )

                        # Save the new maze and its solution
                        new_directions = path_to_directions(new_path)
                        write_maze_output(
                            output_file=config.output_file,
                            grid=new_maze.get_grid(),
                            entry=config.entry,
                            exit_position=config.exit_position,
                            directions=new_directions,
                        )

                        # Use the new maze after all steps succeed
                        maze = new_maze
                        path = new_path
                        directions = new_directions

                        print(f"New maze seed: {maze.get_seed()}")
                        print(
                            f"Number of moves: {len(path) - 1}"
                        )

                    except (ValueError, OSError) as error:
                        print(f"Regeneration failed: {error}")
                else:
                    print("Unknown command.")

    # Handle configuration, generation and file access errors
    except (ValueError, OSError) as error:
        print(f"Error: {error}")
