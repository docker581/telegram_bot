import traceback
import logging
import prettytable

from telegram import Update
from telegram.ext import (
    ContextTypes, CommandHandler, ConversationHandler, 
    MessageHandler, filters, CallbackQueryHandler
)    
from telegram.constants import ParseMode
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP

from models import User, Shift, Point, Session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

POINT_ID, DATE = range(2)


async def schedule(update: Update,  
                   context: ContextTypes.DEFAULT_TYPE) -> None:
    session = Session()
    try:
        shifts = session.query(Shift).all()
        if shifts:
            table = prettytable.PrettyTable(['id', 'point_id', 'date'])
            for shift in shifts:
                table.add_row([
                    shift.id,
                    shift.point_id,
                    shift.date,
                ])
            await update.message.reply_text(
                f'```{table}```',
                parse_mode=ParseMode.MARKDOWN_V2
            )
        else:
            await update.message.reply_text('Смен нет.')
    except Exception:
        logger.error(traceback.format_exc())
        await update.message.reply_text('Некорректный запрос на'
                                        ' просмотр смен.')
    finally:
        session.close()


async def add_shift_start(update: Update, 
                          context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Пожалуйста, укажите id пункта выдачи.')
    return POINT_ID


async def add_shift_point_id(update: Update, 
                             context: ContextTypes.DEFAULT_TYPE) -> int:
    point_id = int(update.message.text)
    session = Session()
    try:
        point = session.query(Point).filter_by(id=point_id).first()
        if not point:
            await update.message.reply_text('Указанный пункт выдачи' 
                                            ' не найден.')
            return ConversationHandler.END

        context.user_data['point_id'] = point_id
        calendar, step = DetailedTelegramCalendar().build()
        await update.message.reply_text(
            f'Пожалуйста, выберите дату смены.', reply_markup=calendar
        )
        return DATE
    except Exception as e:
        logger.error(traceback.format_exc())
        await update.message.reply_text('Некорректный запрос на' 
                                        ' добавление смены.')
    finally:
        session.close()        


async def add_shift_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    result, key, step = DetailedTelegramCalendar().process(query.data)

    logger.info(f'Calendar processing: result={result}, key={key}, step={step}')
    
    if not result and key:
        await query.message.edit_text(
            f"Выберите {LSTEP[step]}", reply_markup=key
        )
    elif result:
        context.user_data['date'] = result
        session = Session()
        try:
            user = session.query(User).filter_by(
                telegram_id=query.from_user.id
            ).first()
            if user and user.role == 'owner':
                shift = Shift(
                    point_id=context.user_data['point_id'],
                    date=context.user_data['date'],
                )
                session.add(shift)
                session.commit()
                await query.message.edit_text('Смена добавлена.')
            else:
                await query.message.edit_text('Нет прав на добавление смены.')
        except Exception:
            logger.error(traceback.format_exc())
            await query.message.edit_text('Некорректный запрос на добавление смены.')
        finally:
            session.close()
        return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Команда отменена.')
    return ConversationHandler.END


schedule_handler = CommandHandler('schedule', schedule)
add_shift_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('addshift', add_shift_start)],
    states={
        POINT_ID: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, add_shift_point_id
            )
        ],
        DATE: [
            CallbackQueryHandler(add_shift_date, pattern="^calendar_")
        ],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)
