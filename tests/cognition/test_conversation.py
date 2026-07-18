import pytest
from cognition.context.service import global_context_manager
from cognition.conversation.service import global_conversation_engine

def test_conversation_response():
    global_context_manager.reset_context()
    res = global_conversation_engine.generate_response("Comment vas-tu ?")
    assert "opérationnel" in res.response

def test_french_conversation():
    global_context_manager.reset_context()
    res = global_conversation_engine.generate_response("Bonjour")
    assert "Comment puis-je vous aider" in res.response

def test_contextual_followup():
    global_context_manager.reset_context()
    # Turn 1: request coding
    res1 = global_conversation_engine.generate_response("Écris-moi un programme Python pour faire la somme de deux entiers.")
    assert "calculer_somme" in res1.response

    # Context should be updated with python domain and last code
    ctx = global_context_manager.get_context()
    assert ctx.active_domain == "python"
    assert "last_generated_code" in ctx.context_references

    # Turn 2: request follow up GUI
    res2 = global_conversation_engine.generate_response("Ajoute maintenant une interface graphique.")
    assert "PyQt6" in res2.response or "QApplication" in res2.response
