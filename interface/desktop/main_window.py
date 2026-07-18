import sys
import os
import sqlite3
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QLineEdit, QPushButton, QLabel, QListWidget, QTabWidget,
    QCheckBox, QProgressBar, QSplitter, QGroupBox, QListWidgetItem
)
from PyQt6.QtCore import Qt, QTimer

from core.security.service import global_security_policy
from core.tasks.service import global_task_manager
from core.system.service import global_resource_monitor
from core.module_registry.service import global_module_registry
from ai_models.llm.service import LLMEngine
from cognition.agents.manager.service import global_agent_manager
from interface.desktop.widgets.security_dialog import SecurityConsentDialog

class HikmaraMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hikmara AI - Universal Intelligent Local Control Center")
        self.resize(1100, 750)

        # Load LLM Engine locally (simulated / offline-first)
        self.llm = LLMEngine("qwen")
        self.llm.load()

        # Set consent handler on the global security policy engine
        global_security_policy.set_consent_handler(self.request_user_consent)

        self.init_ui()

        # Setup real-time updates for metrics and status
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_periodic)
        self.timer.start(1000) # Every 1 second

        # Initial logs and audit refresh
        self.refresh_system_logs()
        self.refresh_security_audit()

    def init_ui(self):
        # Multi-tab view or central structure
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # Tab 1: Dashboard & Conversation
        self.dashboard_tab = QWidget()
        self.init_dashboard_tab()
        self.tab_widget.addTab(self.dashboard_tab, "Dashboard & Conversation")

        # Tab 2: Security & Policy Engine (Onglet Sécurité)
        self.security_tab = QWidget()
        self.init_security_tab()
        self.tab_widget.addTab(self.security_tab, "Sécurité & Audit")

        # Tab 3: System Journal (Journal système)
        self.system_journal_tab = QWidget()
        self.init_system_journal_tab()
        self.tab_widget.addTab(self.system_journal_tab, "Journal Système")

    def init_dashboard_tab(self):
        main_layout = QHBoxLayout()
        self.dashboard_tab.setLayout(main_layout)

        # Splitter to allow resizing of Left Sidebar vs Right Chat
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # --- LEFT SIDEBAR PANEL ---
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)

        # Offline Mode & Simulation Indicator
        offline_group = QGroupBox("Offline Status & Mode")
        offline_group_layout = QVBoxLayout()
        offline_group.setLayout(offline_group_layout)

        self.sim_offline_cb = QCheckBox("Simulation offline / En ligne (Simulé)")
        self.sim_offline_cb.setChecked(True)
        offline_group_layout.addWidget(self.sim_offline_cb)

        self.dev_mode_cb = QCheckBox("Mode Développeur (Developer Mode)")
        self.dev_mode_cb.setChecked(False)
        offline_group_layout.addWidget(self.dev_mode_cb)

        self.offline_badge = QLabel("OFFLINE MODE: ACTIVE (100% Local, Zero Cloud APIs, No GPU Required)")
        self.offline_badge.setWordWrap(True)
        self.offline_badge.setStyleSheet("color: green; font-weight: bold;")
        offline_group_layout.addWidget(self.offline_badge)

        left_layout.addWidget(offline_group)

        # System Resource Usage (CPU / RAM)
        sys_group = QGroupBox("Utilisation CPU / RAM")
        sys_layout = QVBoxLayout()
        sys_group.setLayout(sys_layout)

        sys_layout.addWidget(QLabel("CPU Usage:"))
        self.cpu_progress = QProgressBar()
        self.cpu_progress.setRange(0, 100)
        self.cpu_progress.setValue(0)
        sys_layout.addWidget(self.cpu_progress)

        sys_layout.addWidget(QLabel("RAM Usage:"))
        self.ram_progress = QProgressBar()
        self.ram_progress.setRange(0, 100)
        self.ram_progress.setValue(0)
        sys_layout.addWidget(self.ram_progress)

        self.metrics_label = QLabel("Loading metrics...")
        sys_layout.addWidget(self.metrics_label)

        left_layout.addWidget(sys_group)

        # System State
        state_group = QGroupBox("État du Système & Couches")
        state_layout = QVBoxLayout()
        state_group.setLayout(state_layout)
        self.system_state_label = QLabel("System Status: Operational\nRuntime Core: Active\nLayers: API, Database, Security, Cognition")
        self.system_state_label.setWordWrap(True)
        state_layout.addWidget(self.system_state_label)
        left_layout.addWidget(state_group)

        # Specialized Agents Panel (Panneau des agents)
        agents_group = QGroupBox("Panneau des Agents")
        agents_layout = QVBoxLayout()
        agents_group.setLayout(agents_layout)

        self.agents_list = QListWidget()
        # Populating agents from the agent manager
        agents_list_names = [
            "Manager Core (Manager Agent)",
            "Architect Agent (Blueprint designer)",
            "Programmer Agent (Code synthesizer)",
            "Tester Agent (Validation engineer)",
            "Security Agent (Policy auditor)",
            "Documentation Agent (Manual generator)"
        ]
        self.agents_list.addItems(agents_list_names)
        agents_layout.addWidget(self.agents_list)
        left_layout.addWidget(agents_group)

        # Registered Modules Registry
        modules_group = QGroupBox("Registre des Modules")
        modules_layout = QVBoxLayout()
        modules_group.setLayout(modules_layout)
        self.modules_list = QListWidget()
        modules_layout.addWidget(self.modules_list)
        left_layout.addWidget(modules_group)

        splitter.addWidget(left_panel)

        # --- RIGHT CHAT & TASK PANEL ---
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)

        right_layout.addWidget(QLabel("<b>Conversation Zone (Local Agent Hub)</b>"))

        # Chat display area
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.append("<b>Hikmara AI System:</b> Bootstrapped in offline universal control mode. Ask any question or trigger a system task.")
        right_layout.addWidget(self.chat_display)

        # User input area
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter a command, ask a question, or initiate a local task...")
        self.input_field.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_field)

        self.send_btn = QPushButton("Envoyer")
        self.send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_btn)

        right_layout.addLayout(input_layout)

        # Task manager list view
        task_group = QGroupBox("Active Tasks (Task Manager)")
        task_layout = QVBoxLayout()
        task_group.setLayout(task_layout)
        self.tasks_list = QListWidget()
        task_layout.addWidget(self.tasks_list)
        right_layout.addWidget(task_group)

        splitter.addWidget(right_panel)

        # Set proportions: Left sidebar gets 1/3, Right panel gets 2/3 space
        splitter.setSizes([350, 750])

    def init_security_tab(self):
        layout = QVBoxLayout()
        self.security_tab.setLayout(layout)

        info_label = QLabel("<b>Security Policy & Audit Log Tracker</b>")
        info_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(info_label)

        # Interactive trigger to showcase Policy Engine Security Consent flow
        sim_layout = QHBoxLayout()
        sim_btn = QPushButton("Simuler une action sensible (Policy Engine Consent)")
        sim_btn.clicked.connect(self.simulate_sensitive_action)
        sim_layout.addWidget(sim_btn)

        refresh_btn = QPushButton("Rafraîchir les logs d'audit")
        refresh_btn.clicked.connect(self.refresh_security_audit)
        sim_layout.addWidget(refresh_btn)
        layout.addLayout(sim_layout)

        self.security_logs_display = QTextEdit()
        self.security_logs_display.setReadOnly(True)
        layout.addWidget(self.security_logs_display)

    def init_system_journal_tab(self):
        layout = QVBoxLayout()
        self.system_journal_tab.setLayout(layout)

        info_layout = QHBoxLayout()
        info_layout.addWidget(QLabel("<b>System log tracker (logs/hikmara.log)</b>"))

        refresh_btn = QPushButton("Rafraîchir le journal")
        refresh_btn.clicked.connect(self.refresh_system_logs)
        info_layout.addWidget(refresh_btn)

        layout.addLayout(info_layout)

        self.system_log_display = QTextEdit()
        self.system_log_display.setReadOnly(True)
        layout.addWidget(self.system_log_display)

    def request_user_consent(self, mod, act, params):
        # Open SecurityConsentDialog to request authorization
        d = SecurityConsentDialog(self, mod, act, params)
        d.exec()
        return d.approved

    def send_message(self):
        prompt = self.input_field.text().strip()
        if not prompt:
            return

        self.input_field.clear()
        self.chat_display.append(f"<br/><b>You:</b> {prompt}")

        # Register a local task with the task manager
        task_id = f"task_{int(self.timer.remainingTime() or 1000) + len(prompt)}"
        global_task_manager.create_task(task_id, prompt)
        self.update_tasks_ui()

        try:
            # Execute using global_agent_manager
            res = global_agent_manager.execute_task(prompt, {})

            # 1. In Developer Mode, display comprehensive routing/technical logs
            if self.dev_mode_cb.isChecked():
                self.chat_display.append("<font color='#7289da'><b>[DEVELOPER PANEL]</b></font>")
                self.chat_display.append(f"• <b>Décision du routeur :</b> Intention '{res.get('route_decision')}'")
                self.chat_display.append(f"• <b>Pipeline sélectionné :</b> {res.get('recommended_pipeline')}")
                self.chat_display.append(f"• <b>Justification :</b> {res.get('justification')}")

                agents_used = res.get("agents_used", [])
                agents_str = ", ".join(agents_used) if agents_used else "Aucun (traitement direct)"
                self.chat_display.append(f"• <b>Agents exécutés :</b> {agents_str}")

                if res.get("event_trail"):
                    self.chat_display.append(f"• <b>Événement interne :</b> {res.get('event_trail')}")

                stats = res.get("execution_stats", {})
                self.chat_display.append(
                    f"• <b>Temps d'exécution :</b> {stats.get('execution_time_seconds', 0)} secondes<br/>"
                    f"• <b>Utilisation CPU :</b> {stats.get('cpu_percent', 0)}%<br/>"
                    f"• <b>Utilisation RAM :</b> {stats.get('ram_percent', 0)}%"
                )
                self.chat_display.append("<font color='#7289da'><b>[END DEVELOPER PANEL]</b></font><br/>")

            # 2. Display the main reply depending on orchestration flow
            if res.get("orchestrated"):
                self.chat_display.append(f"<b>Hikmara AI Manager:</b> Orchestration completed successfully.")

                arch_blueprint = res.get("architecture", {}).get("blueprint", "N/A")
                self.chat_display.append(f"• <b>Architect Agent:</b> Designed blueprint: <i>{arch_blueprint}</i>")

                prog_code = res.get("code", {}).get("code", "N/A")
                self.chat_display.append(f"• <b>Programmer Agent:</b> Authored code. Execution status: <i>Success</i>")
            else:
                response_text = res.get("response", "")
                self.chat_display.append(f"<b>Hikmara AI:</b> {response_text}")

            # Update the task state as completed
            global_task_manager.update_task_status(task_id, "completed", progress=100, results=res)

        except Exception as e:
            self.chat_display.append(f"<b>Error during execution:</b> {str(e)}")
            global_task_manager.update_task_status(task_id, "failed", progress=0, results={"error": str(e)})

        self.update_tasks_ui()
        self.refresh_security_audit()
        self.refresh_system_logs()

    def simulate_sensitive_action(self):
        # Trigger a sensitive policy engine action to raise SecurityConsentDialog
        authorized = global_security_policy.authorize_action("system_dashboard", "execute_code", {"cmd": "echo 'Hikmara demo'"})
        self.refresh_security_audit()
        self.refresh_system_logs()

    def update_periodic(self):
        # Update CPU/RAM resource monitors
        metrics = global_resource_monitor.get_metrics()
        cpu_val = int(metrics.get("cpu_percent", 0))
        ram_val = int(metrics.get("ram_percent", 0))

        self.cpu_progress.setValue(cpu_val)
        self.ram_progress.setValue(ram_val)

        self.metrics_label.setText(
            f"CPU: {cpu_val}% | RAM: {ram_val}% | Free Disk: {metrics.get('disk_free_gb', 0)} GB"
        )

        # Keep module registry and task registry refreshed
        self.update_modules_ui()
        self.update_tasks_ui()

    def update_modules_ui(self):
        self.modules_list.clear()
        modules = global_module_registry.list_modules()
        for name, info in modules.items():
            self.modules_list.addItem(f"{info.name} (v{info.version}) - Active")

    def update_tasks_ui(self):
        self.tasks_list.clear()
        tasks = global_task_manager.list_tasks()
        for task in tasks:
            self.tasks_list.addItem(f"[{task.status.upper()}] {task.description[:50]} (Prog: {task.progress}%)")

    def refresh_security_audit(self):
        try:
            conn = sqlite3.connect(global_security_policy.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT timestamp, module, action, authorized, details FROM audit_logs ORDER BY id DESC LIMIT 50")
            rows = cursor.fetchall()
            conn.close()

            text = "<h2>Security Policy Audit Logs (SQLite)</h2>"
            text += "<table border='1' cellpadding='5' style='border-collapse: collapse; width: 100%; font-family: monospace;'>"
            text += "<tr bgcolor='#f2f2f2'><th>Timestamp</th><th>Module</th><th>Action</th><th>Authorized</th><th>Details</th></tr>"
            for row in rows:
                auth_str = "<font color='green'>APPROVED</font>" if row[3] == 1 else "<font color='red'>DENIED</font>"
                text += f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{auth_str}</td><td>{row[4]}</td></tr>"
            text += "</table>"
            self.security_logs_display.setHtml(text)
        except Exception as e:
            self.security_logs_display.setPlainText(f"Error loading security audit logs: {str(e)}")

    def refresh_system_logs(self):
        try:
            log_path = "logs/hikmara.log"
            if os.path.exists(log_path):
                with open(log_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()[-100:]  # Read last 100 lines
                self.system_log_display.setPlainText("".join(lines))
            else:
                self.system_log_display.setPlainText("No system logs found at logs/hikmara.log")
        except Exception as e:
            self.system_log_display.setPlainText(f"Error reading system logs: {str(e)}")
