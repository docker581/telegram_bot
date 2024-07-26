import traceback
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler

from models import User, Session


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        'Привет! Вот список доступных команд:\n'
        '/register - регистрация пользователя\n'
        '/mypoints - просмотр списка пунктов выдачи\n'
        '/addpoint - Добавить пункт выдачи\n'
        '/editpoint - Редактировать пункт выдачи\n'
        '/deletepoint - Удалить пункт выдачи\n'
        '/schedule - просмотр списка смен\n'
        '/addshift - добавление смены\n'
        '/editshift - редактирование смены\n'
        '/deleteshift - удаление смены\n'
    )


async def register(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [
            InlineKeyboardButton('Владелец', callback_data='reg_owner'),
            InlineKeyboardButton('Соискатель', callback_data='reg_worker'),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        'Выберите роль:',
        reply_markup=reply_markup,
    )


async def handle_reg_button(update: Update,
                            context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await save_user(update, query.data)


async def save_user(update: Update, role: str) -> None:
    session = Session()
    try:
        telegram_id = update.callback_query.from_user.id
        user = session.query(User).filter_by(
            telegram_id=telegram_id
        ).first()
        if user:
            await update.callback_query.message.edit_text(
                'Вы уже зарегистрированы.'
            )
        else:
            user = User(telegram_id=telegram_id, role=role)
            session.add(user)
            session.commit()
            await update.callback_query.message.edit_text(
                'Регистрация прошла успешно.'
            )
    except Exception:
        logger.error(traceback.format_exc())
        await update.message.reply_text(
            'Некорректный запрос на регистрацию пользователя.'
        )
    finally:
        session.close()


start_handler = CommandHandler('start', start)
reg_handler = CommandHandler('register', register)
reg_button_handler = CallbackQueryHandler(handle_reg_button, pattern=r'^reg_')
