"""Gumroad product-launch tool (placeholder).

Scaffolding so ``enhancer.py`` imports cleanly. Replace ``_run`` with a real
Gumroad API integration before production use.
"""

from typing import Optional

from crewai.tools import BaseTool


class GumroadTool(BaseTool):
    name: str = "Gumroad Launcher"
    description: str = (
        "Creates a monetized Gumroad product page with pricing tiers and a "
        "call to action, and returns the product URL."
    )
    api_token: Optional[str] = None

    def _run(self, product: str) -> str:
        raise NotImplementedError(
            "GumroadTool is a placeholder. Implement the Gumroad API call in _run()."
        )
