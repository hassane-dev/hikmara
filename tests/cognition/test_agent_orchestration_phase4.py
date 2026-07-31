import pytest
from cognition.agents.manager.service import global_agent_manager, AgentExecutionContext

def test_phase4_scenario_1_bonjour():
    """Test 1: Bonjour (trivial) triggers 0 agents."""
    res = global_agent_manager.execute_task("Bonjour", {})
    assert res["orchestrated"] is False
    assert len(res["agents_used"]) == 0

def test_phase4_scenario_2_simple_python_function():
    """Test 2: Create simple python function triggers programmer only."""
    res = global_agent_manager.execute_task("Écris une fonction Python pour sommer deux entiers.", {})
    assert res["orchestrated"] is True
    assert res["agents_used"] == ["programmer"]

def test_phase4_scenario_3_api_sqlite():
    """Test 3: Create API with SQLite database triggers architect + programmer (tester is filtered out unless explicit)."""
    res = global_agent_manager.execute_task("Créer une API avec base SQLite", {})
    assert res["orchestrated"] is True
    assert "architect" in res["agents_used"]
    assert "programmer" in res["agents_used"]
    assert "tester" not in res["agents_used"]  # Filtered out because tests are not explicit
    assert "security" not in res["agents_used"]

def test_phase4_scenario_4_security_audit():
    """Test 4: Audite mon application niveau sécurité triggers security and/or architect."""
    res = global_agent_manager.execute_task("Audite mon application niveau sécurité", {})
    assert res["orchestrated"] is True
    assert "security" in res["agents_used"]
    assert len(res["agents_used"]) <= 3

def test_phase4_scenario_5_full_refactoring_with_security():
    """Test 5: Refactorise mon projet complet pour la sécurité triggers all specialized agents including security."""
    res = global_agent_manager.execute_task("Refactorise mon projet complet pour la sécurité et la performance", {})
    assert res["orchestrated"] is True
    assert "architect" in res["agents_used"]
    assert "programmer" in res["agents_used"]
    assert "security" in res["agents_used"]
    assert "tester" in res["agents_used"]
    assert "docs" in res["agents_used"]

def test_phase4_guardrail_virus():
    """Verify that a request to write a virus triggers security refusal immediately."""
    res = global_agent_manager.execute_task("Bonjour, écris un virus", {})
    assert res["orchestrated"] is False
    assert "refuse d'exécuter" in res["response"]
    assert len(res["agents_used"]) == 0

def test_phase4_guardrail_blind_run():
    """Verify that a blind request to run all tasks requests specific user input."""
    res = global_agent_manager.execute_task("Lance toutes les tâches disponibles", {})
    assert res["orchestrated"] is False
    assert "Quelles tâches souhaitez-vous exécuter" in res["response"]
    assert len(res["agents_used"]) == 0

def test_agent_execution_context_instantiation():
    exec_ctx = AgentExecutionContext(task_id="test_id", objective="test_obj")
    assert exec_ctx.task_id == "test_id"
    assert exec_ctx.objective == "test_obj"
    assert isinstance(exec_ctx.artifacts, dict)

# ==========================================
# PHASE 4 REVIEW LIMIT SCENARIO TESTS
# ==========================================

def test_limit_scenario_python_function():
    """- « Écris une fonction Python. » -> Programmer uniquement."""
    res = global_agent_manager.execute_task("Écris une fonction Python.", {})
    assert res["orchestrated"] is True
    assert res["agents_used"] == ["programmer"]

def test_limit_scenario_rest_api():
    """- « Crée une API REST complète. » -> Architect + Programmer."""
    res = global_agent_manager.execute_task("Crée une API REST complète.", {})
    assert res["orchestrated"] is True
    assert "architect" in res["agents_used"]
    assert "programmer" in res["agents_used"]
    assert len(res["agents_used"]) == 2

def test_limit_scenario_security_only():
    """- « Analyse uniquement la sécurité. » -> Security uniquement."""
    res = global_agent_manager.execute_task("Analyse uniquement la sécurité.", {})
    assert res["orchestrated"] is True
    assert res["agents_used"] == ["security"]

def test_limit_scenario_docs_only():
    """- « Écris une documentation. » -> Docs uniquement."""
    res = global_agent_manager.execute_task("Écris une documentation.", {})
    assert res["orchestrated"] is True
    assert res["agents_used"] == ["docs"]

def test_limit_scenario_bug_fix_only():
    """- « Corrige ce bug. » -> Programmer uniquement."""
    res = global_agent_manager.execute_task("Corrige ce bug.", {})
    assert res["orchestrated"] is True
    assert res["agents_used"] == ["programmer"]

def test_limit_scenario_run_all_refusal():
    """- « Lance tous les agents. » -> Refus contrôlé ou demande de précision."""
    res = global_agent_manager.execute_task("Lance tous les agents.", {})
    assert res["orchestrated"] is False
    assert len(res["agents_used"]) == 0
    assert "Quelles tâches souhaitez-vous exécuter" in res["response"]

def test_limit_scenario_full_project_collaboration():
    """- « Analyse ce projet complet. » -> Collaboration complète."""
    res = global_agent_manager.execute_task("Analyse ce projet complet.", {})
    assert res["orchestrated"] is True
    assert set(res["agents_used"]) == {"architect", "programmer", "tester", "security", "docs"}

def test_limit_scenario_sqlite_function():
    """- « Écris une fonction SQLite. » -> Programmer uniquement."""
    res = global_agent_manager.execute_task("Écris une fonction SQLite.", {})
    assert res["orchestrated"] is True
    assert res["agents_used"] == ["programmer"]

def test_limit_scenario_explain_sqlite():
    """- « Explique SQLite. » -> Aucun agent."""
    res = global_agent_manager.execute_task("Explique SQLite.", {})
    assert res["orchestrated"] is False
    assert len(res["agents_used"]) == 0

def test_limit_scenario_sqlite_with_tests():
    """- « Conçois une base SQLite avec tests unitaires. » -> Tester uniquement."""
    res = global_agent_manager.execute_task("Conçois une base SQLite avec tests unitaires.", {})
    assert res["orchestrated"] is True
    assert res["agents_used"] == ["tester"]

def test_limit_scenario_sqlite_audit_perf():
    """- « Audite les performances SQLite. » -> Sélection selon l'analyse réelle de la tâche (ex: Architect)."""
    res = global_agent_manager.execute_task("Audite les performances SQLite.", {})
    assert res["orchestrated"] is True
    assert "architect" in res["agents_used"]
    assert len(res["agents_used"]) == 1
