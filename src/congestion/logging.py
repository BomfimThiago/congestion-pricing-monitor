"""Logging configuration.

Use loguru everywhere instead of print(). Logs are how you debug
pipelines that ran at 3am while you were asleep.
"""
import sys
from loguru import logger

def configure_logging(level: str = "INFO") -> None:
    logger.remove()
    logger.add(
        sys.stderr,
        level=level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan> | "
               "<level>{message}</level>",
    )


__all__ = ["logger", "configure_logging"]