import os
from dotenv import load_dotenv
from datetime import date

import telebot
from telebot import types

from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP

from progress import Progress
from projectCode import ProjectCode

load_dotenv()
API_KEY = os.getenv("API_KEY")
bot = telebot.TeleBot(API_KEY)


# constants
DESIGN = "DESIGN"
DRAFTING = "DRAFTING"
RENDERING = "RENDERING"
CANCEL = "CANCEL"
EDIT = "EDIT"

SINGAPORE_CODE = "65"
CAMBODIA_CODE = "855"

list1 = ["beeepo", "notrealjovin"]

# dictionary to keep track of chat progress
chat_progresses: [Progress, ProjectCode] = {}


def add_to_progress(chat_id):
    chat_progresses[chat_id] = [Progress.STEP_1, ProjectCode()]
    print(chat_progresses)


def update_progress(chat_id, updated_progress):
    chat_progresses[chat_id][0] = updated_progress


def delete_progress(chat_id):
    del chat_progresses[chat_id][1]
    del chat_progresses[chat_id]
    print(chat_progresses)


def get_progress(chat_id):
    return chat_progresses[chat_id][0]


def get_project_code(chat_id) -> ProjectCode:
    return chat_progresses[chat_id][1]


# -----------------------------------------------


def markup_inline_step_1():
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 3
    markup.add(types.InlineKeyboardButton("DESIGN", callback_data=DESIGN))
    markup.add(types.InlineKeyboardButton("DRAFTING", callback_data=DRAFTING))
    markup.add(types.InlineKeyboardButton("RENDERING", callback_data=RENDERING))
    markup.add(types.InlineKeyboardButton("CANCEL", callback_data=CANCEL))
    # markup.add(types.InlineKeyboardButton("EDIT", callback_data=EDIT))
    return markup


def markup_inline_step_3():
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 3
    markup.add(types.InlineKeyboardButton("SINGAPORE", callback_data=SINGAPORE_CODE))
    markup.add(types.InlineKeyboardButton("CAMBODIA", callback_data=CAMBODIA_CODE))
    markup.add(types.InlineKeyboardButton("CANCEL", callback_data=CANCEL))
    return markup


@bot.message_handler(commands=["start"])
def new_project(message):
    chat_id = message.chat.id
    if chat_id in chat_progresses:
        bot.send_message(chat_id, "There is already a project in progress")
    else:
        name = message.from_user.username
        if name in list1:
            add_to_progress(chat_id)
            bot.send_message(
                chat_id,
                "PROJECT TYPE",
                reply_markup=markup_inline_step_1(),
            )
        else:
            bot.send_message(chat_id, "NOT AUTHORIZED")


@bot.message_handler(commands=["cancel"])
def cancel(message):
    chat_id = message.chat.id
    if chat_id in chat_progresses:
        delete_progress(chat_id)
        bot.send_message(chat_id, "PROJECT DELETED, TYPE /start TO START A NEW PROJECT")
    else:
        bot.send_message(chat_id, "NO PROJECT IN PROGRESS")


def display_updated_project_code(chat_id):

    string1 = str(get_project_code(chat_id))
    x = string1.replace("None", "")
    print(x)
    bot.send_message(chat_id, "PROJECT ID: " + x)


def display_project_details(chat_id):
    bot.send_message(chat_id, get_project_code(chat_id).get_details())


def update_project_nature_code(chat_id, nature: int):
    chat_progresses[chat_id][1].set_nature_code(nature)


def update_project_date(chat_id, d: date):
    chat_progresses[chat_id][1].set_date(d)


def update_project_country_code(chat_id, country: int):
    chat_progresses[chat_id][1].set_country_code(country)


def update_project_name(chat_id, name: str):
    chat_progresses[chat_id][1].set_name(name)


def process_step_1(call):
    chat_id = call.message.chat.id
    if call.data == "CANCEL":
        delete_progress(chat_id)
        bot.send_message(chat_id, "Project deleted")

    update_project_nature_code(chat_id, call.data)
    bot.answer_callback_query(call.id, "Updated")

    bot.edit_message_text(
        f"TYPE: {call.data} PROJECT", chat_id, call.message.message_id
    )
    # commenting out display proj code
    # display_updated_project_code(chat_id)

    update_progress(chat_id, Progress.STEP_2)

    calendar, step = DetailedTelegramCalendar().build()
    bot.send_message(chat_id, "PROJECT OPEN DATE:", reply_markup=calendar)
    # markup = markup.add(types.InlineKeyboardButton("CANCEL", callback_data=CANCEL))


def process_step_2(call):
    chat_id = call.message.chat.id
    result, key, step = DetailedTelegramCalendar().process(call.data)

    if not result and key:
        print("NONE")
        bot.edit_message_text(
            f"DATE:", chat_id, call.message.message_id, reply_markup=key
        )
    elif result:
        reformatted_date = result.strftime("%d/%m/%y")
        bot.edit_message_text(
            f"DATE: {reformatted_date}", chat_id, call.message.message_id
        )

        update_project_date(chat_id, result)
        # commenting out displaying project code
        # display_updated_project_code(chat_id)

        update_progress(chat_id, Progress.STEP_3)

        bot.send_message(
            chat_id,
            "COUNTRY",
            reply_markup=markup_inline_step_3(),
        )


def process_step_3(call):
    chat_id = call.message.chat.id
    if call.data == "CANCEL":
        update_progress(chat_id, Progress.STEP_4)
    update_project_country_code(chat_id, call.data)
    bot.answer_callback_query(call.id, "Updated")

    bot.edit_message_text(f"COUNTRY: {call.data}", chat_id, call.message.message_id)
    display_updated_project_code(chat_id)

    update_progress(chat_id, Progress.STEP_4)
    bot.send_message(chat_id, "TYPE IN PROJECT NAME/ADDRESS:")


def process_step_4(message):
    chat_id = message.chat.id
    update_project_name(chat_id, message.text)

    bot.send_message(chat_id, f"Your project's name is: {message.text}")
    display_updated_project_code(chat_id)
    display_project_details(chat_id)


@bot.callback_query_handler(func=lambda message: True)
def callback_query(call):
    chat_id = call.message.chat.id
    if chat_id not in chat_progresses:
        bot.answer_callback_query(call.id, "Please start a new project first")
        return

    current_progress = get_progress(chat_id)
    if current_progress == Progress.STEP_1:
        process_step_1(call)
    elif current_progress == Progress.STEP_2:
        process_step_2(call)
    elif current_progress == Progress.STEP_3:
        process_step_3(call)
    else:
        pass


@bot.message_handler(func=lambda message: True)
def handle_text_doc(message):
    chat_id = message.chat.id
    if chat_id not in chat_progresses:
        return

    current_progress = get_progress(chat_id)
    if current_progress == Progress.STEP_4:
        process_step_4(message)


bot.infinity_polling()
