# Hikmara AI - Intent Router Module

This module provides the modular and highly extensible **Intent Router** component for Hikmara AI. It classifies user prompts into various semantic intent classes before executing any multi-agent sequence or background routines.

## Architecture & Design

The module consists of:
- `models.py`: Defines the structured `IntentResult` data model.
- `service.py`: Contains the `IntentRouter` class which evaluates regex-based rules sequentially and exposes dynamic registration of newer rules.

## Intent Categories Supported
1. **Salutations**
2. **Conversation générale**
3. **Développement logiciel**
4. **Génération de code**
5. **Analyse de code**
6. **Explication de code**
7. **Questions techniques**
8. **Commandes système**
9. **Gestion des outils**
10. **Recherche d'informations**
11. **Sécurité**
12. **Requêtes complexes**
13. **Inconnu** (fallback)

## Usage

```python
from cognition.router import global_intent_router

intent_res = global_intent_router.route("Bonjour, comment ça va ?")
print(intent_res.category) # "Salutations"
print(intent_res.recommended_pipeline) # "Conversation"
```
