# from .methods_old import (
#     get_telegram_bot,
#     telegram_bot_updates_url,
#     request_bot_getupdates,
#     extract_chatid_from_response,
#     get_chat_id,
#     save_serialized_chat_id,
#     load_serialized_chat_id,
#     send_photo_msg,
# )
from .methods import (
    request_chat_id,
    save_chatid_to_file,
    extract_chatid_from_response,
    get_chat_token,
)
from .context_managers import TelegramBotController
