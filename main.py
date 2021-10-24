import base64
import datetime
import os
import requests
import utils
from flask import Flask, redirect, url_for, render_template, request
import sqlite3
from CustomErrors import UsernameError
from User import User

app = Flask(__name__, static_folder="static", static_url_path="", template_folder="templates")
UPLOAD_FOLDER = 'static\\uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
current_user: User = None


@app.route('/index.html')
def home():
    con = sqlite3.connect("Users.db")
    ads = con.execute("SELECT * FROM Ad").fetchall()[-6:]
    con.close()
    return render_template("index.html",
                           ads=ads,
                           username="Login / Register" if current_user is None else current_user.username,
                           profile_link="loginRegister.html" if current_user is None else "dashboard.html")


@app.route('/postad.html', methods=["GET", "POST"])
def post_ad():
    if request.method == "GET":
        return render_template('postad.html', username=current_user.username)
    else:
        try:
            con = sqlite3.connect("Users.db")
            form = request.form
            ad_id = hex(abs(hash(str(datetime.datetime.now()) + current_user.username + form.get("ISBN")))).lstrip(
                "0x").rstrip("L")
            con.execute('INSERT INTO Ad VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                        [f'{form.get("title")}',
                         f'{form.get("domain")}',
                         f'{form.get("state")}',
                         f'{form.get("city")}',
                         f'{form.get("author")}',
                         f'{form.get("ISBN")}',
                         f'{current_user.username}',
                         f'{float(form.get("price"))}',
                         f'{form.get("desc")}',
                         ad_id,
                         f'{form.get("age-group")}',
                         "ACTIVE",
                         str(datetime.date.today()),
                         0
                         ]
                        )

            files = request.files.getlist('images')
            print(files)
            for file in files:
                image_path = os.path.join(app.config["UPLOAD_FOLDER"], (ad_id + "_" + file.filename))
                con.execute("INSERT INTO post_images(post_id, image_path) VALUES(?,?)",
                            [
                                ad_id,
                                str(image_path).replace("static\\", "")
                            ]
                            )
                file.save(image_path)
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
    images = []
    for ad in ads:
        print(ad[9])
        img = utils.get_images(ad[9])
        print(img)
        img = img[0] if img else "img/logo_200x200.png"
        print(img)
        images.append(img)
    print(images)
    con.close()
    return render_template("allads.html", ads=ads, images=images)


@app.route("/product")
def product():
    id = request.args.get("id")
    print("id", id)
    con = sqlite3.connect("Users.db")
    ad = con.execute(f"SELECT * FROM Ad JOIN Users ON Ad.username = Users.username WHERE ad_id = ?", (id,)).fetchone()
    print(ad)
    images = con.execute(f"SELECT image_path FROM post_images WHERE post_id = ?", (ad[9],)).fetchall()
    if current_user is not None and not ad[9] == current_user.username:
        con.execute("Update Ad SET views = IFNULL(views, 0) + 1 WHERE ad_id = ?", (id,))
        con.commit()
    images = [i[0] for i in images]
    con.close()
    return render_template("product.html",
                           title=ad[0],
                           price=ad[7],
                           domain=ad[1],
                           seller=ad[6],
                           seller_phone=ad[13],
                           state=ad[2],
                           author=ad[4],
                           ISBN=ad[5],
                           city=ad[3],
                           desc=ad[8],
                           images=images
                           )


@app.route("/category.html")
@app.route("/category", methods=["GET", "POST"])
def category():
    con = sqlite3.connect("Users.db")
    print("category")
    if request.method == "GET":
        if len(request.args) == 0:
            ads = con.execute("SELECT ad_id FROM Ad")
            ads = [utils.get_ad(ad[0]) for ad in ads]
            print(ads)

            con.close()
            return render_template("category.html", ads=ads)
        ads = utils.search(request.args.to_dict())
        print(ads)
        return render_template("category.html", ads=ads)

    if request.method == "POST":
        ads = utils.search(request.form.to_dict())
        print(ads)
        return render_template("category.html", ads=ads)


@app.route("/myads.html")
def myads():
    ads = sqlite3.connect("Users.db").execute("SELECT * FROM Ad WHERE username = ?", (current_user.username,))
    ads = [{"title": ad[0], "image": utils.get_images(ad[9])[0], "category": ad[1], 'views': ad[13], 'status': ad[11]}
           for ad in ads]
    return render_template("myads.html", my_ads=ads)


@app.route("/<resourcename>")
def get_resource(resourcename):
    print(resourcename)
    return render_template(resourcename)


if __name__ == '__main__':
    app.run(port=912)
