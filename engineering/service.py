import os
import sys
import subprocess
from core.security.service import global_security_policy

class CodeGenerator:
    def generate_python_template(self, project_name):
        return f"# {project_name}\nprint('Running offline application...')"

class SandboxExecutor:
    def run_sandboxed(self, filepath):
        try:
            res = subprocess.run([sys.executable, filepath], capture_output=True, text=True, timeout=5.0)
            return {"status": "success", "stdout": res.stdout}
        except Exception as e:
            return {"status": "error", "error": str(e)}

class DependencyManager:
    def __init__(self): self.recorded = {}
    def ensure_dependency(self, package):
        try:
            __import__(package)
            return True
        except ImportError:
            return False

class ProjectManager:
    def create_project(self, name):
        if not name: raise Exception("Empty")
        base = f"projects/{name}"
        os.makedirs(base, exist_ok=True)
        return base

global_dependency_manager = DependencyManager()
global_code_generator = CodeGenerator()
global_sandbox_executor = SandboxExecutor()
global_project_manager = ProjectManager()
