import pytest
from cognition.router.service import global_intent_router

def test_greeting_routing():
    decision = global_intent_router.route("Bonjour")
    assert decision.intent == "Salutations"
    assert decision.complexity == "trivial"
    assert decision.pipeline == "direct_conversation"
    assert decision.requires_agents is False
    assert decision.requires_model is True

def test_general_question_routing():
    decision = global_intent_router.route("Comment fonctionne une base de données ?")
    assert "base de données" in decision.justification or decision.intent == "Questions techniques"
    assert decision.complexity in ["simple", "moderate"]
    assert decision.domain == "database"
    assert decision.requires_model is True
    assert decision.requires_agents is False

def test_simple_programming_routing():
    decision = global_intent_router.route("Écris-moi un programme Python qui calcule la somme de deux entiers.")
    assert decision.intent in ["Génération de code", "Développement logiciel"]
    assert decision.domain == "python"
    assert decision.complexity == "simple"
    assert decision.pipeline == "coding_conversation"
    assert decision.requires_agents is False

def test_complex_task_routing():
    decision = global_intent_router.route("Analyse mon projet PHP, identifie les problèmes de sécurité, corrige-les et écris les tests.")
    assert decision.domain == "php"
    assert decision.complexity == "complex"
    assert decision.pipeline == "agent_task"
    assert decision.requires_agents is True
    assert "architect" in decision.agents_to_trigger

def test_tool_required_routing():
    decision = global_intent_router.route("installe la dépendance Flask avec pip")
    assert decision.requires_tools is True
    assert decision.domain == "tools"

def test_agent_required_routing():
    decision = global_intent_router.route("conçois un système complet de paiement sécurisé")
    assert decision.requires_agents is True
    assert "programmer" in decision.agents_to_trigger

def test_sensitive_action_routing():
    decision = global_intent_router.route("exécute le script de nettoyage systeme")
    assert decision.safety_level == "sensitive"
