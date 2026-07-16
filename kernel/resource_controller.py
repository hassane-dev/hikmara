class ResourceController:
    def check_limits(self) -> bool:
        return True

global_resource_controller = ResourceController()
