"""
K4 — Анализ времени выполнения быстрой сортировки
---------------------------------------------------
Сравниваем QuickSort и сортировку вставками на списках разной длины.
Строим общий график.
"""

import random
import time
import matplotlib.pyplot as plt

from quicksort import quicksort


# ---------------------------------------------------------------------------
# Встроенная сортировка вставками (из hw3, без зависимости от папки)
# ---------------------------------------------------------------------------
def insertion_sort(lst: list) -> list:
    """Сортировка вставками — O(n²)."""
    arr = lst.copy()
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr


# ---------------------------------------------------------------------------
# Замер времени
# ---------------------------------------------------------------------------
def measure(sort_func, data: list) -> float:
    """Возвращает время выполнения sort_func(data) в миллисекундах."""
    start = time.perf_counter()
    sort_func(data)
    return (time.perf_counter() - start) * 1000


def benchmark():
    # QuickSort работает быстро, поэтому берём большие размеры
    sizes = [10, 100, 500, 1000, 2000, 5000, 10_000]

    times_quick     = []
    times_insertion = []

    print("=" * 65)
    print("K4: Быстрая сортировка vs Сортировка вставками")
    print("=" * 65)
    print(f"{'Размер':>8} | {'QuickSort (мс)':>16} | {'Вставками (мс)':>16}")
    print("-" * 47)

    for size in sizes:
        random.seed(0)
        # Один и тот же случайный список для честного сравнения
        data = [random.randint(1, 100_000) for _ in range(size)]

        t_quick     = measure(quicksort,      data)
        t_insertion = measure(insertion_sort, data)

        times_quick.append(t_quick)
        times_insertion.append(t_insertion)

        print(f"{size:>8,} | {t_quick:>16.4f} | {t_insertion:>16.4f}")

    print()
    return sizes, times_quick, times_insertion


# ---------------------------------------------------------------------------
# Построение графика
# ---------------------------------------------------------------------------
def plot_results(sizes, times_quick, times_insertion):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # --- Левый график: линейный масштаб ---
    # Наглядно видна пропасть между O(n log n) и O(n²) на больших n
    axes[0].plot(sizes, times_insertion, marker="o", color="tomato",
                 linewidth=2, label="Вставками O(n²)")
    axes[0].plot(sizes, times_quick,     marker="s", color="steelblue",
                 linewidth=2, label="QuickSort O(n log n)")
    axes[0].set_title("QuickSort vs Вставками\n(линейный масштаб)")
    axes[0].set_xlabel("Размер списка (n)")
    axes[0].set_ylabel("Время выполнения (мс)")
    axes[0].legend()
    axes[0].grid(True, linestyle="--", alpha=0.5)

    # Аннотация: сортировка вставками резко растёт
    axes[0].annotate(
        "Вставками резко\nзамедляется — O(n²)",
        xy=(sizes[-1], times_insertion[-1]),
        xytext=(sizes[-4], times_insertion[-1] * 0.7),
        arrowprops=dict(arrowstyle="->", color="tomato"),
        fontsize=9,
        color="tomato",
    )
    axes[0].annotate(
        "QuickSort почти\nплоский — O(n log n)",
        xy=(sizes[-1], times_quick[-1]),
        xytext=(sizes[-4], times_quick[-1] * 4),
        arrowprops=dict(arrowstyle="->", color="steelblue"),
        fontsize=9,
        color="steelblue",
    )

    # --- Правый график: лог-лог масштаб ---
    # O(n²) → прямая с наклоном 2; O(n log n) → прямая с наклоном чуть меньше 1
    axes[1].plot(sizes, times_insertion, marker="o", color="tomato",
                 linewidth=2, label="Вставками O(n²)")
    axes[1].plot(sizes, times_quick,     marker="s", color="steelblue",
                 linewidth=2, label="QuickSort O(n log n)")
    axes[1].set_xscale("log")
    axes[1].set_yscale("log")
    axes[1].set_title("QuickSort vs Вставками\n(лог-лог масштаб)")
    axes[1].set_xlabel("Размер списка (n)")
    axes[1].set_ylabel("Время выполнения (мс)")
    axes[1].legend()
    axes[1].grid(True, which="both", linestyle="--", alpha=0.5)

    # Аннотации на лог-лог
    axes[1].annotate(
        "Наклон ≈ 2 → O(n²)",
        xy=(sizes[-2], times_insertion[-2]),
        xytext=(sizes[1], times_insertion[-3]),
        arrowprops=dict(arrowstyle="->", color="tomato"),
        fontsize=9,
        color="tomato",
    )
    axes[1].annotate(
        "Наклон ≈ 1 → O(n log n)",
        xy=(sizes[-2], times_quick[-2]),
        xytext=(sizes[1], times_quick[-1] * 2),
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
    sizes, times_quick, times_insertion = benchmark()
    plot_results(sizes, times_quick, times_insertion)
