import psycopg2


def one_query(col, tab, row_id):
    work_query = f'SELECT {col} FROM {tab} WHERE id = %s'
    cursor.execute(work_query, (row_id,))
    connection.commit()
    records = cursor.fetchall()
    return records[0][0]


connection = psycopg2.connect(
        database="clapdb",
        user="postgres",
        password="12345",
        host="127.0.0.1",
        port="5432"
    )
cursor = connection.cursor()
