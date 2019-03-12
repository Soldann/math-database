import pymysql
import sys

def createEntry(cursor):
    command = "INSERT INTO proofs VALUES (NULL, \"{}\", \"{}\")"

    print("Type proof name")
    name = input()
    print("Type proof description")
    desc = input()

    cursor.execute(command.format(name,desc))


    print("Add tags")
    tags = [x for x in input().split()]

    for elements in tags:
        command = "INSERT IGNORE INTO tags VALUES (NULL, \"{}\")"
        cursor.execute(command.format(elements))

        cursor.execute("INSERT INTO tagMap VALUES ((SELECT id FROM tags WHERE name=\"{}\"), (SELECT id FROM proofs WHERE name=\"{}\"))".format(elements, name))
#Establish connection
sql = pymysql.connect(
        host='localhost',
        user='python',
        password='pass',
    )

#access database
try:
    sql.cursor().execute("USE mathData")
except pymysql.err.OperationalError:
    print("User does not have permission on the SQL server")
    sql.close()
    sys.exit()
except pymysql.err.InternalError:
    #Database does not exist, create it.
    sql = pymysql.connect(
        host='localhost',
        user='python',
        password='pass'
    )
    sql.cursor().execute("CREATE DATABASE mathData")
    sql.cursor().execute("USE mathData")


cursor = sql.cursor()
#Create the necessary tables if they don't exist
cursor.execute("SHOW TABLES like 'proofs'")
if cursor.rowcount == 0:
    cursor.execute("CREATE TABLE proofs (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, \
                    name VARCHAR(255), description TEXT)")

cursor.execute("SHOW TABLES like 'tags'") #Using the unique constraint here is not ideal, results in a warning every time you insert a duplicate
if cursor.rowcount == 0:
    cursor.execute("CREATE TABLE tags (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), CONSTRAINT uniqueName UNIQUE(name))")

cursor.execute("SHOW TABLES like 'tagMap'")
if cursor.rowcount == 0:
    cursor.execute("CREATE TABLE tagMap (tagID int, proofID int, \
                    FOREIGN KEY (tagID) REFERENCES tags(id), FOREIGN KEY (proofID) REFERENCES proofs(id))")

#User interaction loop
exitFlag = 0
while not exitFlag:
        print("What would you like to do?")
        command = input()

        if command == "insert":
            createEntry(cursor)
            sql.commit()

        elif command == "exit":
            exitFlag = 1

        elif command == "print all":
            cursor.execute("SELECT * FROM proofs")
            for rows in cursor:
                print(rows[1:])

        else:
            print("Invalid Command, Try again")

sql.close()

