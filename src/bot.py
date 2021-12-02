import telebot
import spotipy
from typing import List, Dict
from src.model.api import MatchCoverAPI


TOKEN = "TOKEN"
use_playlists = True
BOT = telebot.TeleBot(TOKEN)
MODEL = MatchCoverAPI("facebook/deit-tiny-distilled-patch16-224")
USERS: Dict[int, str] = {}


def get_playlist_link(ids_songs: List[str]) -> str:

    scope = "playlist-modify-public"
    bot_id = ""
    client_id = ""
    client_secret = ""

    auth_manager = spotipy.SpotifyOAuth(
        client_id=client_id, client_secret=client_secret, scope=scope, redirect_uri="http://localhost:8888/callback/"
    )

    sp = spotipy.Spotify(auth_manager=auth_manager)

    playlist_name = "Playlist for you"
    playlist = sp.user_playlist_create(bot_id, public=True, name=playlist_name)
    playlist_id = playlist["id"]
    sp.playlist_add_items(playlist_id, ids_songs)
    return playlist["external_urls"]["spotify"]


def get_picture(message):
    if message.photo is None:
        msg = BOT.reply_to(message, "Сначала мне нужна картинка 🥺")
        BOT.register_next_step_handler(msg, get_picture)
        return
    photo = BOT.get_file(message.photo[-1].file_id)
    USERS[message.chat.id] = photo.file_path
    msg = BOT.reply_to(message, "Отлично! Теперь скажи, сколько песен ты хочешь?")
    BOT.register_next_step_handler(msg, get_number_of_songs)


@BOT.message_handler(commands=["start"])
def start(message):
    msg = BOT.reply_to(
        message, "Привет ✨\nОтправь картинку, а я сделаю для тебя плейлист с подходящей по настроению " "музыкой 🧙"
    )
    BOT.register_next_step_handler(msg, get_picture)


def get_number_of_songs(message):
    if str(message.text).isdigit() and int(message.text) > 0:
        BOT.send_message(message.from_user.id, "Дай мне немного времени...")

        file_url = f"https://api.telegram.org/file/bot{TOKEN}/{USERS[message.chat.id]}"

        songs = get_playlist_link(MODEL.predict(file_url, int(message.text)))

        BOT.reply_to(message, f"Готово! Вот что получилось: {songs}")
        msg = BOT.send_message(
            message.from_user.id,
            "Надеюсь, тебе понравится 🥰\nЕсли хочешь еще один плейлист," " пришли мне новую картинку",
        )
        BOT.register_next_step_handler(msg, get_picture)
    else:
        msg = BOT.reply_to(
            message,
            "Что-то пошло не так 😔 Cколько песен ты хочешь? (я жду от тебя некоторое " "разумное натуральное число)",
        )
        BOT.register_next_step_handler(msg, get_number_of_songs)


if __name__ == "__main__":
    MODEL.load_from_disk(f"../data/{'albums' if not use_playlists else 'playlists'}/", use_playlists)
    print("I'm ready")
    BOT.set_my_commands(
        [
            telebot.types.BotCommand("/start", "Для знакомства"),
        ]
    )
    BOT.polling(none_stop=True, interval=0)
