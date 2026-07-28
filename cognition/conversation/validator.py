import re
from typing import Dict, Any

class ResponseValidator:
    def __init__(self):
        pass

    def validate(self, response_text: str) -> Dict[str, Any]:
        """Validates response formatting, matching blocks, and basic safety constraints."""
        is_valid = True
        warnings = []

        # 1. Verify that all markdown code blocks are properly closed
        open_blocks = len(re.findall(r"```", response_text))
        if open_blocks % 2 != 0:
            is_valid = False
            warnings.append("Unclosed markdown code blocks detected.")

        # 2. Check for simple hallucination or leak markers
        if any(h in response_text.lower() for h in ["[hallucination]", "[error_leak]"]):
            is_valid = False
            warnings.append("Potential hallucinatory placeholders detected.")

        # 3. Code block validation (simple balance check)
        if "<?php" in response_text and "?>" not in response_text and "```php" not in response_text:
            warnings.append("PHP opening tag found without standard closing tag outside formatted block.")

        return {
            "is_valid": is_valid,
            "warnings": warnings,
            "final_text": response_text + ("\n\n*Avertissement de validation : " + "; ".join(warnings) + "*" if warnings else "")
        }

global_response_validator = ResponseValidator()
