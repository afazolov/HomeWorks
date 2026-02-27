"""
K4 — Анализ времени выполнения сортировки слиянием
----------------------------------------------------
Сравниваем MergeSort и сортировку пузырьком на списках разной длины.
Строим общий график.
"""

import random
import time
import matplotlib.pyplot as plt

from merge_sort import merge_sort


# ---------------------------------------------------------------------------
# Встроенная сортировка пузырьком (без зависимости от hw3)
# ---------------------------------------------------------------------------
def bubble_sort(lst: list) -> list:
    """Сортировка пузырьком — O(n²)."""
    arr = lst.copy()
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break
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
    # Пузырёк O(n²) — медленный, поэтому не берём слишком большие списки
    sizes = [10, 100, 500, 1000, 2000, 3000, 5000]

    times_merge  = []
    times_bubble = []

    print("=" * 60)
    print("K4: MergeSort vs Сортировка пузырьком")
    print("=" * 60)
    print(f"{'Размер':>8} | {'MergeSort (мс)':>16} | {'Пузырьком (мс)':>16}")
    print("-" * 47)

    for size in sizes:
        random.seed(0)
        # Одинаковый случайный список для честного сравнения
        data = [random.randint(1, 100_000) for _ in range(size)]

        t_merge  = measure(merge_sort,  data)
        t_bubble = measure(bubble_sort, data)

        times_merge.append(t_merge)
        times_bubble.append(t_bubble)

        print(f"{size:>8,} | {t_merge:>16.4f} | {t_bubble:>16.4f}")

    print()
    return sizes, times_merge, times_bubble


# ---------------------------------------------------------------------------
# Построение графика
# ---------------------------------------------------------------------------
def plot_results(sizes, times_merge, times_bubble):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # --- Левый график: линейный масштаб ---
    axes[0].plot(sizes, times_bubble, marker="o", color="tomato",
                 linewidth=2, label="Пузырьком O(n²)")
    axes[0].plot(sizes, times_merge,  marker="s", color="steelblue",
                 linewidth=2, label="MergeSort O(n log n)")
    axes[0].set_title("MergeSort vs Пузырьком\n(линейный масштаб)")
    axes[0].set_xlabel("Размер списка (n)")
    axes[0].set_ylabel("Время выполнения (мс)")
    axes[0].legend()
    axes[0].grid(True, linestyle="--", alpha=0.5)

    # Аннотации
    axes[0].annotate(
        "Пузырьком резко\nзамедляется — O(n²)",
        xy=(sizes[-1], times_bubble[-1]),
        xytext=(sizes[-4], times_bubble[-1] * 0.7),
        arrowprops=dict(arrowstyle="->", color="tomato"),
        fontsize=9,
        color="tomato",
    )
    axes[0].annotate(
        "MergeSort стабилен\n— O(n log n)",
        xy=(sizes[-1], times_merge[-1]),
        xytext=(sizes[-4], times_merge[-1] * 4),
        arrowprops=dict(arrowstyle="->", color="steelblue"),
        fontsize=9,
        color="steelblue",
    )

    # --- Правый график: лог-лог масштаб ---
    # O(n²) → прямая с наклоном 2
    # O(n log n) → прямая с наклоном чуть больше 1
    axes[1].plot(sizes, times_bubble, marker="o", color="tomato",
                 linewidth=2, label="Пузырьком O(n²)")
    axes[1].plot(sizes, times_merge,  marker="s", color="steelblue",
                 linewidth=2, label="MergeSort O(n log n)")
    axes[1].set_xscale("log")
    axes[1].set_yscale("log")
    axes[1].set_title("MergeSort vs Пузырьком\n(лог-лог масштаб)")
    axes[1].set_xlabel("Размер списка (n)")
    axes[1].set_ylabel("Время выполнения (мс)")
    axes[1].legend()
    axes[1].grid(True, which="both", linestyle="--", alpha=0.5)

    axes[1].annotate(
        "Наклон ≈ 2 → O(n²)",
        xy=(sizes[-2], times_bubble[-2]),
        xytext=(sizes[1], times_bubble[-3]),
        arrowprops=dict(arrowstyle="->", color="tomato"),
        fontsize=9,
        color="tomato",
    )
    axes[1].annotate(
        "Наклон ≈ 1 → O(n log n)",
        xy=(sizes[-2], times_merge[-2]),
        xytext=(sizes[1], times_merge[-1] * 2),
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
    sizes, times_merge, times_bubble = benchmark()
    plot_results(sizes, times_merge, times_bubble)
