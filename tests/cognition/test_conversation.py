import pytest
from cognition.context.service import global_context_manager
from cognition.conversation.service import global_conversation_engine
from cognition.conversation.post_processing import global_post_processor

def test_conversation_response():
    global_context_manager.reset_context()
    res = global_conversation_engine.generate_response("Comment vas-tu ?")
    assert "opérationnel" in res.response

def test_french_conversation():
    global_context_manager.reset_context()
    res = global_conversation_engine.generate_response("Bonjour")
    assert "Comment puis-je vous aider" in res.response

def test_progressive_contextual_generation_flow():
    # Reset context first
    global_context_manager.reset_context()

    # 1. Step 1: Request simple coding sum program
    res1 = global_conversation_engine.generate_response("Je veux un programme Python pour additionner deux entiers.")
    assert "calculer_somme" in res1.response

    ctx = global_context_manager.get_context()
    assert ctx.active_domain == "python"
    assert ctx.context_references.get("has_gui") is not True
    assert ctx.context_references.get("has_sqlite") is not True

    # 2. Step 2: Request GUI modification
    res2 = global_conversation_engine.generate_response("Ajoute une interface graphique.")
    assert "PyQt6" in res2.response or "QApplication" in res2.response

    ctx = global_context_manager.get_context()
    assert ctx.active_domain == "python"
    assert ctx.context_references.get("has_gui") is True
    assert ctx.context_references.get("has_sqlite") is not True

    # 3. Step 3: Request SQLite database modification
    res3 = global_conversation_engine.generate_response("Modifie le programme précédent pour ajouter une base SQLite.")
    assert "sqlite3" in res3.response or "SQLite" in res3.response
    assert "PyQt6" in res3.response or "QApplication" in res3.response

    ctx = global_context_manager.get_context()
    assert ctx.active_domain == "python"
    assert ctx.context_references.get("has_gui") is True
    assert ctx.context_references.get("has_sqlite") is True

    # 4. Step 4: Request Conversion to PHP (retaining SQLite logic)
    res4 = global_conversation_engine.generate_response("Convertis le programme précédent en PHP.")
    assert "<?php" in res4.response
    assert "SQLite" in res4.response or "sqlite" in res4.response

    ctx = global_context_manager.get_context()
    assert ctx.active_domain == "php"
    assert ctx.context_references.get("has_sqlite") is True

def test_model_switching_and_fallback():
    # Test switching LLM Engine
    success = global_conversation_engine.change_model("transformers", "qwen2.5-coder-hf")
    assert success is True
    assert global_conversation_engine.active_engine == "transformers"
    assert global_conversation_engine.active_model == "qwen2.5-coder-hf"

    # Reset back to default
    global_conversation_engine.change_model("ollama", "qwen2.5:3b")

def test_post_processing_sanitization():
    raw = "Voici ma clé d'API : ABC123XYZ4567890ABC123XYZ4567890ABC123XYZ4 et mon fichier de conf local est /path/to/.env !"
    processed = global_post_processor.process_response(raw, None)
    assert "[CLE_API_MASQUEE]" in processed
    assert ".env (masqué pour votre sécurité)" in processed
