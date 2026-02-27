"""
K4 — Класс Stack (Стек)
------------------------
Стек — структура данных по принципу LIFO (Last In, First Out):
последний добавленный элемент извлекается первым.

Аналогия: стопка тарелок — кладём сверху, берём тоже сверху.

Реализованные операции:
  push(item)  — добавить элемент на вершину стека
  pop()       — извлечь и вернуть элемент с вершины стека
  peek()      — посмотреть на вершину стека, не извлекая
  is_empty()  — проверить, пуст ли стек
  size()      — количество элементов в стеке
"""


class Stack:
    """
    Стек на основе списка Python.

    Все основные операции (push, pop, peek) работают за O(1).
    """

    def __init__(self):
        # Внутренний список: правый конец — вершина стека
        self._data = []

    def push(self, item) -> None:
        """
        Добавляет элемент item на вершину стека.
        Сложность: O(1)
        """
        self._data.append(item)

    def pop(self):
        """
        Извлекает и возвращает элемент с вершины стека.
        Сложность: O(1)

        Вызывает IndexError, если стек пуст.
        """
        if self.is_empty():
            raise IndexError("pop из пустого стека")
        # list.pop() без аргумента снимает последний элемент — это вершина
        return self._data.pop()

    def peek(self):
        """
        Возвращает элемент с вершины стека, НЕ удаляя его.
        Сложность: O(1)

        Вызывает IndexError, если стек пуст.
        """
        if self.is_empty():
            raise IndexError("peek на пустом стеке")
        return self._data[-1]  # последний элемент = вершина

    def is_empty(self) -> bool:
        """
        Возвращает True, если стек пуст, иначе False.
        Сложность: O(1)
        """
        return len(self._data) == 0

    def size(self) -> int:
        """
        Возвращает количество элементов в стеке.
        Сложность: O(1)
        """
        return len(self._data)

    def __repr__(self) -> str:
        """Текстовое представление стека (вершина справа)."""
        return f"Stack({self._data}  ← вершина)"


# ---------------------------------------------------------------------------
# Демонстрация всех операций
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    stack = Stack()

    print("=== Создали пустой стек ===")
    print(f"Пустой? {stack.is_empty()}")   # True
    print(f"Размер: {stack.size()}\n")     # 0

    print("=== push: добавляем 10, 20, 30 ===")
    stack.push(10)
    stack.push(20)
    stack.push(30)
    print(stack)                           # Stack([10, 20, 30]  ← вершина)
    print(f"Размер: {stack.size()}\n")     # 3

    print("=== peek: смотрим на вершину ===")
    print(f"Вершина: {stack.peek()}")      # 30
    print(f"Стек не изменился: {stack}\n")

    print("=== pop: снимаем элементы ===")
    print(f"Снято: {stack.pop()}")         # 30
    print(f"Снято: {stack.pop()}")         # 20
    print(stack)                           # Stack([10]  ← вершина)
    print(f"Размер: {stack.size()}\n")     # 1

    print("=== pop последнего элемента ===")
    print(f"Снято: {stack.pop()}")         # 10
    print(f"Пустой? {stack.is_empty()}")   # True

    print("\n=== Попытка pop из пустого стека ===")
    try:
        stack.pop()
    except IndexError as e:
        print(f"Ошибка: {e}")
