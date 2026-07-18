# Hikmara AI - Phase 2 Pipeline Audit: Request Routing and Conversation Intelligence

This document details the request execution pipeline audit of Hikmara AI prior to the Phase 2 improvements, as well as the design architecture for the new Intent Router.

---

## 1. Pre-Phase 2 Execution Pipeline Audit

Currently, any user message entered into the user interface is executed via a rigid, non-selective multi-agent sequence, regardless of whether the message is a simple greeting or a complex engineering task.

### **Pipeline Execution Flow**
```
[ User Input in UI ]
         │
         ▼
[ interface/desktop/main_window.py ]
 ├── Register Task in global_task_manager
 ├── Send prompt to global_agent_manager.execute_task(prompt, {})
 │
 ├─► [ cognition/agents/manager/service.py (AgentManager) ]
 │    │
 │    ▼ (Systematic Sequential Execution)
 │   1. ArchitectAgent.execute_task() ────► publishes "architect.completed"
 │   2. ProgrammerAgent.execute_task() ───► publishes "programmer.completed"
 │   3. TesterAgent.execute_task()
 │   4. SecurityAgent.execute_task()
 │   5. DocumentationAgent.execute_task()
 │    │
 │    └─► Returns combined multi-agent result dictionary
 │
 ├── Unpack agent results (Architect blueprint, Programmer code, etc.)
 ├── Call direct LLMEngine.predict({"prompt": prompt})
 └── Display all results & LLM output to chat display area
```

### **Component Responsibilities & Current Issues**

1. **User Message Entry Point**:
   - Captured in `HikmaraMainWindow.send_message()` when the user presses Enter or clicks the "Envoyer" button.
2. **`interface/desktop/main_window.py` (UI Layer)**:
   - Responsible for getting text from the input line, registering tasks in the local task manager, displaying formatted text (blueprints, event logs, code output), and calling the backend.
   - *Issue*: It systematically displays multi-agent headers (Architect, Programmer, and event trails) and simulates direct LLM predictions simultaneously, resulting in cluttered/confusing outputs for simple prompts.
3. **`AgentManager` (Cognitive Orchestrator)**:
   - Responsible for triggering and coordinating the agent team (`ArchitectAgent`, `ProgrammerAgent`, etc.).
   - *Issue*: It lacks selective routing. It always invokes every single specialized agent, consuming computational resources unnecessarily for basic messages like "Bonjour" or "Vérifie la mémoire".
4. **LLM Motor (`ai_models/llm/service.py`)**:
   - The offline mock LLM engine (`LLMEngine`) returns standard static prediction replies.
   - *Issue*: It lacks contextualization for simple conversational dialogues or specific intents.
5. **Agent Triggering Mechanism**:
   - Triggered sequentially in a synchronous block within `AgentManager.execute_task`.
6. **Interface Return & Render**:
   - Direct synchronous return block that gets unpacked in the main window UI.

---

## 2. Proposed Intent Routing & Pipeline Separation Architecture

The purpose of Phase 2 is to introduce a robust **Intent Router** that inspects the query before execution and routes it to the most specific execution pipeline.

### **The Intelligent Routing Flow**
```
      [ User Message Input ]
                │
                ▼
      [ Intent Router ]
                │
        ┌───────┼─────────────────────────┐
        ▼       ▼                         ▼
   [ Simple ] [ System Commands ]  [ Dev/Complex ]
   [  Conv  ]   (Memory, logs,      (Software dev,
   [  Flow  ]    modules status)     architecture)
        │               │                 │
        ▼               ▼                 ▼
   LLMEngine      Direct service      Orchestrate
   Prediction      queries & logs       Agents
        │               │                 │
        └───────┬───────┘                 │
                ▼                         ▼
          Simple Output              Agent Results
                │                         │
                └──────────┬──────────────┘
                           ▼
                 [ Developer Mode Check ]
                 ├── Yes: Append routing & technical metrics
                 └── No: Show only the clean user-facing reply
```

### **Key Improvements in Phase 2**
* **Extensible `IntentRouter`**: A dedicated component classifying inputs into: `Conversation générale`, `Salutations`, `Développement logiciel`, `Génération de code`, `Analyse de code`, `Explication de code`, `Questions techniques`, `Commandes système`, `Gestion des outils`, `Recherche d'informations`, `Sécurité`, `Requêtes complexes`, and `Inconnu`.
* **Resource Optimization**: Basic interactions skip agent initialization, preventing overhead.
* **Developer Mode**: A checkbox to toggle the visibility of router details, execution time, CPU/RAM stats, and internal events.
