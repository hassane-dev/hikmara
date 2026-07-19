import time
import os
from cognition.agents.base_agent import BaseAgent
from cognition.agents.architect.service import ArchitectAgent
from cognition.agents.programmer.service import ProgrammerAgent
from cognition.agents.tester.service import TesterAgent
from cognition.agents.security.service import SecurityAgent
from cognition.agents.documentation.service import DocumentationAgent
from cognition.agent_communication.service import global_agent_comm_bus
from cognition.router.service import global_intent_router
from cognition.understanding.service import global_language_understanding
from cognition.context.service import global_context_manager
from cognition.conversation.service import global_conversation_engine
from core.security.service import global_security_policy
from core.system.service import global_resource_monitor
from core.module_registry.service import global_module_registry
from tools.registry import global_tool_registry

class AgentManager(BaseAgent):
    def __init__(self, agent_id):
        super().__init__(agent_id, "manager", ["admin"])
        self.architect = ArchitectAgent("arch", "architect", [])
        self.programmer = ProgrammerAgent("prog", "programmer", [])
        self.tester = TesterAgent("test", "tester", [])
        self.security = SecurityAgent("sec", "security", [])
        self.documentation = DocumentationAgent("doc", "docs", [])
        self.last_event_msg = ""
        global_agent_comm_bus.subscribe_to_agent_topic("architect.completed", self._on_arch_complete)
        global_agent_comm_bus.subscribe_to_agent_topic("programmer.completed", self._on_prog_complete)

    def _on_arch_complete(self, t, p):
        self.last_event_msg = "Event Triggered: architect.completed - Triggering Programmer Agent next."
    def _on_prog_complete(self, t, p):
        self.last_event_msg = "Event Triggered: programmer.completed - Triggering Tester/Security Agents next."

    def execute_task(self, task, context):
        start_time = time.time()

        # 1. Run Language Understanding Layer analysis (Phase 2.5)
        nlu = global_language_understanding.analyze(task)

        # 2. Route the intent with Phase 2.5 NLU-enhanced RoutingDecision
        intent = global_intent_router.route(task)

        # 3. Update conversation context (Cognition Layer)
        global_context_manager.update_context("user", task, routing_decision=intent, nlu_result=nlu)

        # Get system resource usage at start
        metrics_start = global_resource_monitor.get_metrics()

        # 4. Execution Pipeline Selection based on routing decision
        if intent.pipeline in ["direct_conversation", "conversation", "coding_conversation"]:
            # Route to our high-level contextual ConversationEngine
            conv_res = global_conversation_engine.generate_response(task)
            response_text = conv_res.response

            # Note: ConversationEngine.generate_response internally updates assistant context

            execution_time = time.time() - start_time
            metrics_end = global_resource_monitor.get_metrics()

            return {
                "orchestrated": False,
                "route_decision": intent.category,
                "recommended_pipeline": intent.recommended_pipeline,
                "justification": intent.justification,
                "response": response_text,
                "agents_used": [],
                "event_trail": "",
                "execution_stats": {
                    "execution_time_seconds": round(execution_time, 4),
                    "cpu_percent": metrics_end.get("cpu_percent", 0),
                    "ram_percent": metrics_end.get("ram_percent", 0)
                }
            }

        elif intent.pipeline == "system_commands":
            # Query system status services directly
            task_lower = task.lower()
            if any(k in task_lower for k in ["mémoire", "memory", "cpu", "ram", "metrics"]):
                metrics = global_resource_monitor.get_metrics()
                response_text = (
                    f"État des ressources système :\n"
                    f"- CPU : {metrics.get('cpu_percent', 0)}%\n"
                    f"- RAM : {metrics.get('ram_percent', 0)}% ({metrics.get('ram_available_gb', 0)} GB libres sur {metrics.get('ram_total_gb', 0)} GB)\n"
                    f"- Espace disque disponible : {metrics.get('disk_free_gb', 0)} GB"
                )
            elif any(k in task_lower for k in ["modules", "module"]):
                modules = global_module_registry.list_modules()
                module_list_str = "\n".join([f"- {info.name} (v{info.version}) : Actif" for name, info in modules.items()])
                response_text = f"Liste des modules actifs enregistrés :\n{module_list_str}"
            elif any(k in task_lower for k in ["journaux", "journal", "logs", "log"]):
                log_path = "logs/hikmara.log"
                if os.path.exists(log_path):
                    with open(log_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()[-15:]  # last 15 lines
                    response_text = "Dernières entrées du journal système (logs/hikmara.log) :\n" + "".join(lines)
                else:
                    response_text = "Aucun journal système trouvé à l'emplacement logs/hikmara.log."
            else:
                metrics = global_resource_monitor.get_metrics()
                response_text = f"Service système sollicité. CPU actuelle : {metrics.get('cpu_percent', 0)}% | RAM : {metrics.get('ram_percent', 0)}%."

            global_context_manager.update_context("assistant", response_text)

            execution_time = time.time() - start_time
            metrics_end = global_resource_monitor.get_metrics()

            return {
                "orchestrated": False,
                "route_decision": intent.category,
                "recommended_pipeline": intent.recommended_pipeline,
                "justification": intent.justification,
                "response": response_text,
                "agents_used": [],
                "event_trail": "",
                "execution_stats": {
                    "execution_time_seconds": round(execution_time, 4),
                    "cpu_percent": metrics_end.get("cpu_percent", 0),
                    "ram_percent": metrics_end.get("ram_percent", 0)
                }
            }

        elif intent.pipeline == "tools":
            # Security layer checks authorization for sensitive tool access
            authorized = global_security_policy.authorize_action("agent_manager", "access_tools", {"prompt": task})
            if not authorized:
                response_text = "Sécurité : Action bloquée par la politique de sécurité (consentement refusé ou manquant)."
            else:
                tools = global_tool_registry.list_tools()
                tools_str = "\n".join([f"- {t['name']} : {t['description']} (Permissions : {', '.join(t['permissions'])})" for t in tools])
                response_text = f"Registre des Outils (Tool Registry) :\nLa commande de gestion des outils a été reçue.\nVoici la liste des outils disponibles :\n{tools_str}"

            global_context_manager.update_context("assistant", response_text)

            execution_time = time.time() - start_time
            metrics_end = global_resource_monitor.get_metrics()

            return {
                "orchestrated": False,
                "route_decision": intent.category,
                "recommended_pipeline": intent.recommended_pipeline,
                "justification": intent.justification,
                "response": response_text,
                "agents_used": [],
                "event_trail": "",
                "execution_stats": {
                    "execution_time_seconds": round(execution_time, 4),
                    "cpu_percent": metrics_end.get("cpu_percent", 0),
                    "ram_percent": metrics_end.get("ram_percent", 0)
                }
            }

        else:
            # "agent_task" -> Multi-Agent Task Orchestration
            # Trigger agents conditionally based on intent results
            agents_to_run = intent.agents_to_trigger if intent.agents_to_trigger else ["architect", "programmer", "tester", "security", "docs"]

            arch_res = {}
            if "architect" in agents_to_run:
                arch_res = self.architect.execute_task(task, context)
                global_agent_comm_bus.publish_agent_event("architect.completed", arch_res)
            else:
                arch_res = {"blueprint": "Pas d'architecture requise pour cette tâche."}

            prog_res = {}
            if "programmer" in agents_to_run:
                prog_res = self.programmer.execute_task(task, context)
                global_agent_comm_bus.publish_agent_event("programmer.completed", prog_res)
                # Store programmer code synthesis results in Context Manager
                code_synthesized = prog_res.get("code", "")
                if code_synthesized:
                    global_context_manager.set_last_generated_code(code_synthesized)
            else:
                prog_res = {"code": "Pas de synthèse de code requise pour cette tâche."}

            test_res = self.tester.execute_task(task, context) if "tester" in agents_to_run else {"tests_passed": True}
            sec_res = self.security.execute_task(task, context) if "security" in agents_to_run else {}
            doc_res = self.documentation.execute_task(task, context) if "docs" in agents_to_run else {}

            global_context_manager.update_context("assistant", "Orchestration multi-agents terminée avec succès.")

            execution_time = time.time() - start_time
            metrics_end = global_resource_monitor.get_metrics()

            return {
                "orchestrated": True,
                "route_decision": intent.category,
                "recommended_pipeline": intent.recommended_pipeline,
                "justification": intent.justification,
                "architecture": arch_res,
                "code": prog_res,
                "tests": test_res,
                "security": sec_res,
                "documentation": doc_res,
                "agents_used": agents_to_run,
                "event_trail": self.last_event_msg if any(a in agents_to_run for a in ["architect", "programmer"]) else "",
                "execution_stats": {
                    "execution_time_seconds": round(execution_time, 4),
                    "cpu_percent": metrics_end.get("cpu_percent", 0),
                    "ram_percent": metrics_end.get("ram_percent", 0)
                }
            }

global_agent_manager = AgentManager("manager_core")
