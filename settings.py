DATABASE = 'HIS'  # 选择数据库名称
USER = 'test'  # 数据库用户名
PASSWORD = 'testGauss.'  # 数据库密码
HOST = '121.36.55.115'  # 数据库ip
PORT = '5432'  # 数据库端口
photo_path = r"static/images/"  # 照片存放路径
hospital_info = {  # 模拟医院基本信息数据
    'name': 'Example Hospital',
    'address': '123 Main St',
    'phone': '555-1234',
}
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
    'nurse': {
        'database': 'HIS',
        'user': 'test',
        'password': 'testGauss.',
        'host': '121.36.55.115',
        'port': '5432'

    },
    'drugadmin': {
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
    'unauthorized': {
        'database': 'HIS',
        'user': 'introduce',
        'password': 'Introduce.',
        'host': '121.36.55.115',
        'port': '5432'
    },
}
