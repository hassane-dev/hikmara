# NLU (Language Understanding) Layer

This package is completely decoupled from Request Routing, focusing strictly on semantic parsing:
- `models.py`: Defines the structured `LanguageUnderstandingResult` model.
- `service.py`: Contains pattern-based and semantic analyses to extract intents, domains, language, and confidence levels.
