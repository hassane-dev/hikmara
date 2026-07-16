from tools.base_tool import BaseTool
import subprocess
import os
import sys

class ExecuteCodeTool(BaseTool):
    def __init__(self):
        super().__init__("execute_code", "Runs a Python script.", ["execute_code"])

    def execute(self, params):
        code = params.get("code", "")
        temp = "cache/temporary/sandbox_temp.py"
        os.makedirs(os.path.dirname(temp), exist_ok=True)
        with open(temp, "w", encoding="utf-8") as f:
            f.write(code)
        res = subprocess.run([sys.executable, temp], capture_output=True, text=True, timeout=5.0)
        return {"status": "success" if res.returncode==0 else "error", "stdout": res.stdout}
