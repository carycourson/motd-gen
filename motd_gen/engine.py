"""Core engine that loads config, resolves widgets, and assembles output."""

import os
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
}


def detect_terminal_width() -> int:
    """Detect terminal width, fallback to 80."""
    try:
        return os.get_terminal_size().columns
    except OSError:
        return 80


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

    for widget_config in config["widgets"]:
        widget_type = widget_config["type"]
        enabled = widget_config.get("enabled", True)

        if not enabled:
            continue

        widget_class = WIDGET_REGISTRY.get(widget_type)

        if widget_class is None:
            widget_blocks.append(f"[unknown widget: {widget_type}]")
            continue

        try:
            widget = widget_class(widget_config, width=width)
            lines = widget.render()
            block = "\n".join(lines)

            space_after = widget_config.get("spaceAfter", default_spacing)
            block += "\n" * space_after

            widget_blocks.append(block)
        except Exception as e:
            widget_blocks.append(f"[{widget_type} error: {e}]")

    return "\n".join(widget_blocks)
