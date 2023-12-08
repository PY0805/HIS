import base64
import json
import os
from datetime import datetime

import psycopg2
from psycopg2 import extras

from app.libs.ComplexEncoder import ComplexEncoder


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


class Patient:
    def __init__(self, db_role):
        self.conn = psycopg2.connect(
            database=db_role['database'], user=db_role['user'], password=db_role['password'], host=db_role['host'],
            port=db_role['port']
        )
        self.cur = self.conn.cursor(cursor_factory=extras.RealDictCursor)

    def close(self):
        self.cur.close()
        self.conn.close()


class Drugadmin:
    def __init__(self, db_role):
        self.conn = psycopg2.connect(
            database=db_role['database'], user=db_role['user'], password=db_role['password'], host=db_role['host'],
            port=db_role['port']
        )
        self.cur = self.conn.cursor(cursor_factory=extras.RealDictCursor)

    def close(self):
        self.cur.close()
        self.conn.close()


class Doctor:
    def __init__(self, db_role):
        self.conn = psycopg2.connect(
            database=db_role['database'], user=db_role['user'], password=db_role['password'], host=db_role['host'],
            port=db_role['port']
        )
        self.cur = self.conn.cursor(cursor_factory=extras.RealDictCursor)


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
            else:
                return "插入失败"


class DoctorRole(RoleBase):
    def query_information(self, job_number):
        sql = "SELECT doctor_id, name, sex, age, phone_number, state, work_date, introduction, id_number, job_number, title, photo, department_id FROM doctor WHERE job_number = {} ".format(
            job_number)
        result = []
        self.db_manager.cur.execute(sql)
        self.db_manager.conn.commit()  # 提交当前事务：case
        data_s = self.db_manager.cur.fetchall()
        for data in data_s:
            data_dict = dict(data)
            result.append(data_dict)
        return json.dumps(result[0], ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'))

    def query_schedule(self, doctor_id):
        sql = "select * from schedule where doctor_id={}".format(doctor_id)
        result = []
        self.db_manager.cur.execute(sql)
        self.db_manager.conn.commit()  # 提交当前事务：
        data_s = self.db_manager.cur.fetchall()
        for data in data_s:
            data_dict = dict(data)
            result.append(data_dict)
        return json.dumps(result[0], ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'),
                          cls=ComplexEncoder)

    def query_diagnosis(self, doctor_id):
        sql = "select * from diagnosis where doctor_id={}".format(doctor_id)
        result = []
        self.db_manager.cur.execute(sql)
        self.db_manager.conn.commit()  # 提交当前事务：
        data_s = self.db_manager.cur.fetchall()
        for data in data_s:
            data_dict = dict(data)
            result.append(data_dict)
        return json.dumps(result[0], ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'),
                          cls=ComplexEncoder)

    def update_information(self, new_id, new_passwd, new_introduction, doctor_id, doctor_photo):
        sql = "UPDATE doctor SET doctor_id = {}, password = {} ,introduction = {}, photo={} WHERE doctor_id ={} ".format(
            new_id,
            new_passwd,
            new_introduction,
            doctor_id,
            img2bin(photo, 'doctor'))
        try:
            self.db_manager.cur.execute(sql)
            self.db_manager.conn.commit()
            return "更新成功"
        except:
            return "更新失败"

    def update_schedule_state(self, new_status, doctor_id, schedule_id):
        sql = "UPDATE schedule SET state = {} WHERE doctor_id={} and schedule_id={}".format(new_status, doctor_id,
                                                                                            schedule_id)
        try:
            self.db_manager.cur.execute(sql)
            self.db_manager.conn.commit()
            return "更新成功"
        except:
            return "更新失败"

    def insert_prescription(self, doctor_id, patient_id, content, prescription_id, name, nurse_id):
        sql = "INSERT INTO prescription (doctor_id, patient_id, content,prescription_id,name,nurse_id) VALUES ({}, " \
              "{}, {},{},{},{})".format(
            doctor_id, patient_id, content, prescription_id, str(name), nurse_id)
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


class PatientRole(RoleBase):
    def query_information(self, phone):
        sql = "SELECT * FROM patient WHERE phone = {} ".format(phone)
        result = []
        self.db_manager.cur.execute(sql)
        self.db_manager.conn.commit()  # 提交当前事务：case
        data_s = self.db_manager.cur.fetchall()
        for data in data_s:
            data_dict = dict(data)
            data_dict['photo'] = base64.b64encode(bytes(memoryview(data_dict['photo']))).decode('utf-8')
            result.append(data_dict)
        return json.dumps(result[0], ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'),
                          cls=ComplexEncoder)

    def update_information(self, new_id, new_passwd, new_phone, new_past, new_allergy, new_marry, new_address, phone):
        sql = "UPDATE patient SET patient_id = {}, password = {} ,phone = {},past_history={},allergy={},marry={},address={} WHERE phone = {} ".format(
            new_id,
            new_passwd,
            new_phone,
            new_past,
            new_allergy,
            new_marry,
            new_address,
            phone)
        try:
            self.db_manager.cur.execute(sql)
            self.db_manager.conn.commit()
            return "更新成功"
        except:
            return "更新失败"

    def query_diagnosis(self, patient_id):
        sql = "SELECT * FROM diagnosis WHERE patient_id = {}".format(patient_id)
        result = []
        self.db_manager.cur.execute(sql)
        self.db_manager.conn.commit()  # 提交当前事务：
        data_s = self.db_manager.cur.fetchall()
        for data in data_s:
            data_dict = dict(data)
            result.append(data_dict)
        return json.dumps(result[0], ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'),
                          cls=ComplexEncoder)

    def query_case(self, patient_id):
        sql = "SELECT * FROM case WHERE patient_id = {}".format(patient_id)
        result = []
        self.db_manager.cur.execute(sql)
        self.db_manager.conn.commit()  # 提交当前事务：
        data_s = self.db_manager.cur.fetchall()
        for data in data_s:
            data_dict = dict(data)
            result.append(data_dict)
        return json.dumps(result[0], ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'),
                          cls=ComplexEncoder)

    def query_prescription(self, patient_id):
        sql = "SELECT * FROM prescription WHERE patient_id = {}".format(patient_id)
        result = []
        self.db_manager.cur.execute(sql)
        self.db_manager.conn.commit()  # 提交当前事务：
        data_s = self.db_manager.cur.fetchall()
        for data in data_s:
            data_dict = dict(data)
            result.append(data_dict)
        return json.dumps(result[0], ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'),
                          cls=ComplexEncoder)


class NurseRole(RoleBase):
    def query_information(self, doctor_id):
        sql = "SELECT * FROM doctor WHERE job_number = {} ".format(doctor_id)
        result = []
        self.db_manager.cur.execute(sql)
        self.db_manager.conn.commit()  # 提交当前事务：case
        data_s = self.db_manager.cur.fetchall()
        for data in data_s:
            data_dict = dict(data)
            result.append(data_dict)
        return json.dumps(result[0], ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'))


class DrugadminRole(RoleBase):
    def query_information(self, drugadmin_id):
        try:
            sql = "SELECT drugadmin_id, name, sex, age, phone_number, work_date, id_number, job_number, state, photo FROM drugadmin WHERE drugadmin_id = {} ".format(
                drugadmin_id)
            result = []
            self.db_manager.cur.execute(sql)
            self.db_manager.conn.commit()
            data_s = self.db_manager.cur.fetchall()
            for data in data_s:
                data_dict = dict(data)
                result.append(data_dict)
                data_dict['photo'] = base64.b64encode(bytes(memoryview(data_dict['photo']))).decode('utf-8')
            return json.dumps(result[0], ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'))
        except:
            return "查询失败"

    def update_information(self, new_phone_number, drugadmin_id):
        sql = "UPDATE drugadmin SET phone_number = {}  WHERE drugadmin_id ={} ".format(
            new_phone_number,
            drugadmin_id)
        self.db_manager.cur.execute(sql)
        self.db_manager.conn.commit()

    def insert_drugin(self, in_number, drug_name, batch, n, notes, instruction, supplier_id, admin_id):
        sql1 = ("INSERT INTO drug (name, number, batch, state, n, time, supplier_id, notes, instruction) VALUES ({"
                "}, {}, {}, {}, {}, '{}', {}, {}, {}) RETURNING drug_id").format(
            drug_name,
            in_number,
            batch,
            1,
            n,
            datetime.now(),
            supplier_id,
            notes,
            instruction)
        self.db_manager.cur.execute(sql1)
        self.db_manager.conn.commit()
        drug_id = self.db_manager.cur.fetchone()[0]
        sql2 = "INSERT INTO drugin (in_number, time, admin_id, drug_id) VALUES ({}, {}, {}, {})".format(
            in_number,
            self.db_manager.cur.execute("SELECT time FROM drug WHERE drug_id = {}".format(drug_id)),
            admin_id,
            in_number,
            drug_id)
        self.db_manager.cur.execute(sql2)
        self.db_manager.conn.commit()


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
            data_dict['photo'] = base64.b64encode(bytes(memoryview(data_dict['photo']))).decode('utf-8')
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
        return json.dumps(result[0], ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'),
                          cls=ComplexEncoder)


