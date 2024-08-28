import traceback
import logging
import prettytable

from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    ContextTypes, MessageHandler, ConversationHandler,
    CommandHandler, filters,
)
from telegram.constants import ParseMode

from models import User, Point, Session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

(POINT_NAME, POINT_ADDRESS, POINT_ID, POINT_NEW_NAME,
 POINT_NEW_ADDRESS) = range(5)


async def my_points(update: Update,
                    context: ContextTypes.DEFAULT_TYPE) -> None:
    session = Session()
    try:
        telegram_id = update.message.from_user.id
        user = session.query(User).filter_by(
            telegram_id=telegram_id).first()
        if user and user.role == 'reg_owner':
            points = session.query(Point).all()
            if points:
                table = prettytable.PrettyTable(['id', 'name',
                                                 'address', 'rating'])
                for point in points:
                    table.add_row([
                        point.id,
                        point.name,
                        point.address,
                        point.rating,
                    ])
                await update.message.reply_text(
                    f'```{table}```',
                    parse_mode=ParseMode.MARKDOWN_V2
                )
            else:
                await update.message.reply_text(
                    'Список ваших пунктов выдачи пуст.'
                )
        else:
            await update.message.reply_text(
                'У вас нет доступа к просмотру пунктов выдачи.'
            )
    except Exception:
        logger.error(traceback.format_exc())
        await update.message.reply_text('Некорректный запрос на просмотр'
                                        ' пунктов выдачи.')
    finally:
        session.close()


async def add_point_start(update: Update,
                          context: ContextTypes.DEFAULT_TYPE) -> int:
    session = Session()
    telegram_id = update.message.from_user.id
    user = session.query(User).filter_by(telegram_id=telegram_id).first()
    session.close()

    if user and user.role == 'reg_owner':
        await update.message.reply_text('Введите название пункта выдачи:')
        return POINT_NAME
    else:
        await update.message.reply_text('Вы не имеете права добавлять'
                                        ' пункты выдачи.')
        return ConversationHandler.END


async def add_point_name(update: Update,
                         context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['name'] = update.message.text
    await update.message.reply_text('Введите адрес пункта выдачи:')
    return POINT_ADDRESS


async def add_point_address(update: Update,
                            context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['address'] = update.message.text
    session = Session()
    try:
        telegram_id = update.message.from_user.id
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        if user:
            name = context.user_data['name']
            address = context.user_data['address']
            point = Point(name=name, address=address, owner_id=user.id)
            session.add(point)
            session.commit()
            await update.message.reply_text(
                f'Пункт выдачи "{name}" по адресу "{address}" добавлен.',
                reply_markup=ReplyKeyboardRemove(),
            )
        else:
            await update.message.reply_text('Ошибка добавления пункта выдачи.')
    except Exception:
        logger.error(traceback.format_exc())
        await update.message.reply_text('Некорректный запрос на'
                                        ' добавление пункта выдачи.')
    finally:
        session.close()
    return ConversationHandler.END


async def edit_point_start(update: Update,
                           context: ContextTypes.DEFAULT_TYPE) -> int:
    session = Session()
    telegram_id = update.message.from_user.id
    user = session.query(User).filter_by(telegram_id=telegram_id).first()
    session.close()

    if user and user.role == 'reg_owner':
        await update.message.reply_text('Введите ID пункта выдачи, который'
                                        ' хотите изменить:')
        return POINT_ID
    else:
        await update.message.reply_text('Вы не имеете права редактировать'
                                        ' пункты выдачи.')
        return ConversationHandler.END


async def edit_point_id(update: Update,
                        context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['id'] = update.message.text
    await update.message.reply_text('Введите новое название пункта выдачи:')
    return POINT_NEW_NAME


async def edit_point_new_name(update: Update,
                              context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['new_name'] = update.message.text
    await update.message.reply_text('Введите новый адрес пункта выдачи:')
    return POINT_NEW_ADDRESS


async def edit_point_new_address(update: Update,
                                 context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['new_address'] = update.message.text
    session = Session()
    try:
        telegram_id = update.message.from_user.id
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        if user:
            point_id = context.user_data['id']
            new_name = context.user_data['new_name']
            new_address = context.user_data['new_address']

            point = session.query(Point).filter_by(id=point_id).first()
            if point:
                point.name = new_name
                point.address = new_address
                session.add(point)
                session.commit()
                await update.message.reply_text(
                    f'Пункт выдачи "{point_id}" изменен на "{new_name}" '
                    f'по адресу "{new_address}".',
                    reply_markup=ReplyKeyboardRemove(),
                )
            else:
                await update.message.reply_text('Пункт выдачи с таким ID'
                                                ' не найден.')
        else:
            await update.message.reply_text('Ошибка редактирования пункта'
                                            ' выдачи.')
    except Exception:
        logger.error(traceback.format_exc())
        await update.message.reply_text('Некорректный запрос на'
                                        ' редактирование пункта выдачи.')
    finally:
        session.close()
    return ConversationHandler.END


async def delete_point_start(update: Update,
                             context: ContextTypes.DEFAULT_TYPE) -> int:
    session = Session()
    telegram_id = update.message.from_user.id
    user = session.query(User).filter_by(telegram_id=telegram_id).first()
    session.close()

    if user and user.role == 'reg_owner':
        await update.message.reply_text('Введите ID пункта выдачи,'
                                        ' который хотите удалить:')
        return POINT_ID
    else:
        await update.message.reply_text('Вы не имеете права удалять'
                                        ' пункты выдачи.')
        return ConversationHandler.END


async def delete_point_id(update: Update,
                          context: ContextTypes.DEFAULT_TYPE) -> int:
    point_id = update.message.text
    session = Session()
    try:
        telegram_id = update.message.from_user.id
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        if user:
            point = session.query(Point).filter_by(id=point_id).first()
            if point:
                session.delete(point)
                session.commit()
                await update.message.reply_text(
                    f'Пункт выдачи "{point_id}" удален.',
                    reply_markup=ReplyKeyboardRemove(),
                )
            else:
                await update.message.reply_text('Пункт выдачи с таким ID'
                                                ' не найден.')
        else:
            await update.message.reply_text('Ошибка удаления пункта выдачи.')
    except Exception:
        logger.error(traceback.format_exc())
        await update.message.reply_text('Некорректный запрос на'
                                        ' удаление пункта выдачи.')
    finally:
        session.close()
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Команда отменена.',
                                    reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


my_points_handler = CommandHandler('mypoints',  my_points)
add_point_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('addpoint', add_point_start)],
    states={
        POINT_NAME: [MessageHandler(
            filters.TEXT & ~filters.COMMAND, add_point_name)],
        POINT_ADDRESS: [MessageHandler(
            filters.TEXT & ~filters.COMMAND, add_point_address)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)
edit_point_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('editpoint', edit_point_start)],
    states={
        POINT_ID: [MessageHandler(
            filters.TEXT & ~filters.COMMAND, edit_point_id)],
        POINT_NEW_NAME: [MessageHandler(
            filters.TEXT & ~filters.COMMAND, edit_point_new_name)],
        POINT_NEW_ADDRESS: [MessageHandler(
            filters.TEXT & ~filters.COMMAND, edit_point_new_address)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)
delete_point_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('deletepoint', delete_point_start)],
    states={
        POINT_ID: [MessageHandler(
            filters.TEXT & ~filters.COMMAND, delete_point_id)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)
