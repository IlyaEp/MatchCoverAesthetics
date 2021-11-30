import telebot
import jsonlines
from pathlib import Path
from typing import List
from src.model.api import MatchCoverAPI


TOKEN = "TOKEN"
BOT = telebot.TeleBot(TOKEN)
MODEL = MatchCoverAPI("facebook/deit-tiny-distilled-patch16-224")
with jsonlines.open(Path("../data/songs.jsonl")) as reader:
    train = list(reader)
    MODEL.fit(train, "../data/2k_songs_album_index")

print("I'm ready")


def get_playlist_link(ids_songs: List[str]) -> str:
    return "\n".join(song for song in ids_songs)


@BOT.message_handler(content_types=['photo'])
def get_picture(message):
    BOT.send_message(message.from_user.id, "Сейчас подумаю")

    photo = BOT.get_file(message.photo[-1].file_id)
    file_url = f"https://api.telegram.org/file/bot{TOKEN}/{photo.file_path}"
    songs = get_playlist_link(MODEL.predict(file_url, 3))

    BOT.send_message(message.from_user.id, "Вот что получилось:")
    BOT.send_message(message.from_user.id, songs)


@BOT.message_handler(content_types=['text'])
def start(message):
    if message.text == "/start":
        BOT.send_message(message.from_user.id, "Привет!\nОтправь картинку, а я подберу для тебя музыку по настроению "
                                               "картиники")


if __name__ == '__main__':
    BOT.polling(none_stop=True, interval=0)
