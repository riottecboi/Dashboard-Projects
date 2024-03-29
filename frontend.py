from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from flask import Flask, render_template, request,  redirect, url_for,  session
from flask_wtf.csrf import CSRFProtect, CSRFError
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from flask_env import MetaFlaskEnv
from datamodel import User, Customer, Record, Base
from datetime import timedelta
import json
from datetime import datetime
import pytz
import string
import random


class Configuration(metaclass=MetaFlaskEnv):
    SECRET_KEY = "xxxx"
    WTF_CSRF_SECRET_KEY = "xxxx"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'xxxxx'
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
engine = create_engine(mysql_string, pool_pre_ping=True, echo=False, encoding='utf-8',
                       pool_size=app.config['POOL_SIZE'], pool_recycle=app.config['POOL_RECYCLE'])
sessionFactory = sessionmaker(bind=engine)
Base.metadata.create_all(engine)


csrf = CSRFProtect(app)
login = LoginManager(app)

def add_customer(cus_json):
    records = []
    session = sessionFactory()
    first_check = session.query(Customer.id).filter_by(phone=cus_json['phone']).first()
    if first_check is not None:
        check = session.query(Customer.id).filter_by(dob=cus_json['dob']).first()
        if check is None:
            customer = Customer(name=cus_json['name'].lower(), dob=cus_json['dob'], phone=cus_json['phone'],
                                timereported=datetime.now(pytz.timezone('Asia/Bangkok')), status=cus_json['status'])
            session.add(customer)
            session.commit()
            cus_id = session.query(Customer.id).filter_by(name=cus_json['name']).filter_by(phone=cus_json['phone']).first()
            record = Record(customerid=cus_id[0], jsondata=json.dumps([cus_json]))
            session.add(record)
            session.commit()
        else:
            datas = session.query(Record).filter_by(customerid=check[0]).first()
            for data in json.loads(datas.jsondata):
                records.append(data)
            records.insert(0, cus_json)
            datas.jsondata = json.dumps(records)
            session.commit()
    else:
        customer = Customer(name=cus_json['name'].lower(), dob=cus_json['dob'], phone=cus_json['phone'],
                            timereported=datetime.now(pytz.timezone('Asia/Bangkok')), status=cus_json['status'])
        session.add(customer)
        session.commit()
        cus_id = session.query(Customer.id).filter_by(name=cus_json['name']).filter_by(phone=cus_json['phone']).first()
        record = Record(customerid=cus_id[0], jsondata=json.dumps([cus_json]))
        session.add(record)
        session.commit()

    session.close()

def update_customer(id, cus_json):
    records = []
    session = sessionFactory()
    check = session.query(Customer).filter_by(id=id).first()
    if check is None:
        customer = Customer(name=cus_json['name'].lower(), dob=cus_json['dob'], phone=cus_json['phone'],
                            timereported=datetime.now(pytz.timezone('Asia/Bangkok')), status=cus_json['status'])
        session.add(customer)
        session.commit()
        cus_id = session.query(Customer.id).filter_by(name=cus_json['name']).filter_by(phone=cus_json['phone']).first()
        record = Record(customerid=cus_id[0], jsondata=json.dumps([cus_json]))
        session.add(record)
        session.commit()
    else:
        check.name = cus_json['name'].lower()
        check.dob = cus_json['dob']
        check.phone = cus_json['phone']
        check.status = cus_json['status']
        check.timereported = datetime.now(pytz.timezone('Asia/Bangkok'))
        session.commit()
        datas = session.query(Record).filter_by(customerid=id).first()
        histories = json.loads(datas.jsondata)
        histories.pop(0)
        for data in histories:
            records.append(data)
        records.insert(0, cus_json)
        datas.jsondata = json.dumps(records)
        session.commit()
    session.close()

def get_customers(number=None):
    customners = []
    session = sessionFactory()
    if number is None:
        datas = session.query(Customer).order_by(desc(Customer.timereported)).limit(50).all()
    else:
        datas = session.query(Customer).order_by(desc(Customer.timereported)).limit(int(number)).all()
    if len(datas) != 0:
        for data in datas:
            time = data.timereported.strftime("%d-%m-%Y %H:%M:%S")
            customners.append({'id': data.id, 'timereported': time, 'name': data.name, 'dob':data.dob,
                               'phone': data.phone, 'status': data.status, 'is_display': data.is_display})
    session.close()
    return customners

def get_search_customers(phone=None, name=None):
    customers = []
    session = sessionFactory()
    if name is not None:
        datas = session.query(Customer).filter(Customer.name.like("%{}%".format(name))).all()
        if len(datas) != 0:
            for data in datas:
                time = data.timereported.strftime("%d-%m-%Y %H:%M:%S")
                customers.append({'id': data.id, 'timereported': time, 'name': data.name, 'dob': data.dob,
                                   'phone': data.phone, 'status': data.status, 'is_display': data.is_display})
    else:
        data = session.query(Customer).filter_by(phone=phone).first()
        if data is not None:
            time = data.timereported.strftime("%d-%m-%Y %H:%M:%S")
            customers.append({'id': data.id, 'timereported': time, 'name': data.name, 'dob': data.dob,
                          'phone': data.phone, 'status': data.status, 'is_display': data.is_display})
    session.close()
    return customers

def get_customer_histories(id):
    histories = []
    session = sessionFactory()
    datas = session.query(Record).filter_by(customerid=id).first()
    for data in json.loads(datas.jsondata):
        histories.append(data)
    session.close()
    return histories

def update_status(id, status):
    session = sessionFactory()
    customer = session.query(Customer).filter_by(id=id).first()
    customer.status = status
    session.commit()
    session.close()

def hide_record(id):
    session = sessionFactory()
    customer = session.query(Customer).filter_by(id=id).first()
    customer.is_display = 0
    session.commit()
    session.close()

@login.user_loader
def user_loader(username):
    session = sessionFactory()
    user = session.query(User).filter_by(username=username).first()
    session.close()
    return user

@login.unauthorized_handler
def unauthorized():
    return render_template('error.html',  message="Bạn cần đăng nhập để tiếp tục", redirect='/login')

@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return render_template('error.html',  message="Hết phiên đăng nhập: {}".format(e.description), redirect='/login')

@app.route('/')
def init():
    return redirect(url_for('login'))


@app.route('/menu', methods=['GET', 'POST'])
@login_required
def menu():
    customers = []
    bill = []
    if ss.get('if_logged') == True:
        if request.method == 'POST':
            try:
                drug_name = request.form.getlist('drug_name')
                day_per_times = request.form.getlist('day_per_times')
                quantity_per_times = request.form.getlist('quantity_per_times')
                method = request.form.getlist('method')
                eyes = request.form.getlist('eyes')
                use_when = request.form.getlist('use_when')
                quantity = request.form.getlist('quantity')
                unit = request.form.getlist('unit')
                for a, b, c, d, e, f, g, h in zip(drug_name, day_per_times, quantity_per_times, method, eyes, use_when, quantity, unit):
                    bill.append({
                        "drug_name" : a,
                        "day_per_times" : b,
                        "quantity_per_times" : c,
                        "method" : d,
                        "eyes" : e,
                        "use_when" : f,
                        "quantity" : g,
                        "unit" : h
                    })
                jsondata ={
                    "id": ''.join(random.choices(string.ascii_uppercase + string.digits, k=4)),
                    "history": datetime.now(pytz.timezone('Asia/Bangkok')).strftime('%d-%m-%Y %H:%M:%S'),
                    "status": request.form.get('status'),
                    "name": request.form.get('fullname'),
                    "dob": request.form.get('dob'),
                    "phone": request.form.get('phone'),
                    "rev": request.form.get('rev'),
                    "lev": request.form.get('lev'),
                    "distance": request.form.get('distance'),
                    "frev": request.form.get('frev'),
                    "flev": request.form.get('flev'),
                    "frevo": request.form.get('frevo'),
                    "flevo": request.form.get('flevo'),
                    "crevo": request.form.get('crevo'),
                    "clevo": request.form.get('clevo'),
                    "pd": request.form.get('pd'),
                    "dre": request.form.get('dre'),
                    "dle": request.form.get('dle'),
                    "bill": bill,
                    "lens": request.form.get('lens'),
                    "note": request.form.get('note')
                }
                add_customer(jsondata)
                customers_raw = get_customers()
                for data in customers_raw:
                    if len(customers) == 10:
                        break
                    else:
                        if data['is_display'] == 1:
                            history = get_customer_histories(data['id'])
                            data['history'] = history
                            customers.append(data)
                        else:
                            continue
                return render_template('error.html', message='Thêm thông tin thành công', redirect='/menu')
            except Exception as e:
                return render_template('error.html', message='Lỗi xảy ra: {}'.format(str(e)), redirect='/menu')
        customers_raw = get_customers()
        for data in customers_raw:
            if len(customers) == 10:
                break
            else:
                if data['is_display'] == 1:
                    history = get_customer_histories(data['id'])
                    data['history'] = history
                    customers.append(data)
                else:
                    continue
        return render_template('index.html', customers=customers, user=current_user.username)
    else:
        return render_template('error.html',  message='Đăng nhập thất bại', redirect='/login')

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
        return render_template('error.html', message='Đăng nhập thất bại', redirect='/login')
    elif ss.get('if_logged') == True:
        return redirect(url_for('menu'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    logout_user()
    return render_template('error.html', message='Đăng xuất', redirect='/login')

@app.route('/status', methods=["POST"])
@login_required
def status():
    id = request.form.get('id')
    check = request.form.get('update')
    if check == 'Hoàn thành':
        status = 'Đang tiến hành'
    else:
        status = 'Hoàn thành'
    try:
        update_status(id,status)
    except Exception as e:
        return render_template('error.html', message='Lỗi xảy ra: {}'.format(str(e)), redirect='/menu')
    return redirect(url_for('menu'))

@app.route('/history/<id>', methods=["GET"])
@login_required
def history(id):
    history = []
    try:
        check = get_customer_histories(id)
        if len(check) != 0:
            name = ''
            for n in check:
                name = n['name']
            history.extend(check)
            return render_template('details.html', history=history, name=name)
        else:
            return render_template('error.html', message='Không tìm thấy lịch sử', redirect='/menu')
    except Exception as e:
        return render_template('error.html', message='Lỗi xảy ra: {}'.format(str(e)), redirect='/menu')

@app.route('/edit', methods=['POST'])
@login_required
def edit():
    bill = []
    try:
        id = request.form.get('edit_id')
        if id is None:
            return render_template('error.html', message='Không tìm thấy dữ liêu khách hàng', redirect='/menu')
        drug_name = request.form.getlist('editdrug_name')
        day_per_times = request.form.getlist('editday_per_times')
        quantity_per_times = request.form.getlist('editquantity_per_times')
        method = request.form.getlist('editmethod')
        eyes = request.form.getlist('editeyes')
        use_when = request.form.getlist('edituse_when')
        quantity = request.form.getlist('editquantity')
        unit = request.form.getlist('editunit')

        for a, b, c, d, e, f, g, h in zip(drug_name, day_per_times, quantity_per_times, method, eyes, use_when,
                                          quantity, unit):
            bill.append({
                "drug_name": a,
                "day_per_times": b,
                "quantity_per_times": c,
                "method": d,
                "eyes": e,
                "use_when": f,
                "quantity": g,
                "unit": h
            })
        jsondata = {
            "id": ''.join(random.choices(string.ascii_uppercase + string.digits, k=4)),
            "history": datetime.now(pytz.timezone('Asia/Bangkok')).strftime('%d-%m-%Y %H:%M:%S'),
            "status": request.form.get('editstatus'),
            "name": request.form.get('editfullname'),
            "dob": request.form.get('editdob'),
            "phone": request.form.get('editphone'),
            "rev": request.form.get('editrev'),
            "lev": request.form.get('editlev'),
            "distance": request.form.get('editdistance'),
            "frev": request.form.get('editfrev'),
            "flev": request.form.get('editflev'),
            "frevo": request.form.get('editfrevo'),
            "flevo": request.form.get('editflevo'),
            "crevo": request.form.get('editcrevo'),
            "clevo": request.form.get('editclevo'),
            "pd": request.form.get('editpd'),
            "dre": request.form.get('editdre'),
            "dle": request.form.get('editdle'),
            "bill": bill,
            "lens": request.form.get('editlens'),
            "note": request.form.get('editnote')

        }
        update_customer(id, jsondata)
        return render_template('error.html', message='Thay đổi thành công', redirect='/menu')
    except Exception as e:
        return render_template('error.html', message='Lỗi xảy ra: {}'.format(str(e)), redirect='/menu')

@app.route('/hide', methods=["POST"])
@login_required
def hide():
    id = request.form.get('hideid')
    try:
        hide_record(id)
    except Exception as e:
        return render_template('error.html', message='Lỗi xảy ra: {}'.format(str(e)), redirect='/menu')
    return redirect(url_for('menu'))

@app.route('/search', methods=['POST'])
@login_required
def search():
    search_for = request.form.get('search')
    return render_template('error.html', message='Tìm kiếm thông tin', redirect="/result?search=" + search_for)

@app.route('/result', methods=['GET'])
@login_required
def result():
    customers=[]
    check = request.args.get('search')
    if check.isnumeric() is True:
        customer_raw = get_search_customers(phone=int(check))
    else:
        customer_raw = get_search_customers(name=check)
    if len(customer_raw) != 0:
        for data in customer_raw:
            history = get_customer_histories(data['id'])
            data['history'] = history
            customers.append(data)
        return render_template('search.html', customers=customers, user=current_user.username, term=check)
    else:
        return render_template('error.html', message='Không tìm thấy kết quả', redirect='/menu')

@app.route('/filter', methods=['POST'])
@login_required
def filter():
    number = request.form.get('filter')
    return render_template('error.html', message='Đang lấy thông tin', redirect="/list?number=" + number)

@app.route('/list', methods=['GET'])
@login_required
def list():
    customers = []
    try:
        number_raw = request.args.get('number')
        if number_raw is None:
            number = 50
        else:
            number=number_raw
        customer_raw = get_customers(number=number)
        if len(customer_raw) !=0:
            for data in customer_raw:
                history = get_customer_histories(data['id'])
                data['history'] = history
                customers.append(data)
            return render_template('list.html', customers=customers, user=current_user.username, number=number)
        else:
            return render_template('error.html', message='Không có dữ liệu', redirect='/menu')
    except Exception as e:
        return render_template('error.html', message='Có lỗi xảy ra: {}'.format(str(e)), redirect='/menu')

if __name__ == '__main__':
    app.run()