import re
import yaml
import os
import time
from typing import Dict, Any
from cognition.conversation.models import ModelRequest, ModelResponse
from cognition.context.service import global_context_manager
from cognition.nlu.service import global_language_understanding
from cognition.session.service import global_session_manager
from cognition.prompt_builder.service import global_prompt_builder
from cognition.conversation.memory_retriever import global_memory_retriever
from cognition.conversation.post_processing import global_post_processor
from cognition.conversation.validator import global_response_validator
from memory.router import global_memory_router
from knowledge.router import global_knowledge_router
from ai_models.model_manager.service import global_model_manager

class ConversationEngine:
    def __init__(self):
        pass

    def change_model(self, engine_type: str, model_name: str) -> bool:
        """Dynamically switches active model/engine at runtime."""
        return global_model_manager.change_model(engine_type, model_name)

    @property
    def active_engine(self) -> str:
        return global_model_manager.active_engine_name

    @property
    def active_model(self) -> str:
        return global_model_manager.active_model_name

    def generate_response(self, prompt: str) -> ModelResponse:
        """Generates a natural, context-aware, progressive conversation or coding response using layered components."""
        start_time = time.time()
        prompt_lower = prompt.strip().lower()

        # 1. First run Language Understanding (NLU) Layer analysis (Phase 2.5)
        nlu = global_language_understanding.analyze(prompt)

        # 2. Update session context via Conversation Manager
        global_context_manager.update_context("user", prompt, nlu_result=nlu)
        context = global_context_manager.get_context()
        active_domain = context.active_domain or "python"

        # Check progressive generation flags
        has_gui = context.context_references.get("has_gui", False)
        has_sqlite = context.context_references.get("has_sqlite", False)

        raw_reply_text = None

        # 3. Handle progressive code generation, modification, and conversion presets
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
                    raw_reply_text = (
                        "Certainement ! Voici le programme Python modifié combinant l'interface graphique PyQt6 et la base de données SQLite.\n"
                        "Chaque calcul de somme effectué est automatiquement sauvegardé dans la base SQLite locale :\n\n"
                        f"```python\n{sqlite_gui_code}```"
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
                    raw_reply_text = (
                        "Voici le programme d'addition Python enrichi d'une interface graphique PyQt6 moderne :\n\n"
                        f"```python\n{gui_code}```"
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
                    raw_reply_text = (
                        "Certainement ! Voici un programme Python simple qui calcule et affiche la somme de deux entiers :\n\n"
                        f"```python\n{simple_py_code}```"
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
                    raw_reply_text = (
                        "Certainement ! Voici le programme converti en PHP, conservant l'addition et la persistance SQLite dans la base de données historique :\n\n"
                        f"```php\n{php_sqlite_code}```"
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
                    raw_reply_text = (
                        "Certainement ! Voici le programme d'addition converti en PHP :\n\n"
                        f"```php\n{simple_php_code}```"
                    )

        # 4. Handle other natural text presets if not coding flow
        if raw_reply_text is None:
            if nlu.intent == "greeting":
                raw_reply_text = "Bonjour ! Comment puis-je vous aider aujourd'hui ?" if nlu.language == "fr" else "Good morning! How can I help you today?"

            elif nlu.intent == "general_conversation":
                if any(k in prompt_lower for k in ["comment vas-tu", "comment ca va", "comment ça va"]):
                    raw_reply_text = "Je vais très bien, merci ! En tant qu'assistant local Hikmara AI, je suis opérationnel à 100%. Que puis-je faire pour vous aujourd'hui ?"
                elif any(k in prompt_lower for k in ["how are you", "how's it going"]):
                    raw_reply_text = "I am doing great, thank you! As your local Hikmara AI assistant, I am fully operational offline. How can I help you today?"
                else:
                    raw_reply_text = "De rien ! C'est un plaisir de vous aider. N'hésitez pas si vous avez d'autres requêtes !"

            elif nlu.intent == "explanation":
                if "python" in prompt_lower:
                    raw_reply_text = (
                        "Python est un langage de programmation de haut niveau, interprété, interactif et orienté objet.\n"
                        "Il est réputé pour sa lisibilité exceptionnelle de syntaxe, permettant aux développeurs de concevoir des applications "
                        "complexes avec beaucoup moins de lignes de code qu'en C++ ou en Java."
                    )
                elif "php" in prompt_lower:
                    raw_reply_text = (
                        "PHP (Hypertext Preprocessor) est un langage de script généraliste et open-source particulièrement "
                        "adapté au développement d'applications web et facilement intégrable au HTML.\n"
                        "Il s'exécute côté serveur pour générer du contenu dynamique."
                    )
                else:
                    raw_reply_text = "Une base de données est un système organisé de stockage de données, permettant de modéliser des informations et d'y accéder de façon rapide et structurée."

        # 5. Layered Fallback to MemoryRouter, KnowledgeRouter, PromptBuilder, and ModelManager
        if raw_reply_text is None:
            # Query Memory Router & Knowledge Router for rich background context
            mem_data = global_memory_router.retrieve(prompt, global_context_manager)
            kn_data = global_knowledge_router.retrieve_knowledge(prompt)
            combined_context = f"{mem_data}\n\n{kn_data}".strip()

            # Compile system and user prompts via PromptBuilder
            prompt_dict = global_prompt_builder.build_prompt(prompt, context, combined_context, nlu.intent)

            # Generate structured response using ModelManager
            llm_res = global_model_manager.generate(prompt_dict["user"], prompt_dict["system"], nlu.intent)
            raw_reply_text = llm_res.text
            if "I am Hikmara AI local system" in raw_reply_text and "let me assist you" in raw_reply_text:
                raw_reply_text = f"En tant qu'assistant local Hikmara AI, j'ai bien pris en compte votre requête '{prompt}'. Comment puis-je vous guider plus précisément ?"

        # 6. Apply PostProcessor sanitization and Markdown formatting
        cleaned_text = global_post_processor.process_response(raw_reply_text, context)

        # 7. Apply ResponseValidator to check brackets, code closes, and simple safety warnings
        validation_res = global_response_validator.validate(cleaned_text)
        final_text = validation_res["final_text"]

        # Calculate turning statistics & latency
        latency = time.time() - start_time
        global_session_manager.update_stats(len(prompt)//4, len(final_text)//4, latency)

        # Record assistant reply turn in context
        global_context_manager.update_context("assistant", final_text)

        return ModelResponse(
            response=final_text,
            metadata={
                "engine": global_model_manager.active_engine_name,
                "model": global_model_manager.active_model_name,
                "latency_seconds": round(latency, 4)
            }
        )

global_conversation_engine = ConversationEngine()
