import time
from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from sqlalchemy import text
from app.core.database import async_session_factory, get_engine
from app.core.cache import get_redis
from app.core.celery_app import celery_app
from app.core.config import get_settings
from app.schemas.automation import HealthResponse

router = APIRouter(tags=["Health"])
_start_time = time.time()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    settings = get_settings()
    db_status = "ok"
    redis_status = "ok"
    celery_status = "ok"

    try:
        engine = get_engine()
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {str(e)}"

    try:
        r = await get_redis()
        await r.ping()
    except Exception as e:
        redis_status = f"error: {str(e)}"

    try:
        workers = celery_app.control.ping(timeout=3)
        if not workers:
            celery_status = "no_workers"
    except Exception:
        celery_status = "unavailable"

    overall = all(s == "ok" for s in [db_status, redis_status])
    return HealthResponse(
        status="healthy" if overall else "degraded",
        version=settings.APP_VERSION,
        database=db_status,
        redis=redis_status,
        celery=celery_status,
        uptime_seconds=round(time.time() - _start_time, 2),
    )


@router.get("/health/ready")
async def readiness_probe():
    try:
        engine = get_engine()
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception:
        from fastapi.responses import JSONResponse

        return JSONResponse(status_code=503, content={"status": "not_ready"})


@router.get("/health/live")
async def liveness_probe():
    return {"status": "alive"}


@router.get("/metrics")
async def prometheus_metrics():
    from app.core.cache import get_redis
    from sqlalchemy import text
    from app.core.database import get_engine

    metrics_lines = [
        "# HELP marketing_platform_info Marketing Automation Platform info",
        "# TYPE marketing_platform_info gauge",
        f'marketing_platform_info{{version="{get_settings().APP_VERSION}",env="{get_settings().APP_ENV}"}} 1',
    ]

    try:
        engine = get_engine()
        async with engine.connect() as session:
            result = await session.execute(text("SELECT COUNT(*) FROM campaigns"))
            total = result.scalar() or 0
            metrics_lines.append("# HELP marketing_campaigns_total Total number of campaigns")
            metrics_lines.append("# TYPE marketing_campaigns_total gauge")
            metrics_lines.append(f"marketing_campaigns_total {total}")

            result = await session.execute(
                text("SELECT COALESCE(SUM(spend), 0) FROM campaign_metrics WHERE date = CURRENT_DATE")
            )
            today_spend = float(result.scalar() or 0)
            metrics_lines.append("# HELP marketing_spend_today Today's total spend")
            metrics_lines.append("# TYPE marketing_spend_today gauge")
            metrics_lines.append(f"marketing_spend_today {today_spend}")

            result = await session.execute(text("SELECT COUNT(*) FROM contacts"))
            contacts = result.scalar() or 0
            metrics_lines.append("# HELP marketing_contacts_total Total contacts")
            metrics_lines.append("# TYPE marketing_contacts_total gauge")
            metrics_lines.append(f"marketing_contacts_total {contacts}")

            result = await session.execute(text("SELECT COUNT(*) FROM automation_jobs WHERE status = 'failed'"))
            failed = result.scalar() or 0
            metrics_lines.append("# HELP marketing_failed_jobs_total Failed automation jobs")
            metrics_lines.append("# TYPE marketing_failed_jobs_total gauge")
            metrics_lines.append(f"marketing_failed_jobs_total {failed}")
    except Exception:
        pass

    try:
        r = await get_redis()
        info = await r.info()
        metrics_lines.append("# HELP marketing_redis_memory Redis memory usage")
        metrics_lines.append("# TYPE marketing_redis_memory gauge")
        metrics_lines.append(f"marketing_redis_memory {info.get('used_memory', 0)}")
    except Exception:
        pass

    return PlainTextResponse("\n".join(metrics_lines))
