from asyncio import QueueEmpty
import logging
import os
import pandas as pd
from telegram import ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)
import src.credentials
from src.filters import FilterEducation, FilterAge
from src.respond_logic import (
    age, gender, info, invalid_age, simple_test_q1, simple_test_q2, simple_test_res, start, start_dialog, options,
    education, job_sphere, cancel, analyze, vacancy
)

START, GENDER, AGE, EDUCATION, JOB_SPHERE, OPTIONS, Q2, SIMPLE_TEST_PASSED, VACANCY = range(9)
PROF_MATRIX = pd.read_excel('https://raw.githubusercontent.com/harbachonakk/files-for-heroku/main/professions_matrix.xlsx',
                            header=0)

filter_age = FilterAge()
filter_education = FilterEducation()


def location(update: Update, context: CallbackContext) -> int:
    """Stores the location and asks for some info about the user."""
    user = update.message.from_user
    user_location = update.message.location
    logger.info(
        "Location of %s: %f / %f", user.first_name, user_location.latitude, user_location.longitude
    )
    update.message.reply_text(
        'Maybe I can visit you sometime! At last, tell me something about yourself.'
    )

    return


if __name__ == "__main__":
    token = src.credentials.TOKEN
    name = src.credentials.NAME

    # Port is given by Heroku
    PORT = os.environ.get('PORT')

    # Enable logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Set up the Updater
    updater = Updater(token)
    dp = updater.dispatcher
    # Add handlers
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            START: [MessageHandler(Filters.text & ~Filters.command, start_dialog)],
            GENDER: [MessageHandler(Filters.regex('^(Женский|Мужской)$'), gender)],
            AGE: [MessageHandler(filter_age, age), MessageHandler(~filter_age, invalid_age)],
            EDUCATION: [MessageHandler(filter_education, education)],
            JOB_SPHERE: [CallbackQueryHandler(job_sphere), MessageHandler(Filters.text & ~Filters.command, job_sphere)],
            OPTIONS: [MessageHandler(Filters.text & ~Filters.command, options),
                      CallbackQueryHandler(simple_test_q1, pattern='1'),
                      CallbackQueryHandler(analyze, pattern='3'),
                      CallbackQueryHandler(info, pattern='4')],
            Q2: [CallbackQueryHandler(simple_test_q2)],
            SIMPLE_TEST_PASSED: [CallbackQueryHandler(simple_test_res)],
            VACANCY: [MessageHandler(Filters.text & ~Filters.command, vacancy)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dp.add_handler(conv_handler)
    # Start the webhook
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=token,
                          webhook_url=f"https://{name}.herokuapp.com/{token}")
    updater.idle()
