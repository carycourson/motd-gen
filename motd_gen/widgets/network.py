"""Network information widget."""

import socket
import subprocess
import requests
from motd_gen.widgets.base import BaseWidget


class NetworkWidget(BaseWidget):
    """Displays hostname, IP addresses, gateway, and public IP in two columns."""

    @property
    def name(self) -> str:
        return "network"

    def render(self) -> list[str]:
        """Gather network info and format as two-column layout."""
        label = self.config.get("label", "Network")
        show_public_ip = self.config.get("show_public_ip", True)
        public_ip_timeout = self.config.get("public_ip_timeout", 5)
        gap = self.config.get("column_gap", 4)

        left_entries = []
        right_entries = []

        # Left column: interfaces and gateway
        try:
            interfaces = self._get_interfaces()
            for iface, addr in interfaces:
                left_entries.append(f"{iface}:    {addr}")
        except Exception:
            left_entries.append("Interfaces: unavailable")

        try:
            gateway = self._get_default_gateway()
            left_entries.append(f"Gateway: {gateway}")
        except Exception:
            left_entries.append("Gateway: unavailable")

        # Right column: hostname and public IP
        try:
            hostname = socket.gethostname()
            right_entries.append(f"Hostname:  {hostname}")
        except Exception:
            right_entries.append("Hostname:  unavailable")

        if show_public_ip:
            try:
                response = requests.get("https://api.ipify.org", timeout=public_ip_timeout)
                response.raise_for_status()
                right_entries.append(f"Public IP: {response.text}")
            except Exception:
                right_entries.append("Public IP: unavailable")

        # Pad columns to same height
        max_height = max(len(left_entries), len(right_entries))
        while len(left_entries) < max_height:
            left_entries.append("")
        while len(right_entries) < max_height:
            right_entries.append("")

        # Calculate left column width
        left_width = max(len(e) for e in left_entries)

        lines = [f"{label}:"]
        for i in range(max_height):
            left = f"  {left_entries[i]}"
            if right_entries[i]:
                padding = left_width - len(left_entries[i]) + gap
                lines.append(f"{left}{' ' * padding}{right_entries[i]}")
            else:
                lines.append(left)

        return lines

    def _get_interfaces(self) -> list[tuple[str, str]]:
        """Parse 'ip -4 addr' for interface names and IPv4 addresses."""
        result = subprocess.run(
            ["ip", "-4", "-o", "addr", "show"],
            capture_output=True, text=True, timeout=5
        )

        interfaces = []
        excluded = self.config.get("excluded_interfaces", ["lo"])

        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            parts = line.split()
            iface = parts[1]
            addr = parts[3].split("/")[0]

            if iface not in excluded:
                interfaces.append((iface, addr))

        return interfaces

    def _get_default_gateway(self) -> str:
        """Parse 'ip route' for the default gateway."""
        result = subprocess.run(
            ["ip", "route", "show", "default"],
            capture_output=True, text=True, timeout=5
        )

        for line in result.stdout.strip().split("\n"):
            if line.startswith("default via"):
                parts = line.split()
                gateway = parts[2]
                iface = parts[4] if len(parts) > 4 else ""
                return f"{gateway} ({iface})" if iface else gateway

        return "no default route"