from core.database.service import global_database

class GeneralKnowledgeBase:
    def __init__(self):
        self.populate_default_knowledge()

    def populate_default_knowledge(self):
        defaults = [
            ("programming", "python_venv", "To create a Python virtual environment run: python -m venv venv"),
            ("operating_system", "linux_kernel", "The Linux Kernel forms the foundational core running hardware tasks.")
        ]
        for cat, topic, content in defaults:
            global_database.execute_write("""
                INSERT INTO general_knowledge (category, topic, content, created_at)
                SELECT ?, ?, ?, ?
                WHERE NOT EXISTS (SELECT 1 FROM general_knowledge WHERE category = ? AND topic = ?)
            """, (cat, topic, content, "2026-01-01", cat, topic))

    def query_knowledge(self, topic_query):
        rows = global_database.execute_read("SELECT category, topic, content FROM general_knowledge WHERE topic LIKE ?", (f"%{topic_query}%",))
        return [{"category": r[0], "topic": r[1], "content": r[2]} for r in rows]

global_knowledge_base = GeneralKnowledgeBase()
