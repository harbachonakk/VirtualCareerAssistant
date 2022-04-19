from src.utils import build_menu
from telegram.ext import CallbackContext, ConversationHandler
from telegram import (
    InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, ReplyKeyboardRemove, Update)
import hh_research.researcher
import pandas as pd
import logging
import pandas as pd
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

logger = logging.getLogger(__name__)

START, GENDER, AGE, EDUCATION, JOB_SPHERE, OPTIONS, Q2, SIMPLE_TEST_PASSED, VACANCY = range(
    9)

SPHERES = [
    'IT', 'Аудит', 'Бизнес-аналитика', 'Закупки', 'Инженерия и производство', 'Консалтинг',
    'Контент и дизайн', 'Логистика и Supply Chain', 'Маркетинг и PR', 'Менеджмент', 'Продажи',
    'HR (Управление персоналом)', 'Финансы', 'Не знаю'
]

PROF_MATRIX = pd.read_excel('https://raw.githubusercontent.com/harbachonakk/files-for-heroku/main/professions_matrix.xlsx',
                            header=0)

ANS1 = 0
ANS2 = 0


def start(update: Update, context: CallbackContext) -> int:
    """Starts the conversation and asks if the user wants to proceed"""
    user = update.message.from_user
    update.message.reply_text(
        f'Привет, {user.first_name}! Я Виртуальный Карьерный Помощник.\n'
        'Я могу предложить Вам пройти профориентационные тесты, а также рассказать, '
        'как обстоят дела на карьерном рынке интересующих Вас профессий.\n\n'
        'Вы можете отправить мне /cancel, чтобы прекратить общение\n\n'
        'Или напишите что-нибудь другое - и мы продолжим знакомство :)'
    )
    return START


def start_dialog(update: Update, context: CallbackContext) -> int:
    """Asks user's genger"""
    reply_keyboard = [['Женский', 'Мужской']]
    update.message.reply_text(
        'Отлично! Я задам буквально пару вопросов, а потом покажу, что умею\n'
        'Укажите, пожалуйста, Ваш пол',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Женский или Мужской?'
        ),
    )
    return GENDER


def gender(update: Update, context: CallbackContext) -> int:
    """Stores the selected gender and asks for age"""
    user = update.message.from_user
    logger.info("GENDER of %s: %s", user.first_name, update.message.text)

    update.message.reply_text(
        'Теперь напишите, сколько Вам лет',
        reply_markup=ReplyKeyboardRemove(),
    )
    return AGE


def age(update: Update, context: CallbackContext) -> int:
    """Stores the age and asks for education level"""
    user = update.message.from_user
    logger.info("AGE of %s: %s", user.first_name, update.message.text)

    reply_keyboard = [['Среднее', 'Средне-специальное'],
                      ['Высшее', 'Получаю высшее'],
                      ['Получаю средне-специальное']]
    update.message.reply_text((
        'Понял!\n'
        'Укажите, пожалуйста, какое у Вас образование на данный момент'),
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Степень образования?'
    ),
    )
    return EDUCATION


def invalid_age(update: Update, context: CallbackContext) -> int:
    """Asks to send the correct age again"""
    user = update.message.from_user
    logger.info("AGE of %s is incorrect: %s",
                user.first_name, update.message.text)
    update.message.reply_text(
        'Такое значение не подходит.\n'
        'Укажите Ваш возраст, пожалуйста'
    )
    return


def education(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("EDUCATION of %s: %s", user.first_name, update.message.text)

    button_list = []
    for (i, item) in enumerate(SPHERES, start=0):
        button_list.append(InlineKeyboardButton(item, callback_data=i))

    reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=2))
    # update.callback_query.message.edit_reply_markup(reply_markup=ReplyKeyboardRemove())
    update.message.reply_text(
        'Замечательно!', reply_markup=ReplyKeyboardRemove())
    update.message.reply_text(
        'Если вы знаете, какая сфера Вас интересует профессионально - поделитесь со мной :)\n'
        'Вы можете выбрать из предложенных вариантов или написать что-нибудь другое',
        reply_markup=reply_markup
    )
    return JOB_SPHERE


def job_sphere(update: Update, context: CallbackContext) -> int:
    """Stores preffered job sphere and sends a message with three inline buttons.
    \nOptions are 1. take simple test, 2. take longer test, 3. see analysis, 4. get information"""

    button_list = [
        InlineKeyboardButton("Пройти краткий тест", callback_data='1'),
        InlineKeyboardButton("Пройти более полный тест", callback_data='2'),
        InlineKeyboardButton("Анализ вакансии", callback_data='3'),
        InlineKeyboardButton("Узнать больше", callback_data='4'),
    ]
    reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=1))
    text = ('Спасибо! Эти данные помогут мне развиваться и быть полезнее\n'
            'Давайте решим, чем займемся теперь :)\n'
            'Нажмите "Узнать больше", чтобы я рассказал Вам подробнее об активностях')

    if (update.message is not None):
        user = update.message.from_user
        logger.info("Desired JOB SPHERE of %s: %s",
                    user.first_name, update.message.text)
        update.message.reply_text(text, reply_markup=reply_markup)
    else:
        query = update.callback_query
        query.answer()
        user = query.from_user
        logger.info("Desired JOB SPHERE of %s: %s",
                    user.first_name, query.data)
        query.edit_message_text(text=text, reply_markup=reply_markup)
    return OPTIONS


def options(update: Update, context: CallbackContext) -> int:
    text = 'Вы выбрали активность'
    if (update.message is not None):
        update.message.reply_text(text=text)
    else:
        query = update.callback_query
        query.answer()
        user = query.from_user
        logger.info("Desired JOB SPHERE of %s: %s",
                    user.first_name, query.data)
        query.edit_message_text(text=text)

    return


def analyze(update: Update, context: CallbackContext) -> int:
    """Starts vacancy analyzing"""

    text = ("Вы выбрали анализ вакансий. Отлично!"
            "\nНапишите название вакансии, которая Вас интересует")
    update.effective_message.reply_text(text=text)

    return VACANCY


def vacancy(update: Update, context: CallbackContext) -> int:
    logger.info("def vacancy working")
    vacancy = None
    if (update.message is not None):
        user = update.message.from_user
        logger.info("Chosen vacancy of %s: %s",
                    user.first_name, update.message.text)
        vacancy = update.message.text
        text = (f'Начинаю делать для Вас анализ вакансии {vacancy}...'
                '\nПодготовка отчета может занять до нескольких минут, не уходите далеко :)')
        update.message.reply_text(text=text)
    else:
        query = update.callback_query
        query.answer()
        user = query.from_user
        logger.info("Chosen vacancy of %s: %s",
                    user.first_name, query.data)
        vacancy = query.data
        text = (f'Начинаю делать для Вас анализ вакансии {vacancy}...'
                '\nПодготовка отчета может занять до нескольких минут, не уходите далеко :)')
        query.edit_message_text(text=text)

    settings_dict = {
        "options": {
            "text": "Data Science", "area": 1, "per_page": 50
        },
        "refresh": True, "max_workers": 7, "save_result": False,
        "rates": {
            "USD": 0.012641, "EUR": 0.010831, "UAH": 0.35902, "RUB": 1
        }
    }
    settings_dict['options']['text'] = vacancy

    hh_analyzer = hh_research.researcher.Researcher(
        settings_dict=settings_dict)
    hh_analyzer.update()
    num_of_vacancies, max_salary, min_salary, mean_salary, median_salary, most_keys, most_words = hh_analyzer()
    if num_of_vacancies is not None:
        update.effective_message.reply_text("Отчет готов! Давайте смотреть:\n"
                                            f"{max_salary}\n"
                                            f"{min_salary}\n"
                                            f"{mean_salary}\n"
                                            f"{median_salary}\n\n"
                                            f"Самые популярные навыки и количество вхождений:\n{most_keys}\n\n"
                                            f"Самые популярные слова и количество вхождений:\n{most_words}\n\n")

    button_list = [
        InlineKeyboardButton("Пройти краткий тест", callback_data='1'),
        InlineKeyboardButton("Пройти более полный тест", callback_data='2'),
        InlineKeyboardButton("Анализ вакансии", callback_data='3'),
        InlineKeyboardButton("Узнать больше", callback_data='4'),
    ]
    reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=1))

    update.effective_message.reply_text("В резюме, как правило, работодатели указывают зарплатную вилку: диапазон, в котором вакансия будет оплачиваться. "
                                        f"Вот так на данный момент выглядят распределения зарплат От и До для вакансии {vacancy} в Москве, "
                                        "где От - нижняя граница зарплатной вилки, а До - верхняя. "
                                        "Обратите внимание на первый график - график с усами. Средняя черта внутри цветного прямоугольника - "
                                        "диапазона наиболее обычных зарплат - означает медианную зарплату: такую, что ровно половина предложений - "
                                        "меньше, а половина - больше. ")
    update.effective_message.reply_text(
        'Как-то так! Чем займемся дальше?', reply_markup=reply_markup)
    return OPTIONS


def info(update: Update, context: CallbackContext) -> int:
    text = ("Итак!"
            "\n\n1. Краткий тест представлен Матрицей выбора профессий по методике Г.В. Резапкиной. "
            "При выборе опции Пройти краткий тест Вам будет предложено ответить всего на два вопроса, после чего я "
            "пришлю Вам список профессий, соответствующих Вашим предрасположенностям по данной методике."

            "\n\n2. Более полный тест составлен по методике Е.А. Климова. Этот тест включает в себя 30 вопросов. "
            "По результатам теста Вам также будет предложен список профессий для ознакомления."

            "\n\n3. Выберите опцию с Анализом, чтобы я показал вам актуальные систематизированные данные по профессии: "
            "распределение зарплат, необходимые навыки. Я беру свежие данные с HeadHunter для составления такого отчета."

            "\n\nЧем займемся?"
            )

    button_list = [
        InlineKeyboardButton("Пройти краткий тест", callback_data='1'),
        InlineKeyboardButton("Пройти более полный тест", callback_data='2'),
        InlineKeyboardButton("Анализ вакансии", callback_data='3'),
        InlineKeyboardButton("Узнать больше", callback_data='4'),
    ]
    reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=1))

    update.effective_message.reply_text(text=text, reply_markup=reply_markup)
    return OPTIONS


def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Всего доброго! Обращайтесь, если понадобится помощь :)', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def simple_test_q1(update: Update, context: CallbackContext) -> int:
    text = (
        'С кем или с чем Вы бы хотели работать? Какой объект деятельности Вас привлекает?'
    )

    button_list = ['1. Человек', '2. Информация', '3. Финансы', '4. Техника', '5. Искусство', '6. Животные', '7. Растения',
                   '8. Продукты питания', '9. Изделия', '10. Природные ресурсы']

    for (i, item) in enumerate(button_list, start=0):
        button_list.append(InlineKeyboardButton(item, callback_data=i))
    reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=1))

    update.effective_message.reply_text(text=text, reply_markup=reply_markup)
    return Q2


def simple_test_q2(update: Update, context: CallbackContext) -> int:
    """Stores answer to Q1 and asks Q2 of simple test"""
    query = update.callback_query
    query.answer()
    ANS1 = query.data
    user = query.from_user
    logger.info("Answer on Q1 of %s: %s",
                user.first_name, query.data)

    text = (
        'Чем бы Вы хотели заниматься? Какой вид деятельности Вас привлекает?'
    )
    button_list = ['1. Управление', '2. Обслуживание', '3. Образование', '4. Оздоровление', '5. Творчество', '6. Производство', '7. Конструирование',
                   '8. Исследование', '9. Защита', '10. Контроль']

    for (i, item) in enumerate(SPHERES, start=0):
        button_list.append(InlineKeyboardButton(item, callback_data=i))
    reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=1))

    update.effective_message.reply_text(text=text, reply_markup=reply_markup)
    return SIMPLE_TEST_PASSED


def simple_test_res(update: Update, context: CallbackContext) -> int:
    """Stores answer to Q1 and tell result of simple test"""
    res = str(PROF_MATRIX.iloc[ANS1, ANS2+1])
    text = (
        'По результатам краткого самотестирования могу Вам посоветовать подумать о следующих профессиях:\n' + res +
        '\n\nЧем займемся теперь? :)'
    )
    button_list = [
        InlineKeyboardButton("Пройти краткий тест", callback_data='1'),
        InlineKeyboardButton("Пройти более полный тест", callback_data='2'),
        InlineKeyboardButton("Анализ вакансии", callback_data='3'),
        InlineKeyboardButton("Узнать больше", callback_data='4'),
    ]
    reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=1))

    update.effective_message.reply_text(text=text, reply_markup=reply_markup)

    return OPTIONS


def klimov_test():
    marks = ''
    questions = [
        '1. Легко знакомлюсь с людьми.',
        '2. Охотно и подолгу могу что-нибудь мастерить.',
        '3. Люблю ходить в музеи, театры, на выставки.',
        '4. Охотно и постоянно ухаживаю за растениями, животными.',
        '5. Охотно и подолгу могу что-нибудь вычислять, чертить.',
        '6. С удовольствием общаюсь со сверстниками или малышами.',
        '7. С удовольствием ухаживаю за растениями и животными.',
        '8. Обычно делаю мало ошибок в письменных работах.',
        '9. Мои изделия обычно вызывают интерес у товарищей, старших.',
        '10. Люди считают, что у меня есть художественные способности.',
        '11. Охотно читаю о растениях, животных.',
        '12. Принимаю участие в спектаклях, концертах.',
        '13. Люблю читать об устройстве механизмов, приборов, машин',
        '14. Подолгу могу разгадывать головоломки, задачи, ребусы.',
        '15. Легко улаживаю разногласия между людьми.',
        '16. Считают, что у меня есть способности к работе с техникой.',
        '17. Людям нравится мое художественное творчество',
        '18. У меня есть способности к работе с растениями и животными.',
        '19. Я могу ясно излагать свои мысли в письменной форме.',
        '20. Я почти никогда ни с кем не ссорюсь.',
        '21. Результаты моего технического творчества одобряют даже незнакомые люди.',
        '22. Без особого труда усваиваю иностранные языки.',
        '23. Мне часто случается помогать даже незнакомым людям.',
        '24. Подолгу могу заниматься музыкой, рисованием, читать книги и т. д.',
        '25. Могу влиять на ход развития растений и животных.',
        '26. Люблю разбираться в устройстве механизмов, приборов.',
        '27. Мне обычно удается убедить людей в своей правоте.',
        '28. Охотно наблюдаю за растениями или животными.',
        '29.Охотно читаю научно-популярную, критическую литературу, публицистику.',
        '30. Стараюсь понять секреты мастерства и пробую свои силы в живописи, музыке и т. п.'
    ]
