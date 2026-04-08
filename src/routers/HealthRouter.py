# Joao Vitor Coelho de Souza
from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from datetime import datetime, timezone
import psutil
from infra.database import engine
from infra.orm.models import FuncionarioModel as FuncionarioDB

router = APIRouter()


@router.get("/health", tags=["Health"], summary="Health check básico - pública")
async def health_check():
    return {
        "status":    "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service":   "comandas-api",
        "version":   "1.0.0"
    }


@router.get("/health/database", tags=["Health"], summary="Health check do banco - pública")
async def database_health():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test")).fetchone()
        if result and result[0] == 1:
            return {"status": "healthy", "database": "connected",
                    "timestamp": datetime.now(timezone.utc).isoformat()}
        raise HTTPException(status_code=503, detail="Database query failed")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {str(e)}")


@router.get("/health/database/tables", tags=["Health"], summary="Health check das tabelas - pública")
async def database_tables_health():
    try:
        checks = {}
        with engine.connect() as conn:
            try:
                count = conn.execute(text("SELECT COUNT(*) FROM tb_funcionario")).scalar()
                checks["funcionarios"] = {"status": "healthy", "count": count}
            except Exception as e:
                checks["funcionarios"] = {"status": "error", "error": str(e)}

        all_healthy = all(c["status"] == "healthy" for c in checks.values())
        return {"status": "healthy" if all_healthy else "unhealthy",
                "tables": checks, "timestamp": datetime.now(timezone.utc).isoformat()}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/health/system", tags=["Health"], summary="Health check do sistema - pública")
async def system_health():
    try:
        memory = psutil.virtual_memory()
        disk   = psutil.disk_usage(".")
        cpu    = psutil.cpu_percent(interval=1)

        disk_pct = (disk.used / disk.total) * 100

        return {
            "status": "healthy" if memory.percent < 90 and disk_pct < 90 and cpu < 80 else "warning",
            "memory": {"total": memory.total, "available": memory.available,
                       "percent": memory.percent,
                       "status": "healthy" if memory.percent < 90 else "warning"},
            "disk":   {"total": disk.total, "used": disk.used, "free": disk.free,
                       "percent": disk_pct,
                       "status": "healthy" if disk_pct < 90 else "warning"},
            "cpu":    {"percent": cpu, "count": psutil.cpu_count(),
                       "status": "healthy" if cpu < 80 else "warning"},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/health/full", tags=["Health"], summary="Health check completo - pública")
async def full_health_check():
    checks = {}
    checks["api"] = {"status": "healthy", "message": "API responding"}

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        checks["database"] = {"status": "healthy", "message": "Database connected"}
    except Exception as e:
        checks["database"] = {"status": "unhealthy", "message": str(e)}

    try:
        memory = psutil.virtual_memory()
        disk   = psutil.disk_usage(".")
        cpu    = psutil.cpu_percent(interval=1)
        disk_pct = (disk.used / disk.total) * 100
        ok = memory.percent < 90 and disk_pct < 90 and cpu < 80
        checks["system"] = {"status": "healthy" if ok else "warning",
                             "memory_percent": memory.percent,
                             "disk_percent": disk_pct, "cpu_percent": cpu}
    except Exception as e:
        checks["system"] = {"status": "error", "message": str(e)}

    overall = "healthy"
    for c in checks.values():
        if c["status"] == "unhealthy":
            overall = "unhealthy"; break
        elif c["status"] in ("warning", "error") and overall == "healthy":
            overall = c["status"]

    return {"status": overall, "checks": checks,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": "comandas-api", "version": "1.0.0"}


@router.get("/ready", tags=["Health"], summary="Readiness probe - pública")
async def readiness_check():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Not ready: {str(e)}")
    return {"status": "ready", "timestamp": datetime.now(timezone.utc).isoformat()}


@router.get("/live", tags=["Health"], summary="Liveness probe - pública")
async def liveness_check():
    return {"status": "alive", "timestamp": datetime.now(timezone.utc).isoformat()}
