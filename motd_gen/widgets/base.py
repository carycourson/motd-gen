"""Abstract base class defining the widget contract."""

from abc import ABC, abstractmethod
from typing import Any


class BaseWidget(ABC):
    """All widgets must inherit from this class.

    Each widget receives its own config section and returns
    rendered lines for the MOTD output.
    """

    def __init__(self, config: dict[str, Any], width: int = 80) -> None:
        """Initialize with widget-specific config from motd.json."""
        self.config = config
        self.width = width

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for this widget, matches config key."""
        ...

    @abstractmethod
    def render(self) -> list[str]:
        """Return lines of text to display in the MOTD.

        Returns:
            A list of strings, one per line. Empty list if nothing to show.
        """
        ...
