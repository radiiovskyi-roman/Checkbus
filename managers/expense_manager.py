import os
import pandas as pd

class ExpenseManager:
    """
    Відповідає за роботу з витратами (CSV-файл).
    Ініціалізація, додавання, зчитування тощо.
    """
    def __init__(self, csv_file_path="expenses.csv"):
        self.csv_file_path = csv_file_path
        self.init_csv()

    def init_csv(self):
        """
        Перевіряє, чи існує файл із витратами,
        якщо ні — створює зі стандартними стовпцями.
        """
        if not os.path.exists(self.csv_file_path):
            pd.DataFrame(columns=["Дата", "Сума", "Категорія", "Підкатегорія", "Коментар"]) \
              .to_csv(self.csv_file_path, index=False)

    def add_expense(self, record: dict):
        """
        Додає витрату до CSV-файлу.
        Параметр record — це словник із ключами:
        ["Дата", "Сума", "Категорія", "Підкатегорія", "Коментар"]
        """
        df = pd.read_csv(self.csv_file_path)
        df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
        df.to_csv(self.csv_file_path, index=False)

    def get_expenses(self) -> pd.DataFrame:
        """
        Повертає витрати у вигляді DataFrame.
        """
        return pd.read_csv(self.csv_file_path)
