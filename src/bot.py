import telebot
from src.model.api import MatchCoverAPI


TOKEN = "TOKEN"
BOT = telebot.TeleBot(TOKEN)
model = MatchCoverAPI("facebook/deit-tiny-distilled-patch16-224")


def predict(picture):
    pass


@BOT.message_handler(content_types=['photo'])
def get_picture(message):
    BOT.send_message(message.from_user.id, "Сейчас подумаю")
    predict(message.photo)
    BOT.send_message(message.from_user.id, "Вот что получилось:")
    file_path = BOT.get_file(message.photo[-1].file_id).file_path
    file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"
    file_id = message.photo[-1].file_id
    BOT.send_photo(message.from_user.id, file_id)


@BOT.message_handler(content_types=['text'])
def start(message):
    if message.text == "/start":
        BOT.send_message(message.from_user.id, "Привет!\nОтправь картинку, а я подберу для тебя музыку по настроению "
                                               "картиники")


if __name__ == '__main__':
    BOT.polling(none_stop=True, interval=0)
