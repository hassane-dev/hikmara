# Getting Started with Hikmara AI

Welcome to **Hikmara AI**, a modular, offline-first universal local AI platform designed to evolve into an intelligent Operating System architect. This guide will walk you through setting up and running your first instance of Hikmara AI.

## Prerequisites

- **Python**: Version 3.11 or higher is required.
- **Operating System**: Linux, macOS, or Windows (Windows 11 recommended for full support).
- **Hardware**: Hikmara AI runs local models. A minimum of 8 GB RAM is recommended (16 GB for optimal local AI performance).

---

## Installation

### 1. Clone the Repository
Clone the codebase to your local workspace:
```bash
git clone https://github.com/your-repo/hikmara.git
cd hikmara
```

### 2. Configure Virtual Environment
It is highly recommended to isolate the dependencies inside a dedicated virtual environment:

On **Linux & macOS**:
```bash
python3 -m venv venv
source venv/bin/activate
```

On **Windows**:
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Core Dependencies
Use the provided `requirements.txt` to install the package suite:
```bash
pip install -r requirements.txt
```

---

## Configuration

Hikmara AI uses local YAML files for configuration. The files are located in the `config/` directory:

- **`config/system.yaml`**: Standard system options.
- **`config/models.yaml`**: Map local model filenames (GGUF, Whisper, YOLO) here.
- **`config/security.yaml`**: Access lists, sandbox consent prompts, encryption modes.
- **`config/hardware.yaml`**: Core limits and GPU toggles.
- **`config/user.yaml`**: Administrative username and role profile.

For a summary of supported environment variables, see `.env.example`.

---

## Running the Application

### 1. Headless Execution
To run Hikmara AI's backend services, kernel loop, scheduler, memory systems, and multi-agent loops:
```bash
python app/main.py
```

### 2. Desktop Interface (GUI Dashboard)
To open the interactive dashboard showing real-time agent activities, SQLite memory inspector, resource meters, and policy configurations:
```bash
python3 -B -m interface.desktop.app
```

---

## Running the Test Suite

We practice strict test-driven checks to ensure correctness across core subsystems. To run the automated unit/integration tests:
```bash
python3 -B -m pytest -o pythonpath=.
```
All unit tests mock UI elements to run successfully even on headless remote execution boxes or GitHub Action workflows.
