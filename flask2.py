from flask import Flask, render_template, request, redirect, url_for, session
import psycopg2
import json
from role_class import *

app = Flask(__name__)


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

db_manager = DatabaseManager(db_log['UnauthorizedRole'])  # 未授权用户登录
UnloginRole = UnauthorizedRole(db_manager, 'UnauthorizedRole')  # 创建未授权用户
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
        data = UnloginRole.query_hospital(search_term)
        columns = get_table_columns('hospital')
        # 渲染HTML页面，将查询结果传递给页面
        return render_template('hospital_info.html', data=data, search_term=search_term, columns=columns)

    columns = get_table_columns('hospital')
    return render_template('hospital_info.html', data=None, search_term=None, columns=columns)


# 路由：医生信息页面
@app.route('/doctor_info', methods=['GET', 'POST'])
def doctor_info_page():
    if request.method == 'POST':
        # 获取前端传递的参数
        search_term = request.form['search_term']
        data = UnloginRole.query_doctor(search_term)
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
        data = UnloginRole.query_department(search_term)
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
        data = UnloginRole.query_schedule(search_term)

        columns = get_table_columns('schedule')
        # 渲染HTML页面，将查询结果传递给页面
        return render_template('schedule_info.html', data=data, search_term=search_term, columns=columns)

    columns = get_table_columns('schedule')
    return render_template('schedule_info.html', data=None, search_term=None, columns=columns)


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
            "SELECT job_number,password FROM doctor where job_number= {} union select job_number,password from nurse WHERE job_number= {} ".format(
                job_number, job_number))

        users = cursor.fetchall()
        # 验证用户名和密码
        user = users[0][0]
        passwd = users[0][1]
        conn.close()

        if user and passwd == password and user[0] == '1':
            # 如果验证通过，将用户信息存储在session中
            session['user_info'] = user

            return redirect(url_for('doctor_dashboard'))
        elif user and passwd == password and user[0] == '2':
            session['user_info'] = user

            return redirect(url_for('nurse_dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials. Please try again.')

    return render_template('login.html', error=None)


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
