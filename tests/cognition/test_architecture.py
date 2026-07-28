import pytest
from cognition.session.service import global_session_manager
from cognition.prompt_builder.service import global_prompt_builder
from cognition.conversation.validator import global_response_validator
from memory.router import global_memory_router
from knowledge.router import global_knowledge_router

def test_session_manager():
    # Test session stats
    session = global_session_manager.get_active_session()
    assert session is not None
    assert session.current_user == "admin"

    global_session_manager.update_stats(100, 200, 1.25)
    updated = global_session_manager.get_active_session()
    assert updated.statistics.total_turns == 1
    assert updated.statistics.total_tokens_input == 100
    assert updated.statistics.total_tokens_output == 200
    assert updated.statistics.average_latency == 1.25

def test_prompt_builder():
    prompt_dict = global_prompt_builder.build_prompt("hello", None, "recalled memory context", "Salutations")
    assert "system" in prompt_dict
    assert "user" in prompt_dict
    assert "hello" in prompt_dict["user"]
    assert "recalled memory context" in prompt_dict["system"]

def test_memory_and_knowledge_routers():
    mem_res = global_memory_router.retrieve("Test", None)
    assert mem_res is not None

    kn_res = global_knowledge_router.retrieve_knowledge("how to use venv?")
    assert "venv" in kn_res or kn_res == ""

def test_response_validator():
    # Valid text
    res1 = global_response_validator.validate("Hello world")
    assert res1["is_valid"] is True

    # Unclosed block text
    res2 = global_response_validator.validate("```python\ndef test():")
    assert res2["is_valid"] is False
    assert len(res2["warnings"]) > 0
    assert "*Avertissement de validation :" in res2["final_text"]
