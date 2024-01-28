"""
Module for logging conventions
"""

import logging
from rich.logging import RichHandler


format = "%(module)s %(levelname)s: %(message)s"
logging.basicConfig(level=logging.INFO, format=format, handlers=[RichHandler()])


def getLogger(name: str) -> logging.Logger:
    return logging.getLogger(name)
