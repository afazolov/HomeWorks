"""
Главное окно приложения — Симулятор магазина.
Запуск: python main.py
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from catalog import Catalog
from cart import Cart
from sorting import sort_cart, ALGORITHMS, SORT_KEYS
from ui_steps import StepsWindow


# ===========================================================================
# Главное окно
# ===========================================================================

class ShopApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🛒  Симулятор магазина")
        self.geometry("1100x640")
        self.minsize(900, 500)
        self.resizable(True, True)

        self.catalog = Catalog.default()
        self.cart    = Cart()

        self._build_ui()
        self._refresh_catalog()
        self._refresh_cart()

    # -----------------------------------------------------------------------
    # Построение интерфейса
    # -----------------------------------------------------------------------

    def _build_ui(self) -> None:
        # Главный контейнер разделён на левую и правую части
        paned = ttk.PanedWindow(self, orient="horizontal")
        paned.pack(fill="both", expand=True, padx=8, pady=8)

        self._build_catalog_panel(paned)
        self._build_cart_panel(paned)
        self._build_bottom_bar()

    # --- Каталог (левая панель) ---

    def _build_catalog_panel(self, parent) -> None:
        frame = ttk.LabelFrame(parent, text="📦  Каталог товаров", padding=4)
        parent.add(frame, weight=1)

        # Панель кнопок НАД таблицей каталога
        ctrl = ttk.Frame(frame)
        ctrl.pack(fill="x", pady=(0, 4))

        ttk.Label(ctrl, text="Кол-во:").pack(side="left")
        self.qty_var = tk.IntVar(value=1)
        ttk.Spinbox(ctrl, from_=1, to=99, textvariable=self.qty_var,
                    width=4).pack(side="left", padx=4)
        ttk.Button(ctrl, text="➕ В корзину",
                   command=self._add_to_cart).pack(side="left", padx=4)

        # CRUD каталога
        ttk.Separator(ctrl, orient="vertical").pack(side="left",
                                                    fill="y", padx=6)
        ttk.Button(ctrl, text="Добавить товар",
                   command=self._add_product_dialog).pack(side="left", padx=2)
        ttk.Button(ctrl, text="Редактировать",
                   command=self._edit_product_dialog).pack(side="left", padx=2)
        ttk.Button(ctrl, text="Удалить",
                   command=self._remove_product).pack(side="left", padx=2)

        # Таблица каталога
        cols = ("id", "name", "category", "price", "weight")
        self.cat_tree = ttk.Treeview(frame, columns=cols, show="headings",
                                     selectmode="browse", height=20)
        headings = {
            "id":       ("ID",        45),
            "name":     ("Название",  180),
            "category": ("Категория", 110),
            "price":    ("Цена, ₽",   80),
            "weight":   ("Вес, г",    70),
        }
        for col, (label, width) in headings.items():
            self.cat_tree.heading(col, text=label,
                                  command=lambda c=col: self._sort_catalog(c))
            self.cat_tree.column(col, width=width, anchor="center")

        vsb = ttk.Scrollbar(frame, orient="vertical",
                            command=self.cat_tree.yview)
        self.cat_tree.configure(yscrollcommand=vsb.set)
        self.cat_tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="left", fill="y")

    # --- Корзина (правая панель) ---

    def _build_cart_panel(self, parent) -> None:
        frame = ttk.LabelFrame(parent, text="🛒  Корзина", padding=4)
        parent.add(frame, weight=1)

        # Кнопки управления корзиной НАД таблицей
        ctrl = ttk.Frame(frame)
        ctrl.pack(fill="x", pady=(0, 4))

        ttk.Button(ctrl, text="➖ Минус 1",
                   command=self._cart_minus).pack(side="left", padx=2)
        ttk.Button(ctrl, text="➕ Плюс 1",
                   command=self._cart_plus).pack(side="left", padx=2)
        ttk.Button(ctrl, text="🗑 Удалить позицию",
                   command=self._cart_remove).pack(side="left", padx=2)
        ttk.Button(ctrl, text="🧹 Очистить",
                   command=self._cart_clear).pack(side="left", padx=2)

        # Таблица корзины
        cols = ("name", "category", "price", "weight", "qty", "total")
        self.cart_tree = ttk.Treeview(frame, columns=cols, show="headings",
                                      selectmode="browse", height=20)
        headings = {
            "name":     ("Название",   170),
            "category": ("Категория",  100),
            "price":    ("Цена, ₽",     80),
            "weight":   ("Вес, г",      70),
            "qty":      ("Кол-во",      60),
            "total":    ("Сумма, ₽",    85),
        }
        for col, (label, width) in headings.items():
            self.cart_tree.heading(col, text=label)
            self.cart_tree.column(col, width=width, anchor="center")

        vsb = ttk.Scrollbar(frame, orient="vertical",
                            command=self.cart_tree.yview)
        self.cart_tree.configure(yscrollcommand=vsb.set)
        self.cart_tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="left", fill="y")

    # --- Нижняя панель: сортировка и итог ---

    def _build_bottom_bar(self) -> None:
        bar = ttk.Frame(self, padding=(8, 4))
        bar.pack(fill="x", side="bottom")

        ttk.Separator(self).pack(fill="x", side="bottom")

        # Сортировка
        ttk.Label(bar, text="Сортировать:").pack(side="left")

        self.sort_key_var = tk.StringVar(value="Цена")
        ttk.Combobox(bar, textvariable=self.sort_key_var,
                     values=list(SORT_KEYS.keys()),
                     width=10, state="readonly").pack(side="left", padx=4)

        self.sort_algo_var = tk.StringVar(value="Пузырьком")
        ttk.Combobox(bar, textvariable=self.sort_algo_var,
                     values=list(ALGORITHMS.keys()),
                     width=12, state="readonly").pack(side="left", padx=4)

        self.sort_order_var = tk.StringVar(value="По возрастанию")
        ttk.Combobox(bar, textvariable=self.sort_order_var,
                     values=["По возрастанию", "По убыванию"],
                     width=14, state="readonly").pack(side="left", padx=4)

        self.show_steps_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(bar, text="Показывать шаги",
                        variable=self.show_steps_var).pack(side="left", padx=6)

        ttk.Button(bar, text="▶ Сортировать",
                   command=self._do_sort).pack(side="left", padx=4)

        ttk.Separator(bar, orient="vertical").pack(side="left",
                                                   fill="y", padx=12)

        # Итог
        self.total_var = tk.StringVar(value="Итого: 0.00 ₽")
        ttk.Label(bar, textvariable=self.total_var,
                  font=("Arial", 12, "bold")).pack(side="left", padx=4)

        self.discount_var = tk.StringVar(value="")
        ttk.Label(bar, textvariable=self.discount_var,
                  foreground="green").pack(side="left", padx=4)

        self.weight_var = tk.StringVar(value="")
        ttk.Label(bar, textvariable=self.weight_var).pack(side="left", padx=8)

    # -----------------------------------------------------------------------
    # Обновление таблиц
    # -----------------------------------------------------------------------

    def _refresh_catalog(self) -> None:
        """Перерисовать таблицу каталога."""
        for row in self.cat_tree.get_children():
            self.cat_tree.delete(row)
        for p in self.catalog.all():
            self.cat_tree.insert("", "end", iid=str(p.id), values=(
                p.id, p.name, p.category, f"{p.price:.2f}", p.weight,
            ))

    def _refresh_cart(self) -> None:
        """Перерисовать таблицу корзины и пересчитать итог."""
        for row in self.cart_tree.get_children():
            self.cart_tree.delete(row)
        for item in self.cart.items():
            p = item.product
            self.cart_tree.insert("", "end", iid=str(p.id), values=(
                p.name, p.category,
                f"{p.price:.2f}", p.weight,
                item.qty, f"{item.total_price:.2f}",
            ))
        # Итог
        sub      = self.cart.subtotal()
        discount = self.cart.discount()
        total    = self.cart.total()
        weight   = self.cart.total_weight()

        self.total_var.set(f"Итого: {total:.2f} ₽")
        if discount > 0:
            self.discount_var.set(f"(скидка 5%: −{discount:.2f} ₽)")
        else:
            self.discount_var.set("")
        if weight > 0:
            kg = weight / 1000
            self.weight_var.set(f"Вес: {kg:.2f} кг")
        else:
            self.weight_var.set("")

    # -----------------------------------------------------------------------
    # Обработчики: каталог
    # -----------------------------------------------------------------------

    def _add_to_cart(self) -> None:
        sel = self.cat_tree.selection()
        if not sel:
            messagebox.showwarning("Внимание", "Выберите товар из каталога")
            return
        product_id = int(sel[0])
        product = self.catalog.get(product_id)
        try:
            qty = int(self.qty_var.get())
            if qty <= 0:
                raise ValueError
        except (ValueError, tk.TclError):
            messagebox.showerror("Ошибка", "Введите корректное количество (> 0)")
            return
        self.cart.add(product, qty)
        self._refresh_cart()

    def _add_product_dialog(self) -> None:
        """Диалог добавления нового товара в каталог."""
        dlg = ProductDialog(self, title="Добавить товар")
        self.wait_window(dlg)
        if dlg.result:
            try:
                self.catalog.add(**dlg.result)
                self._refresh_catalog()
            except ValueError as e:
                messagebox.showerror("Ошибка", str(e))

    def _edit_product_dialog(self) -> None:
        """Диалог редактирования выбранного товара."""
        sel = self.cat_tree.selection()
        if not sel:
            messagebox.showwarning("Внимание", "Выберите товар для редактирования")
            return
        product_id = int(sel[0])
        product = self.catalog.get(product_id)
        dlg = ProductDialog(self, title="Редактировать товар", product=product)
        self.wait_window(dlg)
        if dlg.result:
            try:
                self.catalog.update(product_id, **dlg.result)
                self._refresh_catalog()
                self._refresh_cart()  # цена могла измениться
            except (ValueError, AttributeError) as e:
                messagebox.showerror("Ошибка", str(e))

    def _remove_product(self) -> None:
        """Удалить товар из каталога."""
        sel = self.cat_tree.selection()
        if not sel:
            messagebox.showwarning("Внимание", "Выберите товар для удаления")
            return
        product_id = int(sel[0])
        if not messagebox.askyesno("Подтверждение",
                                   "Удалить товар из каталога?"):
            return
        try:
            self.catalog.remove(product_id)
        except KeyError:
            pass
        # Если товар был в корзине — убрать
        if product_id in [item.product.id for item in self.cart.items()]:
            self.cart.remove(product_id)
        self._refresh_catalog()
        self._refresh_cart()

    def _sort_catalog(self, col: str) -> None:
        """Сортировка каталога по клику на заголовок колонки."""
        items = self.catalog.all()
        reverse = getattr(self, f"_cat_sort_{col}_rev", False)
        if col == "id":
            items.sort(key=lambda p: p.id, reverse=reverse)
        elif col == "name":
            items.sort(key=lambda p: p.name.lower(), reverse=reverse)
        elif col == "category":
            items.sort(key=lambda p: p.category.lower(), reverse=reverse)
        elif col == "price":
            items.sort(key=lambda p: p.price, reverse=reverse)
        elif col == "weight":
            items.sort(key=lambda p: p.weight, reverse=reverse)
        setattr(self, f"_cat_sort_{col}_rev", not reverse)
        # Перерисовываем в нужном порядке
        for row in self.cat_tree.get_children():
            self.cat_tree.delete(row)
        for p in items:
            self.cat_tree.insert("", "end", iid=str(p.id), values=(
                p.id, p.name, p.category, f"{p.price:.2f}", p.weight,
            ))

    # -----------------------------------------------------------------------
    # Обработчики: корзина
    # -----------------------------------------------------------------------

    def _selected_cart_id(self) -> int | None:
        sel = self.cart_tree.selection()
        if not sel:
            messagebox.showwarning("Внимание", "Выберите позицию в корзине")
            return None
        return int(sel[0])

    def _cart_minus(self) -> None:
        pid = self._selected_cart_id()
        if pid is None:
            return
        try:
            self.cart.change_qty(pid, -1)
        except KeyError:
            pass
        self._refresh_cart()

    def _cart_plus(self) -> None:
        pid = self._selected_cart_id()
        if pid is None:
            return
        try:
            self.cart.change_qty(pid, +1)
        except KeyError:
            pass
        self._refresh_cart()

    def _cart_remove(self) -> None:
        pid = self._selected_cart_id()
        if pid is None:
            return
        try:
            self.cart.remove(pid)
        except KeyError:
            pass
        self._refresh_cart()

    def _cart_clear(self) -> None:
        if self.cart.is_empty():
            return
        if messagebox.askyesno("Подтверждение", "Очистить корзину?"):
            self.cart.clear()
            self._refresh_cart()

    # -----------------------------------------------------------------------
    # Сортировка корзины
    # -----------------------------------------------------------------------

    def _do_sort(self) -> None:
        if self.cart.is_empty():
            messagebox.showinfo("Сортировка", "Корзина пуста — нечего сортировать")
            return

        algorithm = self.sort_algo_var.get()
        key       = self.sort_key_var.get()
        reverse   = self.sort_order_var.get() == "По убыванию"
        show_steps = self.show_steps_var.get()

        sorted_items, steps_log = sort_cart(
            self.cart.items(), algorithm, key, reverse, show_steps
        )
        self.cart.set_items(sorted_items)
        self._refresh_cart()

        if show_steps and steps_log:
            StepsWindow(self, algorithm, steps_log)
        elif show_steps:
            messagebox.showinfo("Шаги", "Шаги не зафиксированы "
                                        "(возможно, список уже отсортирован)")


# ===========================================================================
# Диалог добавления / редактирования товара
# ===========================================================================

class ProductDialog(tk.Toplevel):
    """Модальный диалог для ввода / редактирования данных товара."""

    def __init__(self, parent, title: str, product=None):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.grab_set()   # модальность
        self.result = None

        fields = [
            ("Название",   "name",        product.name        if product else ""),
            ("Категория",  "category",    product.category    if product else ""),
            ("Цена (₽)",   "price",       str(product.price)  if product else ""),
            ("Вес (г)",    "weight",      str(product.weight) if product else ""),
            ("Описание",   "description", product.description if product else ""),
        ]

        self._entries: dict[str, tk.Entry] = {}

        for i, (label, key, default) in enumerate(fields):
            ttk.Label(self, text=label + ":").grid(
                row=i, column=0, sticky="e", padx=8, pady=4)
            var = tk.StringVar(value=default)
            entry = ttk.Entry(self, textvariable=var, width=28)
            entry.grid(row=i, column=1, padx=8, pady=4)
            self._entries[key] = var

        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=len(fields), column=0, columnspan=2, pady=8)
        ttk.Button(btn_frame, text="Сохранить",
                   command=self._save).pack(side="left", padx=6)
        ttk.Button(btn_frame, text="Отмена",
                   command=self.destroy).pack(side="left", padx=6)

        self._entries["name"].set(self._entries["name"].get())  # фокус

    def _save(self) -> None:
        try:
            name     = self._entries["name"].get().strip()
            category = self._entries["category"].get().strip()
            price    = float(self._entries["price"].get())
            weight   = float(self._entries["weight"].get())
            desc     = self._entries["description"].get().strip()
            if not name or not category:
                raise ValueError("Название и категория обязательны")
            if price < 0 or weight < 0:
                raise ValueError("Цена и вес не могут быть отрицательными")
        except ValueError as e:
            messagebox.showerror("Ошибка ввода", str(e), parent=self)
            return
        self.result = dict(name=name, category=category,
                           price=price, weight=weight, description=desc)
        self.destroy()


# ===========================================================================
# Точка входа
# ===========================================================================

if __name__ == "__main__":
    app = ShopApp()
    app.mainloop()
