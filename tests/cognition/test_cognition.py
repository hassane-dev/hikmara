import pytest
from cognition.reasoning.service import global_reasoning_engine
from cognition.planner.service import global_planner
from cognition.agents.manager.service import global_agent_manager

def test_planner_decomposition():
    steps = global_planner.decompose_target("build web site")
    assert len(steps) > 3

def test_logical_reasoning():
    res = global_reasoning_engine.reason(["fact 1"], "query")
    assert res["aligned"] is True

def test_multi_agent_team():
    res = global_agent_manager.execute_task("build dynamic database integration", {})
    assert res["orchestrated"] is True
