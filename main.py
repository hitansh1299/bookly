from flask import Flask, redirect, url_for, render_template, request

app = Flask(__name__, static_folder="static", static_url_path="", template_folder="templates")


@app.route('/index.html')
@app.route('/')
def home():
    return render_template("index.html")


@app.route('/category.html')
def category():
    return render_template('category.html')


@app.route('/404not.html')
def not_found():
    return render_template('404not.html')


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

@app.route('/search.html')
def search_page():
    return render_template("search.html")

if __name__ == '__main__':
    app.run()

