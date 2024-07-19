from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from telegram_token import TELEGRAM_TOKEN
from handlers1 import (
    start, register, handle_reg_button,
    my_points, add_point, edit_point, delete_point,
    schedule, add_shift, edit_shift, delete_shift,
    rate_manager, rate_worker, view_ratings,
)


def main() -> None:
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('register', register))
    application.add_handler(CallbackQueryHandler(handle_reg_button))

    application.add_handler(CommandHandler('mypoints',  my_points))
    application.add_handler(CommandHandler('addpoint', add_point))
    application.add_handler(CommandHandler('editpoint', edit_point))
    application.add_handler(CommandHandler('deletepoint', delete_point))

    application.add_handler(CommandHandler('schedule',  schedule))
    application.add_handler(CommandHandler('addshift', add_shift))
    application.add_handler(CommandHandler('editshift', edit_shift))
    application.add_handler(CommandHandler('deleteshift', delete_shift))

    application.add_handler(CommandHandler('ratemanager', rate_manager))
    application.add_handler(CommandHandler('rateworker', rate_worker))
    application.add_handler(CommandHandler('viewratings', view_ratings))

    application.run_polling()


if __name__ == '__main__':
    main()
