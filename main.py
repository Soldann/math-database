import pymysql

connection = pymysql.connect(
    host='localhost',
    user='python',
    password='pass'
)

try:
    with connection.cursor() as cursor:
        sql = "USE events"

        cursor.execute(sql)

        sql = "SELECT * FROM potluck"

        cursor.execute(sql)

        for rows in cursor:
            print(rows)
finally:
    connection.close()