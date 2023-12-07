import psycopg2
from psycopg2 import extras
import json
import os

photo_path = r"static/images/doctor"


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


def img2bin(doctor_photo):
    with open(os.path.join(photo_path, doctor_photo), 'rb') as f:
        img = f.read()
    return psycopg2.Binary(img)


class RoleBase:
    def __init__(self, db_manager, role_name):
        self.db_manager = db_manager
        self.role_name = role_name


class AdminRole(RoleBase):
    def query(self, column_name, table_name, id_name, id_num):
        try:
            sql = "SELECT {} FROM {} where {}={}".format(column_name, table_name, id_name, id_num)
            result = []
            self.db_manager.cur.execute(sql)
            self.db_manager.conn.commit()  # 提交当前事务：case
            data_s = self.db_manager.cur.fetchall()
            for data in data_s:
                data_dict = dict(data)
                result.append(data_dict)
        except Exception as e:
            if "permission denied" in str(e):
                return "权限不足"
            else:
                return "查询失败"
        return json.dumps(result[0], ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'))

    def insert(self, column_name, table_name, data):
        try:
            sql = "INSERT INTO {} ({}) VALUES ({})".format(table_name, column_name, data)
            self.db_manager.cur.execute(sql)
            self.db_manager.conn.commit()
        except Exception as e:
            if "permission denied" in str(e):
                return "权限不足"
            elif "already exists." in str(e):
                return "插入序号已经存在"
            else:
                return "插入失败"
        return "插入成功"

    def update(self, column_name, column_value, table_name, id_name, id_num):
        try:
            sql = "UPDATE {} SET {}={} WHERE {}={}".format(table_name, column_name, column_value, id_name, id_num)
            self.db_manager.cur.execute(sql)
            self.db_manager.conn.commit()
        except Exception as e:
            if "permission denied" in str(e):
                return "权限不足"
            else:
                return "插入失败"
        return "更新成功"

    def remove(self, table_name, id_name, id_num):
        try:
            sql = "DELETE FROM {} WHERE {}={}".format(table_name, id_name, id_num)
            self.db_manager.cur.execute(sql)
            self.db_manager.conn.commit()
        except Exception as e:
            if "permission denied" in str(e):
                return "权限不足"
            else:
                return "插入失败"
        return "删除成功"


class DoctorRole(RoleBase):
    def query_information(self, doctor_id):
        try:
            sql = "SELECT doctor_id, name, sex, age, phone_number, state, work_date, introduction, id_number, job_number, title, photo, department_id FROM doctor WHERE job_number = {} ".format(
                doctor_id)
            result = []
            self.db_manager.cur.execute(sql)
            self.db_manager.conn.commit()  # 提交当前事务：case
            data_s = self.db_manager.cur.fetchall()
            for data in data_s:
                data_dict = dict(data)
                result.append(data_dict)
        except Exception as e:
            if "permission denied" in str(e):
                return "权限不足"
            else:
                return "查询失败"
        return json.dumps(result[0], ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'))

    def query_schedule(self, doctor_id):
        try:
            sql = "select * from schedule where doctor_id={}".format(doctor_id)
            result = []
            self.db_manager.cur.execute(sql)
            self.db_manager.conn.commit()  # 提交当前事务：
            data_s = self.db_manager.cur.fetchall()
            for data in data_s:
                data_dict = dict(data)
                result.append(data_dict)
        except Exception as e:
            if "permission denied" in str(e):
                return "权限不足"
            else:
                return "查询失败"
        return json.dumps(result[0], ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'))

    def query_diagnosis(self, doctor_id):
        try:
            sql = "select * from diagnosis where doctor_id={}".format(doctor_id)
            result = []
            self.db_manager.cur.execute(sql)
            self.db_manager.conn.commit()  # 提交当前事务：
            data_s = self.db_manager.cur.fetchall()
            for data in data_s:
                data_dict = dict(data)
                result.append(data_dict)
        except Exception as e:
            if "permission denied" in str(e):
                return "权限不足"
            else:
                return "查询失败"
        return json.dumps(result[0], ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'))

    def update_information(self, new_passwd, new_introduction, doctor_id, doctor_photo):
        try:
            sql = "UPDATE doctor SET password = {} ,introduction = {}, photo={} WHERE doctor_id ={} ".format(
                new_passwd,
                new_introduction,
                img2bin(doctor_photo),
                doctor_id)
            self.db_manager.cur.execute(sql)
            self.db_manager.conn.commit()
        except:
            return "更新失败"
        return "更新成功"

    def update_schedule_state(self, new_status, doctor_id, schedule_id):
        try:
            sql = "UPDATE schedule SET state = {} WHERE doctor_id={} and schedule_id={}".format(new_status, doctor_id,
                                                                                                schedule_id)
            self.db_manager.cur.execute(sql)
            self.db_manager.conn.commit()
        except Exception:
            return "更新失败"
        return "更新成功"

    def insert_prescription(self, doctor_id, patient_id, content, prescription_id, name, nurse_id):
        try:
            sql = "INSERT INTO prescription (doctor_id, patient_id, content,prescription_id,name,nurse_id) VALUES ({}, " \
                  "{}, {},{},{},{})".format(
                doctor_id, patient_id, content, prescription_id, str(name), nurse_id)
            self.db_manager.cur.execute(sql)
            self.db_manager.conn.commit()
        except Exception as e:
            if "permission denied" in str(e):
                return "权限不足"
            elif "already exists." in str(e):
                return "插入序号已经存在"
            else:
                return "插入失败"
        return "插入成功"


class NurseRole(RoleBase):
    def query_information(self, doctor_id):
        try:
            sql = "SELECT * FROM doctor WHERE job_number = {} ".format(doctor_id)
            result = []
            self.db_manager.cur.execute(sql)
            self.db_manager.conn.commit()  # 提交当前事务：case
            data_s = self.db_manager.cur.fetchall()
            for data in data_s:
                data_dict = dict(data)
                result.append(data_dict)
        except Exception as e:
            if "permission denied" in str(e):
                return "权限不足"
            else:
                return "查询失败"
        return json.dumps(result[0], ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'))


class DrugadminRole(RoleBase):
    def query_information(self, drugadmin_id):
        try:
            sql = "SELECT drugadmin_id, name, sex, age, phone_number, work_date, id_number, job_number, state, photo FROM drugadmin WHERE drugadmin_id = {} ".format(
                drugadmin_id)
            result = []
            self.db_manager.cur.execute(sql)
            self.db_manager.conn.commit()  # 提交当前事务：case
            data_s = self.db_manager.cur.fetchall()
            for data in data_s:
                data_dict = dict(data)
                result.append(data_dict)
        except:
            return "查询失败"

    def update_information(self, new_phone_number, new_photo, drugadmin_id):
        try:
            sql = "UPDATE drugadmin SET phone_number = {} ,photo = {} WHERE drugadmin_id ={} ".format(
                new_phone_number,
                img2bin(new_photo),
                drugadmin_id)
            self.db_manager.cur.execute(sql)
            self.db_manager.conn.commit()
        except Exception:
            return "更新失败"
        return "更新成功"

    def update_drugin(self, in_number, drug_name, batch, n, notes, instruction, supplier_id):
        try:
            sql = "UPDATE drug SET n = {} ,notes = {}, instruction={} WHERE name ={} and batch={} and supplier_id={}".format(
                in_number,
                notes,
                instruction,
                drug_name,
                batch,
                supplier_id)
            self.db_manager.cur.execute(sql)
            self.db_manager.conn.commit()
        except Exception:
            return "更新失败"
        return "更新成功"


class SupplierRole(RoleBase):
    def query_information(self, supplier_id):
        try:
            sql = "SELECT * FROM supplier WHERE supplier_id = {} ".format(supplier_id)
            result = []
            self.db_manager.cur.execute(sql)
            self.db_manager.conn.commit()  # 提交当前事务：case
            data_s = self.db_manager.cur.fetchall()
            for data in data_s:
                data_dict = dict(data)
                result.append(data_dict)
        except Exception as e:
            if "permission denied" in str(e):
                return "权限不足"
            else:
                return "查询失败"
        return json.dumps(result[0], ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'))

    def update_information(self, new_passwd, new_person, new_phone_number, new_address, supplier_id):
        try:
            sql = "UPDATE supplier SET password = {} ,person = {}, phone_number={}, address={} WHERE supplier_id ={} ".format(
                new_passwd,
                new_person,
                new_phone_number,
                new_address,
                supplier_id)
            self.db_manager.cur.execute(sql)
            self.db_manager.conn.commit()
            return "更新成功"
        except Exception:
            return "更新失败"

    def query_supply_drug(self, supplier_id):
        try:
            sql = "select drug_id, name, batch, state, n, notes, instruction from drug where supplier_id={}".format(
                supplier_id)
            result = []
            self.db_manager.cur.execute(sql)
            self.db_manager.conn.commit()
            data_s = self.db_manager.cur.fetchall()
            for data in data_s:
                data_dict = dict(data)
                result.append(data_dict)
        except Exception as e:
            if "permission denied" in str(e):
                return "权限不足"
            else:
                return "查询失败"
        return json.dumps(result[0], ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'))


class UnauthorizedRole(RoleBase):

    def query_department(self, department_id):
        try:
            sql = "select department_id,department_name,hospital_id from department where department_id={}".format(
                department_id)
            result = []
            self.db_manager.cur.execute(sql)
            self.db_manager.conn.commit()  # 提交当前事务：
            data_s = self.db_manager.cur.fetchall()
            for data in data_s:
                data_dict = dict(data)
                result.append(data_dict)
        except:
            return "查询失败"
        return json.dumps(result[0], ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'))

    def query_hospital(self, id_num):
        try:
            super(UnauthorizedRole, )
            sql = "select * from hospital WHERE hospital_id={}".format(id_num)
            result = []
            self.db_manager.cur.execute(sql)
            self.db_manager.conn.commit()  # 提交当前事务：
            data_s = self.db_manager.cur.fetchall()
            for data in data_s:
                data_dict = dict(data)
                result.append(data_dict)
        except Exception:
            return "查询失败"
        return json.dumps(result[0], ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'))

    def query_doctor(self, doctor_id):
        try:
            sql = "select name,photo,department_id,title from doctor where doctor_id={}".format(doctor_id)
            result = []
            self.db_manager.cur.execute(sql)
            self.db_manager.conn.commit()  # 提交当前事务：
            data_s = self.db_manager.cur.fetchall()
            for data in data_s:
                data_dict = dict(data)
                result.append(data_dict)
        except Exception as e:
            if "permission denied" in str(e):
                return "权限不足"
            else:
                return "查询失败"
        return json.dumps(result[0], ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'))

    def query_schedule(self, doctor_id):
        try:
            sql = "select date,time,state,room_id from schedule where doctor_id={}".format(doctor_id)
            result = []
            self.db_manager.cur.execute(sql)
            self.db_manager.conn.commit()  # 提交当前事务：
            data_s = self.db_manager.cur.fetchall()
            for data in data_s:
                data_dict = dict(data)
                result.append(data_dict)
        except Exception as e:
            if "permission denied" in str(e):
                return "权限不足"
            else:
                return "查询失败"
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
    'supplier': {
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
