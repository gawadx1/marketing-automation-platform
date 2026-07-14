#!/usr/bin/env python3
"""Production entrypoint for the APScheduler service with graceful shutdown."""

import asyncio
import signal
import sys
from loguru import logger
from app.core.logging import setup_logging
from app.scheduler.scheduler import start_scheduler, stop_scheduler


def main():
    setup_logging()
    logger.info("Starting APScheduler service")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    start_scheduler()

    shutdown_event = asyncio.Event()

    def signal_handler(sig, frame):
        logger.info(f"Received signal {sig}, shutting down...")
        shutdown_event.set()

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    try:
        loop.run_until_complete(shutdown_event.wait())
    except KeyboardInterrupt:
        pass
    finally:
        logger.info("Shutting down APScheduler")
        stop_scheduler()
        loop.close()
        logger.info("APScheduler service stopped")
        sys.exit(0)


if __name__ == "__main__":
    main()
