from flask import Flask, render_template

app = Flask(__name__)

@app.route("/login")
def login():
    return render_template("BsLam/login.html")

@app.route("/")
def index():
    return render_template("BsLam/index.html")

if __name__ == "__main__":
    app.run()