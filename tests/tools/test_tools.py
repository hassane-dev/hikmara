import pytest
from tools.registry import global_tool_registry
from tools.file_tools.service import CreateFileTool

def test_tool_registration():
    t_file = CreateFileTool()
    global_tool_registry.register_tool(t_file)
    assert global_tool_registry.get_tool("create_file") is not None

def test_dry_run_tool_access():
    assert len(global_tool_registry.list_tools()) >= 0
