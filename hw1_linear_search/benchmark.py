"""
Замер производительности линейного поиска
------------------------------------------
K3: Создаём список из 100 случайных чисел и выполняем поиск нескольких значений.
K4: Сравниваем время выполнения для разных размеров списков и строим график.
"""

import random
import time
import matplotlib.pyplot as plt

from linear_search import linear_search


# ---------------------------------------------------------------------------
# K3 — Список из 100 случайных чисел, поиск нескольких значений
# ---------------------------------------------------------------------------
def demo_100_elements():
    # Фиксируем seed для воспроизводимости результатов
    random.seed(42)
    # Генерируем 100 случайных чисел в диапазоне [1, 200]
    numbers = [random.randint(1, 200) for _ in range(100)]

    print("=" * 55)
    print("K3: Линейный поиск в списке из 100 случайных чисел")
    print("=" * 55)
    print(f"Список: {numbers}\n")

    # Ищем: первый элемент, средний, последний, и два отсутствующих
    search_targets = [numbers[0], numbers[49], numbers[99], 201, 202]

    print(f"{'Элемент':>10} | {'Индекс':>8} | {'Найден?'}")
    print("-" * 35)
    for target in search_targets:
        idx = linear_search(numbers, target)
        found = "Да" if idx != -1 else "Нет"
        print(f"{target:>10} | {idx:>8} | {found}")
    print()


# ---------------------------------------------------------------------------
# K4 — Замер времени для разных размеров списков
# ---------------------------------------------------------------------------
def benchmark():
    # Размеры списков для сравнения
    sizes = [10, 100, 1000, 10_000, 100_000, 1_000_000]
    times = []

    print("=" * 55)
    print("K4: Время выполнения в зависимости от размера списка")
    print("=" * 55)
    print(f"{'Размер':>12} | {'Время (мс)':>12}")
    print("-" * 28)

    for size in sizes:
        # Создаём список [0, 1, 2, ..., size-1]
        data = list(range(size))

        # Худший случай: ищем элемент, которого нет в списке (-1)
        # Алгоритм обойдёт весь список — честное измерение O(n)
        target = -1

        # Повторяем замер несколько раз, чтобы усреднить результат
        # Чем больше список, тем меньше повторений нужно
        repetitions = max(1, 1_000_000 // size)
        start = time.perf_counter()
        for _ in range(repetitions):
            linear_search(data, target)
        # Переводим секунды в миллисекунды на один вызов
        elapsed = (time.perf_counter() - start) / repetitions * 1000

        times.append(elapsed)
        print(f"{size:>12,} | {elapsed:>12.6f}")

    print()
    return sizes, times


def plot_results(sizes, times):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # --- Левый график: линейный масштаб ---
    # Показывает наглядный линейный рост времени с увеличением n
    axes[0].plot(sizes, times, marker="o", color="steelblue", linewidth=2)
    axes[0].set_title("Линейный поиск — время vs размер\n(линейный масштаб)")
    axes[0].set_xlabel("Размер списка (n)")
    axes[0].set_ylabel("Время на один вызов (мс)")
    axes[0].grid(True, linestyle="--", alpha=0.5)

    # Аннотация вывода прямо на левом графике
    axes[0].annotate(
        "Время растёт\nпропорционально n\n→ O(n)",
        xy=(sizes[-1], times[-1]),
        xytext=(sizes[-2], times[-1] * 0.5),
        arrowprops=dict(arrowstyle="->", color="steelblue"),
        fontsize=9,
        color="steelblue",
    )

    # --- Правый график: логарифмический масштаб по обеим осям ---
    # При O(n) зависимость log(t) ~ log(n) — прямая линия с наклоном 1
    # Если бы сложность была O(n²) — наклон был бы 2; O(log n) — наклон < 1
    axes[1].plot(sizes, times, marker="o", color="darkorange", linewidth=2)
    axes[1].set_xscale("log")
    axes[1].set_yscale("log")
    axes[1].set_title("Линейный поиск — время vs размер\n(лог-лог масштаб: O(n) = прямая линия)")
    axes[1].set_xlabel("Размер списка (n)")
    axes[1].set_ylabel("Время на один вызов (мс)")
    axes[1].grid(True, which="both", linestyle="--", alpha=0.5)

    # Аннотация вывода на правом графике
    axes[1].annotate(
        "Прямая линия\nна лог-лог =\nподтверждение O(n)",
        xy=(sizes[-2], times[-2]),
        xytext=(sizes[1], times[-1]),
        arrowprops=dict(arrowstyle="->", color="darkorange"),
        fontsize=9,
        color="darkorange",
    )

    plt.tight_layout()
    output_path = "benchmark_plot.png"
    plt.savefig(output_path, dpi=150)
    print(f"График сохранён: {output_path}")
    plt.show()


if __name__ == "__main__":
    demo_100_elements()
    sizes, times = benchmark()
    plot_results(sizes, times)
