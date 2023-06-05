from get_task_from_ueo_id import get_task_by_numberUEO_id

from updateTaskUeo import updateKontrSrok

from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils import executor, callback_data
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, \
    InlineKeyboardButton
import re
from aiogram.dispatcher.webhook import EditMessageReplyMarkup, EditMessageText
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup
from aiogram.utils.callback_data import CallbackData
from aiogram_calendar import simple_cal_callback, SimpleCalendar, dialog_cal_callback, DialogCalendar
import datetime

API_TOKEN = ""

PROXY_URL = ''

bot = Bot(token=API_TOKEN, proxy=PROXY_URL)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

user_answer = {'key':''}
user_accept = []
#user_accept =[]

call_info = CallbackData('my',"id","alians","bank")

@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply("Помощник\n 1.Для начала работы нажмите  /start\n"
                        "2.В случае если вы решили что не хотите воспроизводить действия по заявке вновь нажмите /start и начните все сначала\n"
                        "3.Напишите номер заявки и получите информацию по ней\n"
                        "4.Выберите удобное для вас изменение времени из двух кнопок\n"
                        " \"Перенести на другую дату\"   \"Перенести на другое время\"\n"
                        "5. Выберите дату или напишите время (в зависимости от того что требует бот)")
async def clean_user_data(user_answer):
    user_answer.clear()
    user_answer['key'] = ''
@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    print("user_id", message.from_user.id, datetime.datetime.now())
    await clean_user_data(user_answer)
    print("start ",user_answer)
    # print(message.from_user.id)
    # user_answer = {'key': ''}
    for user in user_accept:
        if (user == message.from_user.id):
            user_answer[message.from_user.id] = 'id_number'

            kb = InlineKeyboardMarkup(row_width=1)
            com1 = InlineKeyboardButton('ID Терминала', callback_data=call_info.new(id="yes",alians="no",bank="no"))
            com2 = InlineKeyboardButton('Номер заявки (Альянс)', callback_data=call_info.new(id="no",alians="yes",bank="no"))
            com3 = InlineKeyboardButton('Номер заявки (Банк)', callback_data=call_info.new(id="no",alians="no",bank="yes"))
            kb.add(com1, com2, com3)
            return await (message.reply('По какому полю будем искать заявку?', reply_markup=kb))

@dp.callback_query_handler( call_info.filter(id="yes"))
async def terminal_id_yes(callback: types.CallbackQuery,callback_data: dict):
    user_answer['key'] = 'id'
    return EditMessageText(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                           text="Напишите ID Терминала(8 цифр)", reply_markup=None)

@dp.callback_query_handler(call_info.filter(alians="yes"))
async def terminal_id_yes(callback: types.CallbackQuery, callback_data: dict):
    user_answer['key'] = 'alians'
    return EditMessageText(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                           text="Напишите номер заявки в системе альянс(8 цифр)", reply_markup=None)

@dp.callback_query_handler(call_info.filter(bank="yes"))
async def terminal_id_yes(callback: types.CallbackQuery, callback_data: dict):
    user_answer['key'] = 'bank'
    return EditMessageText(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                           text="Напишите номер заявки в системе банка(6 цифр)", reply_markup=None)


@dp.callback_query_handler(text="yes_action")
async def yes_action1(callback: types.CallbackQuery):
    kkb = InlineKeyboardMarkup(row_width=1)
    com1 = InlineKeyboardButton(text='Перенести на другую дату', callback_data="date_enter_calendar")
    com2 = InlineKeyboardButton(text='Перенести на несколько часов', callback_data="time_enter")
    kkb.add(com1, com2)
    return EditMessageText(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                           text="Что вам необходимо сделать?", reply_markup=kkb)


@dp.callback_query_handler(text="no_active")
async def no_action(callback: types.CallbackQuery):
    return EditMessageText(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                           text="Нажмите /start для начала работы", reply_markup=None)


@dp.callback_query_handler(text="date_enter_calendar")
async def nav_cal_handler(callback: types.CallbackQuery):
    return EditMessageText(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                           text="Выберите нужную дату", reply_markup=await SimpleCalendar().start_calendar())


@dp.callback_query_handler(simple_cal_callback.filter())
async def process_simple_calendar(callback_query: CallbackQuery, callback_data: dict):
    selected, datee = await SimpleCalendar().process_selection(callback_query, callback_data)
    if selected:
        now_date = datetime.datetime.now()
        if (now_date >= datee):
            await bot.answer_callback_query(callback_query_id=callback_query.id, text="Слишком ранняя дата. Повторите ввод.", show_alert=True)
            return EditMessageText(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id,
                                   text="Выбрана слишком ранняя дата. Повторите ввод.",
                                   reply_markup=await SimpleCalendar().start_calendar())
        else:
            user_answer['tmp_date']=datee
            user_answer[callback_query.from_user.id]="date_send"

            return EditMessageText(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id,
                                   text="Введите время(0-23)", reply_markup=None)


@dp.callback_query_handler(text="time_enter")
async def enter_date(callback: types.CallbackQuery):
    user_answer[callback.from_user.id] = 'time_send'
    return EditMessageText(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                           text="Введите количество часов", reply_markup=None)
async def get_info_from_db(row,message):
    try:
        if (type(row) is str):
            await message.answer(f"{row} Нажмите /start для нового ввода")
            return
        else:
            user_answer['date']=row[9]
            # print('this date',row[8],'\n',row)
            await message.answer(
                f"<u><b>Номер заявки (Банк)</b></u>:  {row[0]}\n\n"
                f"<u><b>Номер заявки (Альянс)</b></u>:  {row[1]}\n\n"
                f"<u><b>ID Терминала</b></u>:  {row[2]}\n\n"
                f"<u><b>ОО/ДО</b></u>:  {row[3]}\n\n"
                f"<u><b>Организация</b></u>:  {row[4]}\n\n"
                f"<u><b>Контакты</b></u>:  {row[5]}\n\n"
                f"<u><b>Дата создания</b></u>:  {row[6]}\n\n"
                f"<u><b>Задача</b></u>:  {row[7]}\n\n"
                f"<u><b>Подробности</b></u>:  {row[8]}\n\n"
                f"<u><b>Дедлайн</b></u>:  {row[9]}\n\n"
                f"<u><b>Статус</b></u>:  {row[10]}", parse_mode='HTML')
    except Exception as e:
        await message.answer(f"{e}")
    kkb = InlineKeyboardMarkup(row_width=2)
    com1 = InlineKeyboardButton(text='Да', callback_data="yes_action")
    com2 = InlineKeyboardButton(text='Нет', callback_data='no_active')
    kkb.add(com1, com2)
    return await (message.reply('Хотите перенести срок?', reply_markup=kkb))


@dp.message_handler()
async def cheking(message: types.message):
    print("every ",user_answer)

    # print(message.from_user.id)
    if not(message.from_user.id in user_answer):
        await message.answer("Неверный ввод")
    elif user_answer[message.from_user.id] == 'time_send':
        if (message.text.isdigit() and (0<int(message.text)<49) ):
            user_answer[message.from_user.id] = ''
            user_answer['time']=message.text
            user_answer['date']+=datetime.timedelta(hours=int(message.text))
            fin = updateKontrSrok(user_answer["number"],user_answer['date'],user_answer['type_key'])
            await message.answer(f'В заявке №{user_answer["number"]} {fin} ')
            # user_answer.pop('date')
            # user_answer.pop('time')

            print('!!!',user_answer )
            await clean_user_data(user_answer)
            return
        else:
            await message.answer("Некорректный ввод,ведите количество часов повторно")
    elif user_answer[message.from_user.id] == 'date_send':
        if ( message.text.isdigit() and (0<=int(message.text)<24)):
            user_answer[message.from_user.id] = ''
            date_str = user_answer['tmp_date'].strftime('%m/%d/%y ')
            time_str = message.text +":00:00"
            # print("date_str ",date_str)
            # print("time_str ",time_str)

            new_date = date_str + time_str
            user_answer.pop('tmp_date')
            # print("dateee ",new_date)
            user_answer['date'] = datetime.datetime.strptime(new_date, '%m/%d/%y %H:%M:%S')
            # print("dateee ",user_answer['date'])

            fin = updateKontrSrok(user_answer["number"],user_answer['date'],user_answer['type_key'])
            await message.answer(f'В заявке №{user_answer["number"]} {fin} ')
            print(user_answer )

            await clean_user_data(user_answer)

            return
        else:
            await message.answer("Некорректный ввод,ведите правильно время(0-23)")
    elif user_answer[message.from_user.id]  == 'id_number' and user_answer['key'] == 'id':
        print("id: ",message.text)
        if (message.text.isdigit and len(message.text) == 8):
            user_answer['number'] = message.text
            user_answer['type_key'] = '1'
            user_answer['key'] = ''

            row = get_task_by_numberUEO_id(message.text,user_answer['type_key'])
            await get_info_from_db(row, message)
        else:
            await message.answer("Некорректный ввод,введите верный id терминала состоящий из 8 чисел")
    elif user_answer[message.from_user.id]  == 'id_number' and user_answer['key'] == 'bank':
        print("bank: ",message.text, len(message.text))
        if (message.text.isdigit and len(message.text) == 6):
            user_answer['number'] = message.text
            user_answer['type_key'] = '2'
            user_answer['key'] = ''
            row = get_task_by_numberUEO_id(message.text, user_answer['type_key'])
            await get_info_from_db(row, message)
            return
        else:
            await message.answer("Некорректный ввод,введите верный номер заявки в сети банка состоящий из 6 чисел")
    elif user_answer[message.from_user.id]  == 'id_number' and user_answer['key'] == 'alians':
        print("alians: ",message.text, len(message.text))
        if (message.text.isdigit and len(message.text) == 8):
            # user_answer.pop('')
            user_answer['number'] = message.text
            user_answer['type_key'] = '3'
            user_answer['key'] =''

            row = get_task_by_numberUEO_id(message.text,user_answer['type_key'])
            await get_info_from_db(row, message)

        else:
            await message.answer("Некорректный ввод,введите верный номер заявки в сети альянс состоящий из 8 чисел")
    # print(user_answer)
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
