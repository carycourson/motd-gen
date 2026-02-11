"""Last login widget using systemd journal."""

import subprocess
from motd_gen.widgets.base import BaseWidget


class LastLoginWidget(BaseWidget):
    """Displays recent login sessions from systemd-logind."""

    @property
    def name(self) -> str:
        return "last_login"

    def render(self) -> list[str]:
        """Parse journalctl for recent login sessions."""
        label = self.config.get("label", "Last Login")
        count = self.config.get("count", 3)

        try:
            result = subprocess.run(
                [
                    "journalctl", "-t", "systemd-logind",
                    "--no-pager", "-n", "50", "--output", "short"
                ],
                capture_output=True, text=True, timeout=5
            )

            lines = [f"{label}:"]
            entries = 0
            seen = set()

            for line in reversed(result.stdout.strip().split("\n")):
                if "New session" not in line:
                    continue

                parts = line.split()
                date_str = f"{parts[0]} {parts[1]} {parts[2]}"

                msg = line.split("]: ", 1)[1] if "]: " in line else ""
                user = msg.split("of user ")[-1].rstrip(".")

                key = f"{user}-{date_str}"
                if key in seen:
                    continue
                seen.add(key)

                lines.append(f"  {user} at {date_str}")
                entries += 1

                if entries >= count:
                    break

            if entries == 0:
                lines.append("  No recent logins found")

            return lines

        except Exception as e:
            return [f"{label}: unavailable ({e})"]