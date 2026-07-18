import pytest
from cognition.router.service import global_intent_router
from cognition.agents.manager.service import global_agent_manager

def test_intent_router_classification():
    # Salutations
    res_salut = global_intent_router.route("Bonjour")
    assert res_salut.category == "Salutations"
    assert res_salut.recommended_pipeline == "Conversation"
    assert len(res_salut.agents_to_trigger) == 0

    res_salut_en = global_intent_router.route("Good morning")
    assert res_salut_en.category == "Salutations"

    # Conversation générale
    res_conv = global_intent_router.route("comment ça va ?")
    assert res_conv.category == "Conversation générale"
    assert res_conv.recommended_pipeline == "Conversation"

    # Commandes système
    res_sys = global_intent_router.route("vérifie la mémoire")
    assert res_sys.category == "Commandes système"
    assert res_sys.recommended_pipeline == "Commandes système"

    # Développement logiciel
    res_dev = global_intent_router.route("écris une api flask")
    assert res_dev.category == "Développement logiciel"
    assert res_dev.recommended_pipeline == "Développement logiciel"
    assert "architect" in res_dev.agents_to_trigger

    # Génération de code
    res_gen = global_intent_router.route("génère une classe Python")
    assert res_gen.category == "Génération de code"
    assert "programmer" in res_gen.agents_to_trigger

    # Inconnu
    res_inc = global_intent_router.route("something random")
    assert res_inc.category == "Inconnu"
    assert res_inc.recommended_pipeline == "Conversation"

def test_agent_manager_no_orchestration_for_simple_conversation():
    # Bonjour should NOT trigger orchestrator or run any of the agent tasks
    res = global_agent_manager.execute_task("Bonjour", {})
    assert res["orchestrated"] is False
    assert "Bonjour !" in res["response"]
    assert "architecture" not in res
    assert "code" not in res
    assert len(res["agents_used"]) == 0

def test_agent_manager_orchestration_for_development():
    # Complex task should trigger agents
    res = global_agent_manager.execute_task("génère une classe de base de données active record", {})
    assert res["orchestrated"] is True
    assert "architecture" in res
    assert "code" in res
    assert len(res["agents_used"]) > 0

def test_system_command_pipeline():
    # Test that memory command queries the monitor
    res = global_agent_manager.execute_task("vérifie la mémoire", {})
    assert res["orchestrated"] is False
    assert res["route_decision"] == "Commandes système"
    assert "ressources" in res["response"].lower() or "cpu" in res["response"].lower()
