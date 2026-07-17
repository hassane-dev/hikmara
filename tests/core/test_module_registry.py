import pytest
from core.module_registry.service import ModuleRegistry, ModuleInfo

def test_module_registry():
    registry = ModuleRegistry()

    info = registry.register("My_Test_Mod", "1.2.3")
    assert isinstance(info, ModuleInfo)
    assert info.name == "My_Test_Mod"
    assert info.version == "1.2.3"
    assert info.active is True

    modules = registry.list_modules()
    assert "my_test_mod" in modules
    assert modules["my_test_mod"].version == "1.2.3"
