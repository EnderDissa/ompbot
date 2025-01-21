# use after git cloning.
import os
import getpass

required_dirs = [
    'xlsx'
]

def create():
    for directory in required_dirs:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Создана папка: {directory}")

    if not os.path.exists('token.txt'):
        token=getpass.getpass("введи токен приложения VK:\n")
        with open ('token.txt', 'w') as f:
            f.write(token)
        print(f"токен успешно записан")


if __name__ == "__main__":
    create()