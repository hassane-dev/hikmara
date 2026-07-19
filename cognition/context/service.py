from cognition.context.models import ConversationContext
from memory.service import global_memory_system

class ContextManager:
    def __init__(self):
        self._current_context = ConversationContext()

    def get_context(self) -> ConversationContext:
        """Returns the current conversation context, synced with hybrid memory system."""
        self._current_context.messages = global_memory_system.conversation_memory
        return self._current_context

    def update_context(self, role: str, message: str, routing_decision=None, nlu_result=None):
        """Updates context with a new message turn, extracting active domain, language, and references."""
        # Avoid duplicate consecutive turns if they have the exact same message and role
        history = global_memory_system.conversation_memory
        is_duplicate = False
        if history and history[-1]["role"] == role and history[-1]["message"] == message:
            is_duplicate = True

        if not is_duplicate:
            global_memory_system.add_conversation_turn(role, message)

        context = self._current_context
        context.messages = global_memory_system.conversation_memory

        text_lower = message.lower()

        # Update from NLU result first if available (Phase 2.5)
        if nlu_result:
            context.context_references["last_nlu_result"] = nlu_result.model_dump()
            context.language = nlu_result.language
            context.previous_intents.append(nlu_result.intent)

            # Merge entities
            for k, v in nlu_result.entities.items():
                context.detected_entities[k] = v

            # Keep active domain if this is a follow-up or modification request and the new domain is general
            if nlu_result.is_follow_up or nlu_result.intent in ["code_modification", "code_conversion"]:
                if nlu_result.domain in ["general", "conversation"] and context.active_domain:
                    # Keep existing active_domain
                    pass
                elif nlu_result.domain and nlu_result.domain not in ["general", "conversation"]:
                    context.active_domain = nlu_result.domain
            else:
                if nlu_result.domain and nlu_result.domain not in ["general", "conversation"]:
                    context.active_domain = nlu_result.domain

        # Update from routing decision if available
        if routing_decision:
            context.previous_routing_decisions.append(routing_decision.model_dump())
            if not nlu_result:
                context.previous_intents.append(routing_decision.intent)
                if routing_decision.domain and routing_decision.domain not in ["general", "conversation"]:
                    context.active_domain = routing_decision.domain
                if routing_decision.language:
                    context.language = routing_decision.language

        # Text-based features tracking fallback
        if "python" in text_lower:
            context.active_domain = "python"
        elif "php" in text_lower:
            context.active_domain = "php"
        elif "database" in text_lower or "base de données" in text_lower:
            context.active_domain = "database"

        # Manage code references
        if "python" in text_lower and ("code" in text_lower or "programme" in text_lower or "écris" in text_lower):
            context.context_references["last_code_type"] = "python"
        elif "php" in text_lower and ("code" in text_lower or "programme" in text_lower or "écris" in text_lower):
            context.context_references["last_code_type"] = "php"

        # Track features in active code progressively
        if "interface graphique" in text_lower or "gui" in text_lower or "pyqt" in text_lower:
            context.context_references["has_gui"] = True
        if "sqlite" in text_lower or "base de données" in text_lower or "database" in text_lower:
            context.context_references["has_sqlite"] = True

    def set_last_generated_code(self, code_text: str):
        """Stores the latest generated code in contextual references."""
        self._current_context.context_references["last_generated_code"] = code_text

    def reset_context(self):
        """Fully resets the active context and the global hybrid memory system conversation log."""
        self._current_context = ConversationContext()
        global_memory_system.conversation_memory = []

global_context_manager = ContextManager()
