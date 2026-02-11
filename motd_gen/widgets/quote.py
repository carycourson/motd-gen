"""Random quote widget."""

import json
import random
from pathlib import Path
from motd_gen.widgets.base import BaseWidget


class QuoteWidget(BaseWidget):
    """Displays a random quote from a JSON file."""

    @property
    def name(self) -> str:
        return "quote"

    def render(self) -> list[str]:
        """Load quotes file and pick one at random."""
        default_path = str(
            Path(__file__).parent.parent.parent / "config" / "quotes.json"
        )
        quotes_path = self.config.get("quotes_file", default_path)

        try:
            with open(quotes_path, "r") as f:
                quotes = json.load(f)

            if not quotes:
                return ["No quotes found."]

            quote = random.choice(quotes)
            text = quote.get("text", "")
            author = quote.get("author", "Unknown")

            label = self.config.get("label", "")
            lines = []
            if label:
                lines.append(label)
            lines.append(f'  "{text}"')
            lines.append(f"    — {author}")
            return lines

        except FileNotFoundError:
            return ["Quotes file not found."]
        except Exception as e:
            return [f"[quote error: {e}]"]
