"""Configuration loader and validator."""

import json
from pathlib import Path
from typing import Any


def load_config(config_path: str | Path) -> dict[str, Any]:
    """Load and validate the MOTD configuration file.

    Args:
        config_path: Path to the JSON config file.

    Returns:
        Parsed configuration dictionary.

    Raises:
        FileNotFoundError: If config file doesn't exist.
        json.JSONDecodeError: If config file is invalid JSON.
        ValueError: If config is missing required fields.
    """
    path = Path(config_path)

    if not path.exists():
        raise FileNotFoundError(f"Config not found: {path}")

    with open(path, "r") as f:
        config = json.load(f)

    if "widgets" not in config:
        raise ValueError("Config must contain a 'widgets' list")

    if not isinstance(config["widgets"], list):
        raise ValueError("'widgets' must be a list")

    for i, widget in enumerate(config["widgets"]):
        if "type" not in widget:
            raise ValueError(f"Widget at index {i} missing required 'type' field")

    return config
