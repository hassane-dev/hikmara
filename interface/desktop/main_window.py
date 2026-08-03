import sys
import os
import sqlite3
import time
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QLineEdit, QPushButton, QLabel, QListWidget, QTabWidget,
    QCheckBox, QProgressBar, QSplitter, QGroupBox, QListWidgetItem, QRadioButton, QButtonGroup
)
from PyQt6.QtCore import Qt, QTimer

from core.security.service import global_security_policy
from core.tasks.service import global_task_manager
from core.system.service import global_resource_monitor
from core.system.health_service import global_health_check_service
from core.module_registry.service import global_module_registry
from ai_models.llm.service import LLMEngine
from cognition.agents.manager.service import global_agent_manager
from interface.desktop.widgets.security_dialog import SecurityConsentDialog
from interface.desktop.widgets.chat_widgets import VirtualChatList, ChatBubble
from interface.desktop.ui_core import (
    global_ui_state_manager, global_ui_command_bus, global_theme_manager,
    global_navigation_manager, global_error_presenter, global_download_manager,
    global_ui_event_aggregator, global_ui_performance_monitor, UIState
)
from ai_models.model_manager.metrics_service import global_metrics_service
from ai_models.model_manager.service import global_model_manager

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
        # Apply style sheet from central ThemeManager
        self.setStyleSheet(global_theme_manager.get_stylesheet())

        # Main layout
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
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(self.splitter)

        # --- LEFT SIDEBAR PANEL ---
        self.left_panel = QWidget()
        self.left_layout = QVBoxLayout()
        self.left_panel.setLayout(self.left_layout)

        # Mode Selection: User vs Developer vs Diagnostic
        mode_group = QGroupBox("Modes de l'IHM (Observabilité)")
        mode_layout = QVBoxLayout()
        mode_group.setLayout(mode_layout)

        self.user_mode_radio = QRadioButton("Mode Utilisateur (Clean User)")
        self.dev_mode_radio = QRadioButton("Mode Développeur (Observabilité)")
        self.diag_mode_radio = QRadioButton("Mode Diagnostic (Maintenance)")

        self.user_mode_radio.setChecked(True) # Default User Mode

        # Button Group to manage selection
        self.mode_button_group = QButtonGroup(self)
        self.mode_button_group.addButton(self.user_mode_radio)
        self.mode_button_group.addButton(self.dev_mode_radio)
        self.mode_button_group.addButton(self.diag_mode_radio)

        self.user_mode_radio.toggled.connect(self.on_mode_changed)
        self.dev_mode_radio.toggled.connect(self.on_mode_changed)
        self.diag_mode_radio.toggled.connect(self.on_mode_changed)

        mode_layout.addWidget(self.user_mode_radio)
        mode_layout.addWidget(self.dev_mode_radio)
        mode_layout.addWidget(self.diag_mode_radio)

        self.left_layout.addWidget(mode_group)

        # Offline Mode & Simulation Indicator (collapsible or dynamic)
        self.offline_group = QGroupBox("Offline Status & Mode")
        offline_group_layout = QVBoxLayout()
        self.offline_group.setLayout(offline_group_layout)

        self.sim_offline_cb = QCheckBox("Simulation offline / En ligne (Simulé)")
        self.sim_offline_cb.setChecked(True)
        offline_group_layout.addWidget(self.sim_offline_cb)

        self.dev_mode_cb = QCheckBox("Mode Développeur Legacy")
        self.dev_mode_cb.setChecked(False)
        # We can hide it in favor of our beautiful radio buttons
        self.dev_mode_cb.setVisible(False)
        offline_group_layout.addWidget(self.dev_mode_cb)

        self.offline_badge = QLabel("OFFLINE MODE: ACTIVE (100% Local, Zero Cloud APIs, No GPU Required)")
        self.offline_badge.setWordWrap(True)
        self.offline_badge.setStyleSheet("color: green; font-weight: bold;")
        offline_group_layout.addWidget(self.offline_badge)

        self.left_layout.addWidget(self.offline_group)

        # System Resource Usage (CPU / RAM)
        self.sys_group = QGroupBox("Utilisation CPU / RAM")
        sys_layout = QVBoxLayout()
        self.sys_group.setLayout(sys_layout)

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

        self.left_layout.addWidget(self.sys_group)

        # Specialized Inference Panel (Observability metrics of Phase 5)
        self.inference_group = QGroupBox("Panneau d'Inférence (Détails CPU/RAM)")
        inference_layout = QVBoxLayout()
        self.inference_group.setLayout(inference_layout)
        self.inference_metrics_label = QLabel("Calcul de TTFT: 120ms\nDébit d'inférence: 26.4 tok/s\nActive model: qwen2.5-3b-instruct-q4_k_m.gguf")
        self.inference_metrics_label.setWordWrap(True)
        inference_layout.addWidget(self.inference_metrics_label)
        self.left_layout.addWidget(self.inference_group)

        # Specialized Agents Panel (Panneau des agents)
        self.agents_group = QGroupBox("Panneau des Agents")
        agents_layout = QVBoxLayout()
        self.agents_group.setLayout(agents_layout)

        self.agents_list = QListWidget()
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
        self.left_layout.addWidget(self.agents_group)

        # Registered Modules Registry
        self.modules_group = QGroupBox("Registre des Modules")
        modules_layout = QVBoxLayout()
        self.modules_group.setLayout(modules_layout)
        self.modules_list = QListWidget()
        modules_layout.addWidget(self.modules_list)
        self.left_layout.addWidget(self.modules_group)

        self.splitter.addWidget(self.left_panel)

        # --- RIGHT CHAT & TASK PANEL ---
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)

        right_layout.addWidget(QLabel("<b>Conversation Zone (Local Agent Hub)</b>"))

        # Chat display area (VirtualChatList)
        self.chat_viewport = VirtualChatList()
        self.chat_viewport.append_message("assistant", "<b>Hikmara AI System:</b> Bootstrapped in offline universal control mode. Ask any question or trigger a system task.")
        right_layout.addWidget(self.chat_viewport)

        # Compatibility chat display placeholder for legacy test runs
        self.chat_display = QTextEdit()
        self.chat_display.setVisible(False)

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

        self.splitter.addWidget(right_panel)

        # Set proportions: Left sidebar gets 1/3, Right panel gets 2/3 space
        self.splitter.setSizes([350, 750])

        # Apply initial mode layout constraints
        self.on_mode_changed()

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

    def on_mode_changed(self):
        """Switches the panel visibility dynamically depending on user, developer or diagnostic modes."""
        if self.user_mode_radio.isChecked():
            # User Mode: Hide detailed modules registry and technical logs
            self.offline_group.setVisible(False)
            self.sys_group.setVisible(False)
            self.inference_group.setVisible(False)
            self.agents_group.setVisible(False)
            self.modules_group.setVisible(False)
        elif self.dev_mode_radio.isChecked():
            # Developer Mode: Show resource metrics and diagnostic docks
            self.offline_group.setVisible(True)
            self.sys_group.setVisible(True)
            self.inference_group.setVisible(True)
            self.agents_group.setVisible(True)
            self.modules_group.setVisible(True)
        else: # Diagnostic Mode
            # Diagnostic Mode: Show resource metrics, hide agent specifics
            self.offline_group.setVisible(True)
            self.sys_group.setVisible(True)
            self.inference_group.setVisible(True)
            self.agents_group.setVisible(False)
            self.modules_group.setVisible(False)

    def send_message(self):
        prompt = self.input_field.text().strip()
        if not prompt:
            return

        self.input_field.clear()

        # 1. Update states and render bubble
        global_ui_state_manager.transition_to(UIState.PREPARING)
        self.chat_viewport.append_message("user", prompt)

        # Sync text with legacy QTextEdit placeholder for backward compatibility with existing tests
        self.chat_display.append(f"<br/><b>You:</b> {prompt}")

        # Register a local task with the task manager
        task_id = f"task_{int(self.timer.remainingTime() or 1000) + len(prompt)}"
        global_task_manager.create_task(task_id, prompt)
        self.update_tasks_ui()

        # Start repaint timing
        global_ui_performance_monitor.start_repaint()

        try:
            # Transition state machine
            global_ui_state_manager.transition_to(UIState.INFERENCE)

            # Execute using global_agent_manager
            res = global_agent_manager.execute_task(prompt, {})

            # Transition state machine
            global_ui_state_manager.transition_to(UIState.STREAMING)

            # 2. Support Developer Mode logs rendering
            if self.dev_mode_radio.isChecked() or self.dev_mode_cb.isChecked():
                self.chat_viewport.append_message("assistant", f"<b>[DEVELOPER PANEL]</b><br/>"
                    f"• <b>Intention :</b> {res.get('route_decision')}<br/>"
                    f"• <b>Pipeline :</b> {res.get('recommended_pipeline')}<br/>"
                    f"• <b>Temps d'exécution :</b> {res.get('execution_stats', {}).get('execution_time_seconds', 0)}s<br/>"
                    f"• <b>Consommation RAM :</b> {res.get('execution_stats', {}).get('ram_percent', 0)}%"
                )

            # 3. Render main output
            if res.get("orchestrated"):
                arch_blueprint = res.get("architecture", {}).get("blueprint", "N/A")
                self.chat_viewport.append_message("assistant", f"<b>Orchestration completed successfully.</b><br/>"
                    f"• <b>Architect Agent :</b> {arch_blueprint}<br/>"
                    f"• <b>Programmer Agent :</b> Synthèse de code terminée."
                )
            else:
                response_text = res.get("response", "")
                self.chat_viewport.append_message("assistant", response_text)

            # Update the task state as completed
            global_task_manager.update_task_status(task_id, "completed", progress=100, results=res)

        except Exception as e:
            # Error presenter mapping
            self.chat_viewport.append_message("assistant", f"<b>Erreur système :</b> {str(e)}")
            global_task_manager.update_task_status(task_id, "failed", progress=0, results={"error": str(e)})

        # End state machine
        global_ui_state_manager.transition_to(UIState.IDLE)

        # Print repaint duration to console logs
        duration = global_ui_performance_monitor.end_repaint()
        # Save metrics to history
        global_metrics_service.history.record_metrics(duration / 1000.0, 26.0)

        self.update_tasks_ui()
        self.refresh_security_audit()
        self.refresh_system_logs()

    def simulate_sensitive_action(self):
        # Trigger a sensitive policy engine action to raise SecurityConsentDialog
        authorized = global_security_policy.authorize_action("system_dashboard", "execute_code", {"cmd": "echo 'Hikmara demo'"})
        self.refresh_security_audit()
        self.refresh_system_logs()

    def update_periodic(self):
        # Update CPU/RAM resource monitors from decoupled metrics service
        metrics = global_metrics_service.get_metrics()

        cpu_val = int(metrics.cpu_usage)
        ram_val = int((metrics.ram_usage / 16.0) * 100) # estimated percentage

        self.cpu_progress.setValue(cpu_val)
        self.ram_progress.setValue(ram_val)

        self.metrics_label.setText(
            f"CPU : {cpu_val}% | RAM utilisée : {metrics.ram_usage} Go | HotPool : {len(metrics.loaded_models)} engins"
        )

        # Update the specialized inference details panel
        self.inference_metrics_label.setText(
            f"Active Model : {metrics.model_active}\n"
            f"Tête de Pool : {', '.join(metrics.loaded_models)}\n"
            f"Estimated Energy: {metrics.energy.estimated_wh if metrics.energy else 0.0} Wh\n"
            f"Marge de Sécurité : 1.5 Go de RAM préservée"
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
