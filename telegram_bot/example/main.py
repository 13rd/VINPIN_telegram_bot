import re

import telebot
import answers
import random
import config
import json


TOKEN = config.TOKEN
user_states = {}
FORMAT_REGEX = r"^[a-zA-Z0-9_\-]+:[a-zA-Z0-9_\-]+@[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:[0-9]+$"

bot = telebot.TeleBot(TOKEN)



@bot.message_handler(commands=['start'])
def welcome(message):
    with open("users.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    users = data.get("user_ids", [])
    new_user_id = message.chat.id
    if new_user_id not in users:
        print(f"Доступ запрещен: {new_user_id}")
        bot.send_message(message.chat.id, text="Доступ запрещен")
    else:
        bot.send_message(message.chat.id,
                     text=answers.greetings.format(user_name=message.from_user.first_name),
                     reply_markup=answers.keyboard1, parse_mode='Markdown')

#
# @bot.message_handler(content_types=['text'])
# def answer(message):
#     if message.text == "Мои сервера":
#         bot.send_message(message.chat.id, text=answers.ans1)

@bot.message_handler(func=lambda message: message.text == "Мои сервера")
def button_handler(message):
    bot.send_message(message.chat.id, text=answers.ans1)

@bot.message_handler(func=lambda message: message.text == "Добавить сервер")
def button_handler(message):
    user_id = message.from_user.id
    user_states[user_id] = "awaiting_input"
    print(user_states[user_id])
    bot.send_message(message.chat.id, answers.ans2)

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "awaiting_input")
def message_handler(message):
    user_id = message.from_user.id
    input_data = message.text.strip()

    # Проверяем формат ввода
    if re.match(FORMAT_REGEX, input_data):
        bot.send_message(message.chat.id, answers.ans3)
        # Сохраняем данные (например, в базу данных или файл)
        save_user_data(user_id, input_data)
        del user_states[user_id]  # Сбрасываем состояние
    else:
        bot.send_message(message.chat.id, answers.ans4)

def save_user_data(user_id, data):
    print(f"User {user_id} entered data: {data}")


def main():
    try:
        bot.infinity_polling()
    except Exception as e:
        print(e)


if __name__ == '__main__':
    while True:
        main()
