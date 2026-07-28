import os
from typing import Dict, Any

class PromptBuilder:
    def __init__(self):
        self.prompts_dir = "prompts"

    def _load_template(self, filename: str) -> str:
        """Helper to safely read prompt files from prompts/ directory."""
        path = os.path.join(self.prompts_dir, filename)
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return f.read().strip()
            except Exception:
                pass
        return ""

    def build_prompt(self, user_message: str, context: Any, memory_context: str, intent: str) -> Dict[str, str]:
        """Assembles the final prompt dictionary with 'system' and 'user' sections."""
        # 1. Load system base prompt
        system_base = self._load_template("system.md")
        if not system_base:
            system_base = "Vous êtes Hikmara AI, un assistant d'intelligence locale universel hors-ligne."

        # 2. Select specific template based on parsed intent
        intent_template = ""
        if intent in ["Salutations", "Conversation générale"]:
            intent_template = self._load_template("conversation.md")
        elif intent in ["Génération de code", "Développement logiciel", "Explication de code"]:
            intent_template = self._load_template("coding.md")
        elif intent == "Sécurité":
            intent_template = self._load_template("security.md")
        elif intent == "Requêtes complexes":
            intent_template = self._load_template("planning.md")
        else:
            intent_template = self._load_template("conversation.md")

        # Combine system sections
        system_parts = [system_base]
        if intent_template:
            system_parts.append(intent_template)

        # 3. Inject memory / retrieved RAG facts
        if memory_context:
            system_parts.append(f"## Contexte de la mémoire locale :\n{memory_context}")

        # 4. Inject active session / context references (previous code, active domain, active language)
        if context:
            ctx_parts = []
            if context.active_domain:
                ctx_parts.append(f"Domaine actif : {context.active_domain}")
            if context.language:
                ctx_parts.append(f"Langue d'interaction : {context.language}")

            last_code = context.context_references.get("last_generated_code")
            if last_code:
                ctx_parts.append(f"Dernier code généré de l'échange :\n```\n{last_code}\n```")

            if ctx_parts:
                system_parts.append("## Contexte de la session active :\n" + "\n".join(ctx_parts))

        system_prompt = "\n\n".join(system_parts)

        # 5. User prompt formatting
        user_prompt = f"Message utilisateur :\n{user_message}"

        return {
            "system": system_prompt,
            "user": user_prompt
        }

global_prompt_builder = PromptBuilder()
