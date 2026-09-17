from typing import Any, Dict, List

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models.entities import ModuleConfig


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
            description="MySQL FULLTEXT（ngram）关键词检索，SQLite 测试环境回退 LIKE",
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

    def persist_to_db(self, db: Session, module_id: str) -> None:
        mod = self._modules.get(module_id)
        if not mod:
            return
        status = "enabled" if mod.enabled else "disabled"
        row = db.query(ModuleConfig).filter(ModuleConfig.module_id == module_id).first()
        if row is None:
            db.add(ModuleConfig(
                module_id=module_id,
                name=mod.manifest.name,
                version=mod.manifest.version,
                status=status,
                config=mod.config or {},
            ))
        else:
            row.name = mod.manifest.name
            row.version = mod.manifest.version
            row.status = status
            row.config = mod.config or {}
        db.commit()

    def load_from_db(self, db: Session) -> None:
        try:
            rows = {row.module_id: row for row in db.query(ModuleConfig).all()}
        except Exception:
            db.rollback()
            return

        if not rows:
            for module_id in list(self._modules):
                self.persist_to_db(db, module_id)
            return

        for module_id, mod in self._modules.items():
            row = rows.get(module_id)
            if row is None:
                self.persist_to_db(db, module_id)
                continue
            mod.enabled = row.status != "disabled"
            if row.config:
                mod.config = row.config


module_registry = ModuleRegistry()
