import pytest
from cognition.context.service import global_context_manager
from cognition.router.service import global_intent_router

def test_context_creation():
    global_context_manager.reset_context()
    ctx = global_context_manager.get_context()
    assert len(ctx.messages) == 0
    assert ctx.active_domain is None
    assert ctx.language == "fr"

def test_context_update():
    global_context_manager.reset_context()
    prompt = "Écris une fonction en Python"
    decision = global_intent_router.route(prompt)

    global_context_manager.update_context("user", prompt, routing_decision=decision)
    ctx = global_context_manager.get_context()

    assert len(ctx.messages) == 1
    assert ctx.messages[0]["role"] == "user"
    assert ctx.messages[0]["message"] == prompt
    assert ctx.active_domain == "python"

def test_previous_conversation_reference():
    global_context_manager.reset_context()
    global_context_manager.update_context("user", "Écris un script Python pour additionner")
    global_context_manager.set_last_generated_code("def add(a, b): return a + b")

    ctx = global_context_manager.get_context()
    assert ctx.context_references.get("last_generated_code") == "def add(a, b): return a + b"
    assert ctx.active_domain == "python"

def test_context_reset():
    global_context_manager.update_context("user", "Hello Python")
    global_context_manager.reset_context()
    ctx = global_context_manager.get_context()
    assert len(ctx.messages) == 0
    assert ctx.active_domain is None
