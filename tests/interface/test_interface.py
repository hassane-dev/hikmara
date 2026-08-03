import pytest
import os
import time
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QTimer
from interface.desktop.main_window import HikmaraMainWindow
from interface.desktop.widgets.security_dialog import SecurityConsentDialog
from core.security.service import global_security_policy
from interface.desktop.ui_core import (
    global_ui_state_manager, global_ui_command_bus, global_theme_manager, UIState
)
from ai_models.model_manager.metrics_service import global_metrics_service

# Ensure we use offscreen platform for tests to prevent displaying actual windows
os.environ["QT_QPA_PLATFORM"] = "offscreen"

# Ensure QApplication is initialized
app = QApplication.instance()
if app is None:
    app = QApplication([])

def test_qapplication_creation():
    assert QApplication.instance() is not None

def test_mainwindow_construction_and_widgets():
    # Construct the main window
    window = HikmaraMainWindow()
    window.show()

    # Assert window title
    assert window.windowTitle() == "Hikmara AI - Universal Intelligent Local Control Center"

    # Assert widgets are initialized
    assert window.input_field is not None
    assert window.send_btn is not None
    assert window.cpu_progress is not None
    assert window.ram_progress is not None
    assert window.offline_badge is not None
    assert window.security_logs_display is not None
    assert window.system_log_display is not None

    window.close()

def test_send_message_button_and_signal_handling():
    window = HikmaraMainWindow()
    window.show()

    # Simulate typing in input field
    window.input_field.setText("What is your architectural style?")

    # Trigger message send directly
    window.send_message()

    # Verify input is cleared
    assert window.input_field.text() == ""

    window.close()

def test_security_consent_dialog_approved():
    # Construct a SecurityConsentDialog and check behavior
    dialog = SecurityConsentDialog(None, "test_module", "execute_code", {"cmd": "test"})

    # Force single-shot execution to approve the dialog
    QTimer.singleShot(50, dialog.accept_action)
    dialog.exec()

    assert dialog.approved is True

def test_security_consent_dialog_denied():
    dialog = SecurityConsentDialog(None, "test_module", "execute_code", {"cmd": "test"})

    # Force single-shot execution to deny (reject) the dialog
    QTimer.singleShot(50, dialog.reject)
    dialog.exec()

    assert dialog.approved is False

# ----------------------------------------------------
# NEW PHASE 5.2 EXTENDED INTERFACE TESTS
# ----------------------------------------------------
def test_ui_theme_switching():
    # Verify we can swap stylesheet dynamically
    global_theme_manager.dark_mode = True
    sheet_dark = global_theme_manager.get_stylesheet()
    assert "background-color: #1e1e1e;" in sheet_dark

    global_theme_manager.dark_mode = False
    sheet_light = global_theme_manager.get_stylesheet()
    assert "background-color: #f3f3f3;" in sheet_light

def test_ui_state_machine_transitions():
    # Verify state machine starts in IDLE and registers transitions
    assert global_ui_state_manager.active_state == UIState.IDLE

    states = []
    def on_state(key):
        if key == "active_state":
            states.append(global_ui_state_manager.active_state)

    global_ui_state_manager.state_changed.connect(on_state)
    global_ui_state_manager.transition_to(UIState.INFERENCE)

    assert global_ui_state_manager.active_state == UIState.INFERENCE
    assert UIState.INFERENCE in states

def test_ui_mode_toggle_visibility():
    window = HikmaraMainWindow()
    window.show()

    # Toggle to User Mode
    window.user_mode_radio.setChecked(True)
    window.on_mode_changed()
    assert window.inference_group.isVisible() is False
    assert window.modules_group.isVisible() is False

    # Toggle to Developer Mode
    window.dev_mode_radio.setChecked(True)
    window.on_mode_changed()
    assert window.inference_group.isVisible() is True
    assert window.modules_group.isVisible() is True

    window.close()
