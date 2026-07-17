# Hikmara AI Architecture

This document describes the high-level architecture of **Hikmara AI**, a universal, modular local AI platform designed to become an autonomous local OS Architect.

## Architectural Principles

1. **Strict Offline-First**: Zero dependency on external networks, CDNs, or cloud service APIs. All computation (LLM, embeddings, audio transcription, database storage) happens strictly locally on device.
2. **Modular Isolation**: Each subsystem resides within its own module namespace. No direct cross-imports are permitted unless funneled through defined routing pathways like `core/api`, `core/events`, or `core/communication`.
3. **Hardware-Aware Adaptive Optimization**: Core monitors and schedulers dynamically adapt active workloads based on hardware constraints like CPU core limits or RAM availability.
4. **Agentic Autonomy & Self-Healing**: A multi-agent framework manages system diagnostics, coding, testing, and continuous document assembly.

---

## High-Level Module Blueprint

```
                     ┌─────────────────────────────┐
                     │    interface/ (PyQt6 UI)    │
                     └──────────────┬──────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                                kernel/                                 │
│      (Event Loops, Soft Scheduler, Subsystem Module Managers)          │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│                                 core/                                  │
│ (Security Policies, DB Registry, API Router, Events Bus, Task Queues) │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────┴─────────────────────────────────────┐
│                             runtime/                                   │
│                 (Subsystem state machines)                             │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        ▼                          ▼                          ▼
┌───────────────┐          ┌───────────────┐          ┌───────────────┐
│  ai_models/   │          │    memory/    │          │  knowledge/   │
│ (Simulated LLM│          │ (Local sqlite │          │ (Local sqlite │
│ Embed, Audio, │          │ Vector Store, │          │ factual base) │
│ Vision)       │          │ Short-Term)   │          │               │
└───────────────┘          └───────────────┘          └───────────────┘
        │                          │                          │
        └──────────────────────────┼──────────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│                              cognition/                                │
│       (Reasoning Rule Engine, Task Planners, Multi-Agent Swarms)       │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│                                 tools/                                 │
│               (File Handlers, Shell & Sandboxed Runners)               │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Subsystem Details

### 1. **Kernel Subsystem (`kernel/`)**
- Runs the primary multi-threaded execution scheduler and resource loop.
- Manages sub-process scheduling priorities via `scheduler.py`.
- Coordinates lifecycle hooks for all sub-modules using `module_manager.py`.

### 2. **Core Subsystem (`core/`)**
Acts as the inter-module mediator.
- **`communication/`**: Processes message requests via the `global_message_bus` utilizing unified request/response schemas.
- **`events/`**: Implements a publish-subscribe event-driven model via `global_event_bus`.
- **`security/`**: Policy engine validating code executions and installing libraries.
- **`system/`**: Measures resource statistics (CPU, RAM, Core distribution) via the `psutil` package.
- **`database/`**: Manages low-level SQLite connections to maintain persistence safely.
- **`configuration/`**: Parses files from `config/*.yaml` and supports runtime updates.

### 3. **Runtime Subsystem (`runtime/`)**
- Oversees active execution loops.
- Emits health parameters and verifies continuous execution alignment.

### 4. **AI Models Layer (`ai_models/`)**
- Implements base specifications and simulation wrappers for localized AI.
- Hosts specific pipelines: LLM, local vector embeddings generator, Whisper-based speech transcriber, and yolov8-based computer vision layers.

### 5. **Memory and Knowledge (`memory/` & `knowledge/`)**
- **Memory**: Features short-term active contexts paired with SQLite-backed Vector Stores matching Cosine-Similarity metrics.
- **Knowledge**: Holds permanent system relational facts retrieved via database structures.

### 6. **Cognition Engine (`cognition/`)**
The brain of Hikmara AI.
- **`reasoning/`**: Evaluates conditions and facts via a customized offline rules engine.
- **`planner/`**: Decomposes high-level requests into smaller, actionable task pipelines.
- **Specialized Agents**: Five task-oriented entities communicating through an internal mailbox broker:
  - **Architect Agent**
  - **Programmer Agent**
  - **Tester Agent**
  - **Security Agent**
  - **Documentation Agent**

### 7. **Tools Execution Registry (`tools/`)**
- Safe file readers and writer generators under `file_tools`.
- Shell execution code runners under `code_tools`.
- Policy-gated mechanisms ensuring security confirmation before actions.

### 8. **Interface Layer (`interface/`)**
- Rich GUI Desktop application built on **PyQt6**.
- Features system monitor graphs, prompt entries, model switches, and pop-up authorization overlays.
