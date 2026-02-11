"""Network information widget."""

import socket
import subprocess
from motd_gen.widgets.base import BaseWidget


class NetworkWidget(BaseWidget):
    """Displays hostname, IP addresses, gateway, and active interface."""

    @property
    def name(self) -> str:
        return "network"

    def render(self) -> list[str]:
        """Gather network info from system commands and sockets."""
        label = self.config.get("label", "Network")
        lines = [f"{label}:"]

        try:
            hostname = socket.gethostname()
            lines.append(f"  Hostname:  {hostname}")
        except Exception:
            lines.append("  Hostname:  unavailable")

        try:
            interfaces = self._get_interfaces()
            for iface, addr in interfaces:
                lines.append(f"  {iface}:  {addr}")
            if not interfaces:
                lines.append("  Interfaces: none detected")
        except Exception:
            lines.append("  Interfaces: unavailable")

        try:
            gateway = self._get_default_gateway()
            lines.append(f"  Gateway:   {gateway}")
        except Exception:
            lines.append("  Gateway:   unavailable")

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
            # Format: index iface inet addr/prefix ...
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
