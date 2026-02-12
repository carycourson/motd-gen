"""System temperature widget."""

import psutil
from motd_gen.widgets.base import BaseWidget


class TemperatureWidget(BaseWidget):
    """Displays system temperatures from hardware sensors."""

    @property
    def name(self) -> str:
        return "temperature"

    def render(self) -> list[str]:
        """Read temperatures via psutil sensors."""
        label = self.config.get("label", "Temperature")
        show_all = self.config.get("show_all", False)
        unit = self.config.get("unit", "f")

        try:
            temps = psutil.sensors_temperatures()

            if not temps:
                return [f"{label}: no sensors found"]

            if show_all:
                return self._render_all(label, temps, unit)

            # Default: show just the CPU package temp
            for chip, entries in temps.items():
                if chip in ("coretemp", "k10temp", "zenpower"):
                    for entry in entries:
                        if "package" in entry.label.lower() or "tctl" in entry.label.lower():
                            temp = self._format_temp(entry.current, unit)
                            return [f"{label}: {temp}"]

            # Fallback: first sensor with a reasonable reading
            for chip, entries in temps.items():
                for entry in entries:
                    if entry.current > 0:
                        temp = self._format_temp(entry.current, unit)
                        return [f"{label}: {temp} ({chip})"]

            return [f"{label}: no valid readings"]

        except Exception as e:
            return [f"{label}: unavailable ({e})"]

    def _format_temp(self, celsius: float, unit: str) -> str:
        """Format temperature in the configured unit."""
        if unit == "f":
            return f"{celsius * 9/5 + 32:.1f}°F"
        return f"{celsius:.1f}°C"

    def _render_all(self, label: str, temps: dict, unit: str) -> list[str]:
        """Render all available sensor readings."""
        lines = [f"{label}:"]
        for chip, entries in temps.items():
            for entry in entries:
                if entry.current <= 0:
                    continue
                name = entry.label or chip
                temp = self._format_temp(entry.current, unit)
                lines.append(f"  {name}: {temp}")
        return lines