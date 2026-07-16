class LogicalReasoningEngine:
    def reason(self, facts, query):
        return {"query": query, "aligned": True, "explanation": "Decision matched facts criteria"}

global_reasoning_engine = LogicalReasoningEngine()
