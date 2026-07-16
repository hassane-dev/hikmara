class PlannerModule:
    def decompose_target(self, target):
        return ["Analyze requirements", "Create directory layout", "Generate backend files, schemas & GUI code", "Run validation", "Audit release details"]

global_planner = PlannerModule()
