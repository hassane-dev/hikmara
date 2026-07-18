from cognition.context.models import ConversationContext
from memory.service import global_memory_system

class ContextManager:
    def __init__(self):
        self._current_context = ConversationContext()

    def get_context(self) -> ConversationContext:
        """Returns the current conversation context, synced with hybrid memory system."""
        self._current_context.messages = global_memory_system.conversation_memory
        return self._current_context

    def update_context(self, role: str, message: str, routing_decision=None):
        """Updates context with a new message turn, extracting active domain, language, and references."""
        # Add to the global memory system to prevent duplication
        global_memory_system.add_conversation_turn(role, message)

        context = self._current_context
        context.messages = global_memory_system.conversation_memory

        text_lower = message.lower()

        # Update from routing decision if available
        if routing_decision:
            context.previous_intents.append(routing_decision.intent)
            context.previous_routing_decisions.append(routing_decision.model_dump())
            if routing_decision.domain and routing_decision.domain not in ["general", "conversation"]:
                context.active_domain = routing_decision.domain
            if routing_decision.language:
                context.language = routing_decision.language

        # Text-based domain detection fallback
        if "python" in text_lower:
            context.active_domain = "python"
        elif "php" in text_lower:
            context.active_domain = "php"
        elif "database" in text_lower or "base de données" in text_lower:
            context.active_domain = "database"

        # Detect entity references
        if "pyqt" in text_lower or "pyqt6" in text_lower:
            context.detected_entities["gui_framework"] = "pyqt6"
        elif "tkinter" in text_lower:
            context.detected_entities["gui_framework"] = "tkinter"

        # Manage code references
        if "python" in text_lower and ("code" in text_lower or "programme" in text_lower or "écris" in text_lower):
            context.context_references["last_code_type"] = "python"
        elif "php" in text_lower and ("code" in text_lower or "programme" in text_lower or "écris" in text_lower):
            context.context_references["last_code_type"] = "php"

    def set_last_generated_code(self, code_text: str):
        """Stores the latest generated code in contextual references."""
        self._current_context.context_references["last_generated_code"] = code_text

    def reset_context(self):
        """Fully resets the active context and the global hybrid memory system conversation log."""
        self._current_context = ConversationContext()
        global_memory_system.conversation_memory = []

global_context_manager = ContextManager()
