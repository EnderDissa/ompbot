import os
import yaml
from datetime import datetime

class Metrics:
    def __init__(self):
        self.data = {
            "memo_received": 0,
            "memo_approved": 0,
            "memo_filtered": 0,
            "errors": 0,
            "history": []
        }
        self.filename = "metrics.yaml"
        if os.path.exists(self.filename):
            self.load_from_file()

    def record_memo_received(self, trigger):
        self.data["memo_received"] += 1
        self.data["history"].append({
            "timestamp": datetime.now().isoformat(),
            "event": "memo_received",
            "trigger": trigger
        })

    def record_memo_approved(self, trigger):
        self.data["memo_approved"] += 1
        self.data["history"].append({
            "timestamp": datetime.now().isoformat(),
            "event": "memo_approved",
            "trigger": trigger
        })

    def record_memo_filtered(self, trigger):
        self.data["memo_filtered"] += 1
        self.data["history"].append({
            "timestamp": datetime.now().isoformat(),
            "event": "memo_filtered",
            "trigger": trigger
        })

    def record_message(self, trigger):
        self.data["message"] += 1
        self.data["history"].append({
            "timestamp": datetime.now().isoformat(),
            "event": "message",
            "trigger": trigger
        })

    def record_error(self, trigger):
        self.data["error"] += 1
        self.data["history"].append({
            "timestamp": datetime.now().isoformat(),
            "event": "error",
            "trigger": trigger
        })
    def record_manager(self, trigger):
        self.data["manager"] += 1
        self.data["history"].append({
            "timestamp": datetime.now().isoformat(),
            "event": "manager",
            "trigger": trigger
        })

    def save_to_file(self):
        try:
            with open(self.filename, "w", encoding="utf-8") as file:
                yaml.dump(self.data, file, allow_unicode=True)
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
                        "received": 0,
                        "approved": 0,
                        "filtered": 0,
                        "errors": 0,
                        "history": []
                    }
        except Exception as e:
            print(f"Ошибка при загрузке метрик: {e}")

    def get_report(self):
        report = (
            f"Общее количество полученных записей: {self.data.get('received', 0)}\n"
            f"Сохранено записей: {self.data.get('saved', 0)}\n"
            f"Отфильтровано записей: {self.data.get('filtered', 0)}\n"
            f"Ошибок при обработке: {self.data.get('errors', 0)}\n"
        )
        return report