import random
import uuid

from flask import Flask, render_template, request, redirect, url_for, session

from Roles import *
from libs.DB import create_conn, get_table_columns
from settings import db_log, hospital_info

app = Flask(__name__)
adminRole = AdminRole(db_log['admin'])  # 创建管理员
unauthorizedRole = UnauthorizedRole(db_log['unauthorized'])  # 创建未授权用户
doctorRole = DoctorRole(db_log['doctor'])  # 创建医生
patientRole = PatientRole(db_log['patient'])  # 创建患者
nurseRole = NurseRole(db_log['nurse'])  # 创建护士
drugadminRole = DrugadminRole(db_log['drugadmin'])  # 创建药房管理员
supplierRole = SupplierRole(db_log['supplier'])  # 创建供应商


# 路由：医院主页
@app.route('/')
def home():
    return render_template('home.html', hospital_info=hospital_info)


# 路由：查询医院基本信息
@app.route('/hospital_info', methods=['GET', 'POST'])
def hospital_info_page():
    if request.method == 'POST':
        # 获取前端传递的参数
        search_term = request.form['search_term']
        # 使用参数进行查询
        data = eval(unauthorizedRole.query_hospital(search_term))
        # 渲染HTML页面，将查询结果传递给页面
        return render_template('hospital_info.html', data=data, search_term=search_term)
    return render_template('hospital_info.html', data=None, search_term=None, columns=None)


# 路由：查询科室基本信息
@app.route('/department_info', methods=['GET', 'POST'])
def department_info_page():
    if request.method == 'POST':
        # 获取前端传递的参数
        search_term = request.form['search_term']
        # 使用参数进行查询
        data = eval(unauthorizedRole.query_department(search_term))
        # 渲染HTML页面，将查询结果传递给页面
        return render_template('department_info.html', data=data, search_term=search_term)
    return render_template('department_info.html', data=None, search_term=None, columns=None)


# 路由：查询医生基本信息
@app.route('/doctor_info', methods=['GET', 'POST'])
def doctor_info_page():
    if request.method == 'POST':
        # 获取前端传递的参数
        search_term = request.form['search_term']
        # 使用参数进行查询
        data = eval(unauthorizedRole.query_doctor(search_term))
        # 渲染HTML页面，将查询结果传递给页面
        return render_template('doctor_info.html', data=data, search_term=search_term)
    return render_template('doctor_info.html', data=None, search_term=None, columns=None)


# 路由：查询医生排班日程
@app.route('/schedule_info', methods=['GET', 'POST'])
def schedule_info_page():
    if request.method == 'POST':
        # 获取前端传递的参数
        search_term = request.form['search_term']
        # 使用参数进行查询
        data = eval(unauthorizedRole.query_schedule(search_term))
        # 渲染HTML页面，将查询结果传递给页面
        return render_template('schedule_info.html', data=data, search_term=search_term)
    return render_template('schedule_info.html', data=None, search_term=None, columns=None)


# 路由：登录页面
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # 获取前端传递的参数
        username = request.form['job_number']
        password = request.form['password']
        # 查询数据库数据
        user, id, role = adminRole.login(username, password)
        if user is not False and id is not False and role is not False:
            # 如果验证通过，将用户信息存储在session中
            session['user_info'] = user
            session[f'{role}_id'] = id
            # 根据用户角色跳转到对应的页面
            return redirect(url_for(f'{role}_dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials. Please try again.')
    return render_template('login.html', error='')


# 路由：医生仪表盘
@app.route('/doctor_dashboard')
def doctor_dashboard():
    user_info = session.get('user_info')
    if user_info and user_info[0] == '1':
        conn = create_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM doctor WHERE job_number = {} ".format(user_info))
        doctor_info = cursor.fetchone()
        doctor_columns = [column[0] for column in cursor.description]
        conn.close()
        return render_template('doctor/dashboard.html', user_info=user_info, doctor_info=doctor_info,
                               doctor_columns=doctor_columns)
    else:
        return redirect(url_for('login'))


# 新增路由：医生个人信息编辑
@app.route('/doctor_profile', methods=['GET', 'POST'])
def edit_doctor_profile():
    user_info = session.get('user_info')
    doctor_id = session.get('doctor_id')
    if user_info and user_info[0] == '1':
        if request.method == 'POST':
            new_passwd = request.form.get('passwd')
            new_introduction = request.form.get('introduction')
            new_photo = request.files['file']
            new_photo.filename = uuid.uuid4().hex + '.' + new_photo.filename.split('.')[-1]
            doctorRole.update_information(new_passwd, new_introduction, new_photo, doctor_id)
            return redirect(url_for('login'))
        else:
            return render_template('doctor/profile.html', id=doctor_id)
    else:
        return redirect(url_for('login'))


# 路由：医生排班日程页面
@app.route('/doctor_schedule')
def doctor_schedule():
    user_info = session.get('user_info')
    doctor_id = session.get('doctor_id')
    if user_info:
        conn = create_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM schedule WHERE doctor_id = {}'.format(doctor_id))
        doctor_schedule = cursor.fetchall()
        columns = get_table_columns('schedule')
        conn.close()
        return render_template('doctor/schedule.html', columns=columns, doctor_schedule=doctor_schedule,
                               doctor_id=doctor_id)
    else:
        return redirect(url_for('login'))


# 路由：医生确认排班
@app.route('/confirm_schedule', methods=['GET', 'POST'])
def confirm_schedule():
    user_info = session.get('user_info')
    doctor_id = session.get('doctor_id')
    if user_info:
        if request.method == 'POST':
            schedule_id = request.form.get('schedule_id')
            new_status = request.form.get('new_status')
            conn = create_conn()
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE schedule SET state = {} WHERE doctor_id={} and schedule_id={}'.format(new_status, doctor_id,
                                                                                              schedule_id))
            conn.commit()
            conn.close()
        # 查询未确认的排班日程
        conn = create_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM schedule WHERE state = 0 and doctor_id={}'.format(doctor_id))
        schedule = cursor.fetchall()
        columns = get_table_columns('schedule')
        conn.close()

        return render_template('doctor/confirm_schedule.html', user_info=user_info, schedule=schedule, columns=columns)
    else:
        return redirect(url_for('login'))


@app.route('/doctor_diagnosis')
def doctor_diagnosis():
    user_info = session.get('user_info')
    doctor_id = session.get('doctor_id')
    if user_info:
        # 在实际应用中，使用数据库连接执行查询
        # 这里假设有一个名为 'doctor_schedule' 的表存储医生排班信息
        conn = create_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM diagnosis WHERE doctor_id = {} and state=1'.format(doctor_id))
        doctor_diagnosis = cursor.fetchall()
        columns = get_table_columns('diagnosis')
        conn.close()

        return render_template('doctor/diagnosis.html', columns=columns, doctor_diagnosis=doctor_diagnosis,
                               doctor_id=doctor_id)
    else:
        return redirect(url_for('login'))


# 开处方
@app.route('/prescriptions', methods=['GET', 'POST'])
def prescriptions():
    user_info = session.get('user_info')
    doctor_id = session.get('doctor_id')
    if user_info:
        if request.method == 'POST':
            # 处理处方开具表单提交
            patient_id = request.form.get('patient_id')
            content = request.form.get('content')
            notes = request.form.get('notes')
            flag = doctorRole.insert_prescription(doctor_id, patient_id, content, notes)
            return render_template('doctor/prescriptions.html', user_info=user_info, success=flag)
        else:
            return render_template('doctor/prescriptions.html', user_info=user_info, error='')
    else:
        return redirect(url_for('login'))


@app.route('/patient_dashboard')
def patient_dashboard():
    user_info = session.get('user_info')
    patient_id = session.get('patient_id')
    if user_info:
        conn = create_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patient WHERE patient_id = {} ".format(patient_id))
        patient_info = cursor.fetchone()
        patient_columns = [column[0] for column in cursor.description]
        conn.close()
        return render_template('patient/patient_dashboard.html', user_info=user_info, patient_info=patient_info,
                               patient_columns=patient_columns)
    else:
        return redirect(url_for('login'))


# 路由：患者个人信息编辑
@app.route('/patient_profile', methods=['GET', 'POST'])
def edit_patient_profile():
    user_info = session.get('user_info')
    patient_id = session.get('patient_id')
    if user_info:
        if request.method == 'POST':
            new_passwd = request.form.get('passwd')
            new_phone = request.form.get('new_phone')
            new_past = request.form.get('new_past')
            new_allergy = request.form.get('new_allergy')
            new_marry = request.form.get('new_marry')
            new_address = request.form.get('new_address')
            new_photo = request.files['file']
            new_photo.filename = uuid.uuid4().hex + '.' + new_photo.filename.split('.')[-1]
            patientRole.update_information(new_passwd, new_phone, new_past, new_allergy, new_marry, new_address,
                                           new_photo, patient_id)
            return redirect(url_for('login'))
        else:
            return render_template('patient/patient_profile.html', patient_id=patient_id)
    return redirect(url_for('login'))


@app.route('/patient_diagnosis')
def patient_diagnosis():
    user_info = session.get('user_info')
    patient_id = session.get('patient_id')
    if user_info:
        conn = create_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM diagnosis WHERE patient_id = {}'.format(patient_id))
        patient_diagnosis = cursor.fetchall()
        columns = get_table_columns('diagnosis')
        conn.close()
        return render_template('patient/patient_diagnosis.html', columns=columns, patient_diagnosis=patient_diagnosis,
                               patient_id=patient_id)
    else:
        return redirect(url_for('login'))


@app.route('/patient_case')
def patient_case():
    user_info = session.get('user_info')
    patient_id = session.get('patient_id')
    if user_info:
        conn = create_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM case WHERE patient_id = {}'.format(patient_id))
        patient_case = cursor.fetchall()
        columns = get_table_columns('case')
        conn.close()

        return render_template('patient/patient_case.html', columns=columns, patient_case=patient_case,
                               patient_id=patient_id)
    else:
        return redirect(url_for('login'))


# 患者查看处方
@app.route('/patient_prescription')
def patient_prescription():
    user_info = session.get('user_info')
    patient_id = session.get('patient_id')
    if user_info:
        prescription = patientRole.query_prescription(patient_id)
        return render_template('patient/patient_prescription.html', prescription=prescription)
    else:
        return redirect(url_for('login'))


@app.route('/nurse_dashboard')
def nurse_dashboard():
    user_info = session.get('user_info')
    nurse_id = session.get('nurse_id')
    if user_info:
        data = eval(nurseRole.query_information(user_info))
        return render_template('nurse/nurse_dashboard.html', nurse_id=nurse_id, data=data)
    else:
        return redirect(url_for('login'))


@app.route('/nurse_profile', methods=['GET', 'POST'])
def edit_nurse_profile():
    user_info = session.get('user_info')
    nurse_id = session.get('nurse_id')
    if user_info:
        if request.method == 'POST':
            new_passwd = request.form.get('new_passwd')
            new_phone = request.form.get('new_phone')
            new_photo = request.files['file']
            new_photo.filename = uuid.uuid4().hex + '.' + new_photo.filename.split('.')[-1]
            nurseRole.update_information(nurse_id, new_passwd, new_phone, new_photo)
            return redirect(url_for('login'))
        else:
            return render_template('nurse/nurse_profile.html', nurse_id=nurse_id)
    else:
        return redirect(url_for('login'))


@app.route('/handle_prescription', methods=['GET', 'POST'])
def handle_prescription():
    user_info = session.get('user_info')
    nurse_id = session.get('nurse_id')
    if user_info:
        if request.method == 'POST':
            prescription_id = request.form.get('prescription_id')
            flag = nurseRole.handle_prescription(prescription_id, nurse_id)
            return render_template('nurse/handle_prescription.html', nurse_id=nurse_id, success=flag)
        else:
            return render_template('nurse/handle_prescription.html', nurse_id=nurse_id, error='')
    else:
        return redirect(url_for('login'))


@app.route('/drugadmin_dashboard')
def drugadmin_dashboard():
    user_info = session.get('user_info')
    drugadmin_id = session.get('drugadmin_id')
    if user_info:
        data = eval(drugadminRole.query_information(drugadmin_id))
        return render_template('drugadmin/drugadmin_dashboard.html', drugadmin_id=drugadmin_id, data=data)
    else:
        return redirect(url_for('login'))


@app.route('/drugadmin_profile', methods=['GET', 'POST'])
def edit_drugadmin_profile():
    user_info = session.get('user_info')
    drugadmin_id = session.get('drugadmin_id')
    if user_info:
        if request.method == 'POST':
            new_phone = request.form.get('new_phone')
            new_photo = request.files['file']
            new_photo.filename = uuid.uuid4().hex + '.' + new_photo.filename.split('.')[-1]
            drugadminRole.update_information(new_phone, new_photo, drugadmin_id)
            return redirect(url_for('login'))
        else:
            return render_template('drugadmin/drugadmin_profile.html', drugadmin_id=drugadmin_id)
    else:
        return redirect(url_for('login'))


@app.route('/insert_drugin', methods=['GET', 'POST'])
def insert_drugin():
    user_info = session.get('user_info')
    drugadmin_id = session.get('drugadmin_id')
    if user_info:
        if request.method == 'POST':
            drug_name = request.form.get('drug_name')
            in_number = request.form.get('in_number')
            batch = request.form.get('batch')
            supplier_id = request.form.get('supplier_id')
            notes = request.form.get('notes')
            instruction = request.form.get('instruction')
            n = request.form.get('n')
            drugadminRole.insert_drugin(in_number, drug_name, batch, n, notes, instruction, supplier_id, drugadmin_id)
        return render_template('drugadmin/insert_drugin.html', user_info=user_info)
    else:
        return redirect(url_for('login'))


@app.route('/supplier_dashboard')
def supplier_dashboard():
    user_info = session.get('user_info')
    supplier_id = session.get('supplier_id')
    if user_info:
        data = eval(supplierRole.query_information(supplier_id))
        return render_template('supplier/supplier_dashboard.html', supplier_id=supplier_id, data=data)
    else:
        return redirect(url_for('login'))


@app.route('/supplier_profile', methods=['GET', 'POST'])
def edit_supplier_profile():
    user_info = session.get('user_info')
    supplier_id = session.get('supplier_id')
    if user_info:
        if request.method == 'POST':
            new_passwd = request.form.get('new_passwd')
            new_person = request.form.get('new_person')
            new_phone_number = request.form.get('new_phone_number')
            new_address = request.form.get('new_address')
            supplierRole.update_information(new_passwd, new_person, new_phone_number, new_address, supplier_id)
            return redirect(url_for('login'))
        else:
            return render_template('supplier/supplier_profile.html', supplier_id=supplier_id)
    else:
        return redirect(url_for('login'))


@app.route('/query_drug_supplied')
def query_drug_supplied():
    user_info = session.get('user_info')
    supplier_id = session.get('supplier_id')
    if user_info:
        data = eval(supplierRole.query_supply_drug(supplier_id))
        return render_template('supplier/query_drug_supplied.html', supplier_id=supplier_id, data=data)
    else:
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.secret_key = 'your_secret_key'
    app.run(debug=True)
