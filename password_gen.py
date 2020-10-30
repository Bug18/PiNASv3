import random as rd
import string


def list_str():
    list_of_strings = []
    for x in string.ascii_letters:
        list_of_strings.append(x)
    for y in range(1, 10):
        list_of_strings.append(str(y))
    rd.shuffle(list_of_strings)
    return list_of_strings


def gen_passwd():
    chars = list_str()
    passwd = ""
    for i in range(10):
        index = rd.randint(0, len(chars) - 1)
        passwd += str(chars[index])
    return passwd
