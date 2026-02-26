"""
Сравнение производительности алгоритмов сортировки
----------------------------------------------------
K3: Замеряем время работы трёх алгоритмов (пузырьком, выбором,
    вставками) на одинаковых списках разного размера.
    Строим общий график зависимости времени от размера списка.
"""

import random
import time
import matplotlib.pyplot as plt

from bubble_sort import bubble_sort
from selection_sort import selection_sort
from insertion_sort import insertion_sort


def measure_time(sort_func, data: list) -> float:
    """
    Замеряет время выполнения sort_func на списке data.
    Возвращает время в миллисекундах.
    """
    start = time.perf_counter()
    sort_func(data)
    return (time.perf_counter() - start) * 1000  # переводим в мс


def benchmark():
    # Размеры списков для сравнения
    # Алгоритмы O(n²) медленные, поэтому ограничиваемся 5000
    sizes = [10, 100, 500, 1000, 2000, 3000, 5000]

    times_bubble    = []
    times_selection = []
    times_insertion = []

    print("=" * 70)
    print("K3: Сравнение времени сортировки пузырьком, выбором и вставками")
    print("=" * 70)
    print(f"{'Размер':>8} | {'Пузырьком (мс)':>16} | {'Выбором (мс)':>14} | {'Вставками (мс)':>16}")
    print("-" * 62)

    for size in sizes:
        # Одинаковый случайный список для честного сравнения
        random.seed(0)
        data = [random.randint(1, 10_000) for _ in range(size)]

        t_bubble    = measure_time(bubble_sort,    data)
        t_selection = measure_time(selection_sort, data)
        t_insertion = measure_time(insertion_sort, data)

        times_bubble.append(t_bubble)
        times_selection.append(t_selection)
        times_insertion.append(t_insertion)

        print(f"{size:>8,} | {t_bubble:>16.4f} | {t_selection:>14.4f} | {t_insertion:>16.4f}")

    print()
    return sizes, times_bubble, times_selection, times_insertion


def plot_results(sizes, times_bubble, times_selection, times_insertion):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # --- Левый график: линейный масштаб ---
    # Хорошо показывает разницу в абсолютном времени
    axes[0].plot(sizes, times_bubble,    marker="o", color="tomato",
                 linewidth=2, label="Пузырьком O(n²)")
    axes[0].plot(sizes, times_selection, marker="s", color="steelblue",
                 linewidth=2, label="Выбором O(n²)")
    axes[0].plot(sizes, times_insertion, marker="^", color="seagreen",
                 linewidth=2, label="Вставками O(n²)")
    axes[0].set_title("Сравнение алгоритмов сортировки\n(линейный масштаб)")
    axes[0].set_xlabel("Размер списка (n)")
    axes[0].set_ylabel("Время выполнения (мс)")
    axes[0].legend()
    axes[0].grid(True, linestyle="--", alpha=0.5)

    # Аннотация: пузырьковая сортировка обычно медленнее остальных
    axes[0].annotate(
        "Пузырьковая\nчаще всего\nмедленнее",
        xy=(sizes[-1], times_bubble[-1]),
        xytext=(sizes[-3], times_bubble[-1] * 0.7),
        arrowprops=dict(arrowstyle="->", color="tomato"),
        fontsize=9,
        color="tomato",
    )

    # --- Правый график: логарифмический масштаб ---
    # На лог-лог все три O(n²) алгоритма дают прямые с наклоном ~2
    axes[1].plot(sizes, times_bubble,    marker="o", color="tomato",
                 linewidth=2, label="Пузырьком O(n²)")
    axes[1].plot(sizes, times_selection, marker="s", color="steelblue",
                 linewidth=2, label="Выбором O(n²)")
    axes[1].plot(sizes, times_insertion, marker="^", color="seagreen",
                 linewidth=2, label="Вставками O(n²)")
    axes[1].set_xscale("log")
    axes[1].set_yscale("log")
    axes[1].set_title("Сравнение алгоритмов сортировки\n(лог-лог масштаб: O(n²) = прямая с наклоном 2)")
    axes[1].set_xlabel("Размер списка (n)")
    axes[1].set_ylabel("Время выполнения (мс)")
    axes[1].legend()
    axes[1].grid(True, which="both", linestyle="--", alpha=0.5)

    # Аннотация на лог-лог графике
    axes[1].annotate(
        "Все три — наклон ≈ 2\n→ подтверждение O(n²)",
        xy=(sizes[-2], times_selection[-2]),
        xytext=(sizes[1], times_selection[-2] * 0.3),
        arrowprops=dict(arrowstyle="->", color="steelblue"),
        fontsize=9,
        color="steelblue",
    )

    plt.tight_layout()
    output_path = "benchmark_plot.png"
    plt.savefig(output_path, dpi=150)
    print(f"График сохранён: {output_path}")
    plt.show()


if __name__ == "__main__":
    sizes, t_bubble, t_selection, t_insertion = benchmark()
    plot_results(sizes, t_bubble, t_selection, t_insertion)
