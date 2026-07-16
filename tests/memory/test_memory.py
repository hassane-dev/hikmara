import pytest
from memory.service import global_memory_system
from memory.vector_store.service import global_vector_store
from knowledge.service import global_knowledge_base

def test_hybrid_memory():
    global_memory_system.add_conversation_turn("user", "how are you?")
    assert len(global_memory_system.conversation_memory) > 0

def test_vector_store():
    global_vector_store.clear()
    global_vector_store.add_vector("hello", [0.5]*128)
    res = global_vector_store.search([0.5]*128, top_k=1)
    assert len(res) == 1

def test_offline_knowledge():
    res = global_knowledge_base.query_knowledge("python_venv")
    assert len(res) == 1
