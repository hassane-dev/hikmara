from typing import Dict, Any
from core.security.service import global_security_policy
from tools.registry import global_tool_registry

class ToolExecutor:
    """
    Decoupled tool executor component. It receives the tool call,
    validates the request via the security policy engine, gets user consent
    if necessary, and then executes the requested tool.
    """
    def __init__(self):
        pass

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        tool_inst = global_tool_registry.get_tool(tool_name)
        if not tool_inst:
            return {"status": "error", "output": f"Outil '{tool_name}' non trouvé dans le registre."}

        # Check safety permissions
        permissions = getattr(tool_inst, "permissions_required", [tool_name])
        for perm in permissions:
            auth = global_security_policy.authorize_action("tool_executor", "use_tool", {"tool": tool_name, "permission": perm})
            if not auth:
                return {"status": "error", "output": f"Action refusée par la politique de sécurité : permission '{perm}' requise."}

        # Execute tool
        try:
            output = tool_inst.execute(arguments)
            return {"status": "success", "output": str(output)}
        except Exception as e:
            return {"status": "error", "output": f"Erreur lors de l'exécution de l'outil : {str(e)}"}

global_tool_executor = ToolExecutor()
