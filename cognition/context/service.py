import re
from datetime import datetime
from typing import Dict, Any, List, Optional
from cognition.context.models import ConversationContext, WorkContext
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
        # Sync conversation memory
        history = global_memory_system.conversation_memory
        is_duplicate = False
        if history and history[-1]["role"] == role and history[-1]["message"] == message:
            is_duplicate = True

        if not is_duplicate:
            global_memory_system.add_conversation_turn(role, message)

        context = self._current_context
        context.messages = global_memory_system.conversation_memory
        text_lower = message.lower()

        if role == "assistant":
            context.previous_responses.append(message)

        # 1. Update general conversation and user preferences (survive subject shifts)
        if nlu_result:
            context.context_references["last_nlu_result"] = nlu_result.model_dump()
            context.language = nlu_result.language
            context.active_work_context.language = nlu_result.language
            context.previous_intents.append(nlu_result.intent)
            context.current_topic = nlu_result.intent

            # Subject Change Detection
            self.detect_subject_change(nlu_result)

            # Merge entities
            for k, v in nlu_result.entities.items():
                context.detected_entities[k] = v

        if routing_decision:
            context.previous_routing_decisions.append(routing_decision.model_dump())
            if not nlu_result:
                context.previous_intents.append(routing_decision.intent)
                context.current_topic = routing_decision.intent
                context.language = routing_decision.language
                context.active_work_context.language = routing_decision.language

        # User preferences / style profiling
        if "s'il te plaît" in text_lower or "please" in text_lower:
            context.user_preferences["polite"] = True
        if "court" in text_lower or "concis" in text_lower or "short" in text_lower:
            context.user_preferences["concise"] = True

        # 2. Update Work Context with technical variables
        work_ctx = context.active_work_context

        # Domain tracking on active work context
        if nlu_result and nlu_result.domain and nlu_result.domain not in ["general", "conversation"]:
            # Standardize db/sql domains
            domain_val = nlu_result.domain
            if domain_val == "sql":
                domain_val = "database"
            work_ctx.active_domain = domain_val
            context.active_domain = domain_val

        # Text-based features tracking fallback for backwards compatibility
        if "python" in text_lower:
            work_ctx.active_domain = "python"
            context.active_domain = "python"
        elif "php" in text_lower:
            work_ctx.active_domain = "php"
            context.active_domain = "php"
        elif "database" in text_lower or "base de données" in text_lower or "sqlite" in text_lower:
            work_ctx.active_domain = "database"
            context.active_domain = "database"

        # Manage code references
        if "python" in text_lower and ("code" in text_lower or "programme" in text_lower or "écris" in text_lower):
            work_ctx.context_references["last_code_type"] = "python"
        elif "php" in text_lower and ("code" in text_lower or "programme" in text_lower or "écris" in text_lower):
            work_ctx.context_references["last_code_type"] = "php"

        # Track features in active code progressively on active work context
        if "interface graphique" in text_lower or "gui" in text_lower or "pyqt" in text_lower:
            work_ctx.context_references["has_gui"] = True
            if "PyQt6" not in work_ctx.technologies:
                work_ctx.technologies.append("PyQt6")
        if "sqlite" in text_lower or "base de données" in text_lower or "database" in text_lower:
            work_ctx.context_references["has_sqlite"] = True
            if "SQLite" not in work_ctx.technologies:
                work_ctx.technologies.append("SQLite")

        # Map to old properties for full backward compatibility
        context.context_references.update(work_ctx.context_references)

        # Extract file references
        file_matches = re.findall(r"\b\w+\.(?:py|php|json|db|txt|yaml|yml|md)\b", text_lower)
        for f in file_matches:
            if f not in work_ctx.file_references:
                work_ctx.file_references.append(f)
            if f not in context.file_references:
                context.file_references.append(f)

        # 3. Apply Context Decay (decay old flags if query is unrelated)
        if role == "user":
            self.apply_context_decay(message, nlu_result)

    def detect_subject_change(self, new_nlu_result):
        """
        Detects semantic boundary breaks (e.g. switching from Python to weather, or SQLite to general greetings).
        Archives the current Work Context and spawns a fresh clean Work Context on shift.
        """
        context = self._current_context
        current_domain = context.active_work_context.active_domain
        new_domain = new_nlu_result.domain
        new_intent = new_nlu_result.intent

        # Standardize db/sql sub-domains
        if current_domain == "sql":
            current_domain = "database"
        if new_domain == "sql":
            new_domain = "database"

        # Safe guard: If the user is explicitly requesting code modification, conversion or a follow-up, it is NOT a subject shift
        if new_nlu_result.is_follow_up or new_nlu_result.references_previous_context or new_intent in ["code_modification", "code_conversion"]:
            return

        # Determine if a subject shift has occurred
        is_shift = False

        # 1. From active coding/tech domain to purely casual greeting/conversation/general topics
        if current_domain and current_domain not in ["general", "conversation"]:
            if new_domain in ["general", "conversation"] or new_intent in ["greeting", "general_conversation"]:
                is_shift = True

        # 2. Shift between two distinct non-compatible technical domains (e.g. python vs php, or python vs database)
        if current_domain and new_domain and current_domain != new_domain:
            tech_domains = ["python", "php", "javascript", "database", "cpp", "java"]
            if current_domain in tech_domains and new_domain in tech_domains:
                is_shift = True

        if is_shift:
            # Clôturer et archiver le contexte de travail courant
            self.archive_current_work_context(f"Rupture sémantique détectée : changement de domaine de {current_domain} vers {new_domain}.")

    def apply_context_decay(self, message: str, nlu_result=None):
        """
        Applies decay (gradual expiration) to context reference indicators (has_gui, has_sqlite)
        when the user message does not carry any related semantic keywords.
        """
        context = self._current_context
        work_ctx = context.active_work_context
        text_lower = message.lower()

        # Safeguard: Do not decay if this is an explicit follow-up or a code modification/conversion request!
        if nlu_result and (nlu_result.is_follow_up or nlu_result.references_previous_context or nlu_result.intent in ["code_modification", "code_conversion"]):
            return

        # Decresing indicator persistence if they exist and aren't mentioned
        if work_ctx.context_references.get("has_gui"):
            if not any(k in text_lower for k in ["gui", "interface", "visuel", "fenêtre", "pyqt"]):
                # Decay has_gui if it has been inactive
                work_ctx.context_references.pop("has_gui", None)
                context.context_references.pop("has_gui", None)

        if work_ctx.context_references.get("has_sqlite"):
            if not any(k in text_lower for k in ["sqlite", "base", "données", "db", "sql", "table"]):
                # Decay has_sqlite
                work_ctx.context_references.pop("has_sqlite", None)
                context.context_references.pop("has_sqlite", None)

    def archive_current_work_context(self, reason: str = ""):
        """Archives the active Work Context with an automated summary and timestamp."""
        context = self._current_context
        work_ctx = context.active_work_context

        # Archive only if it contains actual technical stack/domain
        if work_ctx.active_domain or work_ctx.context_references or work_ctx.technologies:
            archive_entry = {
                "archive_id": len(context.archived_contexts) + 1,
                "timestamp": datetime.now().isoformat(),
                "active_domain": work_ctx.active_domain,
                "technologies": list(work_ctx.technologies),
                "context_references": dict(work_ctx.context_references),
                "file_references": list(work_ctx.file_references),
                "summary": f"Context archivé. Raison : {reason or 'Archivage manuel'}."
            }
            context.archived_contexts.append(archive_entry)

        # Clear and restore a fresh active work context (controlled inheritance)
        old_language = work_ctx.language
        context.active_work_context = WorkContext()
        context.active_work_context.language = old_language

        # Reset old context references (clearing GUI/SQLite leakage indicators)
        context.context_references = {}
        context.active_domain = None

    def restore_work_context(self, archive_id: int) -> bool:
        """Restores a historically archived work context by ID (Phase 6 preparation)."""
        context = self._current_context
        for entry in context.archived_contexts:
            if entry.get("archive_id") == archive_id:
                # Restore to active work context
                restored = WorkContext(
                    active_domain=entry.get("active_domain"),
                    language=context.active_work_context.language,
                    technologies=entry.get("technologies", []),
                    context_references=entry.get("context_references", {}),
                    file_references=entry.get("file_references", []),
                    current_topic=None
                )
                context.active_work_context = restored
                context.active_domain = restored.active_domain
                context.context_references.update(restored.context_references)
                return True
        return False

    def set_last_generated_code(self, code_text: str):
        """Stores the latest generated code in contextual references."""
        self._current_context.active_work_context.context_references["last_generated_code"] = code_text
        self._current_context.context_references["last_generated_code"] = code_text

    def reset_context(self):
        """Fully resets the active context and the global hybrid memory system conversation log."""
        self._current_context = ConversationContext()
        global_memory_system.conversation_memory = []

global_context_manager = ContextManager()
global_conversation_manager = global_context_manager  # Expose as Conversation Manager for architectural alignment
