import pytest
from engineering.service import global_project_manager

def test_project_folder_initialization():
    project_dir = global_project_manager.create_project("test_school_system")
    assert "test_school_system" in project_dir
