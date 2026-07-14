import sys
import json
import logging
from loguru import logger
from app.core.config import get_settings

settings = get_settings()


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        logger.opt(depth=6, exception=record.exc_info).log(level, record.getMessage())


def setup_logging():
    logger.remove()

    log_format = settings.LOG_FORMAT

    if settings.LOG_JSON_FORMAT:
        logger.add(
            sys.stdout,
            format="{message}",
            level=settings.LOG_LEVEL,
            serialize=True,
        )
    else:
        logger.add(
            sys.stdout,
            format=log_format,
            level=settings.LOG_LEVEL,
            colorize=not settings.IS_PRODUCTION,
        )

    logger.add(
        "logs/app_{time:YYYY-MM-DD}.log",
        format=log_format,
        level="DEBUG",
        rotation="50 MB",
        retention="30 days",
        compression="gz",
        backtrace=True,
        diagnose=not settings.IS_PRODUCTION,
    )

    logger.add(
        "logs/errors_{time:YYYY-MM-DD}.log",
        format=log_format,
        level="ERROR",
        rotation="50 MB",
        retention="60 days",
        compression="gz",
        backtrace=True,
        diagnose=not settings.IS_PRODUCTION,
    )

    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    for lib_logger in ("uvicorn", "uvicorn.access", "fastapi", "sqlalchemy.engine"):
        logging.getLogger(lib_logger).handlers = [InterceptHandler()]
        logging.getLogger(lib_logger).propagate = False

    logger.info(f"Logging configured - level={settings.LOG_LEVEL}, env={settings.APP_ENV}")
    return logger
