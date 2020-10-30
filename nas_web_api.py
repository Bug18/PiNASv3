#! /usr/bin/env python3
# NAS Web API

from flask import Flask, redirect, url_for, render_template, request, session, flash, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from hashing_alg_v2 import hashing_func, check_passwd
from nas_conf import *
from password_gen import gen_passwd


app = Flask(__name__)
app.secret_key = gen_passwd()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Users.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

database = SQLAlchemy(app)

ftp_password = gen_passwd()
logged_in_users = []


class Users(database.Model):
    _id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(100))
    email = database.Column(database.String(100))
    passwd = database.Column(database.String(200))

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.passwd = password


@app.route("/")
def home_page():
    return render_template("home.html")


@app.route("/admin/<actions>", methods=["POST", "GET"])
def admin_page(actions):
    try:
        if session["username"] != "admin":
            flash("You are not allowed to accesses that page!")
            return redirect(url_for("home_page"))
    except:
        flash("Log In first!")
        return redirect(url_for("login"))
    rowsa = Users.query.all()
    if request.method == "GET":
        if actions == "addusr":
            return render_template("adduser.html")
        elif actions == "rmusr":
            rows = Users.query.all()
            return render_template("rmuser.html", rows=rows)
    if request.method == "POST":
        if "0add" in actions:
            name = request.form["username"]
            email = request.form["email"]
            passwd = request.form["password"]
            passwd2 = request.form["password2"]
            if name == "" or email == "" or passwd == "":
                flash("You didn't enter valid user information! Try again!")
                return redirect(url_for("admin_page", actions=0))
            if passwd != passwd2:
                flash("Passwords don't match!")
                name, email, passwd, passwd2 = None, None, None, None
                return render_template("adduser.html")
            else:
                hashpasswd = hashing_func(passwd)
                user = Users(name=name, email=email, password=hashpasswd)
                database.session.add(user)
                database.session.commit()
                flash("User added successfully!")
                return redirect(url_for("admin_page", actions=0))
        elif "0rm" in actions:
            user_id = request.form["idvalue"]
            try:
                usernm = Users.query.filter_by(_id=user_id).first()
                usernm = usernm.name
                Users.query.filter_by(_id=user_id).delete()
                database.session.commit()
                flash("User " + usernm + " successfully removed!")
                return redirect(url_for("admin_page", actions=0))
            except:
                flash("You didn't enter user id!")
                return redirect(url_for("admin_page", actions=0))
    return render_template("admin.html", rows=rowsa)


@app.route("/drives")
def drives():
    if "username" not in session:
        flash("Log in first!")
        return redirect(url_for("login"))
    drives = []
    avb_drives = check_drives()
    if avb_drives == []:
        set_drive()
    total, used, free = get_drive_info(avb_drives)
    for i in range(len(avb_drives)):
        drives.append([avb_drives[i], total[i], used[i], free[i]])
    return render_template("drives.html", drives=drives)


@app.route("/userinfo/<actions2>", methods=["POST", "GET"])
def userinfo(actions2):
    if "username" not in session:
        flash("Log in first!")
        return redirect(url_for("login"))
    user = session["username"]
    for n in range(len(logged_in_users) + 1):
        try:
            if user not in logged_in_users[n] and ftp_password not in logged_in_users[n] and user != "admin":
                ftp_data(user, ftp_password)
                logged_in_users.append([user, ftp_password])
        except:
            if logged_in_users == []:
                ftp_data(user, ftp_password)
                logged_in_users.append([user, ftp_password])
    if request.method == "GET":
        if actions2 == "chgusrinfo":
            rows = Users.query.all()
            return render_template("chgusrinfo.html", rows=rows)
        elif actions2 == "chgusrpass":
            rows = Users.query.all()
            return render_template("chgusrpass.html", rows=rows)
    elif request.method == "POST":
        if "0chg" in actions2:
            usr_id = request.form["idchg"]
            if usr_id == "":
                flash("You did not enter user ID!")
                return render_template("userinfo.html", user=user)
            usrnm = Users.query.filter_by(_id=usr_id).first()
            if usrnm == None:
                flash("Please enter valid user ID!")
                return redirect(url_for("userinfo", actions2='/chgusrinfo'))
            else:
                new_usrnm = request.form["usrchg"]
                new_em = request.form["emchg"]
                if new_usrnm == "" and new_em == "":
                    flash("Please enter new username or new email!")
                    return redirect(url_for("userinfo", actions2='/chgusrinfo'))
                if new_usrnm != "":
                    usrnm.name = new_usrnm
                if new_em != "":
                    usrnm.email = new_em
                database.session.commit()
                flash("Please log in again with new username!")
                return redirect(url_for("logout"))
        elif "0pass" in actions2:
            usr_id = request.form["idpasschg"]
            if usr_id == "":
                flash("You did not enter user ID!")
                return render_template("userinfo.html", user=user)
            usrnm = Users.query.filter_by(_id=usr_id).first()
            if usrnm == None:
                flash("Please enter valid user ID!")
                return redirect(url_for("userinfo", actions2='/chgusrinfo'))
            else:
                password = check_passwd(bytes(request.form["passwdchk"], "utf8"), usrnm.passwd)
                if password == False:
                    flash("You entered wrong password! Try again!")
                    return redirect(url_for("userinfo"), actions2=0, name=user, ftp_passwd=ftp_password)
                elif password == True:
                    new_passwd = request.form["passchg1"]
                    new_passwd2 = request.form["passchg2"]
                    if new_passwd != new_passwd2:
                        flash("New password do not match! Try again!")
                        return render_template("chgusrpass.html")
                    elif new_passwd == new_passwd2:
                        usrnm.passwd = hashing_func(new_passwd)
                        database.session.commit()
                        new_passwd, new_passwd2 = None, None
                        flash("Log in with new password!")
                        return redirect(url_for("logout"))
    return render_template("userinfo.html", user=user, ftp_passwd=ftp_password)


@app.route("/login", methods=["POST", "GET"])
def login():
    if "username" in session:
        flash("Already logged in!")
        return redirect(url_for("userinfo", actions2=0))
    if request.method == "POST":
        name = request.form["username"]
        if name == "admin":
            user = Users.query.filter_by(name=name).first()
            password = check_passwd(bytes(request.form["password"], "utf8"), user.passwd)
            if password == True:
                session["username"] = name
                return redirect(url_for("admin_page", actions=0))
            else:
                flash("Incorrect password!")
                return redirect(url_for("login"))
        try:
            user = Users.query.filter_by(name=name).first()
            password = check_passwd(bytes(request.form["password"], "utf8"), user.passwd)
            if name == user.name:
                if password == True:
                    session["username"] = name
                    flash("Logged in successfully!")
                    return redirect(url_for("userinfo", actions2=0))
                else:
                    flash("Wrong password!")
                    return redirect(url_for("login"))
        except:
            flash("User does not exist!")
            return redirect(url_for("login"))
    return render_template("login.html")


@app.route("/logout")
def logout():
    try:
        username = session["username"]
        if username == "admin":
            session.pop("username", None)
            session.pop("flag", None)
            return redirect(url_for("login"))
        else:
            session.pop("username", None)
            flash("Logged out successfully!", "info")
            return redirect(url_for("login"))
    except:
        flash("Please login first!", "info")
        return redirect(url_for("login"))


if __name__ == "__main__":
    database.create_all()
    app.run(debug=True, host='0.0.0.0') #you can also add port=80 if you will be running server as root or port=8080 if you won't
