import sqlite3
import os
import base64
from datetime import datetime

class SecurityPolicyEngine:
    def __init__(self, db_path="database/hikmara.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_db()
        self.consent_handler = None

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                module TEXT,
                action TEXT,
                user TEXT,
                authorized INTEGER,
                details TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT,
                role TEXT
            )
        """)
        cursor.execute("INSERT OR IGNORE INTO users VALUES ('admin', 'admin123', 'super_user')")
        conn.commit()
        conn.close()

    def set_consent_handler(self, handler):
        self.consent_handler = handler

    def authenticate(self, username, password_raw):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()
        return bool(row and row[0] == password_raw)

    def authorize_action(self, module, action, parameters, user="admin"):
        sensitive_actions = ["execute_code", "install_dependency", "access_system_files", "write_file", "delete_file", "hardware_access"]
        is_sensitive = (action in sensitive_actions) or ("execute" in action) or ("install" in action)
        authorized = True
        if is_sensitive:
            if self.consent_handler:
                authorized = self.consent_handler(module, action, parameters)
            else:
                authorized = False
        self.log_audit(module, action, user, authorized, str(parameters))
        return authorized

    def log_audit(self, module, action, user, authorized, details):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO audit_logs (timestamp, module, action, user, authorized, details)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (datetime.now().isoformat(), module, action, user, 1 if authorized else 0, details))
        conn.commit()
        conn.close()

global_security_policy = SecurityPolicyEngine()
