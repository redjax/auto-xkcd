import typing as t

from _setup import base_app_setup
from core import database, paths, request_client
from core.constants import PQ_ENGINE
from core.dependencies import db_settings, settings, telegram_settings
from domain.pipelines import ExecutePipelineReport, PipelineHandler
from domain.xkcd.comic.schemas import XKCDComic
from entrypoints import pipeline_entrypoints
from helpers import data_ctl
import hishel
import httpx
from loguru import logger as log
from modules import data_mod, xkcd_mod, msg_mod
from pipelines import execute_pipelines, pipeline_prefab

import telegram

if __name__ == "__main__":
    base_app_setup()

    CACHE_TRANSPORT: hishel.CacheTransport = request_client.get_cache_transport()

    log.info("[TEST] App start")

    # with msg_mod.TelegramBotController(
    #     bot_token=telegram_settings.bot_token, bot_name=telegram_settings.bot_username
    # ) as bot_ctl:
    #     log.debug(f"Bot: {bot_ctl.bot}")
    #     log.debug(f"Bot info URL: {bot_ctl.updates_url}")

    #     chatid: str = bot_ctl.get_chat_id()

    # bot_updates: httpx.Response = msg_mod.telegram_mod.request_bot_getupdates(
    #     telegram_bot_getupdates_url=bot_ctl.updates_url,
    #     cache_transport=CACHE_TRANSPORT,
    # )
    # if bot_updates.status_code == 200:
    #     log.debug(f"Response: {bot_updates.text}")
    # else:
    #     log.warning(
    #         f"Non-200 response: [{bot_updates.status_code}: {bot_updates.reason_phrase}]: {bot_updates.text}"
    #     )

    # chat_id: str | None = msg_mod.telegram_mod.extract_chatid_from_response(
    #     response=bot_updates
    # )
    # if chat_id is None:
    #     log.warning(
    #         f"Chat ID not found. Please send a message to the bot before running this script again."
    #     )
    #     raise ValueError(
    #         "Missing chat ID from Telegram getUpdates response. Send a message to the bot, then try running again."
    #     )

    # log.debug(f"Chat ID ({type(chat_id)}): {chat_id}")

    # chat_id_test = msg_mod.telegram_mod.get_chat_id(
    #     telegram_settings=telegram_settings,
    #     cache_transport=CACHE_TRANSPORT,
    #     serial_file=f"{paths.SERIALIZE_DIR}/telegram/chat_id.msgpack",
    # )
    # log.debug(f"Chat ID test: {chat_id_test}")

    # load_chat_id = msg_mod.telegram_mod.load_serialized_chat_id(
    #     file=f"{paths.SERIALIZE_DIR}/telegram/chat_id.msgpack"
    # )
    # log.debug(f"Loaded chat ID: {load_chat_id}")

    with data_ctl.DuckDBController(db_path=f"{paths.DATA_DIR}/app.ddb") as duckdb_ctl:
        db_tbls = duckdb_ctl.get_tables()
        duckdb_ctl.create_table(table_name="comic_nums", schema="comic_num INT")

        duckdb_ctl.load_pq(pq=f"{paths.COMICS_PQ_FILE.parent}")
