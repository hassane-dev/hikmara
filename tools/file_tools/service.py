from tools.base_tool import BaseTool
import os

class CreateFileTool(BaseTool):
    def __init__(self):
        super().__init__("create_file", "Creates a local code file.", ["write_file"])

    def execute(self, params):
        filepath = params.get("filepath", "")
        content = params.get("content", "")
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return {"status": "success", "filepath": filepath}
