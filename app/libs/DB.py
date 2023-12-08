import psycopg2
from settings import DATABASE, USER, PASSWORD, HOST, PORT


def create_conn():
    conn = psycopg2.connect(database=DATABASE, user=USER, password=PASSWORD, host=HOST, port=PORT)  # 连接数据库
    return conn


def get_table_columns(table):
    conn = create_conn()
    cursor = conn.cursor()
    cursor.execute(f'SELECT * FROM %s LIMIT 1' % (table))
    columns = [column[0] for column in cursor.description]
    conn.close()
    return columns
