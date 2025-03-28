from telebot import types

all_ans = "Выберете ваш вопрос:\n" \
          "#1 Что такое «Город открытий»?\n" \
          "#2 Какие маршруты есть в «Городе открытий»?\n" \
          "#3 Как отправиться в путешествие?\n" \
          "#4 Кто может отправиться в путешествие?\n" \
          "#5 Как купить тур?"

greetings = """Здравствуйте, {username}!
Моноспекталь-лекция — формат живого повествования. 
Главная задача - сохранить ваш интерес и внимание, подарить новые эмоциональные переживания.Будет познавательно, смешно и до мурашек трогательно 
Какие жанры объединяет «Мане»:
стендап-комедия
спектакль
лекция
Даты: 21 ноября, 5 декабря, Москва, Брюсов-холл ул, Вознесенский пер. 14 (м. Тверская)
ТГ-канал спектакля:  https://t.me/manemono 
А ещё вы можете пройти тест «Где Мане?» и получить промокод на скидку 10%"""

keyboard1 = types.ReplyKeyboardMarkup(resize_keyboard=True)
a1 = types.InlineKeyboardButton(text="О чём «МАНЕ»?")
a2 = types.InlineKeyboardButton(text="Получить промокод")
a3 = types.InlineKeyboardButton(text="Купить билет")
a4 = types.InlineKeyboardButton(text="Отправить рассылку")
keyboard1.add(a1, a2, a3, a4)

ans1 = """
МАНЕ о том, чего может стоить воплощение мечты в реальность. Эдуарда Мане называли отцом импрессионизма, скандально известным художником.
Над его картинами смеялись,а официальный Парижский салон не признавал в нём художника. Он имел смелость быть собой, писать так как считал нужным. Это история о творческом пути, терниях и звёздах.
МАНЕ создан на основе биографии и писем Эдуарда Мане.
В жизни художника каждый из вас найдёт что-то про себя. Маленькие кусочки больших смыслов, которых нам порой так не хватает в жизни.
Это моноспектакль не только про Мане.
Он — про каждого из нас.
Рассказывает: Илья Шпак
Режиссёр: Валерий Корчанов
Продолжительность: 90 минут 
Даты: 21 ноября, 5 декабря, Москва, Брюсов-холл ул, Вознесенский пер. 14 (м. Тверская)
"""

ans2 = """
Квиз для получения промокода (в разработке)
"""

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
