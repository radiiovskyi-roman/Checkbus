import tkinter as tk
from managers.category_manager import CategoryManager
from managers.expense_manager import ExpenseManager
from app.finance_app import FinanceApp

def main():
    root = tk.Tk()

    category_manager = CategoryManager("categories.json")
    expense_manager = ExpenseManager("expenses.csv")

    app = FinanceApp(root, category_manager, expense_manager)
    root.mainloop()

if __name__ == "__main__":
    main()
