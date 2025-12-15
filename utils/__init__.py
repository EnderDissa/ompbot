from .ignored_list import IgnoredList
from .excel_helper import *
from .vk_helper import *
from .net_helper import *



def get_secrets():
    # with open("token.txt", 'r') as f:
    #     token = f.readline()
    # with open("mail_password.txt", 'r') as f:
    #     mail_password = f.readline()
    token = os.getenv('BOT_TOKEN')
    mail_password = os.getenv('MAIL_PASSWORD')
    return {'token': token, 'mail_password': mail_password}
