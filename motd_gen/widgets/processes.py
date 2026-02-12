"""Process count widget."""

import psutil
from motd_gen.widgets.base import BaseWidget


class ProcessesWidget(BaseWidget):
    """Displays the number of running processes."""

    @property
    def name(self) -> str:
        return "processes"

    def render(self) -> list[str]:
        """Count running processes."""
        label = self.config.get("label", "Processes")

        try:
            count = len(psutil.pids())
            return [f"{label}: {count}"]
        except Exception as e:
            return [f"{label}: unavailable ({e})"]