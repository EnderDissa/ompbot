from .ignored_list import IgnoredList
from .excel import *
from .VKHelper import *
from .IP import *


def initialize():
    with open("token.txt", 'r') as f:
        token = f.readline()
    return token
