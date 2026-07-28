from typing import Optional
from datetime import datetime
from cognition.session.models import Session, SessionStats

class SessionManager:
    def __init__(self):
        self._active_session: Optional[Session] = None
        # Auto-open a default session
        self.open_session("default_session_id", "admin")

    def open_session(self, session_id: str, current_user: str = "admin") -> Session:
        """Creates and registers a new active session."""
        self._active_session = Session(session_id=session_id, current_user=current_user)
        return self._active_session

    def get_active_session(self) -> Optional[Session]:
        """Returns the active session, updating its duration and activity status."""
        if self._active_session:
            now = datetime.now()
            self._active_session.duration_seconds = (now - self._active_session.created_at).total_seconds()
            self._active_session.last_active_at = now
            # Expiration threshold: e.g. 1 hour (3600 seconds)
            if self._active_session.duration_seconds > 3600:
                self._active_session.is_expired = True
        return self._active_session

    def update_stats(self, tokens_in: int, tokens_out: int, latency: float):
        """Updates turn and token statistics on the active session."""
        session = self.get_active_session()
        if session:
            stats = session.statistics
            # Running average of latency
            total_latency = stats.average_latency * stats.total_turns + latency
            stats.total_turns += 1
            stats.total_tokens_input += tokens_in
            stats.total_tokens_output += tokens_out
            stats.average_latency = round(total_latency / stats.total_turns, 4)

    def close_active_session(self):
        """Closes the current active session."""
        self._active_session = None

global_session_manager = SessionManager()
