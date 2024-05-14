import logging

logger = logging.getLogger()

def setupLogger():
    ## Configure Logger
    handler = logging.StreamHandler()
    #formatter = logging.Formatter('%(message)s')
    handler.setFormatter(CustomFormatter())
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)


class CustomFormatter(logging.Formatter):

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    blue = "\x1b[34;20m"
    green = "\x1b[32;20m"
    reset = "\x1b[0m"
    format = "%(message)s (%(filename)s:%(lineno)d)"
    formatInterruption = "- %(message)s"

    FORMATS = {
        logging.DEBUG: blue + formatInterruption + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + formatInterruption + reset,
        logging.ERROR: green + formatInterruption + reset,
        logging.CRITICAL: bold_red + formatInterruption + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


# create console handler with a higher log level



