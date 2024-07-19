from telegram.ext import Application, CommandHandler

from handlers.points import (
    start, add_point_conv_handler, edit_point_conv_handler, 
    delete_point_conv_handler,
)
from telegram_token import TELEGRAM_TOKEN


def main() -> None:
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(add_point_conv_handler)
    application.add_handler(edit_point_conv_handler)
    application.add_handler(delete_point_conv_handler)

    application.run_polling()


if __name__ == '__main__':
    main()
