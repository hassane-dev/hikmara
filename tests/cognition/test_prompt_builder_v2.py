import pytest
from cognition.prompt_builder.service import global_prompt_builder
from cognition.context.service import global_context_manager

def test_prompt_builder_v2_scenario_1_bonjour():
    """1. Test 'bonjour' scenario: ensure no code leakage and correct template."""
    global_context_manager.reset_context()
    context = global_context_manager.get_context()
    context.context_references["last_generated_code"] = "import sys\nprint('old code')"

    prompt = global_prompt_builder.build_prompt(
        user_message="bonjour",
        context=context,
        memory_context="",
        intent="greeting",
        active_model="qwen2.5-3b-instruct-q4_k_m.gguf"
    )

    system_prompt = prompt["system"]
    assert "old code" not in system_prompt
    assert "Hikmara AI" in system_prompt
    # Greeting should use conversation template or default, not coding.md
    assert "expert en développement logiciel" not in system_prompt

def test_prompt_builder_v2_scenario_2_sais_faire():
    """2. Test 'qu'est-ce que tu sais faire ?' scenario: ensure general identity and no technical confinement."""
    global_context_manager.reset_context()
    context = global_context_manager.get_context()
    context.context_references["last_generated_code"] = "const express = require('express');"

    prompt = global_prompt_builder.build_prompt(
        user_message="qu'est-ce que tu sais faire ?",
        context=context,
        memory_context="",
        intent="general_conversation",
        active_model="qwen2.5-3b-instruct-q4_k_m.gguf"
    )

    system_prompt = prompt["system"]
    assert "const express" not in system_prompt
    assert "expert en développement logiciel" not in system_prompt
    assert "chaleureuse" in system_prompt or "naturelle" in system_prompt

def test_prompt_builder_v2_scenario_3_new_code_without_reference():
    """3. Test 'je veux un programme Python' scenario: is code_generation but has no request for adaptation."""
    global_context_manager.reset_context()
    context = global_context_manager.get_context()
    context.context_references["last_generated_code"] = "import sys\nprint('old code')"

    prompt = global_prompt_builder.build_prompt(
        user_message="je veux un programme Python qui additionne deux nombres",
        context=context,
        memory_context="",
        intent="code_generation",
        active_model="qwen2.5-3b-instruct-q4_k_m.gguf"
    )

    system_prompt = prompt["system"]
    # It is code generation, but not adaptation/modification. Old code must NOT be injected.
    assert "old code" not in system_prompt
    assert "expert en développement logiciel" in system_prompt

def test_prompt_builder_v2_scenario_4_modification_request():
    """4. Test 'modifie ce code Python...' scenario: requires modification so old code MUST be injected."""
    global_context_manager.reset_context()
    context = global_context_manager.get_context()
    context.context_references["last_generated_code"] = "def add(a, b):\n    return a + b"

    prompt = global_prompt_builder.build_prompt(
        user_message="modifie ce code Python pour ajouter une interface graphique",
        context=context,
        memory_context="",
        intent="code_modification",
        active_model="qwen2.5-3b-instruct-q4_k_m.gguf"
    )

    system_prompt = prompt["system"]
    assert "def add(a, b):" in system_prompt
    assert "expert en développement logiciel" in system_prompt

def test_prompt_builder_v2_scenario_5_new_conversation_reset():
    """5. Test new conversation after previous task: context reset clears references completely."""
    global_context_manager.reset_context()
    context = global_context_manager.get_context()
    context.context_references["has_gui"] = True
    context.context_references["last_generated_code"] = "import PyQt6"

    # Reset context for a new conversation
    global_context_manager.reset_context()
    fresh_context = global_context_manager.get_context()

    prompt = global_prompt_builder.build_prompt(
        user_message="Quel temps fait-il ?",
        context=fresh_context,
        memory_context="",
        intent="general_conversation",
        active_model="qwen2.5-3b-instruct-q4_k_m.gguf"
    )

    system_prompt = prompt["system"]
    assert "import PyQt6" not in system_prompt
    assert fresh_context.context_references.get("has_gui") is None
    assert fresh_context.context_references.get("last_generated_code") is None

def test_prompt_builder_v2_pyqt6_sqlite_to_greeting():
    """Test PyQt6+SQLite request followed by 'Bonjour, quelles sont tes capacités?'."""
    global_context_manager.reset_context()
    context = global_context_manager.get_context()
    context.context_references["last_generated_code"] = "import PyQt6\n# Some sqlite code"
    context.context_references["has_gui"] = True
    context.context_references["has_sqlite"] = True

    # Ask a general greeting question
    prompt = global_prompt_builder.build_prompt(
        user_message="Bonjour, quelles sont tes capacités ?",
        context=context,
        memory_context="",
        intent="greeting",
        active_model="qwen2.5-3b-instruct-q4_k_m.gguf"
    )

    system_prompt = prompt["system"]
    # Ensure no PyQt6/SQLite leakage in system instructions
    assert "import PyQt6" not in system_prompt
    # Must use general conversation template
    assert "expert en développement logiciel" not in system_prompt
    assert "chaleureuse" in system_prompt or "naturelle" in system_prompt

def test_prompt_builder_v2_pyqt6_sqlite_to_simple_addition():
    """Test PyQt6+SQLite request followed by simple code generation: addition of two numbers."""
    global_context_manager.reset_context()
    context = global_context_manager.get_context()
    context.context_references["last_generated_code"] = "import PyQt6\n# PyQt6 Window and SQLite connection"
    context.context_references["has_gui"] = True
    context.context_references["has_sqlite"] = True

    # Ask a simple code generation question
    prompt = global_prompt_builder.build_prompt(
        user_message="Écris-moi une fonction Python qui additionne deux nombres.",
        context=context,
        memory_context="",
        intent="code_generation",
        active_model="qwen2.5-3b-instruct-q4_k_m.gguf"
    )

    system_prompt = prompt["system"]
    # The system prompt should NOT contain the PyQt6/SQLite code snippet
    assert "import PyQt6" not in system_prompt
    assert "PyQt6 Window" not in system_prompt
