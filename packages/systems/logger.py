from .config import load_config_logger

import sys
from loguru import logger
from rich.traceback import install

install(show_locals=True)

logger.remove()

config_logger = load_config_logger()["config"]

# Console output
logger.add(
    sys.stdout,
    level="INFO",
    colorize=True,
    format="""
        <green>{time:HH:mm:ss}</green> | 
        <level>{level: <8}</level> | 
        <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - 
        <level>{message}</level>
    """
)

# File latest.log
logger.add(
    f"{config_logger["log-dir"]}/latest.log",
    level="INFO",
    rotation=config_logger["latest"]["rotation"],
    retention=config_logger["latest"]["retention"],
    encoding=config_logger["encoding"]
)

# File error.log
logger.add(
    f"{config_logger["log-dir"]}/error.log",
    level="ERROR",
    rotation=config_logger["error"]["rotation"],
    retention=config_logger["error"]["retention"],
    encoding=config_logger["encoding"]
)

# File debug
logger.add(
    f"{config_logger["log-dir"]}/debug.log",
    level="DEBUG",
    rotation=config_logger["debug"]["rotation"],
    retention=config_logger["debug"]["retention"],
    encoding=config_logger["encoding"]
)

