def read_config(path: str) -> dict[str, str]:
    settings: dict[str, str] = {}

    # Define allowed and required keys
    allowed_keys = {
        "WIDTH", "HEIGHT", "ENTRY", "EXIT",
        "OUTPUT_FILE", "PERFECT", "SEED",
    }

    required_keys = {
        "WIDTH", "HEIGHT", "ENTRY", "EXIT",
        "OUTPUT_FILE", "PERFECT",
    }

    # Read config lines
    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            # Skip empty lines and comments
            if not line:
                continue

            if line.startswith("#"):
                continue

            # Split and clean the key-value pair
            try:
                key, value = line.split("=", 1)
            except ValueError:
                raise ValueError(
                    f"Invalid config line: '{line}' - expected KEY=VALUE"
                )

            key = key.strip()
            value = value.strip()

            # Reject empty keys or values
            if not key or not value:
                raise ValueError(
                    f"Invalid config line: '{line}' - empty key or value"
                )

            # Reject unknown and duplicate keys
            if key not in allowed_keys:
                raise ValueError(f"Unknown config key: '{key}'")

            if key in settings:
                raise ValueError(f"Duplicate config key: '{key}'")

            # Store the valid key-value pair
            settings[key] = value

        # Check for missing required keys
        for key in required_keys:
            if key not in settings:
                raise ValueError(f"Missing required config key: '{key}'")

    return settings


if __name__ == "__main__":
    try:
        # Read raw config values
        config = read_config("config.txt")

        # Convert and validate maze dimensions
        width = int(config["WIDTH"])
        height = int(config["HEIGHT"])

        if width <= 0:
            raise ValueError("WIDTH must be greater than 0")

        if height <= 0:
            raise ValueError("HEIGHT must be greater than 0")

        print(f"Width: {width}, height: {height}")

        # Parse and validate entry coordinates
        entry_x_str, entry_y_str = config["ENTRY"].split(",")
        entry = (int(entry_x_str), int(entry_y_str))

        if not (0 <= entry[0] < width and 0 <= entry[1] < height):
            raise ValueError("ENTRY must be inside the maze")

        # Parse and validate exit coordinates
        exit_x_str, exit_y_str = config["EXIT"].split(",")
        exit_position = (int(exit_x_str), int(exit_y_str))

        if not (0 <= exit_position[0] < width and 0 <= exit_position[1] < height):
            raise ValueError("EXIT must be inside the maze")

        # Ensure entry and exit are different
        if entry == exit_position:
            raise ValueError("ENTRY and EXIT must be different")

        # Display validated coordinates
        print(f"Exit: {exit_position}")
        print(f"Entry: {entry}")

        # Convert and validate PERFECT

    except ValueError as error:
        print(f"Error: {error}")