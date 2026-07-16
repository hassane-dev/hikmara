import json
from datetime import datetime
from core.database.service import global_database
from memory.vector_store.service import global_vector_store

class HybridMemorySystem:
    def __init__(self):
        self.working_memory = {}
        self.context_memory = {}
        self.conversation_memory = []

    def add_conversation_turn(self, role, message):
        self.conversation_memory.append({"role": role, "message": message, "timestamp": datetime.now().isoformat()})

    def save_long_term_fact(self, key, value):
        global_database.execute_write("INSERT OR REPLACE INTO user_memory (key, value) VALUES (?, ?)", (key, value))
        global_vector_store.add_vector(f"{key}: {value}", [0.1]*128, {"source": "user_memory"})

    def retrieve_long_term_fact(self, key):
        rows = global_database.execute_read("SELECT value FROM user_memory WHERE key = ?", (key,))
        return rows[0][0] if rows else None

global_memory_system = HybridMemorySystem()
