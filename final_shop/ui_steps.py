"""
Окно визуализации шагов сортировки.
"""
import tkinter as tk
from tkinter import ttk


class StepsWindow(tk.Toplevel):
    """Отдельное окно, показывающее промежуточные шаги сортировки."""

    def __init__(self, parent: tk.Widget, algorithm: str, steps: list[str]):
        super().__init__(parent)
        self.title(f"Шаги сортировки — {algorithm}")
        self.geometry("700x420")
        self.resizable(True, True)
        self._build(algorithm, steps)

    def _build(self, algorithm: str, steps: list[str]) -> None:
        # Заголовок
        tk.Label(
            self,
            text=f"Алгоритм: {algorithm}   |   Шагов: {len(steps)}",
            font=("Arial", 11, "bold"),
            pady=6,
        ).pack(fill="x")

        ttk.Separator(self).pack(fill="x")

        # Область с прокруткой
        frame = tk.Frame(self)
        frame.pack(fill="both", expand=True, padx=8, pady=8)

        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        text = tk.Text(
            frame,
            yscrollcommand=scrollbar.set,
            font=("Courier", 10),
            wrap="word",
            state="normal",
        )
        text.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=text.yview)

        # Заполняем шаги
        if steps:
            for i, step in enumerate(steps, 1):
                text.insert("end", f"Шаг {i:>3}: {step}\n")
        else:
            text.insert("end", "Шаги не были записаны.\n")

        text.config(state="disabled")

        # Кнопка закрыть
        ttk.Button(self, text="Закрыть", command=self.destroy).pack(pady=6)
