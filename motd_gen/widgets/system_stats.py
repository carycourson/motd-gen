"""System stats widget: CPU, memory, and disk usage."""

import psutil
from motd_gen.widgets.base import BaseWidget


class SystemStatsWidget(BaseWidget):
    """Displays CPU, memory, and disk usage."""

    @property
    def name(self) -> str:
        return "system_stats"

    def render(self) -> list[str]:
        """Gather system stats and format as labeled lines."""
        lines = []

        try:
            cpu_percent = psutil.cpu_percent(interval=0.5)
            lines.append(f"  CPU:    {cpu_percent:.1f}%")
        except Exception:
            lines.append("  CPU:    unavailable")

        try:
            mem = psutil.virtual_memory()
            used_gb = mem.used / (1024 ** 3)
            total_gb = mem.total / (1024 ** 3)
            lines.append(f"  Memory: {used_gb:.1f}/{total_gb:.1f} GB ({mem.percent}%)")
        except Exception:
            lines.append("  Memory: unavailable")

        try:
            disk_paths = self.config.get("disk_paths", ["/"])
            for path in disk_paths:
                disk = psutil.disk_usage(path)
                used_gb = disk.used / (1024 ** 3)
                total_gb = disk.total / (1024 ** 3)
                lines.append(f"  Disk:   {used_gb:.1f}/{total_gb:.1f} GB ({disk.percent}%) [{path}]")
        except Exception:
            lines.append("  Disk:   unavailable")

        label = self.config.get("label", "System Stats")
        return [label] + lines
