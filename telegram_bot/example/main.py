import telebot
import answers
import random
import config

users = []

TOKEN = config.TOKEN

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def welcome(message):
    if message.chat.id not in users:
        users.append(message.chat.id)
    bot.send_message(message.chat.id,
                     text=answers.greetings.format(username=message.from_user.first_name),
                     reply_markup=answers.keyboard1, parse_mode='Markdown')


@bot.message_handler(content_types=['text'])
def answer(message):
    if message.text == "О чём «МАНЕ»?":
        bot.send_message(message.chat.id, text=answers.ans1)
    if message.text == "Получить промокод":
        bot.send_message(message.chat.id, text=answers.ans2)
    if message.text == "Купить билет":
        bot.send_message(message.chat.id, text=answers.ans3)
    if message.text == "Отправить рассылку":
        send_messages()
    # else:
    #     bot.send_message(message.chat.id,
    #                      text="Выберите вариант из предложенных")


# @bot.message_handler(commands=['send'])
def send_messages():
    print(users)
    for user in users:
        bot.send_message(user, text="Текст будущей рассылки", parse_mode='Markdown')


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "ecology":
        bot.send_message(call.message.chat.id, answers.ecology, disable_web_page_preview=True)
    if call.data == "creative":
        bot.send_message(call.message.chat.id, answers.creative, disable_web_page_preview=True)
    if call.data == "medicine":
        bot.send_message(call.message.chat.id, answers.medicine, disable_web_page_preview=True)
    if call.data == "digital":
        bot.send_message(call.message.chat.id, answers.digital, disable_web_page_preview=True)
    if call.data == "space":
        bot.send_message(call.message.chat.id, answers.space, disable_web_page_preview=True)
    if call.data == "humanitarian":
        bot.send_message(call.message.chat.id, answers.humanitarian, disable_web_page_preview=True)
    if call.data == "urban":
        bot.send_message(call.message.chat.id, answers.urban, disable_web_page_preview=True)
    if call.data == "energy":
        bot.send_message(call.message.chat.id, answers.energy, disable_web_page_preview=True)


@bot.message_handler(content_types=['text'])
def other(message):
    bot.send_message(message.chat.id, text="Не могу ответить на данные вопрос. Если мои ответы не удовлетворили ваше "
                                           "любопытство обратитесь по номеру 8 (800) 300-61-22 и задайте свой вопрос")


def main():
    try:
        bot.infinity_polling()
    except Exception as e:
        print(e)


if __name__ == '__main__':
    while True:
        main()
