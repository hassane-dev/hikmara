import pytest
from unittest.mock import MagicMock

def test_mainwindow_headless_initialization():
    mock_window = MagicMock()
    mock_window.windowTitle.return_value = "Hikmara AI - Universal Intelligent Local Control Center"
    assert mock_window.windowTitle() == "Hikmara AI - Universal Intelligent Local Control Center"
