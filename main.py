from config import TOKEN
from telegram.ext import Updater, \
    MessageHandler, \
    CommandHandler, Filters, ConversationHandler
import commands
from database.models import Drugs, prepare_database

updater = Updater(use_context=True, token=TOKEN)
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler("start", commands.on_start))
dispatcher.add_handler(MessageHandler(Filters.regex("Списки"), commands.lists_comands))
dispatcher.add_handler(MessageHandler(Filters.regex("Мои списки"), commands.show_lists))

#Поиск аптек по близости
dispatcher.add_handler(ConversationHandler(
    entry_points=[MessageHandler(Filters.regex("Найти аптеки по близости"), commands.geoposition)],
    states={
        1: [MessageHandler(Filters.text, commands.near_places)],
    },
    fallbacks=[[MessageHandler(Filters.regex("Отмена"), commands.cancel)]]
))

#Диспетчер под списки

#Добавить новый
dispatcher.add_handler(ConversationHandler(
    entry_points=[MessageHandler(Filters.regex("Добавить новый список"), commands.create_list)],
    states={
        1: [MessageHandler(Filters.text, commands.add_to_list)],
        2: [MessageHandler(Filters.text, commands.save_list)],
    },
    fallbacks=[[MessageHandler(Filters.regex("сохранить"), commands.cancel)]]
))

#Удалить лист
dispatcher.add_handler(ConversationHandler(
    entry_points=[MessageHandler(Filters.regex("Удалить список"), commands.prepare_list)],
    states={
        1: [MessageHandler(Filters.text, commands.chose_list)],
        2: [MessageHandler(Filters.text, commands.delete_list)],
    },
    fallbacks=[]
))

###########################################################################################

#Диспетчер под поиск лекарств
dispatcher.add_handler(ConversationHandler(
    entry_points=[MessageHandler(Filters.regex("Найти лекарство"), commands.drug_search)],
    states={
        1: [MessageHandler(Filters.text, commands.search)],
        2: [MessageHandler(Filters.text, commands.end_search)],
    },
    fallbacks=[[MessageHandler(Filters.regex("asdasldask;ldkas;ld"), commands.cancel)]]
))
###########################################################################################


prepare_database()
print("Бот запущен")
updater.start_polling()
updater.idle()
