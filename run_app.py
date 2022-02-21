#!/usr/bin/env python3

import os
from logging.config import dictConfig

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"}
    },
    "handlers": {"default": {"level": "DEBUG", "formatter": "standard"}},
    "loggers": {
        "": {"handlers": ["default"], "level": "DEBUG", "propagate": True},
        "urllib3": {"handlers": ["default"], "level": "WARN", "propagate": False},
        "requests": {"handlers": ["default"], "level": "WARN", "propagate": False},
    },
}

if os.path.isdir("/var/log/deskformer/"):
    LOGGING["handlers"]["default"].update(
        {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "when": "midnight",
            "backupCount": 7,
            "filename": "/var/log/deskformer/deskformer_ui.log",
        }
    )
else:
    LOGGING["handlers"]["default"].update({"class": "logging.StreamHandler"})

dictConfig(LOGGING)


if __name__ == '__main__':
    from deskformer_ui.app import DeskFormerApp  # noqa isort:skip
    DeskFormerApp().run()