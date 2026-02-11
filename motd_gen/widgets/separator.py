"""Separator line widget."""

from motd_gen.widgets.base import BaseWidget
from motd_gen.colors import colorize


class SeparatorWidget(BaseWidget):
    """Renders a horizontal separator line."""

    @property
    def name(self) -> str:
        return "separator"

    def render(self) -> list[str]:
        """Draw a line across the terminal width."""
        char = self.config.get("char", "─")
        color = self.config.get("color", "")
        bold = self.config.get("bold", False)
        line = char * self.width

        if color:
            line = colorize(line, color, bold)

        return [line]
