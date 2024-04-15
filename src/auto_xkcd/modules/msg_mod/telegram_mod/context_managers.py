import typing as t
from pathlib import Path
from contextlib import contextmanager, AbstractContextManager

from core import paths
from .methods import (
    get_chat_token,
    request_chat_id,
    save_chatid_to_file,
    extract_chatid_from_response,
)

from loguru import logger as log
import telegram


class TelegramBotController(AbstractContextManager):
    def __init__(self, bot_token: str = None, bot_name: str = None):
        self.token = bot_token
        self.name = bot_name

        ## Initialize empty slot for bot
        self.bot: telegram.Bot | None = None

    def __enter__(self):
        _bot: telegram.Bot = telegram.Bot(token=self.token)

        self.bot = _bot

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # if self.bot is not None:
        #     self.bot.close()

        if exc_type:
            log.error(f"[{exc_type}] {exc_value}")
            log.trace(traceback)

            raise

    @property
    def updates_url(self) -> str:
        _updates_url: str = f"https://api.telegram.org/bot{self.token}/getUpdates"

        return _updates_url

    def get_chat_id(
        self,
        save_chat_id: bool = True,
        chat_id_file: t.Union[str, Path] = paths.TELEGRAM_CHAT_ID_FILE,
        overwrite_if_exists: bool = False,
    ) -> str:
        if save_chat_id:
            if chat_id_file is None:
                chat_id_file: Path = paths.TELEGRAM_CHAT_ID_FILE
            else:
                chat_id_file: Path = Path(f"{chat_id_file}")

        try:
            chat_id: str = get_chat_token(
                bot_token=self.token,
                save_to_file=save_chat_id,
                output_file=chat_id_file,
                overwrite=overwrite_if_exists,
            )
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception saving chat ID to file. Details: {exc}"
            )
            log.error(msg)
            log.warning("chat ID not saved to file")

        return chat_id
