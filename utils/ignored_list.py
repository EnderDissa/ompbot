# -*- coding: utf-8 -*-

class IgnoredList:
    def __init__(self):
        self.ignored = set()

    def add(self, uid):
        if uid not in self.ignored:
            self.ignored.add(uid)
            print("Пользователь {} добавлен в игнор.".format(uid))
        else:
            print("Пользователь {} уже в игноре.".format(uid))

    def remove(self, uid):
        if uid in self.ignored:
            self.ignored.remove(uid)
            print("Пользователь {} удалён из игнора.".format(uid))
        else:
            print("Пользователь {} не найден в списке игнорируемых.".format(uid))

    def is_ignored(self, uid):
        return uid in self.ignored

    def clear(self):
        self.ignored.clear()
        print("Список игнорируемых пользователей очищен.")

    def save_to_file(self):
        try:
            with open("data/ignored.txt", 'w+') as file:
                file.write('\n'.join(map(str, self.ignored)))
            print("Список игнорируемых сохранён.")
        except Exception as e:
            print("Ошибка при сохранении: {}".format(e))

    def load_from_file(self):
        try:
            with open("data/ignored.txt", 'r') as file:
                self.ignored = set(map(lambda x: int(x.strip()), file.readlines()))
            return ("Список игнорируемых загружен.")
        except Exception as e:
            print("Ошибка при загрузке: {}".format(e))
