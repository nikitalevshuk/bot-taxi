from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from .constants import SUPPORTED_LANGUAGES, COUNTRIES, POLISH_CITIES

def get_language_keyboard() -> InlineKeyboardMarkup:
    keyboard = []
    for lang_code, lang_name in SUPPORTED_LANGUAGES.items():
        keyboard.append([InlineKeyboardButton(
            text=lang_name,
            callback_data=lang_code
        )])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_country_keyboard() -> InlineKeyboardMarkup:
    keyboard = []
    for country_code, country_name in COUNTRIES.items():
        keyboard.append([InlineKeyboardButton(
            text=country_name,
            callback_data=country_code
        )])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_city_keyboard() -> InlineKeyboardMarkup:
    keyboard = []
    for city in POLISH_CITIES:
        keyboard.append([InlineKeyboardButton(
            text=city,
            callback_data=city
        )])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="/to_boycott")],
        [KeyboardButton(text="/stats")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Choose a command"
    )
