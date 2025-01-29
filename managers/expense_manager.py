import os
import pandas as pd

class ExpenseManager:
    def __init__(self, csv_file_path="expenses.csv"):
        self.csv_file_path = csv_file_path
        self.init_csv()

    def init_csv(self):
        if not os.path.exists(self.csv_file_path):
            pd.DataFrame(columns=["Дата", "Сума", "Категорія", "Підкатегорія", "Коментар"]) \
              .to_csv(self.csv_file_path, index=False)

    def add_expense(self, record: dict):
        df = pd.read_csv(self.csv_file_path)
        df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
        df.to_csv(self.csv_file_path, index=False)

    def get_expenses(self) -> pd.DataFrame:
        return pd.read_csv(self.csv_file_path)
