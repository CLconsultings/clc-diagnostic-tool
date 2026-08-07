"""Vault parsing tool (placeholder).

Scaffolding so ``enhancer.py`` imports cleanly. Replace ``_run`` with logic
that reads and extracts monetizable prompt tools from the local Vault.
"""

from crewai.tools import BaseTool


class VaultTool(BaseTool):
    name: str = "Vault Parser"
    description: str = (
        "Reads the CLConsulting Vault directory and extracts monetizable "
        "prompt tools as structured text."
    )
    vault_path: str = "./Vault"

    def _run(self, query: str) -> str:
        raise NotImplementedError(
            "VaultTool is a placeholder. Implement Vault extraction in _run()."
        )
