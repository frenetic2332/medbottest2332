from telegram.ext import ConversationHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from database.models import Drugs, RecieptItem, Reciept
import requests
import os

lists_data = {}
on_delete_data = {}

def on_start(update, context):
    chat = update.effective_chat
    main_menue_buttons = [
        ["Найти аптеки по близости", ],
        ["Найти лекарство", "Списки"]
    ]
    buttons = ReplyKeyboardMarkup(main_menue_buttons)
    context.bot.send_message(chat_id=chat.id, text="Привет! Чем я могу помочь тебе?", reply_markup=buttons)


#Отправка аптек по близости
def geoposition(update, context):
    location_keyboard = KeyboardButton(text="Отправить координаты",  request_location=True)
    cancel_keyboard = KeyboardButton(text="Отмена")

    custom_keyboard = [[location_keyboard], [cancel_keyboard]]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    update.message.reply_text(
        "Для поиска ближайших аптек мне нужны твои координаты, готов ими поделиться?" + " После отправки геопозиции напишите Ок",
        reply_markup=reply_markup)
    if update.message.text == "Отмена":
        update.message.reply_text("ОК", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    else:
        return 1

def near_places(update, context):
    chat = update.effective_chat
    places = "https://www.google.ru/maps/search/%D0%B0%D0%BF%D1%82%D0%B5%D0%BA%D0%B8/@42.8668016,74.5727222,15z/data=!3m1!4b1"
    context.bot.send_message(chat_id=chat.id, text="Ближайшие аптеки: {}".format(places))
    return ConversationHandler.END
##################################################################################

#Найти лекартсво в базе
def drug_search(update, context):
    if update.message.text == "Отмена":
        return 2
    stop_button = [["Отмена"]]
    buttons = ReplyKeyboardMarkup(stop_button)
    update.message.reply_text(text = "Введите название лекартсва и я попробую найти его в базе. "
                                     "Для окончания поиска нажмите Отмена", reply_markup=buttons)
    return 1

def search(update, context):
    chat = update.effective_chat
    if update.message.text == "Отмена":
        context.bot.send_message(text = "Ok", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    try:
        info = Drugs.select().where(Drugs.name == update.message.text).get()
        context.bot.send_message(chat_id=chat.id, text="Вот, что я знаю о вашем лекарстве {}".format(info.info))
    except:
        context.bot.send_message(chat_id=chat.id, text="Не могу найти такое, попробуйте снова или нажмите Отмена")
    return 1

def end_search(update, context):
    context.bot.send_message(text="Ок, завершение поиска лекарств", reply_markup=ReplyKeyboardRemove)
    return ConversationHandler.END

##################################################################################

#Списки
def lists_comands(update, context):
    chat = update.effective_chat
    lists_menue_buttons = [
        ["Добавить новый список",],
        ["Удалить список"], ["Мои списки"]
    ]
    buttons = ReplyKeyboardMarkup(lists_menue_buttons)
    context.bot.send_message(chat_id=chat.id, text="Что мне нужно сделать??", reply_markup=buttons)

def create_list(update, context):
    user_id = update.effective_user.id
    lists_data[user_id] = {}
    update.message.reply_text("Введите название списка")
    return 1

def add_to_list(update, context):
    list_name = update.message.text

    user_id = update.effective_user.id
    lists_data[user_id]["listname"] = list_name
    lists_data[user_id]["drugs"] = []

    update.message.reply_text("Вводите название лекартсва для добавления в список, "
                              "для сохранинения списка напишите 'сохранить'")
    return 2


def save_list(update, context):
    user_id = update.effective_user.id
    if update.message.text == "сохранить":
        receipt = Reciept.create(listname=lists_data[user_id]["listname"], user=user_id)
        for drug in lists_data[user_id]["drugs"]:
            RecieptItem.create(reciept=receipt, drug=drug)
        update.message.reply_text("Список удачно сохранен")
        return ConversationHandler.END
    drug = update.message.text
    lists_data[user_id]["drugs"].append(drug)

    update.message.reply_text("Наименование успешно сохранено")
    del lists_data[user_id]
    return 2


def prepare_list(update, context):
    chat = update.effective_chat
    on_delete_data[update.effective_user.id] = {}
    context.bot.send_message(chat_id=chat.id, text="Введите название списка. Все ваши списки:")
    show_lists(update, context)
    return 1


def chose_list(update, context):
    user_id = update.effective_user.id
    chosen_list = update.message.text
    on_delete_data[user_id]["listname"] = chosen_list
    try:
        Reciept.select().where((Reciept.listname == chosen_list) & (Reciept.user == user_id)).get()
        update.message.reply_text(text="Список {} выбран. Напишите удалить для подтверждения".format(chosen_list))
        return 2
    except:
        update.message.reply_text(text="Список {} не найден. Удаление отменено".format(chosen_list))
        return ConversationHandler.END


def delete_list(update, context):
    user_id = update.effective_user.id
    chosen_list = on_delete_data[user_id]["listname"]
    update.message.reply_text("Список удалён")
    Reciept.select().where((Reciept.user == user_id) & (Reciept.listname == chosen_list)).delete()
    return ConversationHandler.END

def show_lists(update, context):
    user_id = update.effective_user.id
    lists = Reciept.select(Reciept.listname).where(Reciept.user == user_id).execute()
    for list in lists:
        update.message.reply_text(list.listname)

#######
def cancel(update, context):
    user_id = update.effective_user.id
    del lists_data[user_id]
    update.message.reply_text("Завершение операции")