#! /usr/bin/env python3
import shutil
import os


def check_drives():
    drives = ['sda1', 'sdb1', 'sdc1', 'sdd1']
    ext_drives = []
    for drive in drives:
        path = "/mnt/media/" + drive
        try:
            directory = os.listdir(path)
            if directory != []:
                ext_drives.append(drive)
        except:
            pass
    return ext_drives


def set_drive():
    drives = os.listdir('/dev/')
    for part in drives:
        if "sda1" in part or "sdb1" in part:
            command = 'sudo mount /dev/' + part + ' /mnt/media/' + part
            os.system(command)


def get_drive_info(drives):
    total, used, free = [], [], []
    for drive in drives:
        path = "/mnt/media" + drive
        total.append(round(shutil.disk_usage(path)[0] / (2 ** 30), 2))
        used.append(round(shutil.disk_usage(path)[1] / (2 ** 30), 2))
        free.append(round(shutil.disk_usage(path)[2] / (2 ** 30), 2))
    return total, used, free


def ftp_data(name, password):
    ftp_data = open("ftp_data.txt", 'w+')
    ftp_data.write(str(name) + ";" + str(password) + " ")
    ftp_data.close()
