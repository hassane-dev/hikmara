# Hikmara AI - Documentation de la Phase 2 : Routage Intelligent, Moteur Conversationnel et Gestion de Contexte

Cette documentation décrit en détail l'architecture, le fonctionnement et l'intégration des composants de la **Phase 2 — Routage Intelligent, Moteur Conversationnel & Gestion de Contexte** dans Hikmara AI.

---

## 1. Architecture Actuelle

Hikmara AI est une plateforme d'IA locale modulaire et offline-first. Le flux général d'une requête utilisateur dans la Phase 2 s'organise ainsi :

```text
Utilisateur / PyQt6 Interface / headless
    │
    ▼
Context Manager (cognition/context/service.py)
    ├── Synced with global_memory_system (no duplication)
    └── Active Session variables (intent history, domain, code ref, etc.)
    │
    ▼
Intelligent Router (cognition/router/service.py)
    ├── Evaluates prompt regexes & keyword scores
    └── Produces structured RoutingDecision
    │
    ▼
Agent Manager (cognition/agents/manager/service.py)
    │
    ├─── [ direct_conversation / conversation / coding_conversation ] ──► Conversation Engine
    │                                                                        ├── Local LLMEngine
    │                                                                        └── Follow-up code modifiers
    │
    ├─── [ system_commands ] ───────────────────────────────────────────► System Services & Resource Monitor
    │
    ├─── [ tools ] ─────────────────────────────────────────────────────► Security Policy & Tool Registry
    │
    └─── [ agent_task ] ────────────────────────────────────────────────► Multi-Agent Orchestration
                                                                             ├── Architect Agent
                                                                             ├── Programmer Agent
                                                                             ├── Tester Agent
                                                                             ├── Security Agent
                                                                             └── Documentation Agent
```

---

## 2. Limites du Routage Actuel (Avant Phase 2)

Avant l'introduction de la Phase 2 :
1. **Absence de routage intelligent sélectif** : Toutes les demandes (des simples salutations aux requêtes complexes) déclenchaient systématiquement la suite d'agents au complet (Architect, Programmer, Tester, etc.). Cela consommait d'importantes ressources locales pour des tâches triviales.
2. **Décision non structurée** : La décision d'intention était représentée par un simple modèle `IntentResult` rudimentaire qui ne permettait pas de capturer la complexité de la requête, la langue, le domaine actif, ou les besoins fins en mémoire/outils.
3. **Absence de Gestion de Contexte** : Chaque message utilisateur était traité de manière isolée, empêchant les demandes séquentielles (ex: *"Écris un programme Python"* suivi de *"Ajoute maintenant une interface graphique"*).
4. **Moteur conversationnel basique** : Les réponses du système local étaient statiques et génériques (*"I am Hikmara AI local system..."*).

---

## 3. La Nouvelle Architecture de Routage

La Phase 2 résout ces limites en introduisant un **pipeline de routage décisionnel structuré, asymétrique et contextuel** qui évalue chaque message de manière fine avant de l'exécuter.
- Les requêtes simples de conversation ou de code basique sont traitées directement par le **Conversation Engine**.
- Les requêtes de diagnostic système sont envoyées au pipeline **System Commands**.
- Les requêtes d'outils complexes ou nécessitant des actions système passent par le **Tool Registry** avec validation du **Security Policy Engine**.
- Seules les tâches de développement d'ingénierie complexes déclenchent le gestionnaire de tâches multi-agents.

---

## 4. `RoutingDecision`

La structure `RoutingDecision` est définie dans `cognition/router/models.py`. Elle étend `BaseModel` de Pydantic et contient :

- **`intent`** (str) : L'intention détectée (ex: `Salutations`, `Conversation générale`, `Génération de code`, etc.).
- **`domain`** (str) : Le domaine thématique (ex: `python`, `php`, `database`, `tools`, `system`, `conversation`).
- **`complexity`** (str) : La complexité évaluée (`trivial`, `simple`, `moderate`, `complex`, `critical`).
- **`language`** (str) : La langue détectée (`fr`, `en`).
- **`pipeline`** (str) : Le canal d'exécution (`direct_conversation`, `conversation`, `coding_conversation`, `agent_task`, `system_commands`, `tools`).
- **`requires_model`** (bool) : Si l'intervention du modèle local est nécessaire.
- **`requires_tools`** (bool) : Si des outils locaux sont nécessaires.
- **`requires_agents`** (bool) : Si la suite multi-agents doit être mobilisée.
- **`requires_memory`** (bool) : Si la requête nécessite l'accès à la mémoire ou au contexte conversationnel historique.
- **`safety_level`** (str) : Niveau de sécurité (`normal`, `sensitive`).
- **`agents_to_trigger`** (List[str]) : Agents à activer si applicable.
- **`justification`** (str) : Explication de la décision de routage.

*Remarque : `IntentResult` hérite de `RoutingDecision` pour assurer une compatibilité totale à 100% avec le code et les tests de la Phase 1.5.*

---

## 5. `Context Manager`

Le `ContextManager` (`cognition/context/service.py`) centralise le contexte d'interaction :
- Il gère un modèle `ConversationContext` décrivant les messages récents, les intentions passées, le domaine actif, la langue et les entités détectées.
- **Pas de duplication de données** : Le gestionnaire de contexte se synchronise de manière bidirectionnelle avec le système de mémoire hybride (`global_memory_system`) existant de Hikmara.
- **Suivi des références de code** : Lors de la génération de code, il conserve une référence de la dernière syntaxe produite afin d'autoriser les modifications progressives.

---

## 6. `Conversation Engine`

Le `ConversationEngine` (`cognition/conversation/service.py`) est responsable de la génération de réponses conversationnelles naturelles offline :
- Il gère les salutations, échanges polis et explications techniques en français et en anglais de manière fluide.
- **Résolution des suivis (Follow-up)** : Si l'utilisateur demande une modification de code (ex: *"Ajoute maintenant une interface graphique"*), le moteur consulte la référence de code dans le contexte, détecte le framework PyQt6 demandé, et génère un programme Python graphique complet intégrant la fonction précédente.

---

## 7. Intégration des Modèles Locaux

L'interaction avec le modèle d'IA local se fait à travers l'interface `BaseAIModel` implémentée par `LLMEngine` (`ai_models/llm/service.py`).
- Le système fonctionne de manière offline-first par défaut avec des fallbacks robustes en cas d'absence de GPU ou de modèle de poids lourd sur la machine de l'utilisateur.

---

## 8. Routage des Outils

Le routeur détecte la nécessité d'utiliser des outils (`requires_tools = True`).
- Toute exécution d'outil sensible (comme `create_file` ou `execute_code`) passe impérativement par le **Security Policy Engine** qui valide les permissions requises et consigne l'action dans les journaux d'audit SQLite de manière inaliénable.

---

## 9. Intégration Multi-Agents

Le système multi-agents n'est déclenché que pour les tâches complexes (`agent_task`), optimisant l'usage CPU/RAM :
- Si la complexité est évaluée comme `trivial` ou `simple` (ex: addition de deux entiers), le système utilise le pipeline direct sans réveiller l'équipe d'agents.
- Si la complexité est `complex` ou `critical`, l'**AgentManager** orchestre la suite (`Architect`, `Programmer`, `Tester`, `Security`, `Docs`).

---

## 10. Sécurité & Audits

La sécurité intercepte transversalement toute action sensible :
- `global_security_policy.authorize_action` est interrogée avant d'accéder au système de fichiers ou d'exécuter du code local.
- Les actions sont consignées de manière persistante en base SQLite avec mention de l'autorisation obtenue (APPROVED / DENIED).

---

## 11. Tests Établis

Les tests de la Phase 2 ont été ajoutés et validés avec succès :
- **`tests/cognition/test_router.py`** : Valide le routage des salutations, questions générales, code simple, tâches complexes, requêtes d'outils, agents et niveaux de sécurité.
- **`tests/cognition/test_context.py`** : Valide l'initialisation, la mise à jour sans duplication de mémoire, les références de code et la réinitialisation du contexte.
- **`tests/cognition/test_conversation.py`** : Valide la fluidité des réponses conversationnelles, le support du français/anglais, et la modification de code contextuelle progressive.

Toutes les suites de tests existantes et nouvelles (50 tests au total) s'exécutent et réussissent à 100 %.

---

## 12. Décisions d'Architecture (ADRs)

Les choix techniques majeurs de cette phase sont documentés dans `docs/adr/` :
- **Sous-classement de `RoutingDecision`** : Permet de répondre aux nouvelles exigences de routage sans réécrire l'existant.
- **Intégration unifiée de la Mémoire** : Liaison directe du Context Manager au `HybridMemorySystem` pour assurer une seule source de vérité.

---

## 13. Évolutions Futures

Pour les phases suivantes de Hikmara AI, plusieurs évolutions sont envisagées :
1. **Intégration de Vector Store avancée** : Exploiter pleinement le `global_vector_store` pour faire du RAG (Retrieval-Augmented Generation) sur les documents locaux et le projet analysé de l'utilisateur.
2. **Orchestration multi-agents asynchrone** : Permettre l'exécution en arrière-plan d'agents d'ingénierie asynchrones via des files d'attente (Task Queues) pour ne pas bloquer l'interface graphique de l'utilisateur sur de très grands projets.
3. **Apprentissage continu local** : Enregistrer les corrections de l'utilisateur pour adapter dynamiquement la confiance du routeur et les paramètres du modèle local.
