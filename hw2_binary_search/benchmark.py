"""
Замер производительности бинарного и линейного поиска
-------------------------------------------------------
K3: Создаём отсортированный список из 100 случайных чисел,
    выполняем бинарный поиск для нескольких значений.
K4: Сравниваем время бинарного и линейного поиска
    для разных размеров списков и строим общий график.
"""

import random
import time
import matplotlib.pyplot as plt

from binary_search import binary_search


# ---------------------------------------------------------------------------
# Встроенный линейный поиск (чтобы не зависеть от соседней папки)
# ---------------------------------------------------------------------------
def linear_search(lst: list, target) -> int:
    """Линейный поиск — O(n)."""
    for index, element in enumerate(lst):
        if element == target:
            return index
    return -1


# ---------------------------------------------------------------------------
# K3 — Отсортированный список из 100 случайных чисел, бинарный поиск
# ---------------------------------------------------------------------------
def demo_100_elements():
    random.seed(42)
    # Генерируем 100 случайных чисел и сортируем — бинарный поиск требует сортировки
    numbers = sorted(random.randint(1, 200) for _ in range(100))

    print("=" * 60)
    print("K3: Бинарный поиск в отсортированном списке из 100 чисел")
    print("=" * 60)
    print(f"Список: {numbers}\n")

    # Ищем: первый, средний, последний элемент, и два отсутствующих
    search_targets = [numbers[0], numbers[49], numbers[99], 201, 202]

    print(f"{'Элемент':>10} | {'Индекс':>8} | {'Найден?'}")
    print("-" * 35)
    for target in search_targets:
        idx = binary_search(numbers, target)
        found = "Да" if idx != -1 else "Нет"
        print(f"{target:>10} | {idx:>8} | {found}")
    print()


# ---------------------------------------------------------------------------
# K4 — Замер и сравнение времени бинарного vs линейного поиска
# ---------------------------------------------------------------------------
def benchmark():
    sizes = [10, 100, 1000, 10_000, 100_000, 1_000_000]
    times_binary = []
    times_linear = []

    print("=" * 65)
    print("K4: Сравнение времени бинарного и линейного поиска")
    print("=" * 65)
    print(f"{'Размер':>12} | {'Бинарный (мс)':>15} | {'Линейный (мс)':>15}")
    print("-" * 48)

    for size in sizes:
        # Отсортированный список — обязательное условие для бинарного поиска
        data = list(range(size))

        # Худший случай: элемент отсутствует (-1)
        # Линейный обойдёт весь список, бинарный сделает log(n) шагов
        target = -1

        repetitions = max(1, 1_000_000 // size)

        # Замер бинарного поиска
        start = time.perf_counter()
        for _ in range(repetitions):
            binary_search(data, target)
        t_binary = (time.perf_counter() - start) / repetitions * 1000

        # Замер линейного поиска
        start = time.perf_counter()
        for _ in range(repetitions):
            linear_search(data, target)
        t_linear = (time.perf_counter() - start) / repetitions * 1000

        times_binary.append(t_binary)
        times_linear.append(t_linear)
        print(f"{size:>12,} | {t_binary:>15.6f} | {t_linear:>15.6f}")

    print()
    return sizes, times_binary, times_linear


def plot_results(sizes, times_binary, times_linear):
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    # --- Левый график: линейный масштаб ---
    # Хорошо видна пропасть между O(n) и O(log n) на больших данных
    axes[0].plot(sizes, times_linear, marker="o", color="tomato",
                 linewidth=2, label="Линейный O(n)")
    axes[0].plot(sizes, times_binary, marker="s", color="steelblue",
                 linewidth=2, label="Бинарный O(log n)")
    axes[0].set_title("Бинарный vs Линейный поиск\n(линейный масштаб)")
    axes[0].set_xlabel("Размер списка (n)")
    axes[0].set_ylabel("Время на один вызов (мс)")
    axes[0].legend()
    axes[0].grid(True, linestyle="--", alpha=0.5)

    # Аннотация разницы на больших данных
    axes[0].annotate(
        "Линейный резко\nрастёт при больших n",
        xy=(sizes[-1], times_linear[-1]),
        xytext=(sizes[-3], times_linear[-1] * 0.6),
        arrowprops=dict(arrowstyle="->", color="tomato"),
        fontsize=9,
        color="tomato",
    )
    axes[0].annotate(
        "Бинарный почти\nне меняется",
        xy=(sizes[-1], times_binary[-1]),
        xytext=(sizes[-3], times_binary[-1] * 5),
        arrowprops=dict(arrowstyle="->", color="steelblue"),
        fontsize=9,
        color="steelblue",
    )

    # --- Правый график: логарифмический масштаб по обеим осям ---
    # O(n) — прямая с наклоном 1; O(log n) — кривая с убывающим наклоном
    axes[1].plot(sizes, times_linear, marker="o", color="tomato",
                 linewidth=2, label="Линейный O(n)")
    axes[1].plot(sizes, times_binary, marker="s", color="steelblue",
                 linewidth=2, label="Бинарный O(log n)")
    axes[1].set_xscale("log")
    axes[1].set_yscale("log")
    axes[1].set_title("Бинарный vs Линейный поиск\n(лог-лог масштаб)")
    axes[1].set_xlabel("Размер списка (n)")
    axes[1].set_ylabel("Время на один вызов (мс)")
    axes[1].legend()
    axes[1].grid(True, which="both", linestyle="--", alpha=0.5)

    # Аннотация на лог-лог графике
    axes[1].annotate(
        "Наклон ≈ 1\n→ O(n)",
        xy=(sizes[-2], times_linear[-2]),
        xytext=(sizes[1], times_linear[-3]),
        arrowprops=dict(arrowstyle="->", color="tomato"),
        fontsize=9,
        color="tomato",
    )
    axes[1].annotate(
        "Наклон < 1\n→ O(log n)",
        xy=(sizes[-2], times_binary[-2]),
        xytext=(sizes[2], times_binary[-1] * 3),
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
    demo_100_elements()
    sizes, times_binary, times_linear = benchmark()
    plot_results(sizes, times_binary, times_linear)
