"""Operating system information widget."""

from cProfile import label
import platform
from pathlib import Path
from motd_gen.widgets.base import BaseWidget


class OSInfoWidget(BaseWidget):
    """Displays OS name, version, and codename."""

    @property
    def name(self) -> str:
        return "os_info"

    def render(self) -> list[str]:
        """Read OS information from /etc/os-release."""
        label = self.config.get("label", "OS")

        try:
            os_data = self._parse_os_release()
            pretty_name = os_data.get("PRETTY_NAME", "Unknown")
            codename = os_data.get("VERSION_CODENAME", "")
            kernel = platform.release()

            parts = [f"{label}: {pretty_name}"]
            if codename:
                parts[0] += f" ({codename})"

            show_kernel = self.config.get("show_kernel", True)
            if show_kernel:
                indent = " " * (len(label) + 2)
                parts.append(f"{indent}Kernel: {kernel}")

            return parts

        except Exception as e:
            return [f"{label}: unavailable ({e})"]

    def _parse_os_release(self) -> dict[str, str]:
        """Parse /etc/os-release into a dictionary."""
        data = {}
        path = Path("/etc/os-release")

        if not path.exists():
            return data

        for line in path.read_text().strip().split("\n"):
            if "=" in line:
                key, value = line.split("=", 1)
                data[key] = value.strip('"')

        return data