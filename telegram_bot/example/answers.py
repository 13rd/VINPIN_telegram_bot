from telebot import types

all_ans = "Выберете ваш вопрос:\n" \
          "#1 Что такое «Город открытий»?\n" \
          "#2 Какие маршруты есть в «Городе открытий»?\n" \
          "#3 Как отправиться в путешествие?\n" \
          "#4 Кто может отправиться в путешествие?\n" \
          "#5 Как купить тур?"

greetings = """Здравствуйте, {user_name}"""

keyboard1 = types.ReplyKeyboardMarkup(resize_keyboard=True)
a1 = types.InlineKeyboardButton(text="Мои сервера")
a2 = types.InlineKeyboardButton(text="Добавить сервер")
keyboard1.add(a1, a2)

ans1 = """ hf"""
ans2 = """Введите данные в формате user:password@ip:port\nПример: admin:password123@192.168.1.1:8080 """
ans3 ="""Данные успешно сохранены!"""
ans4 ="""Неверный формат данных. Попробуйте снова."""

keyboard2 = types.InlineKeyboardMarkup(row_width=1)
b1 = types.InlineKeyboardButton(text="Экология", callback_data="ecology")
b2 = types.InlineKeyboardButton(text="Креативные идустрии", callback_data="creative")
b3 = types.InlineKeyboardButton(text="Биотехнологи и медицина", callback_data="medicine")
b4 = types.InlineKeyboardButton(text="Цифровые технологии", callback_data="digital")
b5 = types.InlineKeyboardButton(text="Транспорт и космос", callback_data="space")
b6 = types.InlineKeyboardButton(text="Гуманитарные технологии", callback_data="humanitarian")
b7 = types.InlineKeyboardButton(text="Урбанистика", callback_data="urban")
b8 = types.InlineKeyboardButton(text="Энергетика", callback_data="energy")
keyboard2.row(b1)
keyboard2.row(b2)
keyboard2.row(b3)
keyboard2.row(b4)
keyboard2.row(b5)
keyboard2.row(b6)
keyboard2.row(b7)
keyboard2.row(b8)
# keyboard2.add(b1, b2, b3, b4, b5, b6, b7, b8)


ans3 = "Приобрести билет можно на нашем сайте https://i-shpak.ru/mane "
