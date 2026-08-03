# ADR 0005: Passive Observability, UI State Machine and Decoupled Presentation Layer

## Status
Accepted

## Context
When building highly interactive, multi-dock, and real-time PyQt6 desktop dashboards for local AI runtimes, the risks of visual state desynchronization, circular widget signals, and UI-thread freeze are extremely high. To guarantee a professional, responsive user experience (60 FPS) and avoid a monolithic, 10,000-line `main_window.py` as new visual tabs (Vision, Audio, Workspace) are added, we must define the presentation layer's governance.

## Decision
We decide to implement the **Passive Observability and UI State Machine Architecture**:

1. **UIStateManager (ADR-003)**:
   * Serving as the single source of truth of the interface, it exposes isolated, reactive sub-states (ChatState, DownloadState, InferenceState). PyQt6 widgets observe this manager and never read backend state directly.
2. **UICommandBus (ADR-004)**:
   * Action triggers (e.g., clicking Download, Stop, Regenerate, Export) are dispatched as asynchronous commands on the `UICommandBus` instead of calling backend services directly, ensuring complete decoupling.
3. **UIPluginManager (ADR-005)**:
   * Implements a modular panel registry where new visual features (e.g., Audio spectrograph, Workspace browser) register their own PyQt6 widgets dynamically, preventing bloating the central main window.
4. **UI State Machine (ADR-007)**:
   * Coordinates the interface through predefined visual states (`IDLE`, `PREPARING`, `SCHEDULING`, `INFERENCE`, `STREAMING`). It handles the enabling/disabling of chat inputs and actions automatically across all widgets.
5. **Rending & Streaming Pipeline (ADR-009)**:
   * Prompts stream asynchronously (word-by-word) via background non-blocking worker threads. It passes tokens through a modular parsing chain (Markdown, LaTeX Math rendering, Mermaid vector diagrams) with active interruption ("Stop generation") controls.

## Consequences
* **Pros**:
  * 100% reactive, zero-freeze PyQt6 user interface.
  * Extensible design system; adding tabs or panels does not require editing `main_window.py`.
  * Standardized widget lifecycles (`initialize`, `subscribe`, `unsubscribe`) completely eliminate memory leaks.
* **Cons**:
  * Developers must follow the `UIStateManager` and `UICommandBus` flow, adding a layer of event dispatching instead of writing direct widget callbacks.
