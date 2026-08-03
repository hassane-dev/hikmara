import time
from typing import Dict, List, Any, Optional, Callable
from pydantic import BaseModel, Field
from enum import Enum
from PyQt6.QtCore import QObject, pyqtSignal, QThread
from PyQt6.QtWidgets import QWidget, QMessageBox, QLabel
from contracts.models import HealthStatus, PerformanceProfile, InferenceMetrics
from contracts.errors import HikmaraError

# ----------------------------------------------------
# 1. GRAPHICAL UI STATE MACHINE & SUB-STATES
# ----------------------------------------------------
class UIState(str, Enum):
    IDLE = "idle"
    PREPARING = "preparing"
    SCHEDULING = "scheduling"
    INFERENCE = "inference"
    STREAMING = "streaming"

class ChatMessage(BaseModel):
    schema_version: int = 1
    sender: str                       # "user" or "assistant"
    text: str
    timestamp: float
    formatted_html: str

class UIStateManager(QObject):
    """Single Source of Truth (SSOT) of the presentation layer. Exposes reactive states."""
    state_changed = pyqtSignal(str) # Emitted whenever any substate changes

    def __init__(self):
        super().__init__()
        self.active_state = UIState.IDLE
        self.chat_history: List[ChatMessage] = []
        self.download_queue: List[Dict[str, Any]] = []
        self.developer_mode: bool = False
        self.diagnostic_mode: bool = False
        self.active_project_id: str = "default_project"
        self.active_workspace_id: str = "default_workspace"

    def transition_to(self, new_state: UIState):
        self.active_state = new_state
        self.state_changed.emit("active_state")

    def add_message(self, sender: str, text: str, html: str):
        msg = ChatMessage(sender=sender, text=text, timestamp=time.time(), formatted_html=html)
        self.chat_history.append(msg)
        self.state_changed.emit("chat_history")

    def update_download_progress(self, model_id: str, progress: int, status: str):
        # Update queue
        found = False
        for item in self.download_queue:
            if item["model_id"] == model_id:
                item["progress"] = progress
                item["status"] = status
                found = True
                break
        if not found:
            self.download_queue.append({"model_id": model_id, "progress": progress, "status": status})
        self.state_changed.emit("download_queue")

global_ui_state_manager = UIStateManager()


# ----------------------------------------------------
# 2. UI COMMAND BUS
# ----------------------------------------------------
class UICommandBus:
    """Asynchronous Decoupled Command Bus transmitting user UI requests to backend application services."""
    def __init__(self):
        self._handlers: Dict[str, Callable[[Any], None]] = {}

    def register_handler(self, command_name: str, handler: Callable[[Any], None]):
        self._handlers[command_name] = handler

    def dispatch(self, command_name: str, payload: Any = None):
        handler = self._handlers.get(command_name)
        if handler:
            handler(payload)

global_ui_command_bus = UICommandBus()


# ----------------------------------------------------
# 3. THEME MANAGER
# ----------------------------------------------------
class ThemeManager:
    """Centralizes CSS/QSS styles, typography, spacing, and dynamic palette swapping."""
    def __init__(self):
        self.dark_mode: bool = True

    def get_stylesheet(self) -> str:
        """Returns the complete, elegant dark/light theme CSS/QSS configurations."""
        if self.dark_mode:
            return """
                QMainWindow { background-color: #1e1e1e; color: #ffffff; }
                QTextEdit { background-color: #252526; color: #ffffff; border: 1px solid #3c3c3c; border-radius: 4px; font-family: monospace; }
                QLineEdit { background-color: #2d2d30; color: #ffffff; border: 1px solid #3e3e42; border-radius: 4px; padding: 6px; }
                QPushButton { background-color: #0e639c; color: #ffffff; border: none; border-radius: 4px; padding: 6px 12px; font-weight: bold; }
                QPushButton:hover { background-color: #1177bb; }
                QProgressBar { border: 1px solid #3c3c3c; border-radius: 4px; text-align: center; }
                QProgressBar::chunk { background-color: #0e639c; }
                QGroupBox { border: 1px solid #3c3c3c; border-radius: 6px; margin-top: 12px; font-weight: bold; padding: 10px; }
                QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 3px; }
                QListWidget { background-color: #252526; color: #ffffff; border: 1px solid #3c3c3c; border-radius: 4px; }
            """
        else:
            return """
                QMainWindow { background-color: #f3f3f3; color: #000000; }
                QTextEdit { background-color: #ffffff; color: #000000; border: 1px solid #cccccc; border-radius: 4px; font-family: monospace; }
                QLineEdit { background-color: #ffffff; color: #000000; border: 1px solid #cccccc; border-radius: 4px; padding: 6px; }
                QPushButton { background-color: #007acc; color: #ffffff; border: none; border-radius: 4px; padding: 6px 12px; font-weight: bold; }
                QPushButton:hover { background-color: #0062a3; }
                QProgressBar { border: 1px solid #cccccc; border-radius: 4px; text-align: center; }
                QProgressBar::chunk { background-color: #007acc; }
                QGroupBox { border: 1px solid #cccccc; border-radius: 6px; margin-top: 12px; font-weight: bold; padding: 10px; }
                QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 3px; }
                QListWidget { background-color: #ffffff; color: #000000; border: 1px solid #cccccc; border-radius: 4px; }
            """

global_theme_manager = ThemeManager()


# ----------------------------------------------------
# 4. NAVIGATION MANAGER
# ----------------------------------------------------
class NavigationManager:
    """Manages the history and view transitions (back, forward, restore) in the application."""
    def __init__(self):
        self._history: List[str] = []
        self._current_idx: int = -1

    def navigate_to(self, view_name: str):
        # Truncate forward history if navigating from back state
        if self._current_idx < len(self._history) - 1:
            self._history = self._history[:self._current_idx + 1]
        self._history.append(view_name)
        self._current_idx = len(self._history) - 1

    def go_back(self) -> Optional[str]:
        if self._current_idx > 0:
            self._current_idx -= 1
            return self._history[self._current_idx]
        return None

global_navigation_manager = NavigationManager()


# ----------------------------------------------------
# 5. ERROR PRESENTER
# ----------------------------------------------------
class ErrorPresenter:
    """Decoupled service mapping HikmaraError types to user-friendly messages and severity tiers."""
    def __init__(self, parent_widget: Optional[QWidget] = None):
        self.parent_widget = parent_widget

    def present_error(self, err: HikmaraError):
        """Displays standard message box depending on the error severity."""
        severity_label = err.severity.upper()
        title = f"Erreur Hikmara AI — {severity_label}"

        msg_box = QMessageBox(self.parent_widget)
        if err.severity == "critical":
            msg_box.setIcon(QMessageBox.Icon.Critical)
        else:
            msg_box.setIcon(QMessageBox.Icon.Warning)

        msg_box.setWindowTitle(title)
        msg_box.setText(f"Code : {err.error_code}\nComposant : {err.component}\n\n{err.message}")
        msg_box.setInformativeText("L'application a géré l'erreur de manière sécurisée." if err.recoverable else "L'action ne peut pas être récupérée.")
        msg_box.exec()

global_error_presenter = ErrorPresenter()


# ----------------------------------------------------
# 6. DOWNLOAD MANAGER
# ----------------------------------------------------
class DownloadManager:
    """Autonomous download queue manager for GGUF/Ollama weight files."""
    def __init__(self):
        self._active_downloads: Dict[str, Dict[str, Any]] = {}

    def start_download(self, model_id: str, size_gb: float):
        self._active_downloads[model_id] = {
            "progress": 0,
            "status": "downloading",
            "size_gb": size_gb
        }
        global_ui_state_manager.update_download_progress(model_id, 0, "downloading")

    def pause_download(self, model_id: str):
        if model_id in self._active_downloads:
            self._active_downloads[model_id]["status"] = "paused"
            global_ui_state_manager.update_download_progress(model_id, self._active_downloads[model_id]["progress"], "paused")

    def resume_download(self, model_id: str):
        if model_id in self._active_downloads:
            self._active_downloads[model_id]["status"] = "downloading"
            global_ui_state_manager.update_download_progress(model_id, self._active_downloads[model_id]["progress"], "downloading")

global_download_manager = DownloadManager()


# ----------------------------------------------------
# 7. UI PLUGIN MANAGER
# ----------------------------------------------------
class UIPluginManager:
    """Registry allowing extension modules to dynamically mount custom panels in the window."""
    def __init__(self):
        self._tab_plugins: List[Dict[str, Any]] = []

    def register_tab(self, tab_name: str, widget_factory: Callable[[], QWidget]):
        self._tab_plugins.append({"name": tab_name, "factory": widget_factory})

    def get_registered_tabs(self) -> List[Dict[str, Any]]:
        return self._tab_plugins

global_ui_plugin_manager = UIPluginManager()


# ----------------------------------------------------
# 8. OBSERVABILITY & EVENTS COUPLING
# ----------------------------------------------------
class UIEventAggregator:
    """Monitors the global_event_bus of the backend and aggregates/filters events for UIState updates."""
    def __init__(self):
        self.recent_events: List[Dict[str, Any]] = []

    def record_event(self, event_name: str, severity: str = "info", payload: Dict[str, Any] = None):
        self.recent_events.append({
            "event": event_name,
            "severity": severity,
            "timestamp": time.time(),
            "payload": payload or {}
        })
        if len(self.recent_events) > 50:
            self.recent_events.pop(0)

global_ui_event_aggregator = UIEventAggregator()


class UIPerformanceMonitor:
    """Tracks frame renderings, repaint duration and widget counts to ensure 60 FPS scrolling."""
    def __init__(self):
        self._start_repaint_time: float = 0.0

    def start_repaint(self):
        self._start_repaint_time = time.time()

    def end_repaint(self) -> float:
        if self._start_repaint_time == 0.0:
            return 0.0
        return round((time.time() - self._start_repaint_time) * 1000.0, 2) # in ms

global_ui_performance_monitor = UIPerformanceMonitor()
