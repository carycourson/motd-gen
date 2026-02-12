"""Core engine that loads config, resolves widgets, and assembles output."""

import os
import re
from motd_gen.config import load_config
from motd_gen.widgets.base import BaseWidget
from motd_gen.widgets.uptime import UptimeWidget
from motd_gen.widgets.system_stats import SystemStatsWidget
from motd_gen.widgets.hostname import HostnameWidget
from motd_gen.widgets.weather import WeatherWidget
from motd_gen.widgets.quote import QuoteWidget
from motd_gen.widgets.network import NetworkWidget
from motd_gen.widgets.last_login import LastLoginWidget
from motd_gen.widgets.updates import UpdatesWidget
from motd_gen.widgets.separator import SeparatorWidget
from motd_gen.widgets.public_ip import PublicIPWidget
from motd_gen.widgets.temperature import TemperatureWidget
from motd_gen.widgets.processes import ProcessesWidget
from motd_gen.widgets.users import UsersWidget
from motd_gen.widgets.os_info import OSInfoWidget

WIDGET_REGISTRY: dict[str, type[BaseWidget]] = {
    "uptime": UptimeWidget,
    "system_stats": SystemStatsWidget,
    "hostname": HostnameWidget,
    "weather": WeatherWidget,
    "quote": QuoteWidget,
    "network": NetworkWidget,
    "last_login": LastLoginWidget,
    "updates": UpdatesWidget,
    "separator": SeparatorWidget,
    "public_ip": PublicIPWidget,
    "temperature": TemperatureWidget,
    "processes": ProcessesWidget,
    "users": UsersWidget,
    "os_info": OSInfoWidget,
}


def detect_terminal_width() -> int:
    """Detect terminal width, fallback to 80."""
    try:
        return os.get_terminal_size().columns
    except OSError:
        return 80


def _strip_ansi(text: str) -> str:
    """Remove ANSI escape codes for accurate length calculation."""
    return re.sub(r"\033\[[0-9;]*m", "", text)


def _visible_len(text: str) -> int:
    """Get the visible length of a string, ignoring ANSI codes."""
    return len(_strip_ansi(text))


def _render_widget(widget_config: dict, width: int) -> list[str] | None:
    """Render a single widget, returning its lines or None on failure."""
    widget_type = widget_config["type"]
    enabled = widget_config.get("enabled", True)

    if not enabled:
        return None

    widget_class = WIDGET_REGISTRY.get(widget_type)

    if widget_class is None:
        return [f"[unknown widget: {widget_type}]"]

    try:
        widget = widget_class(widget_config, width=width)
        return widget.render()
    except Exception as e:
        return [f"[{widget_type} error: {e}]"]


def _render_row(widgets_in_row: list[dict], width: int, gap: int = 4) -> str:
    """Render multiple widgets side by side, packed by content width."""
    # Render each widget
    columns: list[list[str]] = []
    for widget_config in widgets_in_row:
        lines = _render_widget(widget_config, width)
        if lines is None:
            lines = []
        columns.append(lines)

    if not columns:
        return ""

    # Calculate the widest visible line in each column
    col_widths = []
    for col in columns:
        max_line = max((_visible_len(line) for line in col), default=0)
        col_widths.append(max_line)

    # Pad all columns to the same height
    max_height = max(len(col) for col in columns)
    for col in columns:
        while len(col) < max_height:
            col.append("")

    # Merge columns side by side
    merged_lines = []
    for row_idx in range(max_height):
        parts = []
        for col_idx, col in enumerate(columns):
            cell = col[row_idx]
            if col_idx < len(columns) - 1:
                padding = col_widths[col_idx] - _visible_len(cell) + gap
                parts.append(cell + " " * max(padding, 1))
            else:
                parts.append(cell)
        merged_lines.append("".join(parts))

    return "\n".join(merged_lines)


def build_motd(config_path: str) -> str:
    """Load config, run each enabled widget, and assemble the MOTD.

    Args:
        config_path: Path to the JSON config file.

    Returns:
        The fully assembled MOTD as a single string.
    """
    config = load_config(config_path)
    settings = config.get("settings", {})
    default_spacing = settings.get("spacing", 1)
    width = settings.get("width", detect_terminal_width())

    widget_blocks: list[str] = []
    widgets = config["widgets"]
    i = 0

    while i < len(widgets):
        widget_config = widgets[i]

        if not widget_config.get("enabled", True):
            i += 1
            continue

        row = widget_config.get("row")

        if row is not None:
            # Collect all widgets with the same row number
            row_widgets = [widget_config]
            j = i + 1
            while j < len(widgets):
                if widgets[j].get("row") == row and widgets[j].get("enabled", True):
                    row_widgets.append(widgets[j])
                    j += 1
                elif widgets[j].get("row") is not None and widgets[j].get("row") != row:
                    break
                else:
                    break

            block = _render_row(row_widgets, width)

            # Use spaceAfter from the last widget in the row
            space_after = row_widgets[-1].get("spaceAfter", default_spacing)
            block += "\n" * space_after

            widget_blocks.append(block)
            i = j
        else:
            # Single full-width widget
            lines = _render_widget(widget_config, width)
            if lines is not None:
                block = "\n".join(lines)
                space_after = widget_config.get("spaceAfter", default_spacing)
                block += "\n" * space_after
                widget_blocks.append(block)
            i += 1

    return "\n".join(widget_blocks)