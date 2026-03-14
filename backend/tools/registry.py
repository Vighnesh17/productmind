"""
Tool registry — all tools registered at startup.

The agent loop validates every tool_use call against this registry.
Unknown tool name → ToolNotFoundError immediately, before any execution.
This prevents hallucinated tool names from causing silent failures.

Usage:
    from backend.tools.registry import registry
    tool = registry.get("jira_list_issues")
    result = await tool.execute(tenant_id, params)
"""

from backend.tools.base import BaseTool, ToolNotFoundError


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool:
        if name not in self._tools:
            raise ToolNotFoundError(
                f"Unknown tool '{name}'. Available tools: {list(self._tools.keys())}"
            )
        return self._tools[name]

    def all_schemas(self) -> list[dict]:
        """Return all tool definitions in Anthropic's tool_use format."""
        return [tool.to_anthropic_schema() for tool in self._tools.values()]

    def names(self) -> list[str]:
        return list(self._tools.keys())


registry = ToolRegistry()


def setup_tools() -> None:
    """Register all tools at app startup. Import tools here to register them."""
    from backend.tools.jira.tools import JiraListIssuesTool, JiraGetIssueTool
    from backend.tools.slack.tools import SlackReadChannelTool, SlackSearchMessagesTool

    registry.register(JiraListIssuesTool())
    registry.register(JiraGetIssueTool())
    registry.register(SlackReadChannelTool())
    registry.register(SlackSearchMessagesTool())
