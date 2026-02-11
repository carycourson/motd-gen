"""Available package updates widget."""

import subprocess
from motd_gen.widgets.base import BaseWidget


class UpdatesWidget(BaseWidget):
    """Displays count of available apt package updates."""

    @property
    def name(self) -> str:
        return "updates"

    def render(self) -> list[str]:
        """Check apt for available updates."""
        label = self.config.get("label", "Updates")
        show_list = self.config.get("show_list", False)
        max_listed = self.config.get("max_listed", 10)

        try:
            result = subprocess.run(
                ["apt", "list", "--upgradable"],
                capture_output=True, text=True, timeout=30
            )

            # First line is always "Listing..." header
            packages = [
                line.split("/")[0]
                for line in result.stdout.strip().split("\n")[1:]
                if line and "/" in line
            ]

            count = len(packages)

            if count == 0:
                return [f"{label}: system is up to date"]

            lines = [f"{label}: {count} package{'s' if count != 1 else ''} available"]

            if show_list:
                for pkg in packages[:max_listed]:
                    lines.append(f"  - {pkg}")
                if count > max_listed:
                    lines.append(f"  ... and {count - max_listed} more")

            return lines

        except Exception as e:
            return [f"{label}: unavailable ({e})"]