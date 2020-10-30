import bcrypt


def hashing_func(passwd):
    salt = bcrypt.gensalt(rounds=16)
    hashed_password = bcrypt.hashpw(bytes(passwd, "utf8"), salt)
    passwd = None
    return hashed_password


def check_passwd(passwd, hashed_password):
    if bcrypt.checkpw(passwd, hashed_password):
        return True
    else:
        return False
