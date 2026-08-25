import logging

log = logging.getLogger(__name__)


def cleanup(path):
    try:
        path.unlink()
    except FileNotFoundError:
        log.info("cleanup.skip", extra={"path": str(path)})
