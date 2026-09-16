from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class ModuleManifest(BaseModel):
    id: str
    name: str
    version: str
    description: str = ""
    extension_point: str  # source_connector, parser, processor, search_provider, output_integration
    config_schema: Dict[str, Any] = {}

class BaseModule:
    def __init__(self, manifest: ModuleManifest):
        self.manifest = manifest
        self.enabled = True
        self.config: Dict[str, Any] = {}

    def initialize(self, config: Dict[str, Any]):
        self.config = config

    def start(self):
        pass

    def stop(self):
        pass

    def health_check(self) -> bool:
        return True

class ModuleRegistry:
    def __init__(self):
        self._modules: Dict[str, BaseModule] = {}
        # 预注册基础搜索模块与导入模块
        self._register_default_modules()

    def _register_default_modules(self):
        search_mod = BaseModule(ModuleManifest(
            id="search",
            name="Keyword Search",
            version="1.0.0",
            description="基于标题、摘要与正文的关键词检索（不依赖大模型）",
            extension_point="search_provider"
        ))
        file_mod = BaseModule(ModuleManifest(
            id="file-import",
            name="Local File Importer",
            version="1.0.0",
            description="本地文件与 Markdown 上传解析",
            extension_point="source_connector"
        ))
        self.register(search_mod)
        self.register(file_mod)

    def register(self, module: BaseModule):
        self._modules[module.manifest.id] = module

    def is_enabled(self, module_id: str) -> bool:
        mod = self._modules.get(module_id)
        return mod.enabled if mod else False

    def enable(self, module_id: str):
        if module_id in self._modules:
            self._modules[module_id].enabled = True
            self._modules[module_id].start()

    def disable(self, module_id: str):
        if module_id in self._modules:
            self._modules[module_id].enabled = False
            self._modules[module_id].stop()

    def list_modules(self) -> List[Dict[str, Any]]:
        result = []
        for m_id, m in self._modules.items():
            result.append({
                "id": m.manifest.id,
                "name": m.manifest.name,
                "version": m.manifest.version,
                "description": m.manifest.description,
                "extension_point": m.manifest.extension_point,
                "status": "enabled" if m.enabled else "disabled",
                "healthy": m.health_check(),
                "config": m.config
            })
        return result

    def update_config(self, module_id: str, new_config: Dict[str, Any]):
        if module_id in self._modules:
            self._modules[module_id].config.update(new_config)

module_registry = ModuleRegistry()
