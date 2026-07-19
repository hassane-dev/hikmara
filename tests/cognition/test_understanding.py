import pytest
from cognition.understanding.service import global_language_understanding

def test_greeting_nlu():
    res = global_language_understanding.analyze("Bonjour")
    assert res.intent == "greeting"
    assert res.language == "fr"
    assert res.confidence >= 0.90

def test_how_are_you_nlu():
    res = global_language_understanding.analyze("Comment vas-tu ?")
    assert res.intent == "general_conversation"
    assert res.language == "fr"

def test_code_generation_python_nlu():
    res = global_language_understanding.analyze("Je veux un programme Python pour additionner deux entiers.")
    assert res.intent == "code_generation"
    assert res.domain == "python"
    assert res.entities.get("operation") == "addition"
    assert res.entities.get("data_type") == "integer"
    assert res.language == "fr"
    assert res.confidence >= 0.90

def test_code_generation_php_nlu():
    res = global_language_understanding.analyze("Écris un script PHP pour calculer la somme de deux nombres.")
    assert res.intent == "code_generation"
    assert res.domain == "php"
    assert res.entities.get("operation") == "addition"

def test_code_modification_gui_nlu():
    res = global_language_understanding.analyze("Ajoute une interface graphique.")
    assert res.intent == "code_modification"
    assert res.is_follow_up is True
    assert res.references_previous_context is False  # no explicit reference words like 'précédent'
    assert res.entities.get("interface_type") == "pyqt6"

def test_code_modification_sqlite_nlu():
    res = global_language_understanding.analyze("Modifie le programme précédent pour ajouter une base SQLite.")
    assert res.intent == "code_modification"
    assert res.is_follow_up is True
    assert res.references_previous_context is True
    assert res.entities.get("database_type") == "sqlite"

def test_explanation_nlu():
    res = global_language_understanding.analyze("Explique ce code")
    assert res.intent == "explanation"

def test_code_conversion_nlu():
    res = global_language_understanding.analyze("Convertis-le en PHP")
    assert res.intent == "code_conversion"
    assert res.is_follow_up is True

def test_system_nlu():
    res = global_language_understanding.analyze("Quel est l'utilisation du CPU ?")
    assert res.intent == "system"
    assert res.domain == "system"

def test_tools_nlu():
    res = global_language_understanding.analyze("Crée un fichier")
    assert res.intent == "tools"
    assert res.domain == "tools"

def test_low_confidence_nlu():
    res = global_language_understanding.analyze("Fais quelque chose")
    # Low confidence or unknown
    assert res.confidence < 0.80 or res.intent == "unknown"
