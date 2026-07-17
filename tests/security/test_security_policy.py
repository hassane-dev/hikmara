import pytest
import sqlite3
from core.security.service import SecurityPolicyEngine

def test_security_auth():
    engine = SecurityPolicyEngine(db_path="database/test_hikmara_sec.db")
    assert engine.authenticate("admin", "admin123") is True
    assert engine.authenticate("admin", "wrong_pass") is False

def test_security_action_authorization():
    engine = SecurityPolicyEngine(db_path="database/test_hikmara_sec.db")

    # Non-sensitive action should be automatically authorized
    assert engine.authorize_action("test_mod", "read_status", {"foo": "bar"}) is True

    # Sensitive action without handler should fail by default
    assert engine.authorize_action("test_mod", "execute_code", {"cmd": "rm -rf"}) is False

    # Sensitive action with consenting handler should pass
    engine.set_consent_handler(lambda mod, act, params: True)
    assert engine.authorize_action("test_mod", "execute_code", {"cmd": "echo 1"}) is True

    # Sensitive action with denying handler should fail
    engine.set_consent_handler(lambda mod, act, params: False)
    assert engine.authorize_action("test_mod", "execute_code", {"cmd": "echo 2"}) is False

def test_security_audit_logging():
    engine = SecurityPolicyEngine(db_path="database/test_hikmara_sec.db")
    engine.log_audit("test_mod", "some_action", "admin", True, "some_details")

    conn = sqlite3.connect("database/test_hikmara_sec.db")
    cursor = conn.cursor()
    cursor.execute("SELECT module, action, user, authorized, details FROM audit_logs ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()

    assert row is not None
    assert row[0] == "test_mod"
    assert row[1] == "some_action"
    assert row[2] == "admin"
    assert row[3] == 1
    assert row[4] == "some_details"
