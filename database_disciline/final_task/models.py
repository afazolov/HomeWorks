"""
Модель задачи (Task).
"""


class Task:
    """
    Описывает одну задачу в списке дел.

    Поля:
        id           — уникальный номер задачи (генерируется автоматически)
        name         — название задачи
        is_completed — статус выполнения (по умолчанию False)
    """

    # Счётчик для автоматической генерации id (используется при работе без БД)
    _counter: int = 0

    def __init__(self, name: str, task_id: int = None, is_completed: bool = False):
        if task_id is not None:
            # id передан явно (например, из базы данных)
            self.id = task_id
        else:
            # Автогенерация id
            Task._counter += 1
            self.id = Task._counter

        self.name: str = name
        self.is_completed: bool = is_completed  # При создании задача не выполнена

    def complete(self) -> None:
        """Отметить задачу как выполненную."""
        self.is_completed = True

    def __str__(self) -> str:
        """Красивый вывод задачи в чат."""
        status = "✅" if self.is_completed else "❌"
        return f"Задача №{self.id}: {self.name} {status}"
