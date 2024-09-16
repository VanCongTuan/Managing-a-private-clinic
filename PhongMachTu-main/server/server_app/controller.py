from flask import render_template, url_for, redirect, request ,session, jsonify
from server_app import app, dao, login
from flask_login import login_user, logout_user, login_required, current_user
from server_app.models import Role ,NguoiDung
from datetime import datetime
import cloudinary
import cloudinary.uploader
from server_app import utils
import math


@app.route("/")
def home_page():
    return render_template("home_page.html")

@app.route("/blog")
def blog_me():
    return render_template("web/blog.html")

@app.route("/contactme")
def contact_me():
    return render_template("web/contact.html")

@app.route("/Derpartmentme")
def Derpartment_me():
    return render_template("web/Derpartment.html")

@app.route("/doctorme")
def doctor_me():
    return render_template("web/doctor.html")

@app.route("/serviceme")
def service_me():
    return render_template("web/service.html")

@app.route("/aboutme")
def aboutme_me():
    return render_template("web/aboutme.html")

























@app.route("/register", methods=['get', 'post'])
def user_register():
    err_msg = ""
    if request.method.__eq__('POST'):
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        try:
            if (password.strip().__eq__(confirm.strip())):
                dao.add_user(name=name, username=username, password=password)
                return redirect(url_for('user_login'))
            else:
                err_msg = 'Mật khẩu không khớp'
        except Exception as ex:
            err_msg = 'Hệ thống đang có lỗi' + str(ex)

    return render_template("register_page.html", err_msg=err_msg)


@app.route("/login", methods=['get', 'post'])
def user_login():
    err_msg = ''
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        userRole = request.form.get('userRole')

        user = dao.check_login(username=username, password=password, userRole=userRole)

        if user:
            login_user(user=user)  # current_user

            return redirect(url_for('home_page'))
        else:
            err_msg = 'Username hoặc password không chính xác'

    return render_template("login_page.html", err_msg=err_msg)


@app.route('/logout')
def user_signout():
    logout_user()
    return redirect(url_for('user_login'))


@login.user_loader
def user_load(user_id):
    return dao.get_user_by_id(user_id=user_id)


# @app.context_processor
# def common_response():
#     return dict(Role=Role)
@app.context_processor
def common_responses():
    return {
        'medicine_state': utils.counter_medicine(session.get('medicine')),
        'Role': Role
    }

@app.route("/patient_information")
def patient_information():
    return render_template("patient_infomation_page.html")


@app.route("/patient_information/<int:user_id>", methods=['get', 'post'])
def update_patient_infor(user_id):
    if request.method.__eq__('POST'):
        name = request.form.get('name')
        sex = request.form.get('sex')
        birth = request.form.get('birth')
        email = request.form.get('email')
        avatar = request.files.get('avatar')
        avatar_path = None
        if avatar:
            res = cloudinary.uploader.upload(avatar)
            avatar_path = res['secure_url']
        address = request.form.get('address')
        phone = request.form.get('phone')

        dao.update_patient(user_id=user_id, name=name, sex=sex, birth=birth, email=email, avatar=avatar_path,
                           address=address, phone=phone)
        return redirect(url_for('home_page'))


@app.route('/medical_register', methods=['get', 'post'])
def medical_register():
    if request.method.__eq__('POST'):
        phone = request.form.get('phone')
        date = request.form.get('date')
        time = request.form.get('time')

        date_time = datetime.strptime(f'{date} {time}', '%Y-%m-%d %H:%M')

        dao.register_medical(phone=phone, date_time=date_time)
        return redirect(url_for('home_page'))
    return render_template('medical_register_page.html')


@app.route("/medical_register/<int:user_id>", methods=['get', 'post'])
def patient_register_medical(user_id):
    if request.method.__eq__('POST'):
        date = request.form.get('date')
        time = request.form.get('time')

        date_time = datetime.strptime(f'{date} {time}', '%Y-%m-%d %H:%M')

        dao.register_medical(user_id=user_id, date_time=date_time)
        return redirect(url_for('home_page'))


@app.route("/medical_list")
def medical_list():
    return render_template('medical_examination_list_page.html')


@app.route("/medicine")
def medicine_list():
    kw = request.args.get("keywordthuoc")
    counter = utils.count_medicine()
    page = request.args.get("page", 1)
    thuocs = utils.load_medicine(kw=kw, page=int(page))
    return render_template('medicine.html',
                           thuocs=thuocs,
                           pages=math.ceil(counter / app.config['PAGE_SIZE']))


@app.route("/medicine-doctor")
def doctor_login():
    kw = request.args.get("keywordthuoc")
    counter = utils.count_medicine()
    page = request.args.get("page", 1)
    thuocs = utils.load_medicine(kw=kw, page=int(page))
    return render_template('login.html',
                           thuocs=thuocs,
                           pages=math.ceil(counter / app.config['PAGE_SIZE']))

@app.route('/login-admin',methods=['post', 'get'])
def login_admin():
    if request.method == 'POST':
        username = request.form.get('usernameAd')
        password = request.form.get('passwordAd')
        user = utils.check_login(username=username, password=password,role=Role.Admin)
        if user:
            login_user(user=user)
    return redirect('/admin')

@app.route('/prescription')
def prescription_medicine():
    return render_template("prescription.html",stats=utils.counter_medicine(session.get('medicine')))


# @app.context_processor
# def common_responses():
#     return {
#         'medicine_state': utils.counter_medicine(session.get('medicine'))
#     }


@app.route("/api/add-medicine",methods=['post'])
def add_to_medicine():
    data= request.get_json()
    id=str(data.get('id'))
    tenThuoc=data.get('tenThuoc')
    donGia=data.get('donGia')
    medicine =session.get('medicine')
    if not medicine:
        medicine={}

    if id in medicine:
        medicine[id]['quantity']= medicine[id]['quantity']+1
    else:
        medicine[id]={
             'id':id,
            'tenThuoc':tenThuoc,
            'donGia':donGia,
            'quantity': 1
        }
    session['medicine']= medicine

    return jsonify(utils.counter_medicine(medicine))



@app.route('/api/establishment',methods=['POST'])
@login_required
def pay():
    try:
        utils.add_receipt(session.get('medicine'))
        del session['medicine']
    except:
        return jsonify({'code':400})

    return jsonify({'code': 200})

if __name__ == '__main__':
    from server_app.admin import *
    app.run(debug=True)
