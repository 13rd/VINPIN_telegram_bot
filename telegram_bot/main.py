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
    connection_string = user_states[call.from_user.id].replace("awaiting_input_server_os:", "")
    os_type = call.data.lower().replace("os_", "")

    save_user_data(call.from_user.id, os_type+"_"+connection_string)
    bot.send_message(call.message.chat.id, text=answers.ans3)
    del user_states[call.from_user.id]
    bot.answer_callback_query(call.id)

def save_user_data(user_id, data: str):
    print(data)
    server_name, connection_string = data.split("&")[0], data.split("&")[1]
    print(server_name, connection_string)
    scripts.create_server_scripts_folder(server_name)

    database.add_server(user_id, server_name, connection_string)


@bot.message_handler(func=lambda message: message.text == "Мои кластеры")
def show_all_clusters(message):
    clusters = [c["cluster_name"] for c in database.get_clusters(message.from_user.id)]
    keyboard = create_inline_keyboard(clusters, "cluster")
    keyboard.add(telebot.types.InlineKeyboardButton("Добавить кластер", callback_data="cluster_&create_cluster"))
    bot.send_message(message.chat.id, "Выберите кластер:", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith("cluster_"))
def create_cluster_start(call):
    cluster_name = call.data.replace("cluster_", "")
    user_id = call.from_user.id
    if cluster_name == "&create_cluster":
        user_states[user_id] = "awaiting_input_cluster_name"
        print(user_states)
        bot.send_message(call.message.chat.id, "Введите название кластера")
    else:
        user_states[user_id] = "choosing_cluster: " + cluster_name
        cluster_servers = database.get_cluster_by_name(user_id, cluster_name)['server_ids']
        text_clusters_servers = "Сервера:\n" + "\n".join(cluster_servers)
        cluster_scripts = scripts.list_scripts_cluster(cluster_name)
        keyboard = create_inline_keyboard(cluster_scripts, "&cluster_script")
        keyboard.add(telebot.types.InlineKeyboardButton("Удалить этот кластер", callback_data="cluster-delete"))
        keyboard.add(telebot.types.InlineKeyboardButton("Добавить сервер", callback_data="cluster-add_server"))
        keyboard.add(telebot.types.InlineKeyboardButton("Удалить сервер", callback_data="cluster-delete_server"))
        bot.send_message(call.message.chat.id, text=text_clusters_servers, reply_markup=keyboard)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "cluster-delete")
def delete_cluster(call):
    user_id = call.from_user.id
    choosing_cluster = user_states[user_id].replace("choosing_cluster:", "").strip()
    print(choosing_cluster)

    scripts.delete_cluster_scripts_folder(choosing_cluster)
    print(database.delete_cluster(user_id, choosing_cluster))

    del user_states[user_id]
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, text="Кластер удалён")

@bot.callback_query_handler(func=lambda call: call.data == "cluster-add_server")
def add_server_to_cluster(call):
    user_id = call.from_user.id
    choosing_cluster = user_states[user_id].replace("choosing_cluster:", "").strip()
    print(choosing_cluster)
    servers = database.get_servers(user_id)

    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
    buttons = [telebot.types.InlineKeyboardButton(server["server_name"], callback_data="&add_server_"+server["server_name"]) for server in servers]
    keyboard.add(*buttons)
    bot.send_message(call.message.chat.id, text="Выберите какой сервер добавить:", reply_markup=keyboard)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("&add_server_"))
def add_server_to_cluster(call):
    server_name = call.data.replace("&add_server_", "")
    cluster_name = user_states[call.from_user.id].replace("choosing_cluster:", "").strip()

    database.add_server_to_cluster(call.from_user.id, cluster_name, server_name)
    bot.send_message(call.message.chat.id, text="Сервер добавлен")

    bot.answer_callback_query(call.id)
    del user_states[call.from_user.id]


@bot.callback_query_handler(func=lambda call: call.data == "cluster-delete_server")
def delete_server_from_cluster(call):
    user_id = call.from_user.id
    choosing_cluster = user_states[user_id].replace("choosing_cluster:", "").strip()
    print(choosing_cluster)
    servers = database.get_cluster_by_name(user_id, choosing_cluster)

    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
    buttons = [telebot.types.InlineKeyboardButton(server["server_name"], callback_data="&delete_server_"+server["server_name"]) for server in servers]
    keyboard.add(*buttons)
    bot.send_message(call.message.chat.id, text="Выберите какой сервер удалить:", reply_markup=keyboard)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("&delete_server_"))
def delete_server_from_cluster(call):
    server_name = call.data.replace("&delete_server_", "")
    cluster_name = user_states[call.from_user.id].replace("choosing_cluster:", "").strip()

    database.delete_server_from_cluster(call.from_user.id, cluster_name, server_name)
    bot.send_message(call.message.chat.id, text="Сервер удалён")

    bot.answer_callback_query(call.id)
    del user_states[call.from_user.id]

@bot.callback_query_handler(func=lambda call: call.data.startswith("&cluster_script_"))
def execute_script_for_cluster(call):
    script_name = call.data.replace("&cluster_script_", "")
    cluster_name = user_states[call.from_user.id].replace("choosing_cluster:", "").strip()
    cluster_servers = database.get_cluster_by_name(call.from_user.id, cluster_name)["server_ids"]
    servers = []
    for server in cluster_servers:
        servers.append(database.get_server_by_server_name(server))

    result = scripts.execute_script_on_cluster(servers, script_name)
    print(result)
    text = ""
    for server in cluster_servers:
        text += f"Output {server}:\n"+result[server][0]+f"\nErrors {server}: \n"+result[server][1]+"\n~~~~~"
    bot.send_message(call.message.chat.id, text=text)

    bot.answer_callback_query(call.id)
    del user_states[call.from_user.id]


@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "awaiting_input_cluster_name")
def add_cluster_by_name(message):
    user_id = message.from_user.id
    input_data = message.text.strip()
    print(input_data)

    if database.get_cluster_by_name(user_id, input_data):
        print(database.get_cluster_by_name(user_id, input_data))
        bot.send_message(message.chat.id, "Имя сервера занято")
    else:
        database.add_cluster(user_id, input_data)
        scripts.create_cluster_scripts_folder(input_data)
        bot.send_message(message.chat.id, "Кластер сохранён")
        del user_states[user_id]



# @bot.message_handler(commands=["add_server_to_cluster"])
# def add_server_to_cluster_start(message):
#     bot.reply_to(message, "Введите имя кластера:")
#     bot.register_next_step_handler(message, add_server_to_cluster_process_cluster)
#
#
# def add_server_to_cluster_process_cluster(message):
#     cluster_name = message.text
#     user_id = message.from_user.id
#
#     # Получение серверов пользователя
#     servers = get_servers(user_id)
#     if not servers:
#         bot.reply_to(message, "У вас нет добавленных серверов.")
#         return
#
#     keyboard = telebot.types.InlineKeyboardMarkup()
#     for server in servers:
#         button = telebot.types.InlineKeyboardButton(
#             server["server_name"], callback_data=f"add_to_cluster_{cluster_name}_{server['_id']}"
#         )
#         keyboard.add(button)
#
#     bot.reply_to(message, "Выберите сервер для добавления в кластер:", reply_markup=keyboard)
#
#
# @bot.callback_query_handler(func=lambda call: call.data.startswith("add_to_cluster_"))
# def add_server_to_cluster_callback(call):
#     cluster_name, server_id = call.data.split("_")[3], call.data.split("_")[4]
#     user_id = call.from_user.id
#
#     # Добавление сервера в кластер
#     add_server_to_cluster(user_id, cluster_name, server_id)
#     bot.answer_callback_query(call.id, f"Сервер добавлен в кластер '{cluster_name}'.")


def main():
    try:
        bot.infinity_polling()
    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()
