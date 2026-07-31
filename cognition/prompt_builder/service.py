import os
from typing import Dict, Any, List
from cognition.prompt_builder.registry import global_prompt_template_registry
from cognition.prompt_builder.optimizer import global_prompt_optimizer
from ai_models.model_registry.service import global_model_registry

class PromptBuilder:
    def __init__(self):
        pass

    def build_prompt(self, user_message: str, context: Any, memory_context: str, intent: str, active_model: str = "qwen2.5:3b") -> Dict[str, str]:
        """Assembles the final prompt dictionary with 'system' and 'user' sections, optimized for context tokens."""
        language = getattr(context, "language", "fr") or "fr"

        # ==========================================
        # 1. SYSTEM IDENTITY (Identité et règles permanentes)
        # ==========================================
        system_base = global_prompt_template_registry.get_template("system.md", language)
        system_parts = [system_base]

        # ==========================================
        # 2. TASK CONTEXT (Directives de l'intention courante uniquement)
        # ==========================================
        intent_template = ""
        # Map localized intents or keys
        if intent in ["Salutations", "Conversation générale", "greeting", "general_conversation"]:
            intent_template = global_prompt_template_registry.get_template("conversation.md", language)
        elif intent in ["Génération de code", "Développement logiciel", "Explication de code", "code_generation", "code_modification", "code_conversion", "explanation"]:
            intent_template = global_prompt_template_registry.get_template("coding.md", language)
        elif intent in ["Sécurité", "security"]:
            intent_template = global_prompt_template_registry.get_template("security.md", language)
        elif intent in ["Requêtes complexes", "planning"]:
            intent_template = global_prompt_template_registry.get_template("planning.md", language)
        else:
            intent_template = global_prompt_template_registry.get_template("conversation.md", language)

        if intent_template:
            system_parts.append(intent_template)

        # ==========================================
        # 3. ACTIVE CONTEXT (Informations de session éphémères pertinentes)
        # ==========================================
        if context:
            ctx_parts = []
            if context.active_domain:
                ctx_parts.append(f"Domaine actif : {context.active_domain}")
            if context.language:
                ctx_parts.append(f"Langue d'interaction : {context.language}")

            # Règle de cloisonnement spécifique pour last_generated_code
            # Injecté uniquement pour les modifications, conversions de code, ou requêtes d'adaptation explicites
            is_code_adaptation_intent = intent in ["code_modification", "code_conversion", "Développement logiciel"]
            user_msg_lower = user_message.lower()
            is_explicit_adaptation_request = any(k in user_msg_lower for k in [
                "modifie", "change", "ajoute", "corrige", "convertis", "réécris", "adapte", "décline", "en intégrant", "integre"
            ])

            if (is_code_adaptation_intent or is_explicit_adaptation_request) and intent not in ["Salutations", "greeting"]:
                last_code = context.context_references.get("last_generated_code")
                if last_code:
                    ctx_parts.append(f"Dernier code généré de l'échange (à modifier ou adapter si demandé) :\n```\n{last_code}\n```")

            if ctx_parts:
                system_parts.append("## Contexte de la session active :\n" + "\n".join(ctx_parts))

        combined_system = "\n\n".join(system_parts)

        # ==========================================
        # 4. MEMORY / HISTORY (Historique + RAG optimisé)
        # ==========================================
        # Retrieve model constraints (max_context) and run Prompt Optimizer
        specs = global_model_registry.get_model(active_model)
        max_context = specs.max_context if specs else 2048

        # Extract message history turns from context to pass to optimizer
        history_turns: List[Dict[str, str]] = getattr(context, "messages", []) or []

        optimized = global_prompt_optimizer.optimize_prompt_inputs(
            system_base=combined_system,
            history=history_turns,
            retrieved_context=memory_context,
            user_message=user_message
        )

        # Build final combined system prompt including RAG retrieved memories
        system_prompt_parts = [optimized["system_prompt"]]
        if optimized["retrieved_context"]:
            system_prompt_parts.append(f"## Contexte récupéré (RAG) :\n{optimized['retrieved_context']}")

        # Format optimized history turns into prompt system context
        if optimized["history"]:
            hist_str_parts = []
            for h in optimized["history"]:
                role_label = "Utilisateur" if h.get("role") == "user" else "Assistant"
                hist_str_parts.append(f"{role_label}: {h.get('message')}")
            system_prompt_parts.append("## Historique des échanges :\n" + "\n".join(hist_str_parts))

        final_system = "\n\n".join(system_prompt_parts)

        # ==========================================
        # 5. USER REQUEST (La requête actuelle de l'utilisateur)
        # ==========================================
        final_user = f"Message utilisateur :\n{user_message}"

        return {
            "system": final_system,
            "user": final_user
        }

global_prompt_builder = PromptBuilder()
