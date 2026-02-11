"""ANSI color support for terminal output."""

ANSI_COLORS: dict[str, str] = {
    "black": "\033[30m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
    "bright_black": "\033[90m",
    "bright_red": "\033[91m",
    "bright_green": "\033[92m",
    "bright_yellow": "\033[93m",
    "bright_blue": "\033[94m",
    "bright_magenta": "\033[95m",
    "bright_cyan": "\033[96m",
    "bright_white": "\033[97m",
}

RESET = "\033[0m"
BOLD = "\033[1m"


def colorize(text: str, color: str, bold: bool = False) -> str:
    """Wrap text in ANSI color codes.

    Args:
        text: The string to colorize.
        color: Color name from ANSI_COLORS.
        bold: Whether to bold the text.

    Returns:
        The text wrapped in ANSI codes, or unmodified if color not found.
    """
    code = ANSI_COLORS.get(color, "")
    if not code:
        return text

    prefix = BOLD + code if bold else code
    return f"{prefix}{text}{RESET}"
