"""
Алгоритмы сортировки для списка CartItem.

Каждая функция принимает:
    items     — список CartItem
    key       — строка-ключ: "price" | "weight" | "category"
    reverse   — False = по возрастанию, True = по убыванию
    steps     — True = записывать промежуточные состояния

Возвращает кортеж:
    (отсортированный список CartItem, список строк-шагов)
"""

from __future__ import annotations
from models import CartItem


# ---------------------------------------------------------------------------
# Вспомогательные функции
# ---------------------------------------------------------------------------

def _key_func(item: CartItem, key: str) -> float | str:
    """Возвращает значение поля для сравнения."""
    if key == "price":
        return item.product.price
    if key == "weight":
        return item.product.weight
    if key == "category":
        return item.product.category.lower()
    raise ValueError(f"Неизвестный ключ сортировки: {key}")


def _snapshot(items: list[CartItem], key: str) -> str:
    """Текстовый снимок состояния списка для шага сортировки."""
    parts = [f"{item.product.name}({_key_func(item, key)})" for item in items]
    return " → ".join(parts)


def _apply_reverse(items: list[CartItem], reverse: bool) -> list[CartItem]:
    if reverse:
        items.reverse()
    return items


# ---------------------------------------------------------------------------
# Пузырьковая сортировка — O(n²)
# ---------------------------------------------------------------------------

def bubble_sort(
    items: list[CartItem],
    key: str = "price",
    reverse: bool = False,
    steps: bool = False,
) -> tuple[list[CartItem], list[str]]:
    """
    Сортировка пузырьком.
    На каждом проходе «всплывает» наибольший элемент.
    Шаг записывается после каждого прохода внешнего цикла.
    """
    arr = items.copy()
    n = len(arr)
    log: list[str] = []

    for i in range(n):
        swapped = False
        for j in range(n - i - 1):
            # Сравниваем соседние элементы
            if _key_func(arr[j], key) > _key_func(arr[j + 1], key):
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if steps:
            log.append(f"Проход {i + 1}: {_snapshot(arr, key)}")
        if not swapped:
            # Досрочное завершение — список уже отсортирован
            if steps:
                log.append("↳ Список отсортирован досрочно")
            break

    return _apply_reverse(arr, reverse), log


# ---------------------------------------------------------------------------
# Сортировка вставками — O(n²)
# ---------------------------------------------------------------------------

def insertion_sort(
    items: list[CartItem],
    key: str = "price",
    reverse: bool = False,
    steps: bool = False,
) -> tuple[list[CartItem], list[str]]:
    """
    Сортировка вставками.
    Каждый элемент вставляется на своё место в уже отсортированную часть.
    Шаг записывается после каждой вставки.
    """
    arr = items.copy()
    log: list[str] = []

    for i in range(1, len(arr)):
        key_val = _key_func(arr[i], key)
        current = arr[i]
        j = i - 1

        # Сдвигаем элементы отсортированной части вправо
        while j >= 0 and _key_func(arr[j], key) > key_val:
            arr[j + 1] = arr[j]
            j -= 1

        arr[j + 1] = current   # Вставляем на найденное место

        if steps:
            log.append(f"Вставка [{i}]: {_snapshot(arr, key)}")

    return _apply_reverse(arr, reverse), log


# ---------------------------------------------------------------------------
# Быстрая сортировка — O(n log n) в среднем
# ---------------------------------------------------------------------------

def quick_sort(
    items: list[CartItem],
    key: str = "price",
    reverse: bool = False,
    steps: bool = False,
) -> tuple[list[CartItem], list[str]]:
    """
    Быстрая сортировка.
    Делит список на три части вокруг опорного элемента (pivot).
    Шаг записывается после каждого разбиения.
    """
    log: list[str] = []

    def _qsort(arr: list[CartItem]) -> list[CartItem]:
        if len(arr) <= 1:
            return arr
        pivot = arr[len(arr) // 2]
        pivot_val = _key_func(pivot, key)
        left   = [x for x in arr if _key_func(x, key) <  pivot_val]
        middle = [x for x in arr if _key_func(x, key) == pivot_val]
        right  = [x for x in arr if _key_func(x, key) >  pivot_val]
        if steps:
            log.append(
                f"Pivot={pivot.product.name}({pivot_val})  "
                f"< [{', '.join(x.product.name for x in left)}]  "
                f"> [{', '.join(x.product.name for x in right)}]"
            )
        return _qsort(left) + middle + _qsort(right)

    result = _qsort(items.copy())
    return _apply_reverse(result, reverse), log


# ---------------------------------------------------------------------------
# Сортировка слиянием — O(n log n)
# ---------------------------------------------------------------------------

def merge_sort(
    items: list[CartItem],
    key: str = "price",
    reverse: bool = False,
    steps: bool = False,
) -> tuple[list[CartItem], list[str]]:
    """
    Сортировка слиянием.
    Делит список пополам, сортирует рекурсивно, сливает.
    Шаг записывается после каждого слияния.
    """
    log: list[str] = []

    def _merge(left: list[CartItem], right: list[CartItem]) -> list[CartItem]:
        result, i, j = [], 0, 0
        while i < len(left) and j < len(right):
            if _key_func(left[i], key) <= _key_func(right[j], key):
                result.append(left[i]); i += 1
            else:
                result.append(right[j]); j += 1
        result.extend(left[i:])
        result.extend(right[j:])
        if steps:
            log.append(f"Слияние: {_snapshot(result, key)}")
        return result

    def _msort(arr: list[CartItem]) -> list[CartItem]:
        if len(arr) <= 1:
            return arr
        mid = len(arr) // 2
        return _merge(_msort(arr[:mid]), _msort(arr[mid:]))

    result = _msort(items.copy())
    return _apply_reverse(result, reverse), log


# ---------------------------------------------------------------------------
# Единая точка входа
# ---------------------------------------------------------------------------

ALGORITHMS = {
    "Пузырьком":  bubble_sort,
    "Вставками":  insertion_sort,
    "Быстрая":    quick_sort,
    "Слиянием":   merge_sort,
}

SORT_KEYS = {
    "Цена":      "price",
    "Вес":       "weight",
    "Категория": "category",
}


def sort_cart(
    items: list[CartItem],
    algorithm: str,
    key: str,
    reverse: bool = False,
    steps: bool = False,
) -> tuple[list[CartItem], list[str]]:
    """
    Сортирует список CartItem выбранным алгоритмом.

    algorithm — один из ключей ALGORITHMS
    key       — один из ключей SORT_KEYS
    """
    if algorithm not in ALGORITHMS:
        raise ValueError(f"Неизвестный алгоритм: {algorithm}")
    if key not in SORT_KEYS:
        raise ValueError(f"Неизвестный ключ: {key}")
    return ALGORITHMS[algorithm](items, SORT_KEYS[key], reverse, steps)
