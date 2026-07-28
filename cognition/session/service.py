from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from cognition.session.models import Session, SessionStats

class EnhancedSessionStats(SessionStats):
    total_requests: int = Field(default=0, description="Total user requests received")
    total_llm_calls: int = Field(default=0, description="Total LLM model inference calls performed")
    total_cache_hits: int = Field(default=0, description="Total response cache hits")
    ram_usage_peak_gb: float = Field(default=0.0, description="Peak system RAM usage recorded")

class SessionManager:
    def __init__(self):
        self._active_session: Optional[Session] = None
        self._total_requests = 0
        self._total_llm_calls = 0
        self._total_cache_hits = 0
        # Auto-open a default session
        self.open_session("default_session_id", "admin")

    def open_session(self, session_id: str, current_user: str = "admin") -> Session:
        """Creates and registers a new active session."""
        self._active_session = Session(session_id=session_id, current_user=current_user)
        # Re-initialize counters
        self._total_requests = 0
        self._total_llm_calls = 0
        self._total_cache_hits = 0
        return self._active_session

    def get_active_session(self) -> Optional[Session]:
        """Returns the active session, updating its duration and activity status."""
        if self._active_session:
            now = datetime.now()
            self._active_session.duration_seconds = (now - self._active_session.created_at).total_seconds()
            self._active_session.last_active_at = now
            if self._active_session.duration_seconds > 3600:
                self._active_session.is_expired = True
        return self._active_session

    def increment_requests(self):
        self._total_requests += 1

    def increment_llm_calls(self):
        self._total_llm_calls += 1

    def increment_cache_hits(self):
        self._total_cache_hits += 1

    def update_stats(self, tokens_in: int, tokens_out: int, latency: float):
        """Updates turn and token statistics on the active session."""
        session = self.get_active_session()
        if session:
            stats = session.statistics
            total_latency = stats.average_latency * stats.total_turns + latency
            stats.total_turns += 1
            stats.total_tokens_input += tokens_in
            stats.total_tokens_output += tokens_out
            stats.average_latency = round(total_latency / stats.total_turns, 4)

    def get_session_metrics(self) -> Dict[str, Any]:
        """Exposes detailed metrics for observability and developers panel."""
        session = self.get_active_session()
        if not session:
            return {}

        from core.system.service import global_resource_monitor
        metrics = global_resource_monitor.get_metrics()
        ram_used = metrics.get("ram_used_gb", 0.0)

        return {
            "session_id": session.session_id,
            "current_user": session.current_user,
            "duration_seconds": round(session.duration_seconds, 2),
            "total_turns": session.statistics.total_turns,
            "total_requests": self._total_requests,
            "total_llm_calls": self._total_llm_calls,
            "total_cache_hits": self._total_cache_hits,
            "total_tokens_input": session.statistics.total_tokens_input,
            "total_tokens_output": session.statistics.total_tokens_output,
            "average_latency": session.statistics.average_latency,
            "ram_used_gb": ram_used,
            "is_expired": session.is_expired
        }

    def close_active_session(self):
        """Closes the current active session."""
        self._active_session = None

global_session_manager = SessionManager()
