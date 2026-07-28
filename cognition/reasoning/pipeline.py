from typing import List, Dict, Any
from cognition.reasoning.service import global_reasoning_engine
from cognition.planner.service import global_planner

class ReasoningPipeline:
    def __init__(self):
        pass

    def reason_and_plan(self, prompt: str) -> Dict[str, Any]:
        """Decomposes, plans, and aligns reasoning before LLM calls."""
        prompt_lower = prompt.lower()

        # 1. Use global planner to decompose tasks
        steps = global_planner.decompose_target(prompt)

        # 2. Use reasoning engine to align policies
        reason_res = global_reasoning_engine.reason([prompt], "query")

        return {
            "decomposed_steps": steps,
            "policy_aligned": reason_res.get("aligned", True),
            "blueprint_suggestions": ["Étape " + str(i+1) + " : " + step for i, step in enumerate(steps)]
        }

global_reasoning_pipeline = ReasoningPipeline()
