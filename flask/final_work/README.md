# FlaskBlog

Веб-приложение для ведения блогов на Flask с аутентификацией и CRUD постов.

## Стек

- Python 3.10+ / Flask 3.x
- Flask-SQLAlchemy (ORM) + Flask-Migrate (миграции)
- Flask-Login (аутентификация) + Werkzeug (хэширование паролей)
- Flask-WTF (формы + CSRF)
- Bootstrap 5 (UI)
- SQLite (база данных)

## Запуск

```bash
cd flask/final_work
pip install -r requirements.txt
flask db init
flask db migrate -m "initial"
flask db upgrade
python run.py
```

Приложение доступно по адресу: http://localhost:5000

## Функциональность

- Регистрация и вход / выход
- Просмотр всех постов с пагинацией (5 на страницу)
- Создание, редактирование и удаление постов (только для авторизованных)
- Редактирование и удаление доступно только автору поста
- Валидация форм (уникальность email/username, минимальная длина пароля и т.д.)
