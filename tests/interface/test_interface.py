import pytest
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QTimer
from interface.desktop.main_window import HikmaraMainWindow
from interface.desktop.widgets.security_dialog import SecurityConsentDialog
from core.security.service import global_security_policy

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
    assert window.chat_display is not None
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

    # Verify chat display contains user prompt
    assert "What is your architectural style?" in window.chat_display.toPlainText()

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
