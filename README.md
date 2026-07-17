# Hikmara AI

Hikmara AI is a modular, offline-first universal local Artificial Intelligence platform designed to evolve into an intelligent Operating System architect. Operating fully local by design, it ensures zero data leakage, high security, and high performance without relying on cloud-based APIs or CDNs.

## Key Features

- **Offline-First Security**: Operates completely local. Model weights, databases, and logs are kept private on-device.
- **Agentic Cognition**: High-level reasoners and task planners working together with specialized AI agents (Architect, Programmer, Tester, Security, Documentation).
- **Core Orchestration**: Advanced soft scheduling, multi-threaded event-loop mechanism, and structured secure communication buses.
- **Resource Control**: Deep hardware diagnostic and optimization probes tracking RAM, CPU, and core distribution profiles.
- **Polished Desktop UI**: Beautiful PyQt6 interface providing interactive logging, database auditing, agent control panel, and offline mode configuration.

---

## Repository & Architecture Architecture Overview

Hikmara AI's codebase is strictly modularized to guarantee scalability and safety. Below is the directory breakdown:

### 1. Central Bootstrapping & Entry Points
- **`app/`**: Contains main application lifecycles.
  - `main.py`: Headless application launcher.
  - `bootstrap.py`: Initializer of runtime variables, local folders, and sqlite databases.
  - `application.py`: Central orchestrator object.

### 2. Foundational Core & Platform Subsystems
- **`kernel/`**: Provides the foundational event loop (`event_loop.py`), scheduling algorithms (`scheduler.py`), and platform module managers (`module_manager.py`).
- **`core/`**: Central nervous system. Holds the standard JSON API router (`communication/`), event publisher (`events/`), global security policies (`security/`), task dispatcher (`tasks/`), system resource diagnostics (`system/`), database connections (`database/`), and local configurations manager (`configuration/`).
- **`runtime/`**: Drives active subsystem state machines and health loops.

### 3. AI, Knowledge & Memory Layers
- **`ai_models/`**: Manages simulated and local model loaders for:
  - Large Language Models (LLMs)
  - Embeddings Generation
  - Vision Systems
  - Audio Processing (Whisper tiny)
- **`memory/`**: Short-term contexts, persistent SQLite memories, and local Cosine-Similarity Vector Database (`vector_store/`).
- **`knowledge/`**: Facts base and local relational database for offline information retrieval.

### 4. Cognition & Specialized Agents
- **`cognition/`**: Handles rule engines (`reasoning/`), decomposed task planners (`planner/`), multi-agent message buses (`agent_communication/`), self-assessment evaluations (`evaluation/`), and 5 specialized agents:
  - **OS Architect Agent**: Plans system designs.
  - **Programmer Agent**: Codes system files and modifications.
  - **Tester Agent**: Validates and tests system status.
  - **Security Agent**: Policies enforcement and logs scanner.
  - **Documentation Agent**: Writes docs.

### 5. Utilities & Tools
- **`tools/`**: Interface registry for sandboxed scripts execution, file manipulations, and source code modifications (`file_tools/`, `code_tools/`).
- **`engineering/`**: Automatically structures project environments and files.
- **`interface/`**: Implements PyQt6 interactive user controls, logs visualization widgets, and Security Consent Dialogs.

---

## Configuration & Environments

Configurations are located in the `config/` directory as YAML profiles:
- `system.yaml`: Core offline mode variables, versioning, and debugger status.
- `models.yaml`: Selected LLM, embeddings, vision, and audio models.
- `security.yaml`: Security policies regarding consents for code executions and dependency installations.
- `hardware.yaml`: Maximum allowed hardware cores and GPU setups.
- `user.yaml`: Active administrative username and role assignments.

A template for environmental settings is available at `.env.example`.

---

## Installation & Setup

Ensure Python 3.11+ is installed. Follow the commands below to configure your environment:

### 1. Create a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## How to Run

### Run Headless Application Main
Starts all offline layers and launches system structures without the graphical user interface:
```bash
python3 app/main.py
```

### Run GUI Dashboard
If you are running in a GUI-enabled desktop environment, launch the interactive PyQt6 dashboard:
```bash
python3 -B -m interface.desktop.app
```

---

## Testing

The codebase uses `pytest` for unit testing. To run tests in a headless CI/CD environment (mocking graphical assets):
```bash
python3 -B -m pytest -o pythonpath=.
```

---

## License

This project is licensed under the terms of the MIT License. See the `LICENSE` file for more details.
