# ADR 0004: Decoupled Four-Layer Platform Architecture

## Status
Accepted

## Context
As Hikmara AI evolved from an agent-assisted chat tool into a modular, local AI Operating System runtime, the complexity of managing multi-model hot pools, RAG vector searches, and specialized agents scaled rapidly. To prevent design creep, circular dependencies, and a bloated codebase (such as placing cognitive logic or file loading within PyQt6 or model manager files), we must establish clean, non-negotiable architectural boundaries.

## Decision
We decide to divide Hikmara AI into **four hermetically-sealed execution layers** communicating exclusively through typed, versioned data contracts (`schema_version = 1`):

1. **Presentation Layer (PyQt6 GUI)**:
   * **Role**: Exclusively an observer and visualizer of telemetry (via `InferenceMetricsService`) and of the current conversation history.
   * **Invariants**: PyQt6 remains strictly read-only and passive. No direct database queries, no model loading commands, and no cognitive orchestrations can bypass the unified services. It communicates actions only as asynchronous commands dispatched through `UICommandBus`.
2. **Cognition Layer (Orchestration & Reasoning)**:
   * **Role**: Classifies intents and sémantic tasks (`NLU Layer`, `TaskProfile`), plans high-level execution steps (`AgentSelector`, `TaskExecutionPlan`), and generates prompt context structures (`PromptBuilder`).
   * **Invariants**: Strictly independent of GGUF/Ollama file weights and physical memory or CPU architectures.
3. **Inference Layer (Hardware Execution)**:
   * **Role**: Performs resource scheduling (`InferenceScheduler`), technical path and parameter resolution (`InferencePlanner`, `InferenceProfile`), active RAM instance life cycles (`ModelLifecycleManager`), and model prediction streaming (`ModelManager` & `BaseLLM` interface).
   * **Invariants**: Blind to high-level sémantic workflows and business intent rules.
4. **Infrastructure Layer (Passive Resources)**:
   * **Role**: Centralizes file configs (`ConfigurationManager`), hardware diagnostic probes (`ResourceManager`), health reporting (`HealthCheckService`), and system event notifications (`global_event_bus`).

### Additional Presentational Invariants (ADR-008 & ADR-010):
* **Refresh Policy (ADR-008)**: To minimize unnecessary CPU usage, different views adopt adaptive refresh rates (Health diagnostic at 2s interval, chat and agent pipelines driven only by EventBus events).
* **VirtualChatList (ADR-010)**: Chat widgets must virtualize their contents (allocating and rendering only visible message bubbles) to ensure 60 FPS scrolling and zero memory lag even over 20,000+ messages.

## Consequences
* **Pros**:
  * Unprecedented maintainability; each of the four layers can be modified, tested, and upgraded independently.
  * Extensible plugin architecture where new LLM engines (ONNX, vision) can be registered as `EnginePlugin` without touching core logic.
  * Clear code review checklist where developers can instantly verify the 9 Architectural Invariants of the platform.
* **Cons**:
  * Slightly higher initial boilerplate code due to strict separation of contracts and data structures.
