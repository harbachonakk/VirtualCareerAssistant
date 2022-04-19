from re import U
from telegram.ext import MessageFilter
import pandas as pd


class FilterAge(MessageFilter):
    def filter(self, message):
        is_age = message.text.isdigit() and int(
            message.text) >= 14 and int(message.text) <= 60
        return is_age


class FilterEducation(MessageFilter):
    def filter(self, message):
        educations = set(['Среднее', 'Средне-специальное', 'Высшее',
                          'Получаю высшее', 'Получаю средне-специальное'])
        is_education = message.text in educations
        return is_education

