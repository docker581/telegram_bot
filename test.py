from telegram.ext import Application

from handlers.users import start_handler, reg_handler, reg_button_handler
from handlers.points import (
    my_points_handler, add_point_conv_handler, 
    edit_point_conv_handler, delete_point_conv_handler,
)
from handlers.shifts import schedule_handler, add_shift_conv_handler
from telegram_token import TELEGRAM_TOKEN


def main() -> None:
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(start_handler)
    # application.add_handler(reg_handler)
    # application.add_handler(reg_button_handler)

    application.add_handler(schedule_handler)
    application.add_handler(add_shift_conv_handler)
    application.add_handler(reg_handler)
    application.add_handler(reg_button_handler)

    application.add_handler(my_points_handler)
    application.add_handler(add_point_conv_handler)
    application.add_handler(edit_point_conv_handler)
    application.add_handler(delete_point_conv_handler)

    # application.add_handler(schedule_handler)
    # application.add_handler(add_shift_conv_handler)

    application.run_polling()


if __name__ == '__main__':
    main()
