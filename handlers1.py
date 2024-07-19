import traceback
import logging
import prettytable
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from telegram.constants import ParseMode

from models import User, Point, Shift, Review, Session


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: CallbackContext) -> None:
    start_message = (
        r'Добро пожаловать\!' + '\n\n'

        r'Команды:' + '\n\n'

        r'*register* \- регистрация пользователя' + '\n\n'

        r'*mypoints* \- просмотр списка пунктов выдачи' + '\n'
        r'*addpoint \[name\] \[address\]* \- добавление пункта выдачи' + '\n'
        r'*editpoint \[id\] \[new\_name\] \[new\_address\]* \- '
        'редактирование пункта выдачи\n'
        r'*deletepoint \[id\]* \- удаление пункта выдачи' + '\n\n'

        r'*schedule* \- просмотр списка смен' + '\n'
        r'*addshift \[point\_id\] \[start\_time\] \[end\_time\]* '
        r'\- добавление смены' + '\n'
        r'*editshift \[id\] \[new\_start\_time\] \[new\_end\_time\]* '
        r'\- редактирование смены' + '\n'
        r'*deleteshift \[id\]* \- удаление смены' + '\n\n'

        r'*ratemanager \[point\_id\] \[rating\] \[review\]* '
        r'\- оценивание пункта смены' + '\n'
        r'*rateworker \[worker\_id\] \[rating\] \[review\]* '
        r'\- оценивание работника' + '\n'
        r'*viewratings \[point\_id\|worker\_id\]* '
        r'\- просмотр рейтингов и отзывов пункта выдачи или работника' + '\n'
    )
    await update.message.reply_text(
        text=start_message,
        parse_mode=ParseMode.MARKDOWN_V2,
    )


async def register(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [
            InlineKeyboardButton('Владелец', callback_data='owner'),
            InlineKeyboardButton('Соискатель', callback_data='worker'),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        'Выберите роль:',
        reply_markup=reply_markup,
    )


async def handle_reg_button(update: Update, context: CallbackContext) -> None:
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


async def my_points(update: Update, context: CallbackContext) -> None:
    session = Session()
    try:
        telegram_id = update.message.from_user.id
        user = session.query(User).filter_by(
            telegram_id=telegram_id
        ).first()
        if user and user.role == 'owner':
            points = session.query(Point).all()
            if points:
                table = prettytable.PrettyTable(
                    ['id', 'name', 'address', 'rating']
                )
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
        await update.message.reply_text(
            'Некорректный запрос на просмотр пунктов выдачи.'
        )
    finally:
        session.close()


async def add_point(update: Update, context: CallbackContext) -> None:
    if len(context.args) < 2:
        return await update.message.reply_text(
            'Пожалуйста, укажите название и адрес пункта выдачи.'
        )

    session = Session()
    try:
        telegram_id = update.message.from_user.id
        user = session.query(User).filter_by(
            telegram_id=telegram_id
        ).first()
        if user and user.role == 'owner':
            name = context.args[0]
            address = context.args[1]
            point = Point(name=name, address=address, owner_id=user.id)
            session.add(point)
            session.commit()
            await update.message.reply_text(f'Пункт выдачи {name} добавлен.')
        else:
            await update.message.reply_text(
                'Вы не имеете права добавлять пункты выдачи.'
            )
    except Exception:
        logger.error(traceback.format_exc())
        await update.message.reply_text(
            'Некорректный запрос на добавление пункта выдачи.'
        )
    finally:
        session.close()


async def edit_point(update: Update, context: CallbackContext) -> None:
    if len(context.args) < 3:
        return await update.message.reply_text(
            'Пожалуйста, укажите id пункта выдачи, '
            'новое название и новый адрес.'
        )

    session = Session()
    try:
        telegram_id = update.message.from_user.id
        user = session.query(User).filter_by(
            telegram_id=telegram_id
        ).first()
        if user and user.role == 'owner':
            id = context.args[0]
            new_name = context.args[1]
            new_address = context.args[2]

            point = session.query(Point).filter_by(
                id=id
            ).first()
            if point:
                point.name = new_name
                point.address = new_address
                session.add(point)
                session.commit()
                await update.message.reply_text('Пункт выдачи изменен.')
            else:
                await update.message.reply_text(
                    'Пункт выдачи с таким id не найден.'
                )
        else:
            await update.message.reply_text(
                'Вы не имеете права изменять пункты выдачи.'
            )
    except Exception:
        logger.error(traceback.format_exc())
        await update.message.reply_text(
            'Некорректный запрос на редактирование пункта выдачи.'
        )
    finally:
        session.close()


async def delete_point(update: Update, context: CallbackContext) -> None:
    if len(context.args) < 1:
        return await update.message.reply_text(
            'Пожалуйста, укажите id пункта выдачи.'
        )

    session = Session()
    try:
        telegram_id = update.message.from_user.id
        user = session.query(User).filter_by(
            telegram_id=telegram_id
        ).first()
        if user and user.role == 'owner':
            id = context.args[0]

            point = session.query(Point).filter_by(
                id=id
            ).first()
            if point:
                session.delete(point)
                session.commit()
                await update.message.reply_text('Пункт выдачи удален.')
            else:
                await update.message.reply_text(
                    'Пункт выдачи с таким id не найден.'
                )
        else:
            await update.message.reply_text(
                'Вы не имеете права удалять пункты выдачи.'
            )
    except Exception:
        logger.error(traceback.format_exc())
        await update.message.reply_text(
            'Некорректный запрос на удаление пункта выдачи.'
        )
    finally:
        session.close()


async def schedule(update: Update, context: CallbackContext) -> None:
    session = Session()
    try:
        shifts = session.query(Shift).all()
        if shifts:
            table = prettytable.PrettyTable(
                ['id', 'point_id', 'start_time', 'end_time']
            )
            for shift in shifts:
                table.add_row([
                    shift.id,
                    shift.point_id,
                    shift.start_time,
                    shift.end_time,
                ])
            await update.message.reply_text(
                f'```{table}```',
                parse_mode=ParseMode.MARKDOWN_V2
            )
        else:
            await update.message.reply_text('Смен нет.')
    except Exception:
        logger.error(traceback.format_exc())
        await update.message.reply_text(
            'Некорректный запрос на просмотр смен.'
        )
    finally:
        session.close()


async def add_shift(update: Update, context: CallbackContext) -> None:
    if len(context.args) < 3:
        return await update.message.reply_text(
            'Пожалуйста, укажите id пункта выдачи, '
            'дату начала и дату конца смены.'
        )

    session = Session()
    try:
        user = session.query(User).filter_by(
            telegram_id=update.message.from_user.id
        ).first()
        if user and user.role == 'owner':
            point_id = int(context.args[0])
            start_time = datetime.strptime(context.args[1], '%Y.%m.%d.%H.%M')
            end_time = datetime.strptime(context.args[2], '%Y.%m.%d.%H.%M')
            shift = Shift(
                point_id=point_id, start_time=start_time, end_time=end_time
            )
            session.add(shift)
            session.commit()
            await update.message.reply_text('Смена добавлена.')
        else:
            await update.message.reply_text(
                'Вы не имеете права добавлять смены.'
            )
    except Exception:
        logger.error(traceback.format_exc())
        await update.message.reply_text(
            'Некорректный запрос на добавление смены. \n'
            'Проверьте формат даты и времени: ГГГГ.ММ.ДД.ЧЧ.ММ'
        )
    finally:
        session.close()


async def edit_shift(update: Update, context: CallbackContext) -> None:
    if len(context.args) < 3:
        return await update.message.reply_text(
            'Пожалуйста, укажите id, '
            'дату и время начала и конца смены.'
        )

    session = Session()
    try:
        telegram_id = update.message.from_user.id
        user = session.query(User).filter_by(
            telegram_id=telegram_id
        ).first()
        if user and user.role == 'owner':
            id = context.args[0]
            new_start_time = datetime.strptime(context.args[1], '%Y.%m.%d.%H.%M')
            new_end_time = datetime.strptime(context.args[2], '%Y.%m.%d.%H.%M')

            shift = session.query(Shift).filter_by(
                id=id
            ).first()
            if shift:
                shift.start_time = new_start_time 
                shift.end_time = new_end_time
                session.add(shift)
                session.commit()
                await update.message.reply_text('Смена изменена.')
            else:
                await update.message.reply_text(
                    'Смена с таким id не найдена.'
                )
        else:
            await update.message.reply_text(
                'Вы не имеете права изменять смены.'
            )
    except Exception:
        logger.error(traceback.format_exc())
        await update.message.reply_text(
            'Некорректный запрос на редактирование смены. \n'
            'Проверьте формат даты и времени: ГГГГ.ММ.ДД.ЧЧ.ММ'
        )
    finally:
        session.close()


async def delete_shift(update: Update, context: CallbackContext) -> None:
    if len(context.args) < 1:
        return await update.message.reply_text(
            'Пожалуйста, укажите id смены.'
        )

    session = Session()
    try:
        telegram_id = update.message.from_user.id
        user = session.query(User).filter_by(
            telegram_id=telegram_id
        ).first()
        if user and user.role == 'owner':
            id = context.args[0]

            shift = session.query(Shift).filter_by(
                id=id
            ).first()
            if shift:
                session.delete(shift)
                session.commit()
                await update.message.reply_text('Смена удалена.')
            else:
                await update.message.reply_text(
                    'Смена с таким id не найдена.'
                )
        else:
            await update.message.reply_text(
                'Вы не имеете права удалять смены.'
            )
    except Exception:
        logger.error(traceback.format_exc())
        await update.message.reply_text(
            'Некорректный запрос на удаление смены.'
        )
    finally:
        session.close()                


async def rate_manager(update: Update, context: CallbackContext) -> None:
    if len(context.args) < 3:
        return await update.message.reply_text(
            'Пожалуйста, укажите id пункта выдачи, рейтинг и отзыв.'
        )

    session = Session()
    try:
        point_id = int(context.args[0])
        rating = float(context.args[1])
        comment = ' '.join(context.args[2:])
        point = session.query(Point).filter_by(id=point_id).first()
        if point:
            review = Review(
                user_id=update.message.from_user.id,
                point_id=point_id,
                rating=rating,
                comment=comment,
            )
            session.add(review)
            session.commit()
            await update.message.reply_text('Пункт выдачи оценен.')
        else:
            await update.message.reply_text('Пункт выдачи не найден.')
    except Exception:
        logger.error(traceback.format_exc())
        await update.message.reply_text(
            'Некорректный запрос на оценивание пункта выдачи.'
        )        
    finally:
        session.close()


async def rate_worker(update: Update, context: CallbackContext) -> None:
    if len(context.args) < 1:
        return await update.message.reply_text(
            'Пожалуйста, укажите id работника, рейтинг и отзыв.'
        )

    session = Session()
    try:
        user_id = int(context.args[0])
        rating = float(context.args[1])
        comment = ' '.join(context.args[2:])
        worker = session.query(User).filter_by(id=user_id).first()
        if worker:
            review = Review(
                user_id=worker.id, rating=rating, comment=comment
            )
            session.add(review)
            session.commit()
            await update.message.reply_text('Работник оценен.')
        else:
            await update.message.reply_text('Работник не найден.')
    except Exception:
        logger.error(traceback.format_exc())
        await update.message.reply_text(
            'Некорректный запрос на оценивание работника.'
        )        
    finally:
        session.close()


async def view_ratings(update: Update, context: CallbackContext) -> None:
    if len(context.args) < 1:
        return await update.message.reply_text(
            'Пожалуйста, укажите id пункта выдачи или работника.'
        )

    session = Session()
    try:
        point_or_user_id = int(context.args[0])
        reviews = session.query(Review).filter(
            (Review.point_id == point_or_user_id) |
            (Review.user_id == point_or_user_id)
        ).all()
        message = ''
        for review in reviews:
            message += (
                f'Рейтинг: {review.rating}, Отзыв: {review.comment}\n'
            )
        await update.message.reply_text(
            message if message else 'Отзывов нет.'
        )
    except Exception:
        logger.error(traceback.format_exc())
        await update.message.reply_text(
            'Некорректный запрос на просмотр рейтингов и комментариев.'
        )
    finally:
        session.close()
