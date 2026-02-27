"""
Хранилище задач.

Режимы работы:
  - PostgreSQL (задание повышенного уровня) — если доступна БД из .env
  - In-memory fallback                      — если PostgreSQL недоступен

При запуске автоматически проверяется соединение. Если PostgreSQL
недоступен, выводится предупреждение и бот работает с хранением в памяти
(данные сбрасываются при перезапуске).
"""

import os
from models import Task

# ---------------------------------------------------------------------------
# Попытка подключить psycopg2
# ---------------------------------------------------------------------------
try:
    import psycopg2
    _PSYCOPG2_AVAILABLE = True
except ImportError:
    _PSYCOPG2_AVAILABLE = False


# ---------------------------------------------------------------------------
# Глобальное состояние: режим работы и in-memory хранилище
# ---------------------------------------------------------------------------

USE_DB: bool = False   # True если PostgreSQL доступен и настроен

# In-memory хранилище: { user_id: { task_id: Task } }
_store: dict[int, dict[int, Task]] = {}
_next_id: int = 1      # автоинкремент для in-memory режима


# ---------------------------------------------------------------------------
# Подключение к PostgreSQL
# ---------------------------------------------------------------------------

def _get_connection():
    """Создаёт соединение с PostgreSQL из переменных окружения."""
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 5432)),
        database=os.getenv("DB_NAME", "todo_bot"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
    )


# ---------------------------------------------------------------------------
# Инициализация
# ---------------------------------------------------------------------------

def create_table() -> None:
    """
    Пробует подключиться к PostgreSQL и создать таблицу tasks.
    Если не удаётся — переключается на in-memory режим.
    """
    global USE_DB

    if not _PSYCOPG2_AVAILABLE:
        print("[DB] psycopg2 не установлен — используется хранение в памяти")
        USE_DB = False
        return

    try:
        conn = _get_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id           SERIAL PRIMARY KEY,
                user_id      BIGINT      NOT NULL,
                name         TEXT        NOT NULL,
                is_completed BOOLEAN     DEFAULT FALSE
            )
        """)
        conn.commit()
        cur.close()
        conn.close()
        USE_DB = True
        print("[DB] Подключение к PostgreSQL успешно")
    except Exception as e:
        USE_DB = False
        print(f"[DB] PostgreSQL недоступен ({e})\n"
              f"[DB] Используется хранение в памяти (данные сбросятся при перезапуске)")


# ---------------------------------------------------------------------------
# CRUD: PostgreSQL
# ---------------------------------------------------------------------------

def _pg_add_task(user_id: int, name: str) -> Task:
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tasks (user_id, name) VALUES (%s, %s) RETURNING id",
        (user_id, name),
    )
    task_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return Task(name=name, task_id=task_id, is_completed=False)


def _pg_get_tasks(user_id: int) -> list[Task]:
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, name, is_completed FROM tasks WHERE user_id = %s ORDER BY id",
        (user_id,),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [Task(name=row[1], task_id=row[0], is_completed=row[2]) for row in rows]


def _pg_complete_task(user_id: int, task_id: int) -> bool:
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE tasks SET is_completed = TRUE WHERE id = %s AND user_id = %s",
        (task_id, user_id),
    )
    updated = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    return updated > 0


def _pg_delete_task(user_id: int, task_id: int) -> bool:
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM tasks WHERE id = %s AND user_id = %s",
        (task_id, user_id),
    )
    deleted = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    return deleted > 0


# ---------------------------------------------------------------------------
# CRUD: In-memory
# ---------------------------------------------------------------------------

def _mem_add_task(user_id: int, name: str) -> Task:
    global _next_id
    task = Task(name=name, task_id=_next_id, is_completed=False)
    _next_id += 1
    if user_id not in _store:
        _store[user_id] = {}
    _store[user_id][task.id] = task
    return task


def _mem_get_tasks(user_id: int) -> list[Task]:
    return list(_store.get(user_id, {}).values())


def _mem_complete_task(user_id: int, task_id: int) -> bool:
    user_tasks = _store.get(user_id, {})
    if task_id not in user_tasks:
        return False
    user_tasks[task_id].complete()
    return True


def _mem_delete_task(user_id: int, task_id: int) -> bool:
    user_tasks = _store.get(user_id, {})
    if task_id not in user_tasks:
        return False
    del user_tasks[task_id]
    return True


# ---------------------------------------------------------------------------
# Публичный интерфейс — автоматически выбирает нужный бэкенд
# ---------------------------------------------------------------------------

def add_task(user_id: int, name: str) -> Task:
    """Добавить задачу. Возвращает созданный объект Task."""
    return _pg_add_task(user_id, name) if USE_DB else _mem_add_task(user_id, name)


def get_tasks(user_id: int) -> list[Task]:
    """Получить все задачи пользователя."""
    return _pg_get_tasks(user_id) if USE_DB else _mem_get_tasks(user_id)


def complete_task(user_id: int, task_id: int) -> bool:
    """Отметить задачу выполненной. Возвращает False если задача не найдена."""
    return _pg_complete_task(user_id, task_id) if USE_DB else _mem_complete_task(user_id, task_id)


def delete_task(user_id: int, task_id: int) -> bool:
    """Удалить задачу. Возвращает False если задача не найдена."""
    return _pg_delete_task(user_id, task_id) if USE_DB else _mem_delete_task(user_id, task_id)
