from telebot import types

all_ans = "all answers "

greetings = """Здравствуйте, {user_name}"""

keyboard1 = types.ReplyKeyboardMarkup(resize_keyboard=True)
a1 = types.InlineKeyboardButton(text="Мои сервера")
a2 = types.InlineKeyboardButton(text="Добавить сервер")
keyboard1.add(a1, a2)

button_list= ["Server1","Server2","Server3","Server4"]

ans1 = """ Выберите кнопку"""
ans2 = """Введите данные в формате user:password@ip:port\nПример: admin:password123@192.168.1.1:8080 """
ans3 ="""Данные успешно сохранены!"""
ans4 ="""Неверный формат данных. Попробуйте снова."""
ans5 ="""Вы нажали: {btn}"""
keyboard2 = types.ReplyKeyboardMarkup