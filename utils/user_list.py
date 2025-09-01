import yaml

class UserList:
    def __init__(self):
        self.users = {}  # Формат: {uid: set(clubs)}
        self.clubs = set()

    def add(self, uid, club):
        self.load_from_file()

        if uid not in self.users:
            self.users[uid] = set()
        if club not in self.users[uid]:
            self.users[uid].add(club)
            self.clubs.add(club)
            print(f"Пользователь {uid} теперь руководит клубом {club}.")
        else:
            print(f"Пользователь {uid} уже руководит клубом {club}.")

        self.save_to_file()

    # def remove(self, uid, club=None):
    #     if uid not in self.users:
    #         print(f"Пользователь {uid} не найден в списке.")
    #         return
    #
    #     if club:
    #         if club in self.users[uid]:
    #             self.users[uid].remove(club)
    #             print(f"Клуб {club} удалён у пользователя {uid}.")
    #             if not self.users[uid]:  # Если у пользователя больше нет клубов, удаляем его
    #                 del self.users[uid]
    #                 print(f"Пользователь {uid} удалён из списка, так как больше не руководит ни одним клубом.")
    #         else:
    #             print(f"Пользователь {uid} не руководит клубом {club}.")
    #     else:
    #         del self.users[uid]
    #         print(f"Пользователь {uid} полностью удалён из списка.")

    def is_user(self, uid):
        return uid in self.users

    def get_clubs(self, uid):
        return self.users.get(uid, set())

    # def clear(self):
    #     self.users.clear()
    #     self.clubs.clear()
    #     print("Список пользователей и клубов очищен.")

    def save_to_file(self, filename="data/users.yml"):
        try:
            with open(filename, "w", encoding="utf-8") as file:
                yaml.dump({str(uid): list(clubs) for uid, clubs in self.users.items()}, file, allow_unicode=True)
        except Exception as e:
            print(f"Ошибка при сохранении: {e}")

    def load_from_file(self, filename="data/users.yml"):
        try:
            with open(filename, "r+", encoding="utf-8") as file:
                data = yaml.safe_load(file)
                if data is not None:
                    self.users = {int(uid): set(clubs) for uid, clubs in data.items()}
                    self.clubs = {club for clubs in self.users.values() for club in clubs}
                else:
                    self.users = {}
                    self.clubs = set()
        except Exception as e:
            print(f"Ошибка при загрузке: {e}")
