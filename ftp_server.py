#! /usr/bin/env python3

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer


IP = "your IP inside quotes"
FTP_PORT = 2121 #this can be changed to 21 if you will be running server as root


def get_users():
    users_db = open("ftp_data.txt", 'r+')
    lines = users_db.readlines()
    try:
        lines = lines[0].split()
    except:
        return []
    all_users = []
    for n in range(len(lines)):
        user = lines[n].split(';')
        all_users.append(user)
    users_db.close()
    return all_users


def main():
    FTP_DATA = get_users()
    while FTP_DATA == []:
        FTP_DATA = get_users()
    authorizer = DummyAuthorizer()
    for user in FTP_DATA:
        FTP_DIRECTORY = "/mnt/media/"
        FTP_USER = user[0]
        FTP_PASSWORD = user[1]
        print(FTP_PASSWORD)
        authorizer.add_user(FTP_USER, FTP_PASSWORD, FTP_DIRECTORY, perm='elradfmw')
    handler = FTPHandler
    handler.authorizer = authorizer
    handler.max_login_attempts = 3
    handler.banner = "FTP ready..."
    handler.passive_ports = range(60000, 65535)

    address = (IP, FTP_PORT)

    server = FTPServer(address, handler)
    server.max_cons = 128
    server.max_cons_per_ip = 5
    server.serve_forever()


if __name__ == '__main__':
    main()
