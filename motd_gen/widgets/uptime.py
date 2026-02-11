"""System uptime widget."""

from datetime import timedelta
from motd_gen.widgets.base import BaseWidget


class UptimeWidget(BaseWidget):
    """Displays system uptime in a human-readable format."""

    @property
    def name(self) -> str:
        return "uptime"

    def render(self) -> list[str]:
        """Read /proc/uptime and format as days, hours, minutes."""
        try:
            with open("/proc/uptime", "r") as f:
                seconds = float(f.read().split()[0])

            delta = timedelta(seconds=seconds)
            days = delta.days
            hours, remainder = divmod(delta.seconds, 3600)
            minutes, _ = divmod(remainder, 60)

            parts = []
            if days:
                parts.append(f"{days}d")
            if hours:
                parts.append(f"{hours}h")
            parts.append(f"{minutes}m")

            label = self.config.get("label", "Uptime")
            return [f"{label}: {' '.join(parts)}"]

        except OSError:
            return ["Uptime: unavailable"]
