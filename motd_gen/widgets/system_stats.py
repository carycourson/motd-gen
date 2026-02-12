"""System stats widget: CPU, memory, and disk usage."""

import math
import psutil
from motd_gen.widgets.base import BaseWidget


class SystemStatsWidget(BaseWidget):
    """Displays CPU, memory, and disk usage in two columns."""

    @property
    def name(self) -> str:
        return "system_stats"

    def render(self) -> list[str]:
        """Gather system stats and format as two columns."""
        label = self.config.get("label", "System Stats")
        gap = self.config.get("column_gap", 4)
        entries = []

        try:
            cpu_percent = psutil.cpu_percent(interval=0.5)
            entries.append(f"CPU:    {cpu_percent:.1f}%")
        except Exception:
            entries.append("CPU:    unavailable")

        try:
            mem = psutil.virtual_memory()
            used_gb = mem.used / (1024 ** 3)
            total_gb = mem.total / (1024 ** 3)
            entries.append(f"Memory: {used_gb:.1f}/{total_gb:.1f} GB ({mem.percent}%)")
        except Exception:
            entries.append("Memory: unavailable")

        try:
            disk_paths = self.config.get("disk_paths", ["/"])
            for path in disk_paths:
                disk = psutil.disk_usage(path)
                used_gb = disk.used / (1024 ** 3)
                total_gb = disk.total / (1024 ** 3)
                disk_label = path.rsplit("/", 1)[-1] if "/" in path and path != "/" else path
                entries.append(f"Disk:   {used_gb:.1f}/{total_gb:.1f} GB ({disk.percent}%) [{disk_label}]")
        except Exception:
            entries.append("Disk:   unavailable")

        # Split into two columns, left gets the extra if odd
        mid = math.ceil(len(entries) / 2)
        left = entries[:mid]
        right = entries[mid:]

        # Find widest line in left column
        left_width = max(len(line) for line in left)

        lines = [label]
        for i in range(len(left)):
            left_entry = f"  {left[i]}"
            if i < len(right):
                padding = left_width - len(left[i]) + gap
                lines.append(f"{left_entry}{' ' * padding}{right[i]}")
            else:
                lines.append(left_entry)

        return lines
