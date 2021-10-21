import datetime
import os
from flask import Flask, redirect, url_for, render_template, request
import sqlite3
from werkzeug.utils import secure_filename
import utils
from CustomErrors import UsernameError
from User import User

app = Flask(__name__, static_folder="static", static_url_path="", template_folder="templates")

current_user: User = None


@app.route('/index.html')
def home():
    con = sqlite3.connect("Users.db")
    ads = con.execute("SELECT * FROM Ad").fetchall()[:5]
    con.close()
    return render_template("index.html",
                           ads=ads,
                           username="Login / Register" if current_user is None else current_user.username,
                           profile_link="loginRegister.html" if current_user is None else "dashboard.html")


@app.route('/postad.html', methods=["GET", "POST"])
def post_ad():
    if request.method == "GET":
        return render_template('postad.html',username=current_user.username)
    else:
        try:
            con = sqlite3.connect("Users.db")
            form = request.form

            con.execute('INSERT INTO Ad VALUES(?,?,?,?,?,?,?,?,?,?)',
                        [f'{form.get("title")}',
                         f'{form.get("domain")}',
                         f'{form.get("state")}',
                         f'{form.get("city")}',
                         f'{form.get("author")}',
                         f'{form.get("ISBN")}',
                         f'{current_user.username}',
                         f'{float(form.get("price"))}',
                         f'{form.get("desc")}',
                         hash(str(datetime.datetime.now()) + current_user.username + form.get("ISBN"))
                         ]
                        )
            con.commit()
        except Exception as e:
            raise e
    return redirect(url_for('home'))


@app.route('/loginRegister.html', methods=["GET", "POST"])
@app.route('/', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template('loginRegister.html',
                               username_text="",
                               show_signup="",
                               show_signin="show active")
    form = request.form
    if "signupsubmit" in form:
        con = sqlite3.connect('Users.db')
        try:
            if len(con.execute(f'SELECT * FROM Users WHERE username = "{form.get("username")}"').fetchall()) > 0:
                raise UsernameError
            con.execute(
                f'INSERT INTO Users VALUES("{form.get("username")}","{form.get("password")}","{form.get("email")}","{form.get("phone")}")')
            con.commit()
            global current_user
            current_user = User(form.get("username"))
            con.close()
        except sqlite3.IntegrityError:
            return render_template('loginRegister.html',
                                   email_text="ACCOUNT WITH THIS EMAIL ALREADY EXISTS",
                                   show_signup="show active",
                                   show_signin="")
        except UsernameError as e:
            return render_template('loginRegister.html',
                                   username_text=str(e),
                                   show_signup="show active",
                                   show_signin="")

    if "signinsubmit" in form:
        con = sqlite3.connect('Users.db')
        username = form.get("signin_username")
        password = form.get("signin_password")
        x = con.execute(f'SELECT password FROM Users WHERE username = "{username}"').fetchone()
        if x[0] != password:
            return render_template('loginRegister.html',
                                   signin_text="USERNAME OR PASSWORD INCORRECT!",
                                   show_signup="",
                                   show_signin="show active")
        current_user = User(username)
        con.close()

    return redirect(url_for('home'))


@app.route("/allads.html")
def allads():
    con = sqlite3.connect("Users.db")
    ads = con.execute("SELECT * FROM Ad").fetchall()
    con.close()
    return render_template("allads.html", ads=ads)


@app.route("/product")
def product():
    id = request.args.get("id")
    print("id",id)
    con = sqlite3.connect("Users.db")
    ad = con.execute(f"SELECT * FROM Ad JOIN Users ON Ad.username = Users.username WHERE ad_id = {id}").fetchone()
    print(ad)
    con.close()
    return render_template("product.html",
                           title=ad[0],
                           price=ad[7],
                           domain=ad[1],
                           seller=ad[6],
                           seller_phone=ad[12], #KEPT AS EMAIL ID FOR NOW
                           state=ad[2],
                           author=ad[4],
                           ISBN=ad[5],
                           city=ad[3],
                           desc=ad[8]
                           )


@app.route("/<resourcename>")
def get_resource(resourcename):
    print(resourcename)
    return render_template(resourcename)


if __name__ == '__main__':
    app.run(port=912)
