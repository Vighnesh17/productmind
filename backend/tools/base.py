"""
Base class for all MCP tools.

Every tool must implement:
  - name: str          — matches the tool_use name Claude will call
  - description: str   — shown to Claude in the tool list
  - input_schema: dict — JSON Schema for tool inputs (validated by Pydantic)
  - execute()          — the actual API call

Tools are registered at startup via tools/registry.py.
Unknown tool names → ToolNotFoundError (never reaches Claude).
"""

from abc import ABC, abstractmethod
from typing import Any


class ToolNotFoundError(Exception):
    """Raised when Claude calls a tool name not in the registry."""


class ToolExecutionError(Exception):
    """Raised when a tool call fails after retries are exhausted."""

    def __init__(self, tool: str, message: str, retriable: bool = False) -> None:
        self.tool = tool
        self.retriable = retriable
        super().__init__(f"[{tool}] {message}")


class BaseTool(ABC):
    name: str
    description: str
    input_schema: dict[str, Any]

    @abstractmethod
    async def execute(self, tenant_id: str, params: dict[str, Any]) -> dict[str, Any]:
        """
        Execute the tool and return a result dict.
        Raise ToolExecutionError on failure.
        """

    def to_anthropic_schema(self) -> dict[str, Any]:
        """Return the tool definition in Anthropic's tool_use format."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
        }
