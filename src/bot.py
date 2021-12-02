import telebot
import spotipy
from typing import List, Dict
from src.model.api import MatchCoverAPI
import base64
import requests
import io
from PIL import Image
import credentials as cred


TOKEN = cred.TELEGRAM_TOKEN
use_playlists = True
BOT = telebot.TeleBot(TOKEN)
pl_model = MatchCoverAPI("facebook/deit-tiny-distilled-patch16-224")
alb_model = MatchCoverAPI("facebook/deit-tiny-distilled-patch16-224")
USERS: Dict[int, str] = {}


def get_playlist_link(track_ids: List[str], image_url: str) -> str:

    scope = "playlist-modify-public ugc-image-upload"
    bot_id = cred.SPOTIFY_BOT_ID
    client_id = cred.SPOTIFY_CLIENT_ID
    client_secret = cred.SPOTIFY_CLIENT_SECRET

    auth_manager = spotipy.SpotifyOAuth(
        client_id=client_id, client_secret=client_secret, scope=scope, redirect_uri="http://localhost:8888/callback/"
    )

    sp = spotipy.Spotify(auth_manager=auth_manager)

    playlist_name = "Playlist for you"
    playlist = sp.user_playlist_create(bot_id, public=True, name=playlist_name)
    playlist_id = playlist["id"]
    sp.playlist_add_items(playlist_id, track_ids)

    # prepare cover
    img = Image.open(requests.get(image_url, stream=True).raw)
    img.thumbnail((256, 256))
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="JPEG")
    img_byte_arr = img_byte_arr.getvalue()
    coded_img = base64.b64encode(img_byte_arr)

    sp.playlist_upload_cover_image(playlist_id, coded_img)
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
    if str(message.text).isdigit() and 0 < int(message.text) <= 100:
        BOT.send_message(message.from_user.id, "Дай мне немного времени...")

        file_url = f"https://api.telegram.org/file/bot{TOKEN}/{USERS[message.chat.id]}"
        if use_playlists:
            songs = get_playlist_link(pl_model.predict(file_url, int(message.text)), file_url)
        else:
            songs = get_playlist_link(alb_model.predict(file_url, int(message.text)), file_url)

        BOT.reply_to(message, f"Готово! Вот что получилось: {songs}")
        msg = BOT.send_message(
            message.from_user.id,
            "Надеюсь, тебе понравится 🥰\nЕсли хочешь еще один плейлист," " пришли мне новую картинку",
        )
        BOT.register_next_step_handler(msg, get_picture)
    else:
        msg = BOT.reply_to(
            message,
            "Что-то пошло не так 😔 Cколько песен ты хочешь? (я жду от тебя некоторое число от 0 до 100)",
        )
        BOT.register_next_step_handler(msg, get_number_of_songs)


if __name__ == "__main__":
    pl_model.load_from_disk("../data/playlists.pt")
    alb_model.load_from_disk("../data/albums.pt")
    print("I'm ready")
    BOT.set_my_commands(
        [
            telebot.types.BotCommand("/start", "Для знакомства"),
        ]
    )
    BOT.polling(none_stop=True, interval=0)
