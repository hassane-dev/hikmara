import re
from typing import Dict, Any

class PostProcessor:
    def __init__(self):
        pass

    def process_response(self, response_text: str, context: Any) -> str:
        """Post-processes and cleans responses, formatting code/tables and enforcing privacy policies."""
        cleaned = response_text.strip()

        # 1. Clear any raw model prompt injection markers or LLM metadata artifacts
        cleaned = re.sub(r"(<\|im_start\|>|<\|im_end\|>|system\n|user\n|assistant\n)", "", cleaned)

        # 2. Enforce Markdown styling rules for raw tables or unformatted code blocks
        # (e.g., if response has raw Python code without block formatting, wrap it)
        if "def " in cleaned and "```python" not in cleaned:
            # Wrap Python code
            lines = cleaned.split("\n")
            code_lines = [l for l in lines if l.startswith("def ") or l.startswith("    ") or l.startswith("import ") or l.startswith("if __name__")]
            if code_lines:
                code_str = "\n".join(code_lines)
                cleaned = cleaned.replace(code_str, f"```python\n{code_str}\n```")

        # 3. Security/Privacy: filter sensitive local system paths or keys if accidentally outputted
        cleaned = re.sub(r"(/[a-zA-Z0-9_\.\-]+/)*\.env", ".env (masqué pour votre sécurité)", cleaned)
        cleaned = re.sub(r"\b[A-Za-z0-9+/]{32,44}\b", "[CLE_API_MASQUEE]", cleaned) # hide generic api keys

        # 4. Citations & Context Sync
        # Add citations if references are detected
        if context and context.file_references:
            cleaned += f"\n\n*Réf: Fichiers consultés : {', '.join(context.file_references)}*"

        return cleaned

global_post_processor = PostProcessor()
