import pytest
from cognition.understanding.service import global_language_understanding
from cognition.nlu.service import global_language_understanding as legacy_nlu

def test_nlu_multiscore_bonjour():
    res = global_language_understanding.analyze("Bonjour")
    assert res.intent == "greeting"
    assert res.domain == "conversation"

    legacy_res = legacy_nlu.analyze("Bonjour")
    assert legacy_res.intent == "greeting"

def test_nlu_multiscore_salut():
    res = global_language_understanding.analyze("Salut")
    assert res.intent == "greeting"

def test_nlu_multiscore_js_greeting_conflict():
    # Greeting "bonjour" should be overridden by strong technical action "programme", "js"
    res = global_language_understanding.analyze("Je veux un programme JS qui dit bonjour")
    assert res.intent == "code_generation"
    assert res.domain == "javascript"

    legacy_res = legacy_nlu.analyze("Je veux un programme JS qui dit bonjour")
    assert legacy_res.intent == "code_generation"

def test_nlu_multiscore_prefix_greeting_with_python():
    # Greeting "Bonjour" should be overridden by strong technical action "écris-moi", "script", "python"
    res = global_language_understanding.analyze("Bonjour, écris-moi un script Python")
    assert res.intent == "code_generation"
    assert res.domain == "python"

    legacy_res = legacy_nlu.analyze("Bonjour, écris-moi un script Python")
    assert legacy_res.intent == "code_generation"

def test_nlu_multiscore_how_works_sqlite():
    res = global_language_understanding.analyze("Comment fonctionne SQLite ?")
    assert res.intent == "explanation"
    assert res.domain == "database"

def test_nlu_multiscore_corrige_code():
    res = global_language_understanding.analyze("Corrige ce code")
    assert res.intent == "code_modification"

def test_nlu_multiscore_explain_php():
    res = global_language_understanding.analyze("Explique-moi PHP")
    assert res.intent == "explanation"
    assert res.domain == "php"

def test_nlu_multiscore_ouvre_les_parametres():
    res = global_language_understanding.analyze("Ouvre les paramètres")
    # Mapping "paramètres" or system configs resolves to system category
    assert res.intent == "system"

def test_nlu_multiscore_lance_un_audit():
    res_legacy = legacy_nlu.analyze("Lance un audit de sécurité")
    assert res_legacy.intent == "code_modification"
    assert res_legacy.risks_security == "sensitive"

    res = global_language_understanding.analyze("Lance un audit de sécurité")
    assert res.intent == "code_modification"
