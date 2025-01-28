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

        # Створюємо Notebook (вкладки)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill="both")

        # Фрейми для вкладок
        self.entry_frame = ttk.Frame(self.notebook)
        self.analysis_frame = ttk.Frame(self.notebook)
        self.records_frame = ttk.Frame(self.notebook)
        self.admin_frame = ttk.Frame(self.notebook)  # вкладка адміністрування

        # Додаємо фрейми у Notebook
        self.notebook.add(self.entry_frame, text="Додавання витрат")
        self.notebook.add(self.analysis_frame, text="Фінансова аналітика")
        self.notebook.add(self.records_frame, text="Попередні записи")
        self.notebook.add(self.admin_frame, text="Керування категоріями")

        # Налаштовуємо кожну вкладку
        self.setup_entry_tab()
        self.setup_analysis_tab()
        self.setup_records_tab()
        self.setup_admin_tab()

        # Поле для сповіщень
        self.notification_label = ttk.Label(root, text="", foreground="green")
        self.notification_label.pack(side="bottom", anchor="w", padx=10, pady=5)

    def setup_style(self):
        """
        Налаштовуємо базовий стиль через ttk.Style (кольори, шрифти тощо).
        """
        style = ttk.Style(self.root)
        style.theme_use("clam")  # можна спробувати інші теми: "default", "alt", "vista" тощо

        style.configure("TNotebook", background="#f0f0f0", tabposition="nw")
        style.configure("TNotebook.Tab",
                        background="#d7d7d7",
                        foreground="#000",
                        padding=10,
                        font=("Arial", 10, "bold"))
        style.map("TNotebook.Tab",
                  background=[("selected", "#ffffff")],
                  foreground=[("selected", "#000000")])

        style.configure("TFrame", background="#f8f8f8")
        style.configure("TLabel", background="#f8f8f8", foreground="#333333", font=("Arial", 10))
        style.configure("TButton", font=("Arial", 10, "bold"), padding=5)
        style.configure("TEntry", font=("Arial", 10), padding=5)
        style.configure("TCombobox", font=("Arial", 10))

        style.configure("Treeview",
                        background="white",
                        foreground="#333",
                        rowheight=25,
                        fieldbackground="white",
                        font=("Arial", 9))
        style.configure("Treeview.Heading",
                        background="#007acc",
                        foreground="#ffffff",
                        font=("Arial", 10, "bold"))
        style.map("Treeview",
                  background=[("selected", "#cce5ff")])

    # ---------- Вкладка "Додавання витрат" ----------

    def setup_entry_tab(self):
        ttk.Label(self.entry_frame, text="Дата").pack(pady=(10, 0))
        self.date_entry = DateEntry(self.entry_frame, date_pattern='yyyy-MM-dd')
        self.date_entry.pack()

        ttk.Label(self.entry_frame, text="Сума").pack(pady=(10, 0))
        self.amount_entry = ttk.Entry(self.entry_frame)
        self.amount_entry.pack()
        self.amount_entry.bind("<KeyRelease>", self.validate_amount)

        ttk.Label(self.entry_frame, text="Категорія").pack(pady=(10, 0))
        self.category_cb = ttk.Combobox(
            self.entry_frame,
            values=list(self.category_manager.categories.keys()),
            state="readonly"
        )
        self.category_cb.pack()
        self.category_cb.bind("<<ComboboxSelected>>", self.update_subcategories)

        ttk.Label(self.entry_frame, text="Підкатегорія").pack(pady=(10, 0))
        self.subcategory_cb = ttk.Combobox(self.entry_frame, state="readonly")
        self.subcategory_cb.pack()

        ttk.Label(self.entry_frame, text="Коментар").pack(pady=(10, 0))
        self.comment_entry = ttk.Entry(self.entry_frame)
        self.comment_entry.pack()

        ttk.Button(self.entry_frame, text="Додати витрату", command=self.add_expense).pack(pady=(10, 0))

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

    # ---------- Вкладка "Фінансова аналітика" ----------

    def setup_analysis_tab(self):
        controls_frame = ttk.Frame(self.analysis_frame)
        controls_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(controls_frame, text="Оберіть тип аналітики:").pack(side="left", padx=5)

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

        self.canvas_frame = ttk.Frame(self.analysis_frame)
        self.canvas_frame.pack(expand=True, fill="both", padx=5, pady=5)

    def show_statistics(self):
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

        df = self.expense_manager.get_expenses()

        df["Дата"] = pd.to_datetime(df["Дата"], errors="coerce")
        df["Сума"] = pd.to_numeric(df["Сума"], errors="coerce")
        df.dropna(subset=["Дата", "Сума"], inplace=True)

        if df.empty:
            messagebox.showinfo("Інформація", "Немає даних для відображення аналітики.")
            return

        selected_analysis = self.analysis_type_cb.get()
        fig, ax = plt.subplots(figsize=(8, 6), dpi=100)

        # 1. Витрати за категоріями (стовпчиковий графік)
        if "Витрати за категоріями (стовпчиковий графік)" in selected_analysis:
            grouped = df.groupby("Категорія")["Сума"].sum()
            grouped.plot(kind="bar", ax=ax, color="royalblue", alpha=0.8)
            ax.set_title("Витрати за категоріями")
            ax.set_xlabel("Категорія")
            ax.set_ylabel("Сума витрат")
            ax.tick_params(axis='x', rotation=45)

        # 2. Витрати за підкатегоріями (стовпчиковий графік)
        elif "Витрати за підкатегоріями (стовпчиковий графік)" in selected_analysis:
            grouped = df.groupby(["Категорія", "Підкатегорія"])["Сума"].sum()
            grouped.index = grouped.index.map(lambda x: f"{x[0]}: {x[1]}")
            grouped.plot(kind="bar", ax=ax, color="forestgreen", alpha=0.8)
            ax.set_title("Витрати за підкатегоріями")
            ax.set_xlabel("Категорія:Підкатегорія")
            ax.set_ylabel("Сума витрат")
            ax.tick_params(axis='x', rotation=75)

        # 3. Витрати за категоріями (кругова діаграма)
        elif "Витрати за категоріями (кругова діаграма)" in selected_analysis:
            grouped = df.groupby("Категорія")["Сума"].sum()
            ax.pie(grouped, labels=grouped.index, autopct='%1.1f%%', startangle=140)
            ax.set_title("Структура витрат за категоріями")

        # 4. Динаміка витрат за місяцями (лінійний графік)
        elif "Динаміка витрат за місяцями (лінійний графік)" in selected_analysis:
            df.set_index("Дата", inplace=True)
            monthly = df.resample('M')["Сума"].sum()
            monthly.plot(kind="line", ax=ax, marker="o", color="firebrick", linewidth=2)
            ax.set_title("Динаміка витрат за місяцями")
            ax.set_xlabel("Місяць")
            ax.set_ylabel("Сума витрат")
            plt.setp(ax.get_xticklabels(), rotation=45)
            df.reset_index(inplace=True)

        # 5. ТОП-5 найбільших витратних категорій (горизонтальний графік)
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

    # ---------- Вкладка "Попередні записи" ----------

    def setup_records_tab(self):
        self.tree = ttk.Treeview(self.records_frame,
                                 columns=("Дата", "Сума", "Категорія", "Підкатегорія", "Коментар"),
                                 show="headings")
        self.tree.pack(expand=True, fill="both")

        for col in ("Дата", "Сума", "Категорія", "Підкатегорія", "Коментар"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=140)

        ttk.Button(self.records_frame, text="Оновити", command=self.load_records).pack(pady=5)

    def load_records(self):
        df = self.expense_manager.get_expenses()
        self.tree.delete(*self.tree.get_children())
        for _, row in df.iterrows():
            self.tree.insert("", "end", values=list(row))

    # ---------- Вкладка "Керування категоріями" (адміністрування) ----------

    def setup_admin_tab(self):
        admin_main_frame = ttk.Frame(self.admin_frame)
        admin_main_frame.pack(expand=True, fill="both")

        tree_frame = ttk.Frame(admin_main_frame)
        tree_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        self.category_tree = ttk.Treeview(tree_frame, columns=("Type",), show="tree headings")
        self.category_tree.heading("#0", text="Категорія / Підкатегорія", anchor="w")
        self.category_tree.column("#0", width=200)
        self.category_tree.pack(side="left", fill="both", expand=True)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.category_tree.yview)
        vsb.pack(side="right", fill="y")
        self.category_tree.configure(yscrollcommand=vsb.set)

        buttons_frame = ttk.Frame(admin_main_frame)
        buttons_frame.pack(side="right", fill="y", padx=5, pady=5)

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

        # Початково заповнимо дерево
        self.populate_category_tree()

    def populate_category_tree(self):
        self.category_tree.delete(*self.category_tree.get_children())
        for cat, subcats in self.category_manager.categories.items():
            cat_id = self.category_tree.insert("", "end", text=cat, open=True)
            for sub in subcats:
                self.category_tree.insert(cat_id, "end", text=sub)

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

        # Оновлюємо список категорій у вкладці “Додавання витрат”
        self.category_cb["values"] = list(self.category_manager.categories.keys())

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
                self.category_cb["values"] = list(self.category_manager.categories.keys())

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

    def show_notification(self, message):
        self.notification_label.config(text=message, foreground="green")
        self.root.after(3000, lambda: self.notification_label.config(text=""))

