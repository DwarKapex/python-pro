import logging


def configure_logging():
    logging.basicConfig(
        format="[[%(asctime)s] %(levelname).1s %(message)s] %(module)s:%(lineno)d %(levelname)s - %(message)s",
        level=logging.DEBUG,
        datefmt="%Y.%m.%d %H:%M:%S",
    )
