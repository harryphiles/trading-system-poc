import logging.config


class Logger:
    def __init__(self, name: str, log_config: dict, file_name: str | None) -> None:
        self.name = name
        self.log_config = log_config.copy()
        if file_name:
            self.log_config["handlers"]["file"]["filename"] = file_name
        logging.config.dictConfig(config=log_config)
        self.logger = logging.getLogger(name)


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {},
    "formatters": {
        "simple": {
            "format": "%(asctime)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    },
    "handlers": {
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "simple",
            "encoding": "utf-8",
            "filename": "logs/my_app.log",
            "maxBytes": 1_000_000_000_000_000,
            "backupCount": 5,
        }
    },
    "loggers": {
        "root": {
            "level": "DEBUG",
            "handlers": [
                "file",
            ],
        }
    },
}


if __name__ == "__main__":
    # log_file_name = os.path.join(
    #     Config.WORKING_DIRECTORY,
    #     "logs",
    #     f"{"_".join(Config.APP_NAME)}.log",
    # )
    log_file_name = "test.log"
    logger = Logger(__name__, LOGGING_CONFIG, log_file_name).logger
    logger.info("")