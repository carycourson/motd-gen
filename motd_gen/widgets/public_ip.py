"""Public IP address widget."""

import requests
from motd_gen.widgets.base import BaseWidget


class PublicIPWidget(BaseWidget):
    """Displays the public-facing IP address."""

    @property
    def name(self) -> str:
        return "public_ip"

    def render(self) -> list[str]:
        """Fetch public IP from a free API."""
        label = self.config.get("label", "Public IP")
        timeout = self.config.get("timeout", 5)

        try:
            response = requests.get("https://api.ipify.org", timeout=timeout)
            response.raise_for_status()
            return [f"{label}: {response.text}"]
        except requests.ConnectionError:
            return [f"{label}: no internet connection"]
        except requests.Timeout:
            return [f"{label}: request timed out"]
        except Exception as e:
            return [f"{label}: unavailable ({e})"]