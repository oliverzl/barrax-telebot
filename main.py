import os
import gspread
import telebot
import calendar

from dotenv import load_dotenv
import datetime
from datetime import date, datetime
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from telebot import types

# file imports
from progress import Progress
from projectCode import ProjectCode


load_dotenv()
API_KEY = os.getenv("API_KEY")
authorized_users = os.getenv("AUTHORIZED")


bot = telebot.TeleBot(API_KEY)

# connect google sheets
# addes row with 1, 2, 3, 4, 5, 6 every time it runs
sa = gspread.service_account(filename="service_account.json")
sh = sa.open("barrax_projectIDTEST")
wks1 = sh.worksheet("2023")
wks2 = sh.worksheet("2024")
wks3 = sh.worksheet("2025")


un_month = datetime.now()
currentMonth = un_month.strftime("%b").upper()

print(f"type current month: {type(currentMonth)}")
currentDay = datetime.now().day
currentYear = datetime.now().year
currently_now = str(currentDay) + "/" + str(currentMonth) + "/" + str(currentYear)
print(currently_now)


# constants
DESIGN = "DESIGN"
DRAFTING = "DRAFTING"
RENDERING = "RENDERING"
TYPE = "TYPE"
DATE = "DATE"
COUNTRY = "COUNTRY"
NAME_ADDRESS = "NAME_ADDRESS"
CANCEL = "CANCEL"
EDIT = "EDIT"


SINGAPORE_CODE = "65"
CAMBODIA_CODE = "855"
steps = []

# dictionary to keep track of chat progress
chat_progresses: [Progress, ProjectCode] = {}


def add_to_progress(chat_id):
    chat_progresses[chat_id] = [Progress.STEP_1, ProjectCode()]
    print(f"added to progress, chat progresses {chat_progresses}")
    print(chat_progresses)


def update_progress(chat_id, updated_progress):
    chat_progresses[chat_id][0] = updated_progress


def delete_progress(chat_id):
    del chat_progresses[chat_id]
    print(chat_progresses)


def get_progress(chat_id):
    return chat_progresses[chat_id][0]


def get_project_code(chat_id) -> ProjectCode:
    return chat_progresses[chat_id][1]


# -----------------------------------------------

#  -----------------------------------------------COMMANDS/MESSAGE HANDLERS: ---------------------------------------------
@bot.message_handler(commands=["start"])
def new_project(message):
    chat_id = message.chat.id
    if chat_id in chat_progresses:
        bot.send_message(chat_id, "There is already a project in progress")
    else:
        name = message.from_user.username
        if name in authorized_users:
            add_to_progress(chat_id)
            bot.send_message(
                chat_id,
                "PROJECT TYPE",
                reply_markup=project_type_menu(),
            )
        else:
            bot.send_message(chat_id, "NOT AUTHORIZED")


@bot.message_handler(commands=["cancel"])
def cancel(message):
    chat_id = message.chat.id
    if chat_id in chat_progresses:
        if get_progress(chat_id) == Progress.STEP_5:
            bot.send_message(chat_id, "PLEASE START A NEW PROJECT")
            delete_progress(chat_id)
        else:
            delete_progress(chat_id)
            bot.send_message(
                chat_id, "PROJECT DELETED, TYPE /start TO START A NEW PROJECT"
            )
    else:
        bot.send_message(chat_id, "NO PROJECT IN PROGRESS")


@bot.message_handler(commands=["info"])
def info(message):
    chat_id = message.chat.id
    # bot.send_message(chat_id, "*How to read the Project ID?*\n")
    # bot.send_message(
    #     chat_id, "<u>underline?</u>\n<b>bold</b>\n<i>italic</i>", parse_mode="HTML"
    # )
    bot.send_message(
        chat_id,
        "<b>How to read the Project ID?</b>\n<i>eg. 65-01-0123-001</i>\nSG-DESIGN-JAN2023-RUNNINGNO.\n\n<b>Description in sequence:</b>\n<u>65</u> - Singapore\n<u>855</u> - Cambodia\n\n<u>01</u> - Design\n<u>02</u> - Drafting\n<u>03</u> - Rendering\n\n<b>How to use Project ID?</b>\n<i>eg. 65-01-0123-001</i>\n<u>Invoice</u> - INV65010123001-A\n<u>Project ID</u> - BX65-01-0123-001\n<u>Project PO</u> - PO65010123001-A\n",
        parse_mode="HTML",
    )


#  -----------------------------------------------BUTTON CLICK FUNCTION
def cancel_project(call):
    chat_id = call.message.chat.id
    if get_progress(chat_id) != Progress.STEP_5:
        if chat_id in chat_progresses:
            delete_progress(chat_id)
            bot.send_message(
                chat_id, "PROJECT DELETED, TYPE /start TO START A NEW PROJECT"
            )
        else:
            bot.send_message(
                chat_id, "PROJECT DELETED, TYPE /start TO START A NEW PROJECT"
            )
    else:
        delete_progress(chat_id)


def project_type_menu():
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 3
    markup.add(types.InlineKeyboardButton("DESIGN", callback_data=DESIGN))
    markup.add(types.InlineKeyboardButton("DRAFTING", callback_data=DRAFTING))
    markup.add(types.InlineKeyboardButton("RENDERING", callback_data=RENDERING))
    markup.add(types.InlineKeyboardButton("CANCEL", callback_data=CANCEL))
    return markup


# def editing_menu():
#     markup = types.InlineKeyboardMarkup()
#     markup.row_width = 3
#     for item in steps:
#         markup.add(types.InlineKeyboardButton(f"{item}", callback_data=item))
#     markup.add(types.InlineKeyboardButton("DATE", callback_data=DATE))
#     return markup


def country_menu():
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 3
    markup.add(types.InlineKeyboardButton("SINGAPORE", callback_data=SINGAPORE_CODE))
    markup.add(types.InlineKeyboardButton("CAMBODIA", callback_data=CAMBODIA_CODE))
    # markup.add(types.InlineKeyboardButton("EDIT", callback_data=EDIT))
    markup.add(types.InlineKeyboardButton("CANCEL", callback_data=CANCEL))
    return markup


def confirmation():
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 3
    markup.add(types.InlineKeyboardButton("CONFIRM", callback_data=SINGAPORE_CODE))
    # markup.add(types.InlineKeyboardButton("EDIT", callback_data=EDIT))
    markup.add(types.InlineKeyboardButton("CANCEL", callback_data=CANCEL))
    return markup


def display_updated_project_code(chat_id):
    string1 = str(get_project_code(chat_id))
    x = string1.replace("None", "")
    x = str(x)
    y = x.split("-")
    nature = "01"
    if y[1] == "DRAFTING":
        nature = "02"
    elif y[1] == "RENDERING":
        nature = "03"

    project_id_list = [y[0], nature, y[3] + y[4]]
    project_id = ""
    for x in project_id_list:
        project_id += x + "-"
    # bot.send_message(chat_id, "PROJECT ID: " + project_id)
    return project_id

    # 65-02-12-22-01


def display_project_details(chat_id):
    bot.send_message(chat_id, get_project_code(chat_id).get_details())


def update_project_nature_code(chat_id, nature):
    chat_progresses[chat_id][1].set_nature_code(nature)


def update_project_date(chat_id, d: date):
    chat_progresses[chat_id][1].set_date(d)


def update_project_country_code(chat_id, country: int):
    chat_progresses[chat_id][1].set_country_code(country)


def update_project_name(chat_id, name: str):
    chat_progresses[chat_id][1].set_name(name)


# ASKING FOR TYPE OF PROJECT, NOTHING TO EDIT
# steps: update project code, update progress to step 2, send message
# update type of projet, move to step 2: date


def editing(call):
    chat_id = call.message.chat.id
    if call.data == "NATURE":
        bot.send_message(
            chat_id,
            "PROJECT TYPE",
            reply_markup=project_type_menu(),
        )
        nature_select(call)
    elif call.data == "COUNTRY":
        country_select(call)
    elif call.data == "NAME_ADDRESS":
        name_address(call)


def nature_select(call):
    chat_id = call.message.chat.id
    # CANCEL BUTTON CLICKED, ELSE CARRY ON
    if call.data == "CANCEL":
        cancel_project(call)
    else:
        # very first step
        update_project_nature_code(chat_id, call.data)
        bot.answer_callback_query(call.id, "Updated")
        print(f"checking progress: {get_progress(chat_id)}")
        bot.edit_message_text(
            f"TYPE: {call.data} PROJECT", chat_id, call.message.message_id
        )
        steps.append("NATURE")
        update_progress(chat_id, Progress.STEP_2)
        calendar, step = DetailedTelegramCalendar().build()
        bot.send_message(chat_id, "PROJECT OPEN DATE:", reply_markup=calendar)
        # NATURE in steps, update, and resume


def date_select(call):
    chat_id = call.message.chat.id
    result, key, step = DetailedTelegramCalendar().process(call.data)
    if not result and key:
        bot.edit_message_text(
            f"DATE:", chat_id, call.message.message_id, reply_markup=key
        )
    elif result:
        reformatted_date = result.strftime("%d/%m/%y")
        bot.edit_message_text(
            f"DATE: {reformatted_date}", chat_id, call.message.message_id
        )

        update_project_date(chat_id, result)
        update_progress(chat_id, Progress.STEP_3)
        bot.send_message(
            chat_id,
            "COUNTRY",
            reply_markup=country_menu(),
        )


def country_select(call):
    chat_id = call.message.chat.id
    if call.data == "CANCEL":
        cancel_project(call)
    else:
        update_project_country_code(chat_id, call.data)
        bot.answer_callback_query(call.id, "Updated")
        country = "SINGAPORE"
        if call.data == "855":
            country = "CAMBODIA"

        bot.edit_message_text(f"COUNTRY: {country}", chat_id, call.message.message_id)

        update_progress(chat_id, Progress.STEP_4)
        bot.send_message(chat_id, "TYPE IN PROJECT NAME/ADDRESS:")


def name_address(message):
    def next_available_row(worksheet):
        str_list = list(filter(None, worksheet.col_values(1)))
        return str(len(str_list) + 1)

    chat_id = message.chat.id
    print(message.text)
    display_updated_project_code(chat_id)
    update_project_name(chat_id, message.text)
    split1 = str(get_project_code(chat_id)).split("-")
    wks = wks1
    if split1[4] == "24":
        wks = wks2
    if split1[4] == "25":
        wks = wks3
    next_row = next_available_row(wks)
    next_row = int(next_row) - 1
    next_row = str(next_row)
    if int(next_row) < 10:
        next_row = "00" + next_row
    elif int(next_row) > 9:
        next_row = "0" + next_row
        # ________________________________________________
    bot.send_message(chat_id, get_project_code(chat_id).get_details() + next_row)
    update_progress(chat_id, Progress.STEP_5)
    bot.send_message(chat_id, "CONFIRM?", reply_markup=confirmation())


def confirm_select(call):
    chat_id = call.message.chat.id
    if call.data == "CANCEL":
        cancel_project(call)
    else:
        bot.send_message(chat_id, "CONFIRMED")
        split1 = str(get_project_code(chat_id)).split("-")
        username = call.message.chat.username
        country = "SINGAPORE"
        if split1[0] == "855":
            country = "CAMBODIA"

        month_abbr = calendar.month_abbr[int(split1[3])].upper()
        # print(f"type of month is {type(month_abbr)}")
        date_list = [split1[2], month_abbr, split1[4]]

        date_opened = "/".join(date_list)
        # default wks is 2023, unless user chose 24 or 25
        wks = wks1
        if split1[4] == "24":
            wks = wks2
        if split1[4] == "25":
            wks = wks3
        print(f"date opened: {date_opened}")
        # 23/08/22
        def next_available_row(worksheet):
            str_list = list(filter(None, worksheet.col_values(1)))
            return str(len(str_list) + 1)

        next_row = str(int(next_available_row(wks)) - 1)
        if int(next_row) < 10:
            next_row = "00" + next_row
        elif int(next_row) > 9:
            next_row = "0" + next_row
            # nature = split1[1]
            # name = split1[5]
        final_projectcode = display_updated_project_code(chat_id) + next_row
        wks.append_row(
            [
                username,
                # current date when this ID created
                currently_now,
                # nature
                split1[1],
                country,
                # name of project
                split1[5],
                final_projectcode,
                # date of project start??
                date_opened,
            ],
            table_range="A1:G1",
        )
        bot.send_message(
            chat_id, f"PROJECT ID: <b>{final_projectcode}</b>", parse_mode="HTML"
        )
        print(get_progress(chat_id))
        cancel_project(call)

        # ACTUAL

        # cretaed by user
        # date created
        # nature
        # coutnry
        # project name
        # project id
        # date of opening

        # wks1 = sh.worksheet("2023")
        # wks2 = sh.worksheet("2024")


# 65-02-12-22-01

# def process_step_5(call):
#     chat_id = message.chat.id

#     string1 = str(get_project_code(chat_id))
#     x = string1.replace("None", "")
#     print(x)
#     if call.data == "CANCEL":
#         cancel_project(call)
#     bot.send_message(chat_id, f"Your project's name is: {message.text}")
#     display_updated_project_code(chat_id)
#     display_project_details(chat_id)
#     update_progress(chat_id, Progress.STEP_5)
#     bot.send_message(chat_id, "CONFIRM?", reply_markup=confirmation())


# ACTUAL FLOW HANDLING
@bot.callback_query_handler(func=lambda message: True)
def callback_query(call):
    chat_id = call.message.chat.id
    if chat_id not in chat_progresses:
        bot.answer_callback_query(call.id, "Please start a new project first")
        return

    current_progress = get_progress(chat_id)
    print(f"current progress: {current_progress}")
    if current_progress == Progress.STEP_1:
        nature_select(call)
    elif current_progress == Progress.STEP_2:
        date_select(call)
    elif current_progress == Progress.STEP_3:
        country_select(call)
    elif current_progress == Progress.STEP_5:
        confirm_select(call)
    else:
        pass


@bot.message_handler(func=lambda message: True)
def handle_text_doc(message):
    chat_id = message.chat.id
    if chat_id not in chat_progresses:
        return

    current_progress = get_progress(chat_id)
    if current_progress == Progress.STEP_4:
        name_address(message)


bot.infinity_polling()
