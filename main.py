from flask import Flask, redirect, url_for, render_template, request
import sqlite3

from CustomErrors import UsernameError

app = Flask(__name__, static_folder="static", static_url_path="", template_folder="templates")


@app.route('/index.html')
@app.route('/')
def home():
    return render_template("index.html")

@app.route('/postad.html', methods=["GET", "POST"])
def post_ad():
    if request.method == "GET":
        return render_template('postad.html')
    else:
        print(request.values)
        print(request.form)
        print(request.json)
        print(request.files)
        print(request.form.get("price"))
        print(request.form.get("title"))
        return redirect(url_for('home'))


@app.route('/loginRegister.html', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template('loginRegister.html',
                               username_text="",
                               show_signup = "",
                               show_signin="show active")
    form = request.form
    if "signupsubmit" in form:
        con = sqlite3.connect('Users.db')
        print(form.get("username"))
        try:
            if len(con.execute(f'SELECT * FROM Users WHERE username = "{form.get("username")}"').fetchall()) > 0:
                raise UsernameError
            con.execute(f'INSERT INTO Users VALUES("{form.get("username")}","{form.get("password")}","{form.get("email")}","{form.get("phone")}")')
            con.commit()
            con.close()
        except sqlite3.IntegrityError:
            return render_template('loginRegister.html',
                                   email_text="ACCOUNT WITH THIS EMAIL ALREADY EXISTS",
                                   show_signup = "show active",
                                   show_signin="")
        except UsernameError as e:
            return render_template('loginRegister.html',
                                   username_text=str(e),
                                   show_signup="show active",
                                   show_signin="")
    return redirect(url_for('home'))

@app.route("/<resourcename>")
def get_resource(resourcename):
    print(resourcename)
    return render_template(resourcename)

if __name__ == '__main__':
    app.run()

