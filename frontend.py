from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask import Flask, render_template, request, make_response, redirect, url_for, Response, stream_with_context, session
from flask_wtf.csrf import CSRFProtect, CSRFError
from flask_login import LoginManager, login_user, login_required, current_user
from flask_env import MetaFlaskEnv
from datamodel import User, Customer, Base
from datetime import timedelta


class Configuration(metaclass=MetaFlaskEnv):
    SECRET_KEY = "supersecretkey"
    WTF_CSRF_SECRET_KEY = "supersecretkey"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://localhost:3306/test?user=test&password=test'
    POOL_SIZE = 20
    POOL_RECYCLE = 60

ss = session
app = Flask(__name__)
try:
    app.config.from_pyfile('settings.cfg')
except FileNotFoundError:
    app.config.from_object(Configuration)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
app.config['SESSION_COOKIE_SECURE']=True
mysql_string = app.config['SQLALCHEMY_DATABASE_URI']
engine = create_engine(mysql_string, pool_pre_ping=True, echo=False,
                       pool_size=app.config['POOL_SIZE'], pool_recycle=app.config['POOL_RECYCLE'])
sessionFactory = sessionmaker(bind=engine)
Base.metadata.create_all(engine)


csrf = CSRFProtect(app)
login = LoginManager(app)


@login.user_loader
def user_loader(username):
    session = sessionFactory()
    user = session.query(User).filter_by(username=username).first()
    session.close()
    return user

@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return render_template('error.html',  message="Session expired: {}".format(e.description), redirect='/login')

@app.route('/')
def init():
    return redirect(url_for('login'))


@app.route('/menu', methods=['GET', 'POST'])
def menu():
    if ss.get('if_logged') == True:
        return render_template('index.html')
    else:
        return render_template('error.html',  message='Session expired', redirect='/login')

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        ss.permanent = True
        session = sessionFactory()
        username = request.form.get('username')
        password = request.form.get('password')
        user = session.query(User).filter_by(username=username).first()
        if user:
            if user.check_password(password):
                user.set_authenticated(session, True)
                login_user(user)
                session.close()
                ss["if_logged"] = True
                return redirect(url_for('menu'))
        session.close()
        return render_template('error.html', message='Authentication error', redirect='/login')
    elif ss.get('if_logged') == True:
        return redirect(url_for('menu'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return render_template('error.html', message='Session Expired', redirect='/login')
