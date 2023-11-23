import psycopg2
from psycopg2 import extras
import json


class DatabaseManager:
    def __init__(self, db_role):
        self.conn = psycopg2.connect(
            database=db_role['database'], user=db_role['user'], password=db_role['password'], host=db_role['host'],
            port=db_role['port']
        )
        self.cur = self.conn.cursor(cursor_factory=extras.RealDictCursor)

    def close(self):
        self.cur.close()
        self.conn.close()


class RoleBase:
    def __init__(self, db_manager, role_name):
        self.db_manager = db_manager
        self.role_name = role_name


class AdminRole(RoleBase):
    def query(self, column_name, table_name, id_name, id_num):
        sql = "SELECT {} FROM {} where {}={}".format(column_name, table_name, id_name, id_num)
        self.db_manager.cur.execute(sql)
        result = []
        data_s = self.db_manager.cur.fetchall()
        for data in data_s:
            data_dict = dict(data)
            result.append(data_dict)
        return json.dumps(result[0], ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'))

    def insert(self, column_name, table_name, data):
        sql = "INSERT INTO {} ({}) VALUES ({})".format(table_name, column_name, data)
        try:
            self.db_manager.cur.execute(sql)
            self.db_manager.conn.commit()
            return "插入成功"
        except Exception as e:
            if "permission denied" in str(e):
                return "权限不足"
            elif "already exists." in str(e):
                return "插入序号已经存在"
            else:
                return "插入失败"

    def update(self, column_name, column_value, table_name, id_name, id_num):
        sql = "UPDATE {} SET {}={} WHERE {}={}".format(table_name, column_name, column_value, id_name, id_num)
        try:
            self.db_manager.cur.execute(sql)
            self.db_manager.conn.commit()
            return "更新成功"
        except Exception as e:
            if "permission denied" in str(e):
                return "权限不足"
            elif "already exists." in str(e):
                return "序号已经存在"
            else:
                return "插入失败"

    def remove(self, table_name, id_name, id_num):
        sql = "DELETE FROM {} WHERE {}={}".format(table_name, id_name, id_num)
        try:
            self.db_manager.cur.execute(sql)
            self.db_manager.conn.commit()
            return "删除成功"
        except Exception as e:
            if "permission denied" in str(e):
                return "权限不足"
            elif "already exists." in str(e):
                return "序号已经存在"
            else:
                return "插入失败"


class DoctorRole(RoleBase):
    def query(self, doctor_id):
        db_manager = self.db_manager
        sql = "SELECT name, photo, department_id, title FROM doctor WHERE doctor_id = %s"
        db_manager.cur.execute(sql, (doctor_id,))
        data = db_manager.cur.fetchone()
        db_manager.close()
        if data:
            return f"{self.role_name} Information: {data}"
        else:
            return "Doctor not found."


class PatientRole(RoleBase):
    def query(self):
        pass


class UnauthorizedRole(RoleBase):

    def query_department(self, department_id):
        sql = "select department_id,department_name,hospital_id from department where department_id={}".format(
            department_id)
        result = []
        self.db_manager.cur.execute(sql)
        self.db_manager.conn.commit()  # 提交当前事务：
        data_s = self.db_manager.cur.fetchall()
        for data in data_s:
            data_dict = dict(data)
            result.append(data_dict)
        return json.dumps(result[0], ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'))

    def query_hospital(self, id_num):
        super(UnauthorizedRole, )
        sql = "select * from hospital WHERE hospital_id={}".format(id_num)
        result = []
        self.db_manager.cur.execute(sql)
        self.db_manager.conn.commit()  # 提交当前事务：
        data_s = self.db_manager.cur.fetchall()
        for data in data_s:
            data_dict = dict(data)
            result.append(data_dict)
        return json.dumps(result[0], ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'))

    def query_doctor(self, doctor_id):
        sql = "select name,photo,department_id,title from doctor where doctor_id={}".format(doctor_id)
        result = []
        self.db_manager.cur.execute(sql)
        self.db_manager.conn.commit()  # 提交当前事务：case
        data_s = self.db_manager.cur.fetchall()
        for data in data_s:
            data_dict = dict(data)
            result.append(data_dict)
        return json.dumps(result[0], ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'))

    def query_schedule(self, doctor_id):
        sql = "select date,time,state,room_id from schedule where doctor_id={}".format(doctor_id)
        result = []
        self.db_manager.cur.execute(sql)
        self.db_manager.conn.commit()  # 提交当前事务：
        data_s = self.db_manager.cur.fetchall()
        for data in data_s:
            data_dict = dict(data)
            result.append(data_dict)
        return json.dumps(result[0], ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'))


db_log = {
    'admin': {
        'database': 'HIS',
        'user': 'test',
        'password': 'testGauss.',
        'host': '121.36.55.115',
        'port': '5432'

    },
    'doctor': {
        'database': 'HIS',
        'user': 'doctors',
        'password': 'Doctors.',
        'host': '121.36.55.115',
        'port': '5432'
    },
    'patient': {
        'database': 'HIS',
        'user': 'test',
        'password': 'testGauss.',
        'host': '121.36.55.115',
        'port': '5432'

    },
    'pharmacy_admin': {
        'database': 'HIS',
        'user': 'test',
        'password': 'testGauss.',
        'host': '121.36.55.115',
        'port': '5432'

    },
    'pharmacy_nurse': {
        'database': 'HIS',
        'user': 'test',
        'password': 'testGauss.',
        'host': '121.36.55.115',
        'port': '5432'

    },
    'UnauthorizedRole': {
        'database': 'HIS',
        'user': 'introduce',
        'password': 'Introduce.',
        'host': '121.36.55.115',
        'port': '5432'
    },
}
