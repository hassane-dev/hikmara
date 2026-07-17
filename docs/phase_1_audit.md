# Hikmara AI - Phase 1 Core Security & Runtime Audit

This document presents the technical audit of the **Kernel**, **Core**, **Runtime**, and **Security** subsystems of Hikmara AI.

---

## 1. Security Architecture & Policy Engine Flow

### **Question: Do all sensitive actions pass through the policy engine before execution?**

**Yes.** Hikmara AI implements a strict policy execution chain for any sensitive operational instruction. Any action that alters the system state, installs dependencies, or reads/writes files is validated and logged.

### **The Enforcement Flow Diagram**
```
   [ Agent or Subsystem Request ]
                 │
                 ▼
     global_security_policy
     .authorize_action(...)
                 │
                 ├──► [ Non-Sensitive? ] ──────► Permit & Log
                 │
                 ▼
         [ Sensitive? ]
                 │
                 ▼
     [ Consent Manager (UI overlay) ]
                 │
         ┌───────┴───────┐
         ▼               ▼
     [ Approved ]    [ Denied ]
         │               │
         ▼               ▼
     Execution        Blocked
         │               │
         └───────┬───────┘
                 ▼
         [ Write Audit Log ]
         (SQLite audit_logs table)
```

### **Technical Breakdown**
1. **The Policy Engine (`core/security/service.py`)**:
   Exposes the primary hook `authorize_action(module, action, parameters, user="admin")`.
2. **Sensitive Action Detection**:
   The engine automatically marks an action as sensitive if it belongs to the following categories:
   - `execute_code` / any action containing `execute`
   - `install_dependency` / any action containing `install`
   - `access_system_files`
   - `write_file`
   - `delete_file`
   - `hardware_access`
3. **Consent Handler**:
   - The Policy Engine allows registering a custom dynamic `consent_handler` callback via `set_consent_handler(handler)`.
   - In the Desktop graphical interface, the `SecurityConsentDialog` widget (PyQt6 dialog overlay) is registered as the consent handler. It blocks execution and prompts the user to "Approve" or "Reject".
   - If no consent handler is registered (e.g. headless automation), any sensitive action defaults to `False` (safe-by-default behavior).
4. **Audit Logging**:
   Every authorization request, whether approved or denied, logs a secure, timestamped record into the local SQLite database (`database/hikmara.db`) inside the `audit_logs` table.

---

## 2. Runtime Subsystem & Dynamic Module Loading

### **Question: Does the runtime actually load modules dynamically from the module_registry, or is it only a skeleton structure?**

**Answer**: The current implementation utilizes a **hybrid registry-registration approach**:
1. **Active Registration**:
   Upon platform startup, `global_runtime_engine.bootstrap()` invokes `global_module_registry.register(name, version)` to dynamically register the active subsystems (`core_api`, `core_tasks`, `core_security`) in the `global_module_registry` service.
2. **Dynamic Service Management**:
   The `ServiceManager` inside the `RuntimeEngine` manages running services, supporting registration (`register_service`) and lifecycle activation (`start_all`, `stop_all`).
3. **Current Limitations / Code Loading**:
   - While modules are cataloged and queried dynamically via the module registry, the underlying physical importing of python files is managed through static, secure python imports.
   - The system does not currently perform arbitrary runtime hot-swapping or remote script compilation. This is a deliberate security decision to maintain the integrity of the platform and prevent arbitrary code execution attacks.

---

## 3. Subsystem Coherence Check

| Subsystem | Components Checked | Status | Alignment with Design |
|---|---|---|---|
| **`kernel/`** | `scheduler.py`, `event_loop.py`, `module_manager.py`, `resource_controller.py` | **Fully Coherent** | Drives core event post loops and background scheduling reliably. |
| **`core/`** | 10 modular folders (`api/`, `communication/`, `events/`, `logging/`, etc.) | **Fully Coherent** | Standard structure completed with unified interfaces and exceptions files. |
| **`runtime/`** | `__init__.py` bootstrapping engine | **Fully Coherent** | Initializes hardware health loops and logs lifecycle start signals. |
| **`config/`** | YAML config profiles | **Fully Coherent** | Holds absolute local file directories and `offline_mode: true`. |
