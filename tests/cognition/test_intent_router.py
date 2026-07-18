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
    res_conv1 = global_intent_router.route("comment ça va ?")
    assert res_conv1.category == "Conversation générale"
    assert res_conv1.recommended_pipeline == "Conversation"

    res_conv2 = global_intent_router.route("comment vas tu ?")
    assert res_conv2.category == "Conversation générale"
    assert res_conv2.recommended_pipeline == "Conversation"

    # Commandes système
    res_sys = global_intent_router.route("vérifie la mémoire")
    assert res_sys.category == "Commandes système"
    assert res_sys.recommended_pipeline == "Commandes système"

    # PHP script (Génération de code)
    res_php = global_intent_router.route("écris un script PHP qui calcule la somme de deux entiers")
    assert res_php.category == "Génération de code"
    assert res_php.recommended_pipeline == "Développement logiciel"
    assert "programmer" in res_php.agents_to_trigger

    # Project roadmap / planning (Questions techniques)
    res_roadmap = global_intent_router.route("je veux une feuille de route pour un projet web")
    assert res_roadmap.category == "Questions techniques"
    assert res_roadmap.recommended_pipeline == "Conversation"
    assert len(res_roadmap.agents_to_trigger) == 0  # Should not trigger sub-agents needlessly

    # Ambiguous query "code" (Génération de code but Conversation pipeline for clarification)
    res_code = global_intent_router.route("code")
    assert res_code.category == "Génération de code"
    assert res_code.recommended_pipeline == "Conversation"  # To prevent agent orchestration overhead
    assert len(res_code.agents_to_trigger) == 0

    # Fallback / Inconnu
    res_inc = global_intent_router.route("something totally random and meaningless")
    assert res_inc.category == "Inconnu"
    assert res_inc.recommended_pipeline == "Conversation"

def test_agent_manager_no_orchestration_for_simple_conversation():
    # Bonjour should NOT trigger orchestrator or run any of the agent tasks
    res = global_agent_manager.execute_task("Bonjour", {})
    assert res["orchestrated"] is False
    assert "Bonjour !" in res["response"]
    assert len(res["agents_used"]) == 0

def test_agent_manager_conversation_generale():
    # Comment vas tu ? should receive natural conversational response
    res = global_agent_manager.execute_task("comment vas tu ?", {})
    assert res["orchestrated"] is False
    assert "opérationnel" in res["response"] or "très bien" in res["response"]
    assert len(res["agents_used"]) == 0

def test_agent_manager_ambiguous_code_clarification():
    # 'code' should receive clarification prompt
    res = global_agent_manager.execute_task("code", {})
    assert res["orchestrated"] is False
    assert "ambiguë" in res["response"]
    assert len(res["agents_used"]) == 0

def test_agent_manager_project_roadmap():
    # 'feuille de route' should return helpful roadmap outline
    res = global_agent_manager.execute_task("je veux une feuille de route pour un projet web", {})
    assert res["orchestrated"] is False
    assert "feuille de route" in res["response"].lower()
    assert "maquettage" in res["response"].lower() or "conception" in res["response"].lower()
    assert len(res["agents_used"]) == 0

def test_agent_manager_orchestration_for_development_php():
    # Script PHP should trigger agents and produce adapted output code
    res = global_agent_manager.execute_task("écris un script PHP qui calcule la somme de deux entiers", {})
    assert res["orchestrated"] is True
    assert "code" in res
    assert "additionnerEntiers" in res["code"]["code"]
    assert len(res["agents_used"]) > 0

def test_system_command_pipeline():
    # Test that memory command queries the monitor
    res = global_agent_manager.execute_task("vérifie la mémoire", {})
    assert res["orchestrated"] is False
    assert res["route_decision"] == "Commandes système"
    assert "ressources" in res["response"].lower() or "cpu" in res["response"].lower()
