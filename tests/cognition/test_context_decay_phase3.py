import pytest
from cognition.context.service import global_context_manager
from cognition.understanding.service import global_language_understanding

def test_phase3_subject_change_and_archiving():
    """Verify that switching from Python coding task to a general greeting archives the context and opens a fresh one."""
    global_context_manager.reset_context()

    # Simulate first turn: User requests Python script
    nlu_1 = global_language_understanding.analyze("Écris un programme Python")
    global_context_manager.update_context("user", "Écris un programme Python", nlu_result=nlu_1)

    context = global_context_manager.get_context()
    assert context.active_work_context.active_domain == "python"
    assert len(context.archived_contexts) == 0

    # Simulate second turn: User completely shifts to greeting
    nlu_2 = global_language_understanding.analyze("Bonjour, comment ça va ?")
    global_context_manager.update_context("user", "Bonjour, comment ça va ?", nlu_result=nlu_2)

    # Current active domain should be reset/cleared
    assert context.active_work_context.active_domain is None
    # Previous context must be archived
    assert len(context.archived_contexts) == 1
    assert context.archived_contexts[0]["active_domain"] == "python"

def test_phase3_controlled_inheritance():
    """Verify that user preferences and language survive subject shifts, but tech stack resets."""
    global_context_manager.reset_context()

    # User makes request in French and with polite indicators, including a PyQt6 flag
    nlu_1 = global_language_understanding.analyze("S'il te plaît, crée une application PyQt6")
    global_context_manager.update_context("user", "S'il te plaît, crée une application PyQt6", nlu_result=nlu_1)

    context = global_context_manager.get_context()
    assert context.user_preferences.get("polite") is True
    assert context.language == "fr"
    assert context.context_references.get("has_gui") is True

    # Shift domain to weather
    nlu_2 = global_language_understanding.analyze("Quel temps fait-il dehors ?")
    global_context_manager.update_context("user", "Quel temps fait-il dehors ?", nlu_result=nlu_2)

    # Language and preferences survive
    assert context.language == "fr"
    assert context.user_preferences.get("polite") is True
    # PyQt6 flag is completely cleared from current active context
    assert context.context_references.get("has_gui") is None

def test_phase3_context_decay():
    """Verify gradual decay of has_gui and has_sqlite indicator flags when not mentioned."""
    global_context_manager.reset_context()

    # Turn 1: user mentions PyQt6 and SQLite
    nlu_1 = global_language_understanding.analyze("Fais une interface PyQt6 avec SQLite")
    global_context_manager.update_context("user", "Fais une interface PyQt6 avec SQLite", nlu_result=nlu_1)

    context = global_context_manager.get_context()
    assert context.context_references.get("has_gui") is True
    assert context.context_references.get("has_sqlite") is True

    # Turn 2: user asks a follow-up query not mentioning interface/GUI, but mentioning SQL
    nlu_2 = global_language_understanding.analyze("Peux-tu me montrer la table SQL ?")
    global_context_manager.update_context("user", "Peux-tu me montrer la table SQL ?", nlu_result=nlu_2)

    # has_gui should decay; has_sqlite survives because of SQL mention
    assert context.context_references.get("has_gui") is None
    assert context.context_references.get("has_sqlite") is True

    # Turn 3: user asks completely unrelated question
    nlu_3 = global_language_understanding.analyze("C'est quoi la capitale de la France ?")
    global_context_manager.update_context("user", "C'est quoi la capitale de la France ?", nlu_result=nlu_3)

    # both indicators decayed
    assert context.context_references.get("has_gui") is None
    assert context.context_references.get("has_sqlite") is None

def test_phase3_workspace_restoration():
    """Verify manual recovery/restoration of an archived context."""
    global_context_manager.reset_context()

    nlu_1 = global_language_understanding.analyze("Code un programme Python")
    global_context_manager.update_context("user", "Code un programme Python", nlu_result=nlu_1)
    global_context_manager.set_last_generated_code("print('hello')")

    # Shift subject to trigger archiving
    nlu_2 = global_language_understanding.analyze("Raconte-moi une histoire")
    global_context_manager.update_context("user", "Raconte-moi une histoire", nlu_result=nlu_2)

    context = global_context_manager.get_context()
    assert len(context.archived_contexts) == 1
    assert context.context_references.get("last_generated_code") is None

    # Restore the archived Python context
    success = global_context_manager.restore_work_context(1)
    assert success is True
    assert context.active_work_context.active_domain == "python"
    assert context.context_references.get("last_generated_code") == "print('hello')"

def test_phase3_isolation_distinct_technical_domains():
    """Verify separation and archiving when switching from PHP coding directly to Python coding."""
    global_context_manager.reset_context()

    nlu_1 = global_language_understanding.analyze("Écris une fonction PHP")
    global_context_manager.update_context("user", "Écris une fonction PHP", nlu_result=nlu_1)

    context = global_context_manager.get_context()
    assert context.active_work_context.active_domain == "php"

    # Switch directly to Python
    nlu_2 = global_language_understanding.analyze("Maintenant fais un script Python")
    global_context_manager.update_context("user", "Maintenant fais un script Python", nlu_result=nlu_2)

    # PHP context should be archived, and new active context is python
    assert len(context.archived_contexts) == 1
    assert context.archived_contexts[0]["active_domain"] == "php"
    assert context.active_work_context.active_domain == "python"
