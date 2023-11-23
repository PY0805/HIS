from role_class import *

if __name__ == "__main__":

    """
    print("Enter your role (1.admin\n2.doctor\n3.patient\n4.pharmacy_admin\n5.pharmacy_nurse\n6.UnauthorizedRole\n")
    role = input().lower()
    roles = {
        'admin': AdminRole,
        'doctor': DoctorRole,
        'patient': PatientRole,
        'pharmacy_admin': PharmacyAdminRole,
        'pharmacy_nurse': PharmacyNurseRole,
        'UnauthorizedRole': UnauthorizedRole,
    }
    
    if role in roles:
        role_instance = roles[role](db_manager, role)
        if role == "doctor":
            doctor_id = int(input("Enter the doctor's ID: "))
            result = role_instance.query(doctor_id)
        else:
            result = role_instance.query()
        print(result)
    else:
        print("Role not found.")
    """
    db_manager = DatabaseManager(db_log['UnauthorizedRole']) # 未授权用户链接数据库
    UnloginRole = UnauthorizedRole(db_manager, 'UnauthorizedRole')  # 创建未授权用户
    #UnloginRole.query_hospital(1) #
    data = UnloginRole.query_department()
    print(data)
    #UnloginRole.query_doctor()
    #UnloginRole.query_schedule()
    #db_manager = DatabaseManager(db_log['admin']) # 管理员登录
    #AdminRole = AdminRole(db_manager, 'admin')  # 创建管理员
    db_manager.close()
