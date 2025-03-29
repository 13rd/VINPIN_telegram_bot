import re
import os
from dotenv import load_dotenv
import telebot
import answers
import json
import database
import scripts

load_dotenv()

TOKEN = os.getenv("TOKEN")
user_states = {}
FORMAT_REGEX = r"^[a-zA-Z0-9_\-\.\*]+&[a-zA-Z0-9_\-\.\*]+:[a-zA-Z0-9_\-\.\*]+@[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:[0-9]+$"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def welcome(message):
    # db_users = database.get_user_by_id(message.from_user.id)  # get user from db
    db_users = [int(i) for i in os.getenv("USERS").replace("[", "").replace("]", '').split(",")]  # get users from .env
    print(db_users)
    if message.from_user.id in db_users:  # изменить при подключении через бд
        bot.send_message(message.chat.id,
                         text=answers.greetings.format(user_name=message.from_user.first_name),
                         reply_markup=answers.keyboard1, parse_mode='Markdown')
    else:
        print(f"Доступ запрещен: {message.from_user.id}")
        bot.send_message(message.chat.id, text="Доступ запрещен")  # возможна реклама работы в vinpin


@bot.message_handler(func=lambda message: message.text == "Мои сервера")
def button_handler(message):
    servers = database.get_servers(message.from_user.id)
    print(servers)
    button_list = [i['server_name'] for i in servers]
    keyboard = create_inline_keyboard(button_list, 'server')
    # Отправляем сообщение с инлайн-клавиатурой
    bot.send_message(
        message.chat.id,
        answers.ans1,
        reply_markup=keyboard
    )
def create_inline_keyboard(button_list, type):
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        telebot.types.InlineKeyboardButton(text, callback_data=type+"_"+text)
        for text in button_list
    ]
    keyboard.add(*buttons)
    return keyboard

@bot.callback_query_handler(func=lambda call: call.data.startswith("server_"))
def handle_inline_button_click(call):
    user_states[call.message.from_user.id] = f"choosing_server:{call.data.replace("server_", "")}"

    scripts_btn = scripts.list_scripts(call.data.replace("server_", ""))
    keyboard = create_inline_keyboard(scripts_btn, 'script')
    bot.answer_callback_query(call.id)  # Подтверждаем нажатие
    bot.send_message(
        call.message.chat.id,
        answers.ans5.format(btn=call.data),
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("script_"))
def handle_inline_button_click(call):
    script_name = call.data.replace("script_", "")
    try:
        server_name = user_states[call.message.from_user.id]
    except Exception as e:
        print(e)
        bot.send_message(call.message.chat.id, text="Выберете сервер")
        return
    server_name = server_name.replace("choosing_server:", "")
    connection_string = database.get_server_by_server_name(server_name)['connection_string']

    output, errors = scripts.copy_and_execute_script(server_name, script_name, connection_string)
    del user_states[call.message.from_user.id]
    bot.answer_callback_query(call.id)  # Подтверждаем нажатие
    bot.send_message(
        call.message.chat.id,
        text= output + "\n" + errors
    )


@bot.message_handler(func=lambda message: message.text == "Добавить сервер")
def button_handler(message):
    user_id = message.from_user.id
    user_states[user_id] = "awaiting_input_server"
    print(user_states[user_id])
    bot.send_message(message.chat.id, answers.ans2)

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "awaiting_input_server")
def message_handler(message):
    user_id = message.from_user.id
    input_data = message.text.strip()

    # Проверяем формат ввода
    if re.match(FORMAT_REGEX, input_data):  # TODO: сделать проверку имени сервера
        bot.send_message(message.chat.id, answers.ans3)
        # Сохраняем данные (например, в базу данных или файл)
        save_user_data(user_id, input_data)
        del user_states[user_id]  # Сбрасываем состояние
    elif input_data.split("&")[0]:
        ...
    elif input_data == "exit":
        bot.send_message(message.chat.id, "Ввод завершён")
        del user_states[user_id]
    else:
        bot.send_message(message.chat.id, answers.ans4)


def save_user_data(user_id, data: str):
    server_name, connection_string = data.split("&")[0], data.split("&")[1]
    scripts.create_server_scripts_folder(server_name)

    database.add_server(user_id, server_name, connection_string, scripts.list_scripts(server_name))


def main():
    try:
        bot.infinity_polling()
    except Exception as e:
        print(e)


if __name__ == '__main__':
    while True:
        main()
