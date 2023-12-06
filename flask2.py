from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, session
import psycopg2
import json
import base64
import time
from role_class import *

app = Flask(__name__)
db_manager = DatabaseManager(db_log['UnauthorizedRole'])  # 未授权用户登录
UnloginRole = UnauthorizedRole(db_manager, 'UnauthorizedRole')  # 创建未授权用户


def create_conn():
    database = 'HIS'  # 选择数据库名称
    user = 'test'
    password = 'testGauss.'
    host = '121.36.55.115'  # 数据库ip
    port = '5432'
    conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)  # 连接数据库
    return conn


def get_table_columns(table):
    conn = create_conn()
    cursor = conn.cursor()
    cursor.execute(f'SELECT * FROM %s LIMIT 1' % (table))
    columns = [column[0] for column in cursor.description]
    conn.close()
    return columns


# 模拟医院基本信息数据
hospital_info = {
    'name': 'Example Hospital',
    'address': '123 Main St',
    'phone': '555-1234',
}

# 模拟用户角色信息
user_roles = {
    'doctor': {
        'name': 'Dr. John Doe',
        'role': 'doctor',
    },
    'nurse': {
        'name': 'Nurse Jane Smith',
        'role': 'nurse',
    }
}


# 路由：总体页面
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
        data = eval(UnloginRole.query_hospital(search_term))
        columns = get_table_columns('hospital')
        # 渲染HTML页面，将查询结果传递给页面
        return render_template('hospital_info.html', data=data, search_term=search_term)

    columns = get_table_columns('hospital')
    return render_template('hospital_info.html', data=None, search_term=None)


# 路由：医生信息页面
@app.route('/doctor_info', methods=['GET', 'POST'])
def doctor_info_page():
    if request.method == 'POST':
        # 获取前端传递的参数
        search_term = request.form['search_term']
        data = eval(UnloginRole.query_doctor(search_term))
        columns = get_table_columns('doctor')
        # 渲染HTML页面，将查询结果传递给页面
        return render_template('doctor_info.html', data=data, search_term=search_term, columns=columns)
    columns = get_table_columns('doctor')
    return render_template('doctor_info.html', data=None, search_term=None, columns=columns)


@app.route('/department_info', methods=['GET', 'POST'])
def department_info_page():
    if request.method == 'POST':
        # 获取前端传递的参数
        search_term = request.form['search_term']
        data = eval(UnloginRole.query_department(search_term))
        columns = get_table_columns('department')
        # 渲染HTML页面，将查询结果传递给页面
        return render_template('department_info.html', data=data, search_term=search_term, columns=columns)

    columns = get_table_columns('department')
    return render_template('department_info.html', data=None, search_term=None, columns=columns)


@app.route('/schedule_info', methods=['GET', 'POST'])
def schedule_info_page():
    if request.method == 'POST':
        # 获取前端传递的参数
        search_term = request.form['search_term']
        data = eval(UnloginRole.query_schedule(search_term))

        columns = get_table_columns('schedule')
        # 渲染HTML页面，将查询结果传递给页面
        return render_template('schedule_info.html', data=data, search_term=search_term, columns=columns)

    columns = get_table_columns('schedule')
    return render_template('schedule_info.html', data=None, search_term=None, columns=columns)

@app.route('/supplier_info', methods=['GET', 'POST'])
def supplier_info_page():
    if request.method == 'POST':
        # 获取前端传递的参数
        search_term = request.form['search_term']
        data = eval(UnloginRole.query_supplier(search_term))

        columns = get_table_columns('supplier')
        # 渲染HTML页面，将查询结果传递给页面
        return render_template('supplier_info.html', data=data, search_term=search_term, columns=columns)

# 路由：登录页面
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        # 获取前端传递的参数
        job_number = request.form['job_number']
        password = request.form['password']

        # 查询数据库数据
        conn = create_conn()
        cursor = conn.cursor()
        # 使用参数进行查询
        cursor.execute(
            "SELECT doctor_id,job_number,password FROM doctor where job_number= {} union select nurse_id,job_number,password from nurse WHERE job_number= {} union select patient_id,phone,password from patient WHERE phone={}".format(
                job_number, job_number, job_number))

        users = cursor.fetchall()
        # 验证用户名和密码
        id = users[0][0]
        user = users[0][1]
        passwd = users[0][2]
        conn.close()

        if user and passwd == password and user[0] == '1' and len(user) == 10:
            # 如果验证通过，将用户信息存储在session中
            session['user_info'] = user
            session['doctor_id'] = id
            return redirect(url_for('doctor_dashboard'))
        elif user and passwd == password and user[0] == '2' and len(user) == 10:
            session['user_info'] = user
            session['nurse_id'] = id
            return redirect(url_for('nurse_dashboard'))
        elif user and passwd == password and len(user) == 11:
            session['user_info'] = user
            return redirect(url_for('patient_dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials. Please try again.')

    return render_template('login.html', error=None)


@app.route('/patient_dashboard')
def patient_dashboard():
    user_info = session.get('user_info')
    if user_info:
        # 在实际应用中，使用数据库连接执行查询
        # 这里假设有一个名为 'doctors' 的表存储医生信息
        conn = create_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patient WHERE phone = {} ".format(user_info))
        patient_info = cursor.fetchone()
        patient_id = patient_info[0]
        session['patient_id'] = patient_id
        patient_columns = [column[0] for column in cursor.description]
        conn.close()

        return render_template('patient_dashboard.html', user_info=user_info, patient_info=patient_info,
                               patient_columns=patient_columns)
    else:
        return redirect(url_for('login'))


# 新增路由：医生个人信息编辑
@app.route('/patient_profile', methods=['GET', 'POST'])
def edit_patient_profile():
    # 处理医生个人信息编辑的表单提交
    # 在实际应用中，更新数据库中医生的个人信息
    # 这里简化为示例
    user_info = session.get('user_info')
    new_id = request.form.get('id')
    new_passwd = request.form.get('passwd')
    new_phone = request.form.get('new_phone')
    new_past = request.form.get('new_past')
    new_allergy = request.form.get('new_allergy')
    new_marry = request.form.get('new_marry')
    new_address = request.form.get('new_address')
    if user_info:
        if request.method == 'POST':
            # 在实际应用中，更新数据库中医生的个人信息
            new_id = request.form.get('id')
            new_passwd = request.form.get('passwd')
            new_phone = request.form.get('new_phone')
            new_past = request.form.get('new_past')
            new_allergy = request.form.get('new_allergy')
            new_marry = request.form.get('new_marry')
            new_address = request.form.get('new_address')
            conn = create_conn()
            cursor = conn.cursor()

            cursor.execute(
                'UPDATE patient SET patient_id = {}, password = {} ,phone = {},past_history={},allergy={},marry={},address={} WHERE phone = {} '.format(
                    new_id, new_passwd, new_phone, new_past, new_allergy, new_marry, new_address, user_info))
            conn.commit()
            conn.close()

            conn = create_conn()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM patient WHERE phone = {}'.format(user_info))
            patient_info = cursor.fetchone()
            patient_columns = [column[0] for column in cursor.description]
            conn.close()

            return render_template('patient_dashboard.html', user_info=user_info, patient_info=patient_info,
                                   patient_columns=patient_columns)
        else:

            return render_template('patient_profile.html', id=new_id, passwd=new_passwd, new_phone=new_phone)
    else:
        return redirect(url_for('login'))


@app.route('/patient_diagnosis')
def patient_diagnosis():
    user_info = session.get('user_info')
    patient_id = session.get('patient_id')
    if user_info:
        # 在实际应用中，使用数据库连接执行查询
        # 这里假设有一个名为 'doctor_schedule' 的表存储医生排班信息
        conn = create_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM diagnosis WHERE patient_id = {}'.format(patient_id))
        patient_diagnosis = cursor.fetchall()
        columns = get_table_columns('diagnosis')
        conn.close()

        return render_template('patient_diagnosis.html', columns=columns, patient_diagnosis=patient_diagnosis,
                               patient_id=patient_id)
    else:
        return redirect(url_for('login'))


@app.route('/patient_case')
def patient_case():
    user_info = session.get('user_info')
    patient_id = session.get('patient_id')
    if user_info:
        # 在实际应用中，使用数据库连接执行查询
        # 这里假设有一个名为 'doctor_schedule' 的表存储医生排班信息
        conn = create_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM public.case WHERE patient_id = {}'.format(patient_id))
        patient_case = cursor.fetchall()
        columns = get_table_columns('case')
        conn.close()

        return render_template('patient_case.html', columns=columns, patient_case=patient_case, patient_id=patient_id)
    else:
        return redirect(url_for('login'))


@app.route('/patient_prescription')
def patient_prescription():
    user_info = session.get('user_info')
    patient_id = session.get('patient_id')
    if user_info:
        # 在实际应用中，使用数据库连接执行查询
        # 这里假设有一个名为 'doctor_schedule' 的表存储医生排班信息
        conn = create_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM prescription WHERE patient_id = {}'.format(patient_id))
        patient_prescription = cursor.fetchall()
        columns = get_table_columns('prescription')
        conn.close()

        return render_template('patient_prescription.html', columns=columns, patient_prescription=patient_prescription,
                               patient_id=patient_id)
    else:
        return redirect(url_for('login'))


# 路由：医生仪表盘
@app.route('/doctor_dashboard')
def doctor_dashboard():
    user_info = session.get('user_info')
    if user_info and user_info[0] == '1':
        # 在实际应用中，使用数据库连接执行查询
        # 这里假设有一个名为 'doctors' 的表存储医生信息
        conn = create_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM doctor WHERE job_number = {} ".format(user_info))
        doctor_info = cursor.fetchone()
        doctor_columns = [column[0] for column in cursor.description]
        conn.close()

        return render_template('doctor_dashboard.html', user_info=user_info, doctor_info=doctor_info,
                               doctor_columns=doctor_columns)
    else:
        return redirect(url_for('login'))


# 新增路由：医生个人信息编辑
@app.route('/doctor_profile', methods=['GET', 'POST'])
def edit_doctor_profile():
    # 处理医生个人信息编辑的表单提交
    # 在实际应用中，更新数据库中医生的个人信息
    # 这里简化为示例
    user_info = session.get('user_info')
    doctor_id = session.get('doctor_id')
    new_id = request.form.get('id')
    new_passwd = request.form.get('passwd')
    new_introduction = request.form.get('introduction')
    if user_info and user_info[0] == '1':
        if request.method == 'POST':
            # 在实际应用中，更新数据库中医生的个人信息
            new_id = request.form.get('id')
            new_passwd = request.form.get('passwd')
            new_introduction = request.form.get('introduction')
            conn = create_conn()
            cursor = conn.cursor()

            cursor.execute(
                'UPDATE doctor SET doctor_id = {}, password = {} ,introduction = {} WHERE doctor_id ={} '.format(new_id,
                                                                                                                 new_passwd,
                                                                                                                 new_introduction,
                                                                                                                 doctor_id))
            conn.commit()
            conn.close()

            conn = create_conn()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM doctor WHERE doctor_id = {}'.format(doctor_id))
            doctor_info = cursor.fetchone()
            doctor_columns = [column[0] for column in cursor.description]
            conn.close()

            return render_template('doctor_dashboard.html', user_info=user_info, doctor_info=doctor_info,
                                   doctor_columns=doctor_columns)
        else:

            return render_template('doctor_profile.html', id=new_id, passwd=new_passwd, introduction=new_introduction)
    else:
        return redirect(url_for('login'))


# 新增路由：医生确认排班
# 路由：医生排班日程页面
@app.route('/doctor_schedule')
def doctor_schedule():
    user_info = session.get('user_info')
    doctor_id = session.get('doctor_id')
    if user_info:
        # 在实际应用中，使用数据库连接执行查询
        # 这里假设有一个名为 'doctor_schedule' 的表存储医生排班信息
        conn = create_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM schedule WHERE doctor_id = {}'.format(doctor_id))
        doctor_schedule = cursor.fetchall()
        columns = get_table_columns('schedule')
        conn.close()

        return render_template('doctor_schedule.html', columns=columns, doctor_schedule=doctor_schedule,
                               doctor_id=doctor_id)
    else:
        return redirect(url_for('login'))


# 新增路由：医生确认排班
@app.route('/confirm_schedule', methods=['GET', 'POST'])
def confirm_schedule():
    user_info = session.get('user_info')
    doctor_id = session.get('doctor_id')
    if user_info:
        if request.method == 'POST':
            # 处理修改排班状态的表单提交
            schedule_id = request.form.get('schedule_id')
            new_status = request.form.get('new_status')

            # 在实际应用中，更新数据库中排班信息的状态
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

        return render_template('confirm_schedule.html', user_info=user_info, schedule=schedule, columns=columns)
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

        return render_template('doctor_diagnosis.html', columns=columns, doctor_diagnosis=doctor_diagnosis,
                               doctor_id=doctor_id)
    else:
        return redirect(url_for('login'))


@app.route('/prescriptions', methods=['GET', 'POST'])
def prescriptions():
    user_info = session.get('user_info')
    doctor_id = session.get('doctor_id')
    if user_info:
        if request.method == 'POST':
            # 处理处方开具表单提交
            patient_id = request.form.get('patient_id')
            prescription_id = request.form.get('prescription_id')
            content = request.form.get('content')
            name = request.form.get('name')
            nurse_id = request.form.get('nurse_id')
            prescription_date = datetime.now().timestamp()

            # 在实际应用中，将处方信息插入数据库
            conn = create_conn()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO prescription (doctor_id, patient_id, content,prescription_id,name,nurse_id) VALUES ({}, {}, {},{},{},{})'.format(
                    doctor_id, patient_id, content, prescription_id, str(name), nurse_id))
            conn.commit()
            conn.close()

        return render_template('prescriptions.html', user_info=user_info)
    else:
        return redirect(url_for('login'))


# 路由：护士仪表盘
@app.route('/nurse_dashboard')
def nurse_dashboard():
    user_info = session.get('user_info')
    if user_info and user_info[0] == '2':
        # 在实际应用中，使用数据库连接执行查询
        # 这里假设有一个名为 'doctors' 的表存储医生信息
        conn = create_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM nurse WHERE job_number = {} ".format(user_info))
        nurse_info = cursor.fetchone()
        nurse_columns = [column[0] for column in cursor.description]
        conn.close()

        return render_template('nurse_dashboard.html', user_info=user_info, nurse_info=nurse_info,
                               nurse_columns=nurse_columns)
    else:
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.secret_key = 'your_secret_key'
    app.run(debug=True)
