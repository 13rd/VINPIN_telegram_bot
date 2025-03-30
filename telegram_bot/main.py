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
    db_users = database.get_user_by_id(message.from_user.id)  # get user from db
    # db_users = [int(i) for i in os.getenv("USERS").replace("[", "").replace("]", '').split(",")]  # get users from .env
    if db_users:  # изменить при подключении через бд
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
    if not servers:
        bot.send_message(
            message.chat.id,
            "У вас нет сохранённых серверов"
        )
        return
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
    keyboard.add(telebot.types.InlineKeyboardButton("Удалить этот сервер", callback_data="script_delete_server"))
    bot.answer_callback_query(call.id)  # Подтверждаем нажатие
    bot.send_message(
        call.message.chat.id,
        answers.ans5.format(btn=call.data),
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("script_"))
def handle_inline_button_click(call):
    script_name = call.data.replace("script_", "")
    if script_name == "delete_server":
        result = database.delete_server(server_name = user_states[call.message.from_user.id].replace("choosing_server:", ""))
        if result:
            bot.send_message(call.message.chat.id, text="Сервер удалён")
        else:
            bot.send_message(call.message.chat.id, text="Ошибка удаления")
        del user_states[call.message.from_user.id]
        bot.answer_callback_query(call.id)
        return
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
    user_states[user_id] = "awaiting_input_server_string"
    print(user_states[user_id])
    bot.send_message(message.chat.id, answers.ans2)

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "awaiting_input_server_string")
def message_handler(message):
    user_id = message.from_user.id
    input_data = message.text.strip()

    if not scripts.folder_is_available(input_data.split("&")[0]):
        bot.send_message(message.chat.id, "Имя сервера занято")
    elif re.match(FORMAT_REGEX, input_data):
        # Сохраняем данные (например, в базу данных или файл)
        # save_user_data(user_id, input_data)
        user_states[user_id] = "awaiting_input_server_os:"+input_data
        keyboard = create_inline_keyboard(["Linux", "Windows"], 'os')
        bot.send_message(message.chat.id, text="Выберите ОС", reply_markup=keyboard)
    elif input_data == "exit":
        bot.send_message(message.chat.id, "Ввод завершён")
        del user_states[user_id]
    else:
        bot.send_message(message.chat.id, answers.ans4)

@bot.callback_query_handler(func=lambda call: call.data.startswith("os_") )
def offering_server_os(call):
    connection_string = user_states[call.from_user.id].split(":")[1]
    os_type = call.data.lower().replace("os_", "")

    save_user_data(call.from_user.id, os_type+"_"+connection_string)
    bot.send_message(call.message.chat.id, text=answers.ans3)
    del user_states[call.from_user.id]
    bot.answer_callback_query(call.id)

def save_user_data(user_id, data: str):
    server_name, connection_string = data.split("&")[0], data.split("&")[1]
    scripts.create_server_scripts_folder(server_name)

    database.add_server(user_id, server_name, connection_string)


def main():
    try:
        bot.infinity_polling()
    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()
