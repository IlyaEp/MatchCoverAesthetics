import telebot
import spotipy
from typing import List, Dict
from src.model.api import MatchCoverAPI
import base64
import requests
import io
from PIL import Image
import credentials as cred


class Answer:
    """
    This class represents user answer.
    """

    def __init__(self, file_path):
        self.file_path = file_path
        self.use_playlists = True


TOKEN = cred.TELEGRAM_TOKEN
BOT = telebot.TeleBot(TOKEN)
PLAYLIST_MODEL = MatchCoverAPI("facebook/deit-tiny-distilled-patch16-224")
ALBUM_MODEL = MatchCoverAPI("facebook/deit-tiny-distilled-patch16-224")
USERS: Dict[int, Answer] = {}


def get_playlist_link(track_ids: List[str], image_url: str) -> str:
    """
    This function generates a spotify playlist and returns a link to it
    :param track_ids: ID tracks in spotify
    :param image_url: link to picture for download
    :return: link to playlist
    """

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
    """
    This function is responsible for getting a link to the user's picture.
    """
    if message.photo is None:
        msg = BOT.reply_to(message, "Мне нужна картинка 🥺")
        BOT.register_next_step_handler(msg, get_picture)
        return
    photo = BOT.get_file(message.photo[-1].file_id)
    USERS[message.chat.id] = Answer(photo.file_path)
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add("Альбом", "Плейлист")
    msg = BOT.reply_to(
        message, "Отлично! А откуда мне смотреть картинки, из альбомов или из плейлистов?", reply_markup=markup
    )
    BOT.register_next_step_handler(msg, get_type_model)


def get_type_model(message):
    """
    This function is responsible for model selection (album/playlist).
    """
    if message.text != "Альбом" and message.text != "Плейлист":
        markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add("Альбом", "Плейлист")
        msg = BOT.reply_to(
            message,
            "Я не знаю такое🙁\nОткуда мне смотреть картинки, из альбомов или из плейлистов?",
            reply_markup=markup,
        )
        BOT.register_next_step_handler(msg, get_type_model)
        return
    if message.text == "Альбом":
        USERS[message.chat.id].use_playlists = False
    markup = telebot.types.ReplyKeyboardRemove(selective=True)
    msg = BOT.reply_to(message, "Отлично! Теперь скажи, сколько песен ты хочешь?", reply_markup=markup)
    BOT.register_next_step_handler(msg, get_number_of_songs)


@BOT.message_handler(commands=["start"])
def start(message):
    """
    This function handles the start command.
    """
    msg = BOT.reply_to(
        message, "Привет ✨\nОтправь картинку, а я сделаю для тебя плейлист с подходящей по настроению музыкой 🧙"
    )
    BOT.register_next_step_handler(msg, get_picture)


def get_number_of_songs(message):
    """
    This function remembers the number of musical compositions that the user requires and calls the model to get the result.
    """
    if str(message.text).isdigit() and 0 < int(message.text) <= 100:
        BOT.send_message(message.from_user.id, "Дай мне немного времени...")

        file_url = f"https://api.telegram.org/file/bot{TOKEN}/{USERS[message.chat.id].file_path}"
        if USERS[message.chat.id].use_playlists:
            songs = get_playlist_link(PLAYLIST_MODEL.predict(file_url, int(message.text)), file_url)
        else:
            songs = get_playlist_link(ALBUM_MODEL.predict(file_url, int(message.text)), file_url)

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
    PLAYLIST_MODEL.load_from_disk("../data/playlists.pt")
    ALBUM_MODEL.load_from_disk("../data/albums.pt")
    print("I'm ready")
    BOT.set_my_commands(
        [
            telebot.types.BotCommand("/start", "Для знакомства"),
        ]
    )
    BOT.polling(none_stop=True, interval=0)
