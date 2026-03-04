# Group Collects API

REST API для групповых денежных сборов на Django REST Framework.

## Стек

- Python 3.11 / Django 5.2 / DRF 3.15
- PostgreSQL 15
- drf-spectacular (Swagger)
- django-cors-headers
- Docker + docker-compose

## Запуск через Docker (рекомендуется)

```bash
docker-compose up --build
```

После запуска:
- API: http://localhost:8000/api/v1/
- Swagger: http://localhost:8000/api/docs/
- Admin: http://localhost:8000/admin/

Создать суперпользователя:

```bash
docker-compose exec web python manage.py createsuperuser
```

## Запуск локально

1. Установить зависимости:

```bash
pip install -r requirements.txt
```

2. Создать базу данных PostgreSQL:

```sql
CREATE DATABASE backend_final;
```

3. Настроить `.env` (уже создан, при необходимости изменить `DB_HOST=localhost`):

```
DB_HOST=localhost
```

4. Применить миграции и запустить:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Запуск тестов

```bash
pytest
# или
python manage.py test collects
```

## Эндпоинты API

| Метод | URL | Описание |
|-------|-----|----------|
| POST | /api/v1/users/ | Регистрация пользователя |
| GET | /api/v1/users/ | Список пользователей (авт.) |
| GET | /api/v1/collects/ | Список сборов |
| POST | /api/v1/collects/ | Создать сбор (авт.) |
| GET | /api/v1/collects/{id}/ | Детали сбора + платежи |
| PUT/PATCH | /api/v1/collects/{id}/ | Обновить сбор (только автор) |
| DELETE | /api/v1/collects/{id}/ | Удалить сбор (только автор) |
| GET | /api/v1/payments/ | Мои платежи (авт.) |
| POST | /api/v1/payments/ | Сделать платёж (авт.) |

## Суперпользователь (по умолчанию)

Создаётся вручную командой `createsuperuser`.
