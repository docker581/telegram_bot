# telegram_bot

## Описание
Telegram-бот для работы со сменами в ПВЗ (пунктах выдачи заказов)

## Стек технологий
- Python 3.11.4
- prettytable 3.10.0
- python-dotenv 1.0.1
- python-telegram-bot 21.3
- python-telegram-bot-calendar 1.0.5
- SQLAlchemy 2.0.31

## Команды
### Клонирование репозитория
```bash
git clone https://github.com/docker581/telegram_bot
```

### Пример файла .env
```bash
TELEGRAM_TOKEN=token
```

### Запуск приложения
```bash
python bot.py
```

### Команды бота
```bash
/register - регистрация пользователя
/mypoints - просмотр списка пунктов выдачи
/addpoint - добавление пункта выдачи
/editpoint - редактирование пункта выдачи
/deletepoint - удаление пункта выдачи
/schedule - просмотр списка смен
/addshift - добавление смены
/editshift - редактирование смены
/deleteshift - удаление смены
```

## Автор
Докторов Денис
