# Hikmara AI - Documentation de la Phase 2.5 : Couche de Compréhension Linguistique et Stabilisation du Routage

Cette documentation décrit en détail la conception, l'architecture et le fonctionnement de la **Phase 2.5 — Couche de Compréhension Linguistique & Stabilisation du Routage** dans Hikmara AI.

---

## 1. Problème Initial & Motivations

Avant la Phase 2.5, le système s'appuyait sur des expressions régulières définies directement au niveau du routeur d'intentions. Bien que fonctionnel pour des cas unitaires simples, ce couplage posait des limites critiques :
1. **Échecs d'intentions sur les requêtes naturelles de programmation** : Les demandes formulées naturellement (*"Je veux un programme Python..."*) échouaient souvent et retournaient l'intention `Inconnu`.
2. **Perte de contexte lors des suivis** : Les modifications de code successives (*"Ajoute une interface graphique"*, puis *"Ajoute SQLite"*) perdaient la mémoire du domaine d'origine (Python) ou réinitialisaient la mémoire de travail de génération de code.
3. **Mélange des responsabilités** : L'analyse sémantique du texte et la décision de sélection du pipeline étaient confondues au sein d'une seule classe.

---

## 2. Différence entre NLU et Routage

La Phase 2.5 introduit une séparation stricte des responsabilités (separation of concerns) :
- **Language Understanding Layer (NLU)** : Répond à la question *« Que veut dire l'utilisateur ? »* en analysant s'il s'agit d'une salutation, d'une demande de code, d'une modification, d'une conversion, d'une commande système, etc., tout en identifiant la langue et le domaine (Python, PHP, etc.) indépendamment de l'état du système.
- **Intelligent Router** : Répond à la question *« Quel pipeline d'exécution doit prendre en charge cette demande ? »* en combinant le résultat NLU et l'état de la session (le contexte). Par exemple, si le NLU détecte une modification de code sans domaine explicite, mais que le contexte indique que nous parlions de Python, le routeur ré-attribue dynamiquement le domaine Python et sélectionne le pipeline `coding_conversation`.

---

## 3. Architecture en Couches

Le traitement d'une requête utilisateur suit désormais un pipeline asymétrique et hiérarchisé :

```text
Message utilisateur (ex: "Ajoute SQLite.")
        │
        ▼
[ Language Understanding Layer ] ──► Extrait Intention, Domaine, Langue, Entités
        │
        ▼
[ Conversation Context ] ──────────► Injecte les variables d'historique (ex: domaine=python)
        │
        ▼
[ Intelligent Router ] ────────────► Calcule le pipeline optimal (ex: coding_conversation)
        │
        ▼
[ Execution Pipeline ] ────────────► ConversationEngine / AgentManager / System / Tools
```

---

## 4. Modèle `LanguageUnderstandingResult`

Défini dans `cognition/understanding/models.py`, ce modèle Pydantic régit la sortie de la compréhension linguistique :
- **`text`** (str) : Le texte original de la requête utilisateur.
- **`language`** (str) : La langue détectée (`fr` ou `en`).
- **`intent`** (str) : L'intention (`greeting`, `general_conversation`, `code_generation`, `code_modification`, `explanation`, `code_conversion`, `system`, `tools`, `unknown`).
- **`domain`** (str) : Le domaine thématique (`python`, `php`, `database`, `system`, `tools`, `conversation`, `general`).
- **`entities`** (dict) : Entités clés extraites (ex: `operation: addition`, `interface_type: pyqt6`, `database_type: sqlite`).
- **`confidence`** (float) : Le niveau de confiance sémantique (de 0.0 à 1.0).
- **`is_follow_up`** (bool) : `True` si la requête fait référence à une étape précédente ou à un suivi.
- **`references_previous_context`** (bool) : `True` si le prompt mentionne explicitement le contexte précédent (ex: *"précédent"*, *"avant"*).

---

## 5. Détection des Intentions & Domaines

Le service `LanguageUnderstandingService` (`cognition/understanding/service.py`) s'appuie sur une classification multi-signaux :
1. **Intention** : Un ordre de priorité strict est défini (Salutations, Conversation générale, Conversion, Modification, Explication, Système, Outils, Génération de code). Cela évite qu'une demande de modification ou de conversion ne soit par erreur classée en simple génération ou en inconnu.
2. **Domaine** : Reconnaissance robuste des extensions et mots-clés (`python`, `php`, `sqlite`, `database`, etc.) combinée avec une déduction d'historique contextuel.
3. **Langue** : Analyse par dictionnaire de fréquences pour classifier de manière fiable la langue de l'utilisateur (français vs anglais).

---

## 6. Score de Confiance & Fallback Modèle Local

Chaque requête reçoit un score `confidence` :
- **Confiance Élevée** (>= 0.90) : Les intentions claires basées sur des modèles linguistiques reconnus s'exécutent directement via les moteurs déterministes ultra-rapides.
- **Confiance Faible** (< 0.80) : Pour les requêtes ambiguës, le système s'appuie sur une analyse contextuelle étendue ou délègue à l'interface locale du modèle de langage `LLMEngine`. Cela garantit qu'aucune salutation simple ou commande CPU n'utilise inutilement le GPU de l'utilisateur.

---

## 7. Gestion du Contexte & Génération Progressive

Le `ContextManager` maintient la continuité de l'échange de manière incrémentale. Lors du traitement de scénarios de génération de code progressive :
1. **Étape 1 (Génération simple)** : *"Je veux un programme Python pour additionner deux entiers."* -> Génère une fonction mathématique pure et l'enregistre dans `last_generated_code`.
2. **Étape 2 (Modification graphique)** : *"Ajoute une interface graphique."* -> Le contexte détecte `has_gui=True` et le domaine actif Python. Le moteur conversationnel génère l'interface PyQt6 contenant l'addition précédente.
3. **Étape 3 (Persistance base de données)** : *"Ajoute SQLite."* -> Le contexte détecte `has_sqlite=True` tout en retenant `has_gui=True`. Le programme est étendu pour intégrer la base SQLite avec l'interface graphique.
4. **Étape 4 (Conversion linguistique)** : *"Convertis le programme précédent en PHP."* -> Le NLU détecte la conversion vers le domaine PHP, et le moteur génère le code PHP intégrant la persistance SQLite de l'étape précédente.

---

## 8. Sécurité Intégrée

La couche NLU et le routeur n'interfèrent pas avec les contrôles de sécurité :
- Toute requête exigeant un outil (ex: *"Exécute ce script"* ou *"Crée un fichier"*) est routée vers le pipeline `tools` ou `agent_task`.
- L'action sensible interroge le `SecurityPolicyEngine` qui présente un dialogue de consentement utilisateur (ou bloque l'action) et enregistre l'événement dans le journal d'audit SQLite de manière inaltérable.

---

## 9. Validation & Tests

La Phase 2.5 apporte des tests unitaires et d'intégration très complets :
- **`tests/cognition/test_understanding.py`** : Couvre la détection des intentions, des domaines, de la langue et de la confiance.
- **`tests/cognition/test_conversation.py`** : Valide le scénario de génération progressive (Simple -> PyQt6 -> SQLite -> PHP SQLite) en mode multi-tours.
- **`tests/cognition/test_router.py`** & **`tests/cognition/test_intent_router.py`** : Valident la stabilité de l'Intelligent Router et la non-régression de l'existant.

Tous les 61 tests s'exécutent et réussissent à 100 %.
