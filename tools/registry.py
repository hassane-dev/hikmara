from tools.base_tool import BaseTool

class ToolRegistry:
    def __init__(self):
        self._tools = {}

    def register_tool(self, tool: BaseTool):
        self._tools[tool.name.lower()] = tool

    def get_tool(self, name):
        return self._tools.get(name.lower())

    def list_tools(self):
        return [{"name": t.name, "description": t.description, "permissions": t.permissions_required} for t in self._tools.values()]

global_tool_registry = ToolRegistry()
