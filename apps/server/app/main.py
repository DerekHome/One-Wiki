from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.api import api_router
from app.schemas.common import ResponseModel
from app.models.database import get_db
from app.core.config import settings

app = FastAPI(
    title="企业知识中心系统 (Enterprise Knowledge Center API)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    redirect_slashes=False
)

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ResponseModel(
            success=False,
            data=None,
            error={"code": "VALIDATION_ERROR", "message": "请求参数验证失败", "details": exc.errors()}
        ).model_dump()
    )


def _http_error_response(exc: HTTPException):
    detail = exc.detail
    if isinstance(detail, dict):
        code = detail.get("code", "HTTP_ERROR")
        msg = detail.get("message", "请求处理失败")
    else:
        code = "HTTP_ERROR"
        msg = str(detail)
    return JSONResponse(
        status_code=exc.status_code,
        content=ResponseModel(
            success=False,
            data=None,
            error={"code": code, "message": msg}
        ).model_dump()
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return _http_error_response(exc)


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, HTTPException):
        return _http_error_response(exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ResponseModel(
            success=False,
            data=None,
            error={"code": "INTERNAL_SERVER_ERROR", "message": "服务器内部错误"}
        ).model_dump()
    )

app.include_router(api_router, prefix="/api/v1")

@app.get("/health", tags=["系统健康监控"])
async def health_check():
    return {"status": "ok", "service": "knowledge-center"}


@app.get("/ready", tags=["系统健康监控"])
def readiness_check(db: Session = Depends(get_db)):
    """Readiness probe: only succeeds when the configured database accepts queries."""
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": "DATABASE_NOT_READY", "message": "数据库尚未就绪"}
        ) from exc
    return {"status": "ready", "service": "knowledge-center", "database": "ok"}
