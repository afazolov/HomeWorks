# Dating App API

REST API платформы для знакомств — Django REST Framework + JWT + PostgreSQL.

## Стек

- Python 3.11 / Django 5.2 / DRF 3.15
- PostgreSQL 15
- JWT — djangorestframework-simplejwt
- drf-spectacular (Swagger)
- django-cors-headers
- Docker + docker-compose

## Запуск через Docker (рекомендуется)

```bash
cd django_final
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

1. Создать БД:
```sql
CREATE DATABASE dating_app;
```

2. Изменить `DB_HOST=localhost` в `.env`

3. Установить зависимости и применить миграции:
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Запуск тестов

```bash
DB_HOST=localhost python manage.py test profiles
# или
DB_HOST=localhost pytest
```

## Аутентификация (JWT)

```http
POST /api/auth/token/
Content-Type: application/json

{"email": "user@example.com", "password": "pass"}
```

Полученный `access` токен передавать в заголовке:
```
Authorization: Bearer <token>
```

## Основные эндпоинты

| Метод | URL | Описание |
|-------|-----|----------|
| POST | /api/v1/register/ | Регистрация |
| POST | /api/auth/token/ | Получить JWT токен |
| GET/PATCH | /api/v1/users/me/ | Свой профиль |
| GET | /api/v1/users/random/ | Случайный профиль (с фильтрами) |
| GET | /api/v1/users/{id}/profile/ | Просмотр профиля |
| GET | /api/v1/users/liked/ | Кому поставил лайк |
| GET | /api/v1/users/disliked/ | Кому поставил дизлайк |
| GET | /api/v1/users/like-history/ | Кто лайкнул меня |
| GET | /api/v1/users/view-history/ | История просмотров |
| GET | /api/v1/users/mutual-likes/ | Взаимные лайки |
| POST | /api/v1/likes/ | Лайк / дизлайк |
| GET/POST | /api/v1/photos/ | Фотогалерея |
| POST | /api/v1/photos/{id}/set-main/ | Установить заглавное фото |
| GET/POST | /api/v1/invites/ | Приглашения на свидание |
| POST | /api/v1/invites/{id}/respond/ | Принять / отклонить приглашение |

### Фильтры для /api/v1/users/random/

| Параметр | Пример |
|----------|--------|
| gender | ?gender=female |
| city | ?city=Москва |
| status | ?status=searching |
| age_min | ?age_min=20 |
| age_max | ?age_max=35 |
