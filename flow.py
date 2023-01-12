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
