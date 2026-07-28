import re
from typing import List, Dict, Any
from core.security.service import global_security_policy
from tools.registry import global_tool_registry

class ToolRouter:
    def __init__(self):
        pass

    def decide_tools(self, prompt: str) -> Dict[str, Any]:
        """Decides which tools are needed and checks security policies."""
        prompt_lower = prompt.lower()
        required_tools = []
        needs_tools = False

        # Match tool keywords with registry tools
        if any(k in prompt_lower for k in ["crée un fichier", "écris un fichier", "write file", "create file", "modifier le fichier", "save to file"]):
            required_tools.append("create_file")
            needs_tools = True
        if any(k in prompt_lower for k in ["exécute le code", "execute code", "run code", "lance le code"]):
            required_tools.append("execute_code")
            needs_tools = True

        # Perform security policy authorization check for sensitive tools
        is_authorized = True
        if needs_tools:
            for t_name in required_tools:
                tool_inst = global_tool_registry.get_tool(t_name)
                permissions = tool_inst.permissions_required if tool_inst else [t_name]
                for perm in permissions:
                    # Query security policy engine
                    auth = global_security_policy.authorize_action("tool_router", "use_tool", {"tool": t_name, "permission": perm})
                    if not auth:
                        is_authorized = False

        return {
            "needs_tools": needs_tools,
            "tools_to_run": required_tools,
            "security_authorized": is_authorized
        }

global_tool_router = ToolRouter()
