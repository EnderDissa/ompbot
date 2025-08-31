import os
import yaml
from datetime import datetime

class Metrics:
    def __init__(self):
        self.data = {
            "memo_received": 0,
            "memo_approved": 0,
            "memo_filtered": 0,
            "message": 0,
            "errors": 0,
            "manager": 0,
            "history": []
        }
        self.filename = "/data/metrics.yaml"
        if os.path.exists(self.filename):
            self.load_from_file()

    def record_memo_received(self, trigger):
        self.data["memo_received"] += 1
        self.data["history"].append({
            "timestamp": datetime.now().isoformat(),
            "event": "memo_received",
            "trigger": trigger
        })
        self.save_to_file()

    def record_memo_approved(self, trigger):
        self.data["memo_approved"] += 1
        self.data["history"].append({
            "timestamp": datetime.now().isoformat(),
            "event": "memo_approved",
            "trigger": trigger
        })
        self.save_to_file()

    def record_memo_filtered(self, trigger):
        self.data["memo_filtered"] += 1
        self.data["history"].append({
            "timestamp": datetime.now().isoformat(),
            "event": "memo_filtered",
            "trigger": trigger
        })
        self.save_to_file()

    def record_message(self, trigger):
        self.data["message"] += 1
        self.data["history"].append({
            "timestamp": datetime.now().isoformat(),
            "event": "message",
            "trigger": trigger
        })
        self.save_to_file()

    def record_error(self, trigger):
        self.data["errors"] += 1
        self.data["history"].append({
            "timestamp": datetime.now().isoformat(),
            "event": "error",
            "trigger": trigger
        })
        self.save_to_file()

    def record_manager(self, trigger):
        self.data["manager"] += 1
        self.data["history"].append({
            "timestamp": datetime.now().isoformat(),
            "event": "manager",
            "trigger": trigger
        })
        self.save_to_file()

    def save_to_file(self):
        try:
            data_ordered = {
                "memo_received": self.data.get("memo_received", 0),
                "memo_approved": self.data.get("memo_approved", 0),
                "memo_filtered": self.data.get("memo_filtered", 0),
                "message": self.data.get("message", 0),
                "manager": self.data.get("manager", 0),
                "errors": self.data.get("errors", 0),
                "history": self.data.get("history", [])
            }
            with open(self.filename, "w", encoding="utf-8") as file:
                yaml.dump(data_ordered, file, allow_unicode=True)
        except Exception as e:
            print(f"Ошибка при сохранении метрик: {e}")

    def load_from_file(self):
        try:
            with open(self.filename, "r", encoding="utf-8") as file:
                loaded = yaml.safe_load(file)
                if loaded is not None:
                    self.data = loaded
                else:
                    self.data = {
                        "memo_received": 0,
                        "memo_approved": 0,
                        "memo_filtered": 0,
                        "message": 0,
                        "errors": 0,
                        "manager": 0,
                        "history": []
                    }
                    self.save_to_file()
        except Exception as e:
            print(f"Ошибка при загрузке метрик: {e}")

    def get_report(self):
        report = (
            f"Всего сообщений: {self.data.get('message', 0)}\n"
            f"Ошибок при обработке: {self.data.get('errors', 0)}\n"
            f"Помощь менеджера понадобилась: {self.data.get('manager', 0)}\n"
            "\n"
            f"Поступило служебок: {self.data.get('memo_received', 0)}\n"
            f"Одобрено служебок: {self.data.get('memo_approved', 0)}\n"
            f"Отфильтровано служебок: {self.data.get('memo_filtered', 0)}\n"
        )
        return report