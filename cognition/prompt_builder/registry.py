import os
from typing import Dict, Any, Optional

class PromptTemplateRegistry:
    """
    Registry for managing and fetching system prompt templates from prompts/ folder.
    Handles discovery, default fallbacks, and multi-language template versions.
    """
    def __init__(self, templates_dir: str = "prompts"):
        self.templates_dir = templates_dir
        self._cache: Dict[str, str] = {}
        self._discover_templates()

    def _discover_templates(self):
        if not os.path.exists(self.templates_dir):
            os.makedirs(self.templates_dir)

        # Prefill default system fallback files if empty
        defaults = {
            "system.md": "# System Prompt\nVous êtes Hikmara AI, un assistant d'intelligence locale universel hors-ligne.",
            "conversation.md": "# Conversation Template\nVous êtes engagé dans une conversation générale avec l'utilisateur. Répondez de manière naturelle et constructive.",
            "coding.md": "# Coding Template\nVous êtes un expert en développement logiciel. Fournissez toujours du code propre et bien structuré.",
            "planning.md": "# Planning Template\nDécomposez la tâche complexe en étapes structurées et logiques.",
            "security.md": "# Security Template\nAnalysez le code et l'action sous l'angle de la sécurité informatique.",
            "testing.md": "# Testing Template\nConcevez des plans de test robustes et complets.",
            "translation.md": "# Translation Template\nTraduisez fidèlement le texte d'origine dans la langue cible."
        }

        for fname, content in defaults.items():
            path = os.path.join(self.templates_dir, fname)
            if not os.path.exists(path):
                try:
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(content)
                except Exception:
                    pass

    def get_template(self, template_name: str, language: str = "fr") -> str:
        """Retrieves template content from prompts/ directory, falling back gracefully if missing."""
        # Try finding language specific template if exists (e.g. conversation_en.md)
        base_name, ext = os.path.splitext(template_name)
        lang_template_name = f"{base_name}_{language}{ext}"

        path = os.path.join(self.templates_dir, lang_template_name)
        if not os.path.exists(path):
            path = os.path.join(self.templates_dir, template_name)

        if path in self._cache:
            return self._cache[path]

        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    self._cache[path] = content
                    return content
            except Exception:
                pass

        # Final fallback
        return f"# Template {base_name}\nVous êtes Hikmara AI local."

global_prompt_template_registry = PromptTemplateRegistry()
