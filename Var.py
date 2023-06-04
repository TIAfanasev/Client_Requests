import psycopg2
from PyQt5.QtGui import QFont


def one_query(col, tab, row_id):
    work_query = f'SELECT {col} FROM {tab} WHERE id = %s'
    cursor.execute(work_query, (row_id,))
    connection.commit()
    records = cursor.fetchall()
    return records[0][0]


def simple_query(col, tab, check, id_cl):

    work_query = f"SELECT {col} FROM {tab} WHERE NOT id = '{id_cl}'"
    cursor.execute(work_query,)
    connection.commit()
    records = cursor.fetchall()
    unique = True
    for rec in records:
        if rec[0] == str(check):
            unique = False
    return unique


connection = psycopg2.connect(
        database="clapdb",
        user="postgres",
        host="localhost",
        password="94286130Sup",
        port="5432"
    )
cursor = connection.cursor()

font = QFont()
font.setFamily('MS Shell Dlg 2')
font.setPointSize(10)
