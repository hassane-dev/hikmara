# ADR 0003: Autonomous Agents Cognition Framework

## Status
Accepted

## Context
Operating system diagnostics, self-healing code edits, and document generation represent complex, non-linear tasks. A single generalized AI loop struggles to maintain focus, leading to high error rates and security violations (e.g. overwriting protected system files).

We need an orchestration system that can decompose complex system commands, execute actions safely, and evaluate the outcomes.

## Decision
We decide to establish a **Modular Multi-Agent Cognition Framework** backed by:
1. **Decomposed Task Planner**: Splits high-level instructions into concrete sequential pipeline items.
2. **Dedicated Task Specialists**: A cooperative swarm consisting of five specialized agents:
   - **Architect**: Designs layout frameworks and verifies file structures.
   - **Programmer**: Writes source codes and executes non-destructive file updates.
   - **Tester**: Automatically invokes `pytest` and checks system compliance.
   - **Security**: Scans execution commands and checks them against active security policies.
   - **Documentation**: Collects changes and continuously writes reference guides.
3. **Core Policy Gatekeeper**: Any sensitive tool action (e.g., shell command execution or file writes) must pass through a strict Policy verification loop. When configurations require, this pauses and prompts the user via a Security Consent Overlay before proceeding.

## Consequences
- **Pros**:
  - High resilience: specialized agents are more precise than generalized loops.
  - Safe operation: explicit policy-consent gating prevents unauthorized modifications.
  - Modular extension: new specialist agents can be added cleanly.
- **Cons**:
  - Multi-agent communication increases context size and message pass cycles.
  - Requires clear internal communication channels (e.g., our structured agent communication queues).
