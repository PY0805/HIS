import base64
import json
from datetime import datetime

from psycopg2 import *
from psycopg2 import extras

from libs.ComplexEncoder import ComplexEncoder


class RoleBase:
    def __init__(self, db_role):
        self.conn = connect(
            database=db_role['database'], user=db_role['user'], password=db_role['password'], host=db_role['host'],
            port=db_role['port']
        )
        self.cur = self.conn.cursor(cursor_factory=extras.RealDictCursor)

    def close(self):
        self.cur.close()
        self.conn.close()


class AdminRole(RoleBase):
    def query(self, column_name, table_name, id_name, id_num):
        sql = "SELECT {} FROM {} where {}={}".format(column_name, table_name, id_name, id_num)
        self.cur.execute(sql)
        result = []
        data_s = self.cur.fetchall()
        for data in data_s:
            data_dict = dict(data)
            result.append(data_dict)
        return json.dumps(result[0], ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'))

    def insert(self, column_name, table_name, data):
        try:
            sql = "INSERT INTO {} ({}) VALUES ({})".format(table_name, column_name, data)
            self.cur.execute(sql)
            self.conn.commit()
            return "插入成功"
        except Exception as e:
            if "permission denied" in str(e):
                return "权限不足"
            elif "already exists." in str(e):
                return "插入序号已经存在"
            else:
                return "插入失败"

    def update(self, column_name, column_value, table_name, id_name, id_num):
        try:
            sql = "UPDATE {} SET {}={} WHERE {}={}".format(table_name, column_name, column_value, id_name, id_num)
            self.cur.execute(sql)
            self.conn.commit()
            return "更新成功"
        except Exception as e:
            if "permission denied" in str(e):
                return "权限不足"
            else:
                return "插入失败"

    def remove(self, table_name, id_name, id_num):
        try:
            sql = "DELETE FROM {} WHERE {}={}".format(table_name, id_name, id_num)
            self.cur.execute(sql)
            self.conn.commit()
            return "删除成功"
        except Exception as e:
            if "permission denied" in str(e):
                return "权限不足"
            else:
                return "插入失败"

    def login(self, username, password):
        try:
            self.cur.execute("SELECT doctor_id,job_number,password FROM doctor where job_number= {}".format(username))
            data_s = self.cur.fetchall()
            if data_s == []:
                self.cur.execute("SELECT patient_id,phone,password FROM patient where phone= {}".format(username))
                data_s = self.cur.fetchall()
            if data_s == []:
                self.cur.execute("SELECT nurse_id,job_number,password FROM nurse where job_number= {}".format(username))
                data_s = self.cur.fetchall()
            if data_s == []:
                self.cur.execute(
                    "SELECT drugadmin_id,job_number,password FROM drugadmin where job_number = {}".format(username))
                data_s = self.cur.fetchall()
            if data_s == []:
                self.cur.execute(
                    "SELECT supplier_id,phone_number,password FROM supplier where phone_number = {}".format(username))
                data_s = self.cur.fetchall()
            result = []
            for key in data_s[0].keys():
                result.append(str(key))
            for value in data_s[0].values():
                result.append(str(value))
            role = result[0].split('_')[0]
            id = result[3]
            user = result[4]
            passwd = result[5]
            if user and id and passwd == password:
                return user, id, role
            else:
                return False, False, False
        except Exception as e:
            print(e)
            return False, False, False


class DoctorRole(RoleBase):
    def query_information(self, job_number):
        try:
            sql = ("SELECT doctor_id, name, sex, age, phone_number, state, work_date, introduction, id_number, "
                   "job_number, title, photo, department_id FROM doctor WHERE job_number = {} ").format(
                job_number)
            result = []
            self.cur.execute(sql)
            self.conn.commit()  # 提交当前事务：case
            data_s = self.cur.fetchall()
            print(data_s)
            for data in data_s:
                data_dict = dict(data)
                result.append(data_dict)
            print(result)
            return json.dumps(result[0], ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'))
        except Exception as e:
            if "permission denied" in str(e):
                return "权限不足"
            else:
                return "查询失败"

    def query_schedule(self, doctor_id):
        try:
            sql = "select * FROM schedule where doctor_id={}".format(doctor_id)
            result = []
            self.cur.execute(sql)
            self.conn.commit()  # 提交当前事务：
            data_s = self.cur.fetchall()
            for data in data_s:
                data_dict = dict(data)
                result.append(data_dict)
            return json.dumps(result[0], ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'),
                              cls=ComplexEncoder)
        except Exception as e:
            if "permission denied" in str(e):
                return "权限不足"
            else:
                return "查询失败"

    def query_diagnosis(self, doctor_id):
        try:
            sql = "select * FROM diagnosis where doctor_id={}".format(doctor_id)
            result = []
            self.cur.execute(sql)
            self.conn.commit()  # 提交当前事务：
            data_s = self.cur.fetchall()
            for data in data_s:
                data_dict = dict(data)
                result.append(data_dict)
            return json.dumps(result[0], ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'),
                              cls=ComplexEncoder)
        except Exception as e:
            if "permission denied" in str(e):
                return "权限不足"
            else:
                return "查询失败"

    def update_information(self, new_passwd, new_introduction, doctor_photo, doctor_id):
        try:
            if new_passwd != '':
                self.cur.execute(
                    "UPDATE doctor SET password = {} WHERE doctor_id = {}".format(new_passwd, doctor_id))
                self.conn.commit()

            if new_introduction != '':
                self.cur.execute(
                    "UPDATE doctor SET introduction = {} WHERE doctor_id = {}".format(new_introduction, doctor_id))
                self.conn.commit()

            if doctor_photo != '':
                self.cur.execute(
                    "UPDATE doctor SET photo = {} WHERE doctor_id = {}".format(Binary(doctor_photo.read()), doctor_id))
                self.conn.commit()

            return "更新成功"

        except Exception as e:
            print(e)
            return "更新失败"

    def update_schedule_state(self, new_status, doctor_id, schedule_id):
        try:
            sql = "UPDATE schedule SET state = {} WHERE doctor_id={} and schedule_id={}".format(new_status, doctor_id,
                                                                                                schedule_id)
            self.cur.execute(sql)
            self.conn.commit()
            return "更新成功"
        except:
            return "更新失败"

    # 给患者开处方
    # 调用示例：insert_prescription(doctor_id, patient_id, {"hhh": 11, "999感冒灵": 1}, 'this is notes')
    def insert_prescription(self, doctor_id, patient_id, content, notes):
        try:
            drugs = []
            self.conn.commit()
            for drug_name, drug_count in content.items():
                self.cur.execute(
                    "SELECT EXISTS(SELECT drug_id FROM drug WHERE name = '{}' and number != 0)".format(drug_name))
                isexist = str(self.cur.fetchone())
                if 'True' not in isexist:
                    return "药品库存不足"
                drugs.append((drug_name, drug_count))
            self.cur.execute(
                "INSERT INTO prescription (date, doctor_id, patient_id, notes, content, state, name) VALUES ('{}', "
                "{}, {}, '{}', '{}', {}, (SELECT name FROM patient where patient.patient_id = {})) RETURNING "
                "prescription_id".format(
                    datetime.now(), doctor_id, patient_id, notes, str(json.dumps(content)), 1, patient_id))
            self.conn.commit()
            prescription_id = str(self.cur.fetchone()).split(' ')[1].split(')')[0]
            for drug in drugs:
                print(prescription_id, drug[0], drug[1])
                self.cur.execute(
                    "INSERT INTO prescription_content (prescription_id, drugname, drugcount) VALUES ({}, '{}', {})".format(
                        prescription_id, drug[0], drug[1]))
                self.conn.commit()
            return "开处方成功"
        except Exception as e:
            print(e)
            return "开处方失败"


class DrugadminRole(RoleBase):
    def query_information(self, drugadmin_id):
        try:
            sql = "SELECT drugadmin_id, name, sex, age, phone_number, work_date, id_number, job_number, state, photo FROM drugadmin WHERE drugadmin_id = {} ".format(
                drugadmin_id)
            result = []
            self.cur.execute(sql)
            self.conn.commit()
            data_s = self.cur.fetchall()
            for data in data_s:
                data_dict = dict(data)
                result.append(data_dict)
                data_dict['photo'] = base64.b64encode(bytes(memoryview(data_dict['photo']))).decode('utf-8')
            return json.dumps(result[0], ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'))
        except:
            return "查询失败"

    def update_information(self, new_phone_number, new_photo, drugadmin_id):
        try:
            if new_phone_number != '':
                self.cur.execute(
                    "UPDATE drugadmin SET phone_number = {} WHERE drugadmin_id = {}".format(new_phone_number,
                                                                                            drugadmin_id))
                self.conn.commit()

            if new_photo != '':
                self.cur.execute(
                    "UPDATE drugadmin SET photo = {} WHERE drugadmin_id = {} ".format(Binary(new_photo.read()),
                                                                                      drugadmin_id))
                self.conn.commit()

            return "更新成功"

        except:
            return "更新失败"

    def insert_drugin(self, in_number, drug_name, batch, n, notes, instruction, supplier_id, admin_id):
        try:
            sql1 = (
                "INSERT INTO drug (name, number, batch, state, n, time, supplier_id, notes, instruction) VALUES ('{}', {}, '{}', '{}', '{}', '{}', {}, '{}', '{}') RETURNING drug_id").format(
                drug_name,
                in_number,
                batch,
                1,
                n,
                datetime.now(),
                supplier_id,
                notes,
                instruction)
            self.cur.execute(sql1)
            self.conn.commit()
            drug_id = self.cur.fetchone()[0]
            sql2 = "INSERT INTO drugin (in_number, time, admin_id, drug_id) VALUES ({}, '{}', {}, {})".format(
                in_number,
                self.cur.execute("SELECT time FROM drug WHERE drug_id = {}".format(drug_id)),
                admin_id,
                in_number,
                drug_id)
            self.cur.execute(sql2)
            self.conn.commit()
            return "插入成功"
        except Exception as e:
            if "permission denied" in str(e):
                return "权限不足"
            elif "already exists." in str(e):
                return "插入序号已经存在"
            else:
                return "插入失败"


class NurseRole(RoleBase):
    def query_information(self, job_number):
        try:
            sql = "SELECT * FROM nurse WHERE job_number = {} ".format(job_number)
            result = []
            self.cur.execute(sql)
            self.conn.commit()  # 提交当前事务：case
            data_s = self.cur.fetchall()
            for data in data_s:
                data_dict = dict(data)
                data_dict['photo'] = base64.b64encode(bytes(memoryview(data_dict['photo']))).decode('utf-8')
                result.append(data_dict)
            return json.dumps(result[0], ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'),
                              cls=ComplexEncoder)
        except Exception as e:
            if "permission denied" in str(e):
                return "权限不足"
            else:
                return "查询失败"

    def update_information(self, nurse_id, new_passwd, new_phone, new_photo):
        try:
            if new_passwd != '':
                self.cur.execute(
                    "UPDATE nurse SET password = {} WHERE nurse_id = {}".format(new_passwd, nurse_id))
                self.conn.commit()
            if new_phone != '':
                self.cur.execute(
                    "UPDATE nurse SET phone = {} WHERE nurse_id = {}".format(new_phone, nurse_id))
                self.conn.commit()
            if new_photo != '':
                self.cur.execute(
                    "UPDATE nurse SET photo = {} WHERE nurse_id = {} ".format(Binary(new_photo.read()), nurse_id))
                self.conn.commit()
            return "更新成功"
        except Exception as e:
            print(e)
            return "更新失败"

    def insert_drugout(self, drug_name, number, nurse_id):
        try:
            self.cur.execute(
                "SELECT drug_id, number FROM drug WHERE name = '{}' and number != 0 ORDER BY drug_id ".format(
                    drug_name))
            data_s = self.cur.fetchall()
            result = []
            for data in data_s:
                for value in data.values():
                    result.append(value)
            sum = 0
            for i in range(1, len(result), 2):
                sum = sum + result[i]
            if sum >= number:
                for i in range(0, len(result), 2):
                    if result[i + 1] >= number:
                        self.cur.execute(
                            "UPDATE drug SET number = {} WHERE drug_id = {} ".format(result[i + 1] - number,
                                                                                     result[i]))
                        self.conn.commit()
                        self.cur.execute(
                            "INSERT INTO drugout (time, number, nurse_id, drug_id) VALUES ('{}',{},{},{})".format(
                                datetime.now(), number, nurse_id, result[i]))
                        self.conn.commit()
                        number = 0
                    else:
                        self.cur.execute(
                            "UPDATE drug SET number = {} WHERE drug_id = {} ".format(0, result[i]))
                        self.conn.commit()
                        self.cur.execute(
                            "INSERT INTO drugout (time, number, nurse_id, drug_id) VALUES ('{}',{},{},{})".format(
                                datetime.now(), result[i + 1], nurse_id, result[i]))
                        self.conn.commit()
                        number = number - result[i + 1]
                    if number == 0:
                        return '出库成功'
            else:
                return '库存不足'
        except Exception as e:
            print(e)
            return "出库失败"

    def handle_prescription(self, prescription_id, nurse_id):
        try:
            self.cur.execute("SELECT state FROM prescription WHERE prescription_id = {}".format(prescription_id))
            data_s = self.cur.fetchall()
            if int(data_s[0]['state']) == 0:
                return f'处方{prescription_id}暂未生效'
            elif int(data_s[0]['state']) == 2:
                return f'处方{prescription_id}无需处理'
            else:
                try:
                    self.cur.execute(
                        "SELECT drugname, drugcount FROM prescription_content WHERE prescription_id = {} ".format(
                            prescription_id))
                    data_s = self.cur.fetchall()
                    result = []
                    for data in data_s:
                        for value in data.values():
                            result.append(value)
                    for i in range(0, len(result), 2):
                        self.insert_drugout(result[i], result[i + 1], nurse_id)
                    self.cur.execute(
                        "UPDATE prescription SET state = 2, nurse_id = {} WHERE prescription_id = {}".format(nurse_id,
                                                                                                             prescription_id))
                    self.conn.commit()
                    return f'处方{prescription_id}处理成功'
                except Exception as e:
                    print(e)
                    return f'处方{prescription_id}处理失败'
        except Exception as e:
            print(e)
            return f'处方{prescription_id}处理失败'


class PatientRole(RoleBase):
    def query_information(self, phone):
        try:
            sql = "SELECT * FROM patient WHERE phone = {} ".format(phone)
            result = []
            self.cur.execute(sql)
            self.conn.commit()  # 提交当前事务：case
            data_s = self.cur.fetchall()
            for data in data_s:
                data_dict = dict(data)
                data_dict['photo'] = base64.b64encode(bytes(memoryview(data_dict['photo']))).decode('utf-8')
                result.append(data_dict)
            return json.dumps(result[0], ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'),
                              cls=ComplexEncoder)
        except Exception as e:
            print(e)
            return "查询失败"

    def update_information(self, new_passwd, new_phone, new_past, new_allergy, new_marry, new_address, new_photo,
                           patient_id):
        try:
            if new_passwd != '':
                self.cur.execute(
                    "UPDATE patient SET password = {} WHERE patient_id = {} ".format(new_passwd, patient_id))
                self.conn.commit()

            if new_phone != '':
                self.cur.execute(
                    "UPDATE patient SET phone = {} WHERE patient_id = {} ".format(new_phone, patient_id))
                self.conn.commit()

            if new_past != '':
                self.cur.execute(
                    "UPDATE patient SET past_history = {} WHERE patient_id = {} ".format(new_past, patient_id))
                self.conn.commit()

            if new_allergy != '':
                self.cur.execute(
                    "UPDATE patient SET allergy = {} WHERE patient_id = {} ".format(new_allergy, patient_id))
                self.conn.commit()

            if new_marry != '':
                self.cur.execute(
                    "UPDATE patient SET marry = {} WHERE patient_id = {} ".format(new_marry, patient_id))
                self.conn.commit()

            if new_address != '':
                self.cur.execute(
                    "UPDATE patient SET address = {} WHERE patient_id = {} ;".format(new_address, patient_id))
                self.conn.commit()

            if new_photo != '':
                self.cur.execute(
                    "UPDATE patient SET photo = {} WHERE patient_id = {} ".format(Binary(new_photo.read()), patient_id))
                self.conn.commit()

            return "更新成功"

        except Exception as e:
            print(e)
            return "更新失败"

    def query_diagnosis(self, patient_id):
        try:
            sql = "SELECT * FROM diagnosis WHERE patient_id = {}".format(patient_id)
            result = []
            self.cur.execute(sql)
            self.conn.commit()  # 提交当前事务：
            data_s = self.cur.fetchall()
            for data in data_s:
                data_dict = dict(data)
                result.append(data_dict)
            return json.dumps(result[0], ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'),
                              cls=ComplexEncoder)
        except Exception as e:
            if "permission denied" in str(e):
                print(e)
                return "权限不足"
            else:
                print(e)
                return "查询失败"

    def query_case(self, patient_id):
        try:
            sql = "SELECT * FROM case WHERE patient_id = {}".format(patient_id)
            result = []
            self.cur.execute(sql)
            self.conn.commit()  # 提交当前事务：
            data_s = self.cur.fetchall()
            for data in data_s:
                data_dict = dict(data)
                result.append(data_dict)
            return json.dumps(result[0], ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'),
                              cls=ComplexEncoder)
        except Exception as e:
            if "permission denied" in str(e):
                print(e)
                return "权限不足"
            else:
                print(e)
                return "查询失败"

    def query_prescription(self, patient_id):
        try:
            print(patient_id)
            self.cur.execute(
                "SELECT prescription_id, content, date, state, notes FROM prescription WHERE patient_id = {} ".format(
                    patient_id))
            data_s = self.cur.fetchall()
            print(data_s)
            result = []
            for data in data_s:
                data_dict = dict(data)
                result.append(data_dict)
            print(result)
            print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'),
                             cls=ComplexEncoder))
            return json.dumps(result, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'),
                              cls=ComplexEncoder)
        except Exception as e:
            print(e)
            return "查询失败"


class SupplierRole(RoleBase):
    def query_information(self, supplier_id):
        try:
            result = []
            self.cur.execute("SELECT * FROM supplier WHERE supplier_id = {} ".format(supplier_id))
            self.conn.commit()  # 提交当前事务：case
            data_s = self.cur.fetchall()
            for data in data_s:
                data_dict = dict(data)
                result.append(data_dict)
            return json.dumps(result[0], ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'))
        except Exception as e:
            if "permission denied" in str(e):
                return "权限不足"
            else:
                return "查询失败"

    def update_information(self, new_passwd, new_person, new_phone_number, new_address, supplier_id):
        try:
            if new_passwd != '':
                self.cur.execute(
                    "UPDATE supplier SET password = {} WHERE supplier_id = {}".format(new_passwd, supplier_id))
                self.conn.commit()

            if new_person != '':
                self.cur.execute(
                    "UPDATE supplier SET person = '{}' WHERE supplier_id = {}".format(new_person, supplier_id))
                self.conn.commit()

            if new_phone_number != '':
                self.cur.execute(
                    "UPDATE supplier SET phone_number = {} WHERE supplier_id = {}".format(new_phone_number,
                                                                                          supplier_id))
                self.conn.commit()

            if new_address != '':
                self.cur.execute(
                    "UPDATE supplier SET address = '{}' WHERE supplier_id = {}".format(new_address, supplier_id))
                self.conn.commit()

            return "更新成功"

        except Exception as e:
            return "更新失败"

    def query_supply_drug(self, supplier_id):
        try:
            sql = "select drug_id, name, batch, state, n, notes, instruction FROM drug where supplier_id={}".format(
                supplier_id)
            result = []
            self.cur.execute(sql)
            self.conn.commit()
            data_s = self.cur.fetchall()
            for data in data_s:
                data_dict = dict(data)
                result.append(data_dict)
            return json.dumps(result[0], ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'))
        except Exception as e:
            if "permission denied" in str(e):
                return "权限不足"
            else:
                return "查询失败"


class UnauthorizedRole(RoleBase):

    def query_hospital(self, id_num):
        try:
            super(UnauthorizedRole, )
            sql = "SELECT * FROM hospital WHERE hospital_id={}".format(id_num)
            result = []
            self.cur.execute(sql)
            self.conn.commit()  # 提交当前事务：
            data_s = self.cur.fetchall()
            for data in data_s:
                data_dict = dict(data)
                result.append(data_dict)
            return json.dumps(result[0], ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'))
        except Exception as e:
            print(e)
            return "查询失败"

    def query_department(self, department_id):
        try:
            sql = "SELECT department_id,department_name,hospital_id FROM department WHERE department_id={}".format(
                department_id)
            result = []
            self.cur.execute(sql)
            self.conn.commit()  # 提交当前事务：
            data_s = self.cur.fetchall()
            for data in data_s:
                data_dict = dict(data)
                result.append(data_dict)
            return json.dumps(result[0], ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'))
        except Exception as e:
            if "permission denied" in str(e):
                return "权限不足"
            else:
                return "查询失败"

    def query_doctor(self, doctor_id):
        try:
            sql = "SELECT name,photo,department_id,title FROM doctor WHERE doctor_id={}".format(doctor_id)
            result = []
            self.cur.execute(sql)
            self.conn.commit()  # 提交当前事务：case
            data_s = self.cur.fetchall()
            for data in data_s:
                data_dict = dict(data)
                data_dict['photo'] = base64.b64encode(bytes(memoryview(data_dict['photo']))).decode('utf-8')
                result.append(data_dict)
            return json.dumps(result[0], ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'))
        except:
            return "查询失败"

    def query_schedule(self, doctor_id):
        try:
            sql = "select date,time,state,room_id FROM schedule where doctor_id={}".format(doctor_id)
            result = []
            self.cur.execute(sql)
            self.conn.commit()  # 提交当前事务：
            data_s = self.cur.fetchall()
            for data in data_s:
                data_dict = dict(data)
                result.append(data_dict)
            return json.dumps(result[0], ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'),
                              cls=ComplexEncoder)
        except:
            return "查询失败"
