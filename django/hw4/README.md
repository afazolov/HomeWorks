# Django — ДЗ #2

## Описание

Django-проект с двумя приложениями: **рабочие места** и **сотрудники**.

## Запуск

```bash
cd django/hw2
python manage.py migrate
python manage.py runserver
```

Сервер: http://127.0.0.1:8000
Админка: http://127.0.0.1:8000/admin

**Логин:** `admin`
**Пароль:** `admin123`

## Модели

**workplaces** — `Workplace`: номер стола, кабинет, монитор, заметки.

**employees**:
- `Employee` — расширяет стандартного User: отчество, пол, описание, рабочее место (OneToOne → Workplace)
- `Skill` — справочник навыков (фронтенд, бэкенд, тестирование и т.д.)
- `EmployeeSkill` — навык сотрудника с уровнем освоения от 1 до 10

## Зависимости

```bash
pip install -r requirements.txt
```
