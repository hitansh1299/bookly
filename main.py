import datetime
import os
import utils
from flask import Flask, redirect, url_for, render_template, request
import sqlite3
from CustomErrors import UsernameError, PhoneError, AadharError
from User import User

app = Flask(__name__, static_folder="static", static_url_path="", template_folder="templates")
UPLOAD_FOLDER = 'static\\uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
current_user: User = None


@app.route('/index.html')
@app.route('/index',methods=["GET", "POST"])
def home():
    con = sqlite3.connect("Users.db")
    if request.method == "POST":
        return redirect(f'category?domain={request.form.get("domain")}&text={request.form.get("text")}')
    ads = con.execute("SELECT ad_id FROM Ad WHERE status = 'Active'").fetchall()[-6:]
    count = len(con.execute("SELECT * FROM Ad WHERE status = 'Active'").fetchall())
    ads = [utils.get_ad(ad[0]) for ad in ads]
    con.close()
    return render_template("index.html",
                           ads=ads,
                           username="Login / Register" if current_user is None else current_user.username,
                           profile_link="loginRegister.html" if current_user is None else "dashboard.html",
                           count=count
                           )


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
                         "Active",
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
            if len(form.get("phone")) != 10:
                raise PhoneError
            if len(form.get("aadhar").replace(" ","")) != 12:
                raise PhoneError
            con.execute(
                f'INSERT INTO Users VALUES(?,?,?,?,?,?,?)',[
                    form.get("username"),
                    form.get("password"),
                    form.get("email"),
                    form.get("phone"),
                    form.get("fname"),
                    form.get("lname"),
                    form.get("aadhar")
                ])
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
        except PhoneError as e:
            return render_template('loginRegister.html',
                                   phone_text=str(e),
                                   show_signup="show active",
                                   show_signin="")
        except AadharError as e:
            return render_template('loginRegister.html',
                                   aadhar_text=str(e),
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
    ads = con.execute("SELECT * FROM Ad WHERE status = 'Active' ORDER BY date DESC").fetchall()
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
                           seller_phone=ad[16],
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
            ads = con.execute("SELECT ad_id FROM Ad WHERE status = 'Active' ORDER BY date DESC")
            ads = [utils.get_ad(ad[0]) for ad in ads]
            print(ads)

            con.close()
            return render_template("category.html", ads=ads, query={})
        ads = utils.search(request.args.to_dict())
        print(ads)
        return render_template("category.html", ads=ads, query=request.args.to_dict())

    if request.method == "POST":
        ads = utils.search(request.form.to_dict())
        print(ads)
        return render_template("category.html", ads=ads, query=request.form.to_dict())


@app.route("/myads.html")
def myads():
    ads = sqlite3.connect("Users.db").execute("SELECT ad_id FROM Ad WHERE username = ?", (current_user.username,)).fetchall()
    ads = [utils.get_ad(ad[0]) for ad in ads]
    return render_template("myads.html", my_ads=ads)

@app.route("/delete/<ad_id>")
def delete(ad_id):
    ad = utils.get_ad(ad_id)
    if current_user.username == ad['username']:
        con = sqlite3.connect("Users.db")
        con.execute('DELETE FROM Ad WHERE ad_id = ?', [ad_id])
        con.execute('DELETE FROM post_images WHERE post_id = ?', [ad_id])
        con.commit()
    return redirect(url_for('myads'))


@app.route("/toggle_status/<ad_id>")
def toggle_status(ad_id):
    ad = utils.get_ad(ad_id)
    if current_user.username == ad['username']:
        con = sqlite3.connect("Users.db")
        current_status = con.execute("SELECT status FROM Ad WHERE ad_id = ?", [ad_id]).fetchone()[0]
        status = "Inactive" if current_status == "Active" else "Active"
        con.execute('UPDATE Ad SET status = ? WHERE ad_id = ?', [status, ad_id])
        con.commit()
    return redirect(url_for('myads'))


@app.route("/dashboard.html")
@app.route("/dashboard",methods=["GET", "POST"])
def dashboard():
    global current_user
    if request.method == "POST":
        con = sqlite3.connect("Users.db")
        con.execute('''UPDATE Users SET 
        first_name = ?,
        last_name = ?,
        email = ?,
        phone_no = ?,
        password = ?
        WHERE username = ?''',
                    [
                        request.form.get("fname"),
                        request.form.get("lname"),
                        request.form.get("email"),
                        request.form.get("phone"),
                        request.form.get("password"),
                        current_user.username
                    ])
        con.commit()
        current_user = User(current_user.username)
        return render_template("dashboard.html", user=current_user.get_as_dict())

    return render_template("dashboard.html",user=current_user.get_as_dict())


@app.route("/<resourcename>")
def get_resource(resourcename):
    print(resourcename)
    return render_template(resourcename)


if __name__ == '__main__':
    app.run(port=912)

