import telebot

BOT = telebot.TeleBot("TOKEN")


def predict(picture):
    pass


@BOT.message_handler(content_types=['photo'])
def get_picture(message):
    BOT.send_message(message.from_user.id, "Сейчас подумаю")
    predict(message.photo)
    BOT.send_message(message.from_user.id, "Вот что получилось:")
    file_id = message.photo[-1].file_id
    BOT.send_photo(message.from_user.id, file_id)


@BOT.message_handler(content_types=['text'])
def start(message):
    if message.text == "/start":
        BOT.send_message(message.from_user.id, "Привет!\nОтправь картинку, а я подберу для тебя музыку по настроению "
                                               "картиники")


if __name__ == '__main__':
    BOT.polling(none_stop=True, interval=0)
