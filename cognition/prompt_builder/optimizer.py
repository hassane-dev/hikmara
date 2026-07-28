from typing import List, Dict, Any

class TokenBudgetManager:
    """
    Manages the context size of prompts to fit within the active model's context window.
    Calculates estimated token counts and compresses/truncates if budget is exceeded.
    """
    def __init__(self, max_context_tokens: int = 2048):
        self.max_context_tokens = max_context_tokens

    def estimate_tokens(self, text: str) -> int:
        """Simple offline token estimation (approx 4 chars per token)."""
        return max(1, len(text) // 4)

    def optimize_history(self, history: List[Dict[str, str]], budget_tokens: int) -> List[Dict[str, str]]:
        """Prunes oldest history entries if they exceed the allocated token budget."""
        optimized_history = []
        total_tokens = 0
        # Start from newest history turns
        for turn in reversed(history):
            turn_tokens = self.estimate_tokens(turn.get("message", ""))
            if total_tokens + turn_tokens > budget_tokens:
                break
            optimized_history.insert(0, turn)
            total_tokens += turn_tokens
        return optimized_history


class PromptOptimizer:
    def __init__(self, max_context_tokens: int = 2048):
        self.budget_manager = TokenBudgetManager(max_context_tokens)

    def optimize_prompt_inputs(self, system_base: str, history: List[Dict[str, str]], retrieved_context: str, user_message: str) -> Dict[str, Any]:
        """
        Assembles and optimizes context to fit inside the active model's maximum context window.
        """
        sys_tokens = self.budget_manager.estimate_tokens(system_base)
        user_tokens = self.budget_manager.estimate_tokens(user_message)

        # Determine remaining budget for history and memories
        remaining_budget = self.budget_manager.max_context_tokens - sys_tokens - user_tokens - 100 # buffer
        if remaining_budget < 500:
            # Drastic compression if tight
            retrieved_context = retrieved_context[:800] + "\n[Context compressed for context window limits...]"
            remaining_budget = 500

        # Split remaining budget: 40% for memory context, 60% for history
        mem_budget = int(remaining_budget * 0.4)
        hist_budget = int(remaining_budget * 0.6)

        # Truncate memory context if needed
        while self.budget_manager.estimate_tokens(retrieved_context) > mem_budget and len(retrieved_context) > 100:
            retrieved_context = retrieved_context[:int(len(retrieved_context) * 0.8)] + "\n[Context compressed...]"

        # Optimize conversation history turns
        optimized_history = self.budget_manager.optimize_history(history, hist_budget)

        return {
            "history": optimized_history,
            "retrieved_context": retrieved_context,
            "system_prompt": system_base
        }

global_prompt_optimizer = PromptOptimizer()
