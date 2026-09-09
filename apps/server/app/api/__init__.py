from fastapi import APIRouter
from app.api.routers import auth, users, spaces, knowledge, tags, attachments, search, audit, modules, agent, system

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户管理"])
api_router.include_router(spaces.router, prefix="/spaces", tags=["空间管理"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["知识管理"])
api_router.include_router(tags.router, prefix="/tags", tags=["标签管理"])
api_router.include_router(attachments.router, prefix="/attachments", tags=["附件管理"])
api_router.include_router(search.router, prefix="/search", tags=["全文检索"])
api_router.include_router(audit.router, prefix="/audit", tags=["审计日志"])
api_router.include_router(modules.router, prefix="/modules", tags=["模块管理"])
api_router.include_router(agent.router, prefix="/agent", tags=["Agent开放接口"])
api_router.include_router(system.router, prefix="/system", tags=["系统配置中心"])
