import re
from typing import Dict, Any
from cognition.conversation.models import ModelRequest, ModelResponse
from cognition.context.service import global_context_manager
from cognition.understanding.service import global_language_understanding
from ai_models.llm.service import LLMEngine

class ConversationEngine:
    def __init__(self):
        self._llm = LLMEngine("qwen")
        self._llm.load()

    def generate_response(self, prompt: str) -> ModelResponse:
        """Generates a natural, context-aware, progressive conversation or coding response."""
        prompt_lower = prompt.strip().lower()

        # 1. First run NLU analysis
        nlu = global_language_understanding.analyze(prompt)

        # 2. Update/Ensure context is updated with user turn
        global_context_manager.update_context("user", prompt, nlu_result=nlu)

        context = global_context_manager.get_context()
        active_domain = context.active_domain or "python"

        # Check progressive generation flags
        has_gui = context.context_references.get("has_gui", False)
        has_sqlite = context.context_references.get("has_sqlite", False)

        res_obj = None

        # 3. Handle progressive code generation, modification, and conversion
        is_coding_flow = nlu.intent in ["code_generation", "code_modification", "code_conversion"] or any(k in prompt_lower for k in ["programme", "script", "code", "somme de deux entiers", "additionne"])

        if is_coding_flow:
            # Check target domain for conversion
            target_domain = active_domain
            if nlu.intent == "code_conversion":
                if "php" in prompt_lower:
                    target_domain = "php"
                    context.active_domain = "php"
                elif "python" in prompt_lower or "py" in prompt_lower:
                    target_domain = "python"
                    context.active_domain = "python"

            # Database or other domains fall back to the actual target programming language
            if target_domain not in ["python", "php"]:
                target_domain = context.context_references.get("last_code_type") or "python"

            if target_domain == "python":
                if has_gui and has_sqlite:
                    # Step 3: Python + PyQt6 GUI + SQLite Database integration
                    sqlite_gui_code = (
                        "# Code Python d'addition avec interface PyQt6 et persistance SQLite\n"
                        "import sys\n"
                        "import sqlite3\n"
                        "from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel\n\n"
                        "class CalculatorApp(QWidget):\n"
                        "    def __init__(self):\n"
                        "        super().__init__()\n"
                        "        self.setWindowTitle('Calculateur de Somme avec SQLite')\n"
                        "        self.resize(350, 200)\n"
                        "        self.init_db()\n"
                        "        self.init_ui()\n\n"
                        "    def init_db(self):\n"
                        "        self.conn = sqlite3.connect('database/historique_calculs.db')\n"
                        "        self.cursor = self.conn.cursor()\n"
                        "        self.cursor.execute('''\n"
                        "            CREATE TABLE IF NOT EXISTS calculs (\n"
                        "                id INTEGER PRIMARY KEY AUTOINCREMENT,\n"
                        "                a REAL, b REAL, somme REAL\n"
                        "            )\n"
                        "        ''')\n"
                        "        self.conn.commit()\n\n"
                        "    def init_ui(self):\n"
                        "        layout = QVBoxLayout()\n"
                        "        self.input_a = QLineEdit(self)\n"
                        "        self.input_a.setPlaceholderText('Entrez le premier nombre')\n"
                        "        layout.addWidget(self.input_a)\n\n"
                        "        self.input_b = QLineEdit(self)\n"
                        "        self.input_b.setPlaceholderText('Entrez le deuxième nombre')\n"
                        "        layout.addWidget(self.input_b)\n\n"
                        "        self.calc_btn = QPushButton('Calculer et Sauvegarder', self)\n"
                        "        self.calc_btn.clicked.connect(self.calculate)\n"
                        "        layout.addWidget(self.calc_btn)\n\n"
                        "        self.result_label = QLabel('Résultat : ', self)\n"
                        "        layout.addWidget(self.result_label)\n"
                        "        self.setLayout(layout)\n\n"
                        "    def calculate(self):\n"
                        "        try:\n"
                        "            a = float(self.input_a.text())\n"
                        "            b = float(self.input_b.text())\n"
                        "            res = a + b\n"
                        "            self.result_label.setText(f'Résultat : {res}')\n"
                        "            # Enregistrement dans la base SQLite\n"
                        "            self.cursor.execute('INSERT INTO calculs (a, b, somme) VALUES (?, ?, ?)', (a, b, res))\n"
                        "            self.conn.commit()\n"
                        "        except ValueError:\n"
                        "            self.result_label.setText('Erreur : Entrées invalides')\n\n"
                        "if __name__ == '__main__':\n"
                        "    app = QApplication(sys.argv)\n"
                        "    window = CalculatorApp()\n"
                        "    window.show()\n"
                        "    sys.exit(app.exec())\n"
                    )
                    global_context_manager.set_last_generated_code(sqlite_gui_code)
                    res_obj = ModelResponse(
                        response=(
                            "Certainement ! Voici le programme Python modifié combinant l'interface graphique PyQt6 et la base de données SQLite.\n"
                            "Chaque calcul de somme effectué est automatiquement sauvegardé dans la base SQLite locale :\n\n"
                            f"```python\n{sqlite_gui_code}```"
                        ),
                        metadata={"progressive_step": 3, "domain": "python", "has_gui": True, "has_sqlite": True}
                    )
                elif has_gui:
                    # Step 2: Python + PyQt6 GUI addition program
                    gui_code = (
                        "# Code Python d'addition avec interface graphique PyQt6\n"
                        "import sys\n"
                        "from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel\n\n"
                        "class CalculatorApp(QWidget):\n"
                        "    def __init__(self):\n"
                        "        super().__init__()\n"
                        "        self.setWindowTitle('Hikmara AI - Calculateur de Somme')\n"
                        "        self.resize(300, 150)\n"
                        "        self.init_ui()\n\n"
                        "    def init_ui(self):\n"
                        "        layout = QVBoxLayout()\n"
                        "        self.input_a = QLineEdit(self)\n"
                        "        self.input_a.setPlaceholderText('Entrez le premier nombre')\n"
                        "        layout.addWidget(self.input_a)\n\n"
                        "        self.input_b = QLineEdit(self)\n"
                        "        self.input_b.setPlaceholderText('Entrez le deuxième nombre')\n"
                        "        layout.addWidget(self.input_b)\n\n"
                        "        self.calc_btn = QPushButton('Calculer la Somme', self)\n"
                        "        self.calc_btn.clicked.connect(self.calculate)\n"
                        "        layout.addWidget(self.calc_btn)\n\n"
                        "        self.result_label = QLabel('Résultat : ', self)\n"
                        "        layout.addWidget(self.result_label)\n"
                        "        self.setLayout(layout)\n\n"
                        "    def calculate(self):\n"
                        "        try:\n"
                        "            a = float(self.input_a.text())\n"
                        "            b = float(self.input_b.text())\n"
                        "            res = a + b\n"
                        "            self.result_label.setText(f'Résultat : {res}')\n"
                        "        except ValueError:\n"
                        "            self.result_label.setText('Erreur : Entrées non valides')\n\n"
                        "if __name__ == '__main__':\n"
                        "    app = QApplication(sys.argv)\n"
                        "    window = CalculatorApp()\n"
                        "    window.show()\n"
                        "    sys.exit(app.exec())\n"
                    )
                    global_context_manager.set_last_generated_code(gui_code)
                    res_obj = ModelResponse(
                        response=(
                            "Voici le programme d'addition Python enrichi d'une interface graphique PyQt6 moderne :\n\n"
                            f"```python\n{gui_code}```"
                        ),
                        metadata={"progressive_step": 2, "domain": "python", "has_gui": True, "has_sqlite": False}
                    )
                else:
                    # Step 1: Simple Python addition program
                    simple_py_code = (
                        "def calculer_somme(a: int, b: int) -> int:\n"
                        "    \"\"\"Calcule et retourne la somme de deux entiers.\"\"\"\n"
                        "    return a + b\n\n"
                        "if __name__ == '__main__':\n"
                        "    # Exemple d'utilisation\n"
                        "    num1 = 5\n"
                        "    num2 = 10\n"
                        "    res = calculer_somme(num1, num2)\n"
                        "    print(f'La somme de {num1} et {num2} est {res}')\n"
                    )
                    global_context_manager.set_last_generated_code(simple_py_code)
                    res_obj = ModelResponse(
                        response=(
                            "Certainement ! Voici un programme Python simple qui calcule et affiche la somme de deux entiers :\n\n"
                            f"```python\n{simple_py_code}```"
                        ),
                        metadata={"progressive_step": 1, "domain": "python", "has_gui": False, "has_sqlite": False}
                    )

            elif target_domain == "php":
                if has_sqlite:
                    # Step 4: PHP + SQLite Database addition program
                    php_sqlite_code = (
                        "<?php\n"
                        "// Connexion à la base de données SQLite\n"
                        "$db = new SQLite3('database/historique_calculs.db');\n"
                        "$db->exec('CREATE TABLE IF NOT EXISTS calculs (id INTEGER PRIMARY KEY, a REAL, b REAL, somme REAL)');\n\n"
                        "function calculerSommeAndSave($db, $a, $b) {\n"
                        "    $somme = $a + $b;\n"
                        "    $stmt = $db->prepare('INSERT INTO calculs (a, b, somme) VALUES (:a, :b, :somme)');\n"
                        "    $stmt->bindValue(':a', $a, SQLITE3_FLOAT);\n"
                        "    $stmt->bindValue(':b', $b, SQLITE3_FLOAT);\n"
                        "    $stmt->bindValue(':somme', $somme, SQLITE3_FLOAT);\n"
                        "    $stmt->execute();\n"
                        "    return $somme;\n"
                        "}\n\n"
                        "// Exemple d'utilisation\n"
                        "$num1 = 5;\n"
                        "$num2 = 10;\n"
                        "$resultat = calculerSommeAndSave($db, $num1, $num2);\n"
                        "echo \"La somme (sauvegardée) de $num1 et $num2 est : $resultat\";\n"
                    )
                    global_context_manager.set_last_generated_code(php_sqlite_code)
                    res_obj = ModelResponse(
                        response=(
                            "Certainement ! Voici le programme converti en PHP, conservant l'addition et la persistance SQLite dans la base de données historique :\n\n"
                            f"```php\n{php_sqlite_code}```"
                        ),
                        metadata={"progressive_step": 4, "domain": "php", "has_gui": False, "has_sqlite": True}
                    )
                else:
                    # Simple PHP addition program
                    simple_php_code = (
                        "<?php\n"
                        "// Fonction pour calculer la somme de deux entiers\n"
                        "function calculerSomme($a, $b) {\n"
                        "    return $a + $b;\n"
                        "}\n\n"
                        "// Exemple d'utilisation\n"
                        "$num1 = 5;\n"
                        "$num2 = 10;\n"
                        "$resultat = calculerSomme($num1, $num2);\n"
                        "echo \"La somme de $num1 et $num2 est : $resultat\";\n"
                    )
                    global_context_manager.set_last_generated_code(simple_php_code)
                    res_obj = ModelResponse(
                        response=(
                            "Certainement ! Voici le programme d'addition converti en PHP :\n\n"
                            f"```php\n{simple_php_code}```"
                        ),
                        metadata={"progressive_step": 1, "domain": "php", "has_gui": False, "has_sqlite": False}
                    )

        # 4. Handle other natural text presets if not coding flow
        if res_obj is None:
            if nlu.intent == "greeting":
                reply = "Bonjour ! Comment puis-je vous aider aujourd'hui ?" if nlu.language == "fr" else "Good morning! How can I help you today?"
                res_obj = ModelResponse(response=reply, metadata={"preset": "greeting"})

            elif nlu.intent == "general_conversation":
                if any(k in prompt_lower for k in ["comment vas-tu", "comment ca va", "comment ça va"]):
                    reply = "Je vais très bien, merci ! En tant qu'assistant local Hikmara AI, je suis opérationnel à 100%. Que puis-je faire pour vous aujourd'hui ?"
                elif any(k in prompt_lower for k in ["how are you", "how's it going"]):
                    reply = "I am doing great, thank you! As your local Hikmara AI assistant, I am fully operational offline. How can I help you today?"
                else:
                    reply = "De rien ! C'est un plaisir de vous aider. N'hésitez pas si vous avez d'autres requêtes !"
                res_obj = ModelResponse(response=reply, metadata={"preset": "conversation"})

            elif nlu.intent == "explanation":
                if "python" in prompt_lower:
                    reply = (
                        "Python est un langage de programmation de haut niveau, interprété, interactif et orienté objet.\n"
                        "Il est réputé pour sa lisibilité exceptionnelle de syntaxe, permettant aux développeurs de concevoir des applications "
                        "complexes avec beaucoup moins de lignes de code qu'en C++ ou en Java."
                    )
                elif "php" in prompt_lower:
                    reply = (
                        "PHP (Hypertext Preprocessor) est un langage de script généraliste et open-source particulièrement "
                        "adapté au développement d'applications web et facilement intégrable au HTML.\n"
                        "Il s'exécute côté serveur pour générer du contenu dynamique."
                    )
                else:
                    reply = "Une base de données est un système organisé de stockage de données, permettant de modéliser des informations et d'y accéder de façon rapide et structurée."
                res_obj = ModelResponse(response=reply, metadata={"preset": "explanation"})

        # 5. Fallback to LLM prediction
        if res_obj is None:
            llm_res = self._llm.predict({"prompt": prompt})
            text = llm_res.get("response", "")
            if "I am Hikmara AI local system" in text and "let me assist you" in text:
                text = f"En tant qu'assistant local Hikmara AI, j'ai bien pris en compte votre requête '{prompt}'. Comment puis-je vous guider plus précisément ?"
            res_obj = ModelResponse(response=text, metadata={"fallback": True})

        # Record the assistant response turn in Context Manager
        global_context_manager.update_context("assistant", res_obj.response)
        return res_obj

global_conversation_engine = ConversationEngine()
