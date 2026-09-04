"""Notion publishing tool (placeholder).

Scaffolding so ``enhancer.py`` imports cleanly. Replace ``_run`` with a real
Notion API integration (e.g. via ``notion-client``) before production use.
"""

from typing import Optional

from crewai.tools import BaseTool


class NotionTool(BaseTool):
    name: str = "Notion Publisher"
    description: str = (
        "Publishes toolkits and prompt cards to a Notion microsite and "
        "returns the published page URL."
    )
    api_key: Optional[str] = None

    def _run(self, content: str) -> str:
        raise NotImplementedError(
            "NotionTool is a placeholder. Implement the Notion API call in _run()."
        )
