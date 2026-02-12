"""Logged-in users widget."""

import subprocess
from motd_gen.widgets.base import BaseWidget


class UsersWidget(BaseWidget):
    """Displays currently logged-in users via loginctl."""

    @property
    def name(self) -> str:
        return "users"

    def render(self) -> list[str]:
        """List logged-in users via loginctl."""
        label = self.config.get("label", "Users")
        show_list = self.config.get("show_list", True)

        try:
            result = subprocess.run(
                ["loginctl", "list-sessions", "--no-legend"],
                capture_output=True, text=True, timeout=5
            )

            seen_users = {}

            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                parts = line.split()
                if len(parts) >= 3:
                    session_id = parts[0]
                    user = parts[2]

                    # Get session type (graphical, tty, etc.)
                    type_result = subprocess.run(
                        ["loginctl", "show-session", session_id,
                         "--property=Type", "--value"],
                        capture_output=True, text=True, timeout=5
                    )
                    session_type = type_result.stdout.strip() or "unknown"

                    # Skip background/manager sessions
                    if session_type in ("unspecified", ""):
                        continue
                    
                    # Get remote host if any
                    remote_result = subprocess.run(
                        ["loginctl", "show-session", session_id,
                         "--property=Remote,RemoteHost", "--value"],
                        capture_output=True, text=True, timeout=5
                    )
                    remote_lines = remote_result.stdout.strip().split("\n")
                    is_remote = remote_lines[0] == "yes" if remote_lines else False
                    remote_host = remote_lines[1] if len(remote_lines) > 1 and is_remote else ""

                    type_label = session_type
                    if remote_host:
                        type_label = f"ssh from {remote_host}"

                    if user not in seen_users:
                        seen_users[user] = []
                    seen_users[user].append(type_label)

            unique_count = len(seen_users)
            total_sessions = sum(len(s) for s in seen_users.values())

            if unique_count == 0:
                return [f"{label}: none"]

            lines = [f"{label}: {total_sessions} session{'s' if total_sessions != 1 else ''} ({unique_count} user{'s' if unique_count != 1 else ''})"]

            if show_list:
                for user, types in seen_users.items():
                    type_str = ", ".join(types)
                    lines.append(f"  {user}: {type_str}")

            return lines

        except Exception as e:
            return [f"{label}: unavailable ({e})"]