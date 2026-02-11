"""Hostname ASCII art banner widget."""

import socket
import pyfiglet
from motd_gen.widgets.base import BaseWidget
from motd_gen.colors import colorize


class HostnameWidget(BaseWidget):
    """Displays the system hostname as ASCII art."""

    @property
    def name(self) -> str:
        return "hostname"

    def render(self) -> list[str]:
        """Render hostname as ASCII art using pyfiglet."""
        try:
            display_name = self.config.get("custom_name", socket.gethostname())
            font = self.config.get("font", "slant")
            color = self.config.get("color", "")
            bold = self.config.get("bold", False)

            art = pyfiglet.figlet_format(display_name, font=font)
            lines = art.rstrip("\n").split("\n")

            if color:
                lines = [colorize(line, color, bold) for line in lines]

            return lines
        except Exception as e:
            return [f"[hostname error: {e}]"]
