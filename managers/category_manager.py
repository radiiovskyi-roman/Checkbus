import json
import os

class CategoryManager:
    def __init__(self, json_file_path="categories.json"):
        self.json_file_path = json_file_path
        self.categories = self.load_categories()

    def load_categories(self):
        if os.path.exists(self.json_file_path):
            with open(self.json_file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            base_categories = {
                "Оренда": ["Офіс", "Склад", "Дім"],
                "Транспорт": ["Таксі", "Авто", "Громадський транспорт"],
                "Зарплата": ["Співробітники", "Фрілансери"],
                "Інше": ["Канцелярія", "Обладнання", "Реклама"]
            }
            self.save_categories(base_categories)
            return base_categories

    def save_categories(self, categories=None):
        if categories is not None:
            self.categories = categories
        with open(self.json_file_path, "w", encoding="utf-8") as f:
            json.dump(self.categories, f, ensure_ascii=False, indent=2)
