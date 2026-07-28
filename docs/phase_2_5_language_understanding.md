# Hikmara AI - Documentation de la Phase 2.5 : Couche de Compréhension Linguistique, Architecture LLM & Stabilisation du Routage

Cette documentation décrit en détail la conception, l'architecture et le fonctionnement de la **Phase 2.5 — Couche de Compréhension Linguistique & Stabilisation du Routage** dans Hikmara AI, s'appuyant sur une architecture type ChatGPT locale.

---

## 1. Problème Initial & Motivations

Avant la Phase 2.5, le système s'appuyait sur des expressions régulières définies directement au niveau du routeur d'intentions. Bien que fonctionnel pour des cas unitaires simples, ce couplage posait des limites critiques :
1. **Échecs d'intentions sur les requêtes naturelles de programmation** : Les demandes formulées naturellement (*"Je veux un programme Python..."*) échouaient souvent et retournaient l'intention `Inconnu`.
2. **Perte de contexte lors des suivis** : Les modifications de code successives (*"Ajoute une interface graphique"*, puis *"Ajoute SQLite"*) perdaient la mémoire du domaine d'origine (Python) ou réinitialisaient la mémoire de travail de génération de code.
3. **Couplage rigide des réponses** : Les réponses conversationnelles étaient codées en dur, empêchant l'intégration d'un véritable LLM local.

---

## 2. Architecture en Couches (type ChatGPT Local)

La Phase 2.5 sépare strictement les responsabilités pour offrir une architecture extensible, modulaire et hautement réutilisable :

```text
                     ┌─────────────────────────────┐
                     │        Utilisateur          │
                     └──────────────┬──────────────┘
                                    │
                                    ▼
                     Conversation Manager (Context)
             (historique, contexte, session, sujet)
                                    │
                                    ▼
                          Intelligent Router
          (intention, domaine, langue, sécurité,
             complexité, besoin mémoire/outils)
                    ┌─────────┼─────────┐
                    │         │         │
                    ▼         ▼         ▼
               Memory     Tool Router   Agent Router
          (SQLite/RAG)      │              │
                    │        │              │
                    └────────┴──────┬───────┘
                                   ▼
                           Local LLM Engine
             (Ollama, GGUF, Transformers, Cloud)
                                   │
                                   ▼
                           Post Processing
       (formatage, sécurité, citations, contexte,
        traduction, nettoyage de la réponse)
                                   │
                                   ▼
                               Réponse
```

---

## 3. Les Composants Clés

### A. Conversation Manager (`cognition/context/service.py`)
- Conserve l'historique de la discussion de façon transparente sans dupliquer la mémoire grâce à une synchronisation directe avec le système hybride de Hikmara (`global_memory_system`).
- Suit le sujet ou thème courant, les fichiers et les codes générés précédemment, les clés d'API et variables d'environnement.

### B. Intelligent Router (`cognition/router/service.py`)
Combine les signaux du Language Understanding Layer avec les composants découplés :
- **ToolRouter** (`cognition/router/tool_router.py`) : Analyse si la tâche nécessite un outil et effectue des audits de sécurité via le `SecurityPolicyEngine` avant son exécution.
- **AgentRouter** (`cognition/router/agent_router.py`) : Décide s'il est nécessaire de wake up la suite d'agents collaboratifs spécialisés (`Architect`, `Programmer`, `Tester`, `Security`, `Docs`), évitant tout déclenchement inutile pour les demandes simples.

### C. Local LLM Engine (`ai_models/llm/`)
Hikmara s'appuie désormais sur une abstraction flexible `BaseLLM` (`ai_models/llm/base.py`) :
- **OllamaEngine** : Détecte dynamiquement si Ollama est installé en local (sur `localhost:11434`), liste les modèles présents, gère les switchs et bascule de manière invisible sur un mode simulé si aucun modèle n'est présent.
- **TransformersEngine** / **GGUFEngine** / **FutureCloudEngine** : Prêts pour les extensions futures ou les déploiements spécifiques.
- **Configuration YAML** (`config/llm.yaml`) : Centralise l'ensemble des hyperparamètres (température, timeout, contexte maximal, system prompt, device) sans aucun code en dur.

### D. Memory RAG (`cognition/conversation/memory_retriever.py`)
- Analyse la requête utilisateur pour extraire les faits pertinents enregistrés dans la mémoire utilisateur ou le vector store locale *avant* de générer la réponse.
- Injecte ces faits en pré-prompt, de sorte que le LLM réagit avec une connaissance complète de l'historique utilisateur.

### E. Post Processing (`cognition/conversation/post_processing.py`)
- Nettoie les balises d'injection ou artifacts de modèles.
- Enforce le formatage Markdown des codes et des tableaux.
- Masque automatiquement les informations sensibles comme les clés d'API ou les variables locales (`.env`).
- Ajoute des citations aux fichiers consultés.

---

## 4. Tests Unitaires & d'Intégration

Les fonctionnalités ont été éprouvées par 65 tests automatisés :
- `tests/cognition/test_understanding.py` : Teste le moteur de compréhension linguistique et les scores de confiance.
- `tests/cognition/test_router.py` : Teste les décisions découplées de `ToolRouter` et `AgentRouter`.
- `tests/cognition/test_conversation.py` : Valide le cycle complet de modifications progressives de code et de conversion en mode conversationnel.

La suite complète s'exécute avec succès en moins de 1.1s.
