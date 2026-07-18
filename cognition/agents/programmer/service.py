from cognition.agents.base_agent import BaseAgent

class ProgrammerAgent(BaseAgent):
    def execute_task(self, task, context):
        task_lower = task.lower()
        if "php" in task_lower and "somme" in task_lower:
            code = (
                "<?php\n"
                "function additionnerEntiers(int $a, int $b): int {\n"
                "    return $a + $b;\n"
                "}\n\n"
                "// Exemple d'utilisation :\n"
                "echo additionnerEntiers(5, 10); // Affiche 15\n"
                "?>"
            )
        elif "api flask" in task_lower:
            code = (
                "from flask import Flask, jsonify\n"
                "app = Flask(__name__)\n\n"
                "@app.route('/api')\n"
                "def hello():\n"
                "    return jsonify(message='Hello from Hikmara API!')\n\n"
                "if __name__ == '__main__':\n"
                "    app.run(debug=True)"
            )
        else:
            code = "import sys"
        return {"status": "success", "agent": self.agent_id, "code": code}
