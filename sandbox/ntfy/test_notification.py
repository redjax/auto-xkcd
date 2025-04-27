from notifications import ntfy
from domain import ntfy as ntfy_domain
from settings import NTFY_SETTINGS, LOGGING_SETTINGS
import setup

from loguru import logger as log

if __name__ == "__main__":
    setup.setup_loguru_logging(
        log_level=LOGGING_SETTINGS.get("LOG_LEVEL", "INFO"), colorize=True
    )
    log.debug("DEBUG logging enabled")

    log.debug(f"ntfy settings: {NTFY_SETTINGS.as_dict()}")
    ntfy_config = ntfy_domain.NtfyConfig(
        server=NTFY_SETTINGS.get("NTFY_SERVER"),
        topic=NTFY_SETTINGS.get("NTFY_TOPIC"),
        token=NTFY_SETTINGS.get("NTFY_TOKEN"),
    )

    log.info(f"Sending test notification to {ntfy_config.url}")
    try:
        ntfy.send_message(
            topic_url=ntfy_config.url,
            message="Test message",
            title="auto-xkcd Test",
            headers=ntfy_config.auth_headers,
        )
    except Exception as exc:
        log.error(f"Error sending notification to ntfy. Details: {exc}")
