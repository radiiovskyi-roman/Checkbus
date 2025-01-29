import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
import pandas as pd
from tkcalendar import DateEntry
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class FinanceApp:
    """
    Головний клас, що створює вікно (Tk) і керує вкладками:
    1. Додавання витрат
    2. Фінансова аналітика
    3. Попередні записи
    4. Керування категоріями (адмін-вкладка)

    Використовує CategoryManager та ExpenseManager для роботи з даними.
    """
    def __init__(self, root, category_manager, expense_manager):
        self.root = root
        self.root.title("Фінансовий Облік")
        self.root.geometry("1000x700")

        # Збережемо менеджери у поля класу
        self.category_manager = category_manager
        self.expense_manager = expense_manager

        # Налаштуємо стиль для ttk
        self.setup_style()

        # ===== Верхній заголовок (шапка) =====
        header_frame = ttk.Frame(self.root, style="Header.TFrame")
        header_frame.pack(fill="x")

        title_label = ttk.Label(
            header_frame,
            text="Фінансовий Облік",
            style="Header.TLabel"
        )
        title_label.pack(pady=5)

        # ===== Notebook (вкладки) =====
        self.notebook = ttk.Notebook(self.root, style="MainNotebook.TNotebook")
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        self.entry_frame = ttk.Frame(self.notebook, style="MainFrame.TFrame")
        self.analysis_frame = ttk.Frame(self.notebook, style="MainFrame.TFrame")
        self.records_frame = ttk.Frame(self.notebook, style="MainFrame.TFrame")
        self.admin_frame = ttk.Frame(self.notebook, style="MainFrame.TFrame")

        self.notebook.add(self.entry_frame, text="Додавання витрат")
        self.notebook.add(self.analysis_frame, text="Фінансова аналітика")
        self.notebook.add(self.records_frame, text="Попередні записи")
        self.notebook.add(self.admin_frame, text="Керування категоріями")

        # Налаштовуємо вкладки
        self.setup_entry_tab()
        self.setup_analysis_tab()
        self.setup_records_tab()
        self.setup_admin_tab()

        # Поле для сповіщень
        self.notification_label = ttk.Label(root, text="", foreground="green", style="Notification.TLabel")
        self.notification_label.pack(side="bottom", anchor="w", padx=10, pady=5)

    # -------------------------------------------------------------
    # Налаштування стилів (більші шрифти та інше оформлення)
    # -------------------------------------------------------------
    def setup_style(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")

        # ====== Загальні налаштування шрифтів ======
        # Збільшимо шрифти (до 12–14):
        BASE_FONT = ("Arial", 12)
        HEADING_FONT = ("Arial", 14, "bold")
        BIG_HEADING_FONT = ("Helvetica", 20, "bold")

        # ====== Фрейми ======
        style.configure("MainFrame.TFrame", background="#f0f2f5")
        style.configure("Header.TFrame", background="#2c3e50")

        # ====== Label ======
        style.configure("TLabel",
                        background="#f0f2f5",
                        foreground="#333",
                        font=BASE_FONT)
        style.configure("Header.TLabel",
                        background="#2c3e50",
                        foreground="white",
                        font=BIG_HEADING_FONT)
        style.configure("Notification.TLabel",
                        font=("Arial", 12, "italic"))

        # ====== Notebook ======
        style.configure("MainNotebook.TNotebook",
                        background="#f0f2f5",
                        tabposition="nw")
        style.configure("TNotebook.Tab",
                        background="#d7d7d7",
                        foreground="#000",
                        padding=10,
                        font=HEADING_FONT)
        style.map("TNotebook.Tab",
                  background=[("selected", "#ffffff")],
                  foreground=[("selected", "#000000")])

        # ====== Кнопки ======
        style.configure("TButton",
                        font=BASE_FONT,
                        padding=5)

        # ====== Поля вводу ======
        style.configure("TEntry",
                        font=BASE_FONT,
                        padding=3)
        style.configure("TCombobox",
                        font=BASE_FONT,
                        padding=3)

        # ====== Treeview (таблиці) ======
        # Збільшуємо шрифт та rowheight
        style.configure("Treeview",
                        background="white",
                        foreground="#333",
                        rowheight=30,
                        fieldbackground="white",
                        font=BASE_FONT,
                        borderwidth=1)

        style.configure("Treeview.Heading",
                        background="#007acc",
                        foreground="#ffffff",
                        font=HEADING_FONT)
        style.map("Treeview",
                  background=[("selected", "#cce5ff")])

    def load_main_records(self):
        df = self.expense_manager.get_expenses()
        self.tree_main.delete(*self.tree_main.get_children())  # Очищаємо таблицю перед оновленням

        for i, row in enumerate(df.itertuples(index=False), start=1):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.tree_main.insert("", "end", values=row, tags=(tag,))

    # -------------------------------------------------------------
    # Вкладка "Додавання витрат"
    # -------------------------------------------------------------
    def setup_entry_tab(self):
        """ Створює вкладку "Додавання витрат" з таблицею та формою введення. """
        content_frame = ttk.Frame(self.entry_frame, style="MainFrame.TFrame")
        content_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # 📌 Створюємо фрейм для таблиці + вертикального скролбара
        table_frame = ttk.Frame(content_frame)
        table_frame.pack(expand=True, fill="both")

        # 📌 Додаємо тільки вертикальний скролбар
        y_scroll = ttk.Scrollbar(table_frame, orient="vertical")

        # 📌 Таблиця витрат (з виділеними межами між колонками)
        self.tree_main = ttk.Treeview(
            table_frame,
            columns=("Дата", "Сума", "Категорія", "Підкатегорія", "Коментар"),
            show="headings",
            yscrollcommand=y_scroll.set
        )

        # 📌 Прив’язуємо скролбар до таблиці
        y_scroll.config(command=self.tree_main.yview)
        y_scroll.pack(side="right", fill="y")
        self.tree_main.pack(expand=True, fill="both", padx=5, pady=5)

        # 📌 Налаштовуємо заголовки колонок
        self.tree_main.heading("Дата", text="Дата")
        self.tree_main.heading("Сума", text="Сума")
        self.tree_main.heading("Категорія", text="Категорія")
        self.tree_main.heading("Підкатегорія", text="Підкатегорія")
        self.tree_main.heading("Коментар", text="Коментар")

        # 📌 Задаємо ширину колонок (Дата і Сума вужчі)
        self.tree_main.column("Дата", width=100, anchor="center")
        self.tree_main.column("Сума", width=100, anchor="center")
        self.tree_main.column("Категорія", width=200, anchor="center")
        self.tree_main.column("Підкатегорія", width=200, anchor="center")
        self.tree_main.column("Коментар", width=250, anchor="w")

        # 📌 Налаштовуємо стилі для рядків (смугасті рядки)
        self.tree_main.tag_configure("evenrow", background="#ffffff")
        self.tree_main.tag_configure("oddrow", background="#f7f7f7")

        # 📌 Завантажуємо записи у таблицю одразу після запуску
        self.load_main_records()

        # 📌 Форма введення нової витрати
        form_frame = ttk.Frame(content_frame, style="MainFrame.TFrame")
        form_frame.pack(side="bottom", fill="x", pady=10)

        ttk.Label(form_frame, text="Дата").grid(row=0, column=0, sticky="w", padx=5)
        self.date_entry = DateEntry(form_frame, date_pattern='dd.MM.yyyy')
        self.date_entry.grid(row=1, column=0, padx=5)

        ttk.Label(form_frame, text="Сума").grid(row=0, column=1, sticky="w", padx=5)
        self.amount_entry = ttk.Entry(form_frame)
        self.amount_entry.grid(row=1, column=1, padx=5)
        self.amount_entry.bind("<KeyRelease>", self.validate_amount)

        ttk.Label(form_frame, text="Категорія").grid(row=0, column=2, sticky="w", padx=5)
        self.category_cb = ttk.Combobox(
            form_frame,
            values=list(self.category_manager.categories.keys()),
            state="readonly"
        )
        self.category_cb.grid(row=1, column=2, padx=5)
        self.category_cb.bind("<<ComboboxSelected>>", self.update_subcategories)

        ttk.Label(form_frame, text="Підкатегорія").grid(row=0, column=3, sticky="w", padx=5)
        self.subcategory_cb = ttk.Combobox(form_frame, state="readonly")
        self.subcategory_cb.grid(row=1, column=3, padx=5)

        ttk.Label(form_frame, text="Коментар").grid(row=0, column=4, sticky="w", padx=5)
        self.comment_entry = ttk.Entry(form_frame)
        self.comment_entry.grid(row=1, column=4, padx=5)

        add_button = ttk.Button(form_frame, text="Додати витрату", command=self.add_expense)
        add_button.grid(row=1, column=5, padx=5)

        # 📌 Розтягнемо колонки для кращого вирівнювання
        for i in range(6):
            form_frame.columnconfigure(i, weight=1)

    def validate_amount(self, event):
        value = self.amount_entry.get()
        if not value.isdigit() and value != "":
            self.amount_entry.delete(len(value) - 1, tk.END)

    def update_subcategories(self, event):
        category = self.category_cb.get()
        subcats = self.category_manager.categories.get(category, [])
        self.subcategory_cb["values"] = subcats
        self.subcategory_cb.set("")

    def add_expense(self):
        record = {
            "Дата": self.date_entry.get(),
            "Сума": self.amount_entry.get(),
            "Категорія": self.category_cb.get(),
            "Підкатегорія": self.subcategory_cb.get(),
            "Коментар": self.comment_entry.get() if self.comment_entry.get() else ""
        }

        if not all([record["Дата"], record["Сума"], record["Категорія"], record["Підкатегорія"]]):
            messagebox.showerror("Помилка", "Заповніть всі обов'язкові поля!")
            return

        self.expense_manager.add_expense(record)
        self.show_notification("Витрата додана успішно!")

        self.amount_entry.delete(0, tk.END)
        self.comment_entry.delete(0, tk.END)

        # 🔹 Оновлюємо таблицю на головній сторінці після додавання нового запису
        self.load_main_records()

    # -------------------------------------------------------------
    # Вкладка "Фінансова аналітика"
    # -------------------------------------------------------------
    def setup_analysis_tab(self):
        controls_frame = ttk.Frame(self.analysis_frame, style="MainFrame.TFrame")
        controls_frame.pack(fill="x", padx=20, pady=10)

        ttk.Label(controls_frame, text="Оберіть тип аналітики:").pack(side="left", padx=(0, 5))

        analysis_options = [
            "Витрати за категоріями (стовпчиковий графік)",
            "Витрати за підкатегоріями (стовпчиковий графік)",
            "Витрати за категоріями (кругова діаграма)",
            "Динаміка витрат за місяцями (лінійний графік)",
            "ТОП-5 найбільших витратних категорій (горизонтальний графік)"
        ]
        self.analysis_type_cb = ttk.Combobox(controls_frame, values=analysis_options, state="readonly", width=50)
        self.analysis_type_cb.current(0)
        self.analysis_type_cb.pack(side="left", padx=5)

        ttk.Button(controls_frame, text="Оновити аналітику", command=self.show_statistics).pack(side="left", padx=5)

        self.canvas_frame = ttk.Frame(self.analysis_frame, style="MainFrame.TFrame")
        self.canvas_frame.pack(expand=True, fill="both", padx=20, pady=10)

    def show_statistics(self):
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

        df = self.expense_manager.get_expenses()
        # Парсимо дату у форматі dd.MM.yyyy
        df["Дата"] = pd.to_datetime(df["Дата"], errors="coerce", format="%d.%m.%Y")
        df["Сума"] = pd.to_numeric(df["Сума"], errors="coerce")
        df.dropna(subset=["Дата", "Сума"], inplace=True)

        if df.empty:
            messagebox.showinfo("Інформація", "Немає даних для відображення аналітики.")
            return

        selected_analysis = self.analysis_type_cb.get()
        fig, ax = plt.subplots(figsize=(8, 6), dpi=100)

        if "Витрати за категоріями (стовпчиковий графік)" in selected_analysis:
            grouped = df.groupby("Категорія")["Сума"].sum()
            grouped.plot(kind="bar", ax=ax, color="royalblue", alpha=0.8)
            ax.set_title("Витрати за категоріями")
            ax.set_xlabel("Категорія")
            ax.set_ylabel("Сума витрат")
            ax.tick_params(axis='x', rotation=45)

        elif "Витрати за підкатегоріями (стовпчиковий графік)" in selected_analysis:
            grouped = df.groupby(["Категорія", "Підкатегорія"])["Сума"].sum()
            grouped.index = grouped.index.map(lambda x: f"{x[0]}: {x[1]}")
            grouped.plot(kind="bar", ax=ax, color="forestgreen", alpha=0.8)
            ax.set_title("Витрати за підкатегоріями")
            ax.set_xlabel("Категорія:Підкатегорія")
            ax.set_ylabel("Сума витрат")
            ax.tick_params(axis='x', rotation=75)

        elif "Витрати за категоріями (кругова діаграма)" in selected_analysis:
            grouped = df.groupby("Категорія")["Сума"].sum()
            ax.pie(grouped, labels=grouped.index, autopct='%1.1f%%', startangle=140)
            ax.set_title("Структура витрат за категоріями")

        elif "Динаміка витрат за місяцями (лінійний графік)" in selected_analysis:
            df.set_index("Дата", inplace=True)
            monthly = df.resample('M')["Сума"].sum()
            monthly.plot(kind="line", ax=ax, marker="o", color="firebrick", linewidth=2)
            ax.set_title("Динаміка витрат за місяцями")
            ax.set_xlabel("Місяць")
            ax.set_ylabel("Сума витрат")
            plt.setp(ax.get_xticklabels(), rotation=45)
            df.reset_index(inplace=True)

        elif "ТОП-5 найбільших витратних категорій (горизонтальний графік)" in selected_analysis:
            grouped = df.groupby("Категорія")["Сума"].sum().sort_values(ascending=False)
            top_5 = grouped.head(5)
            top_5.plot(kind="barh", ax=ax, color="orange", alpha=0.8)
            ax.set_title("ТОП-5 найбільших витратних категорій")
            ax.set_xlabel("Сума витрат")
            ax.invert_yaxis()

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill="both")

    # -------------------------------------------------------------
    # Вкладка "Попередні записи"
    # -------------------------------------------------------------
    def setup_records_tab(self):
        content_frame = ttk.Frame(self.records_frame, style="MainFrame.TFrame")
        content_frame.pack(expand=True, fill="both", padx=20, pady=20)

        self.tree = ttk.Treeview(
            content_frame,
            columns=("Дата", "Сума", "Категорія", "Підкатегорія", "Коментар"),
            show="headings"
        )
        self.tree.pack(expand=True, fill="both")

        for col in ("Дата", "Сума", "Категорія", "Підкатегорія", "Коментар"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)

        ttk.Button(content_frame, text="Оновити", command=self.load_records).pack(pady=10)

        # Налаштуємо теги для “смугастих” рядків
        self.tree.tag_configure("evenrow", background="#ffffff")
        self.tree.tag_configure("oddrow", background="#f7f7f7")

    def load_records(self):
        df = self.expense_manager.get_expenses()
        self.tree.delete(*self.tree.get_children())

        for i, row in enumerate(df.itertuples(index=False), start=1):
            # row — кортеж з даними (Дата, Сума, Категорія, Підкатегорія, Коментар)
            # i — лічильник рядків
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.tree.insert("", "end", values=row, tags=(tag,))

    # -------------------------------------------------------------
    # Вкладка "Керування категоріями"
    # -------------------------------------------------------------
    def setup_admin_tab(self):
        admin_main_frame = ttk.Frame(self.admin_frame, style="MainFrame.TFrame")
        admin_main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        tree_frame = ttk.Frame(admin_main_frame, style="MainFrame.TFrame")
        tree_frame.pack(side="left", fill="both", expand=True)

        self.category_tree = ttk.Treeview(tree_frame, columns=("Type",), show="tree headings")
        self.category_tree.heading("#0", text="Категорія / Підкатегорія", anchor="w")
        self.category_tree.column("#0", width=200)
        self.category_tree.pack(side="left", fill="both", expand=True)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.category_tree.yview)
        vsb.pack(side="right", fill="y")
        self.category_tree.configure(yscrollcommand=vsb.set)

        # Налаштуємо теги для смугастих рядків
        self.category_tree.tag_configure("evenrow", background="#ffffff")
        self.category_tree.tag_configure("oddrow", background="#f7f7f7")

        buttons_frame = ttk.Frame(admin_main_frame, style="MainFrame.TFrame")
        buttons_frame.pack(side="right", fill="y", padx=10, pady=10)

        ttk.Label(buttons_frame, text="Нова Категорія:").pack(pady=5)
        self.new_category_entry = ttk.Entry(buttons_frame, width=20)
        self.new_category_entry.pack(pady=2)

        ttk.Button(buttons_frame, text="Додати категорію", command=self.add_category).pack(pady=2)
        ttk.Button(buttons_frame, text="Видалити категорію", command=self.delete_category).pack(pady=15)

        ttk.Label(buttons_frame, text="Нова Підкатегорія:").pack(pady=5)
        self.new_subcategory_entry = ttk.Entry(buttons_frame, width=20)
        self.new_subcategory_entry.pack(pady=2)

        ttk.Button(buttons_frame, text="Додати підкатегорію", command=self.add_subcategory).pack(pady=2)
        ttk.Button(buttons_frame, text="Видалити підкатегорію", command=self.delete_subcategory).pack(pady=15)

        ttk.Button(buttons_frame, text="Оновити дерево", command=self.populate_category_tree).pack(pady=20)

        self.populate_category_tree()

    def populate_category_tree(self):
        self.category_tree.delete(*self.category_tree.get_children())

        # Для створення смугастих рядків
        row_index = 1

        for cat, subcats in self.category_manager.categories.items():
            tag = "evenrow" if row_index % 2 == 0 else "oddrow"
            cat_id = self.category_tree.insert("", "end", text=cat, open=True, tags=(tag,))
            row_index += 1

            # Для підкатегорій теж зробимо чергування
            for sub in subcats:
                tag2 = "evenrow" if row_index % 2 == 0 else "oddrow"
                self.category_tree.insert(cat_id, "end", text=sub, tags=(tag2,))
                row_index += 1

    def add_category(self):
        new_cat = self.new_category_entry.get().strip()
        if not new_cat:
            messagebox.showerror("Помилка", "Введіть назву категорії!")
            return
        if new_cat in self.category_manager.categories:
            messagebox.showerror("Помилка", f"Категорія '{new_cat}' вже існує.")
            return

        self.category_manager.categories[new_cat] = []
        self.category_manager.save_categories()
        self.populate_category_tree()
        self.new_category_entry.delete(0, tk.END)
        self.show_notification(f"Категорію '{new_cat}' додано!")

    def delete_category(self):
        selection = self.category_tree.selection()
        if not selection:
            messagebox.showerror("Помилка", "Оберіть категорію для видалення!")
            return

        item_id = selection[0]
        cat_name = self.category_tree.item(item_id, "text")

        parent_id = self.category_tree.parent(item_id)
        if parent_id:
            messagebox.showerror("Помилка", "Оберіть саме категорію, а не підкатегорію.")
            return

        confirm = messagebox.askyesno("Підтвердження", f"Ви дійсно бажаєте видалити категорію '{cat_name}'?")
        if confirm:
            if cat_name in self.category_manager.categories:
                del self.category_manager.categories[cat_name]
                self.category_manager.save_categories()
                self.populate_category_tree()
                self.show_notification(f"Категорію '{cat_name}' видалено!")

    def add_subcategory(self):
        new_sub = self.new_subcategory_entry.get().strip()
        if not new_sub:
            messagebox.showerror("Помилка", "Введіть назву підкатегорії!")
            return

        selection = self.category_tree.selection()
        if not selection:
            messagebox.showerror("Помилка", "Оберіть категорію для додавання підкатегорії!")
            return

        item_id = selection[0]
        cat_name = self.category_tree.item(item_id, "text")
        parent_id = self.category_tree.parent(item_id)
        if parent_id:
            cat_name = self.category_tree.item(parent_id, "text")

        if cat_name not in self.category_manager.categories:
            messagebox.showerror("Помилка", "Оберіть правильну категорію (батьківський вузол)!")
            return

        if new_sub in self.category_manager.categories[cat_name]:
            messagebox.showerror("Помилка", f"Підкатегорія '{new_sub}' вже існує в категорії '{cat_name}'.")
            return

        self.category_manager.categories[cat_name].append(new_sub)
        self.category_manager.save_categories()
        self.populate_category_tree()
        self.new_subcategory_entry.delete(0, tk.END)
        self.show_notification(f"Підкатегорію '{new_sub}' додано до '{cat_name}'!")

    def delete_subcategory(self):
        selection = self.category_tree.selection()
        if not selection:
            messagebox.showerror("Помилка", "Оберіть підкатегорію для видалення!")
            return

        item_id = selection[0]
        sub_name = self.category_tree.item(item_id, "text")
        parent_id = self.category_tree.parent(item_id)
        if not parent_id:
            messagebox.showerror("Помилка", "Оберіть саме підкатегорію, а не категорію.")
            return

        cat_name = self.category_tree.item(parent_id, "text")
        confirm = messagebox.askyesno("Підтвердження", f"Ви дійсно бажаєте видалити підкатегорію '{sub_name}'?")
        if confirm:
            if cat_name in self.category_manager.categories:
                if sub_name in self.category_manager.categories[cat_name]:
                    self.category_manager.categories[cat_name].remove(sub_name)
                    self.category_manager.save_categories()
                    self.populate_category_tree()
                    self.show_notification(f"Підкатегорію '{sub_name}' видалено з '{cat_name}'!")

    # -------------------------------------------------------------
    # Метод для коротких сповіщень
    # -------------------------------------------------------------
    def show_notification(self, message):
        self.notification_label.config(text=message, foreground="green")
        self.root.after(3000, lambda: self.notification_label.config(text=""))
