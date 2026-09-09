from .registry import registry

class ModuleManager:
    @staticmethod
    def enable_module(module_id: str):
        mod = registry.get_module(module_id)
        if mod:
            mod.enabled = True
            
    @staticmethod
    def disable_module(module_id: str):
        mod = registry.get_module(module_id)
        if mod:
            mod.enabled = False
