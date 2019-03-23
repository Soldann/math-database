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
    tags = [str(x) for x in input().split()]

    for elements in tags:
        command = "INSERT IGNORE INTO tags VALUES (NULL, \"{}\")"
        cursor.execute(command.format(elements))

        cursor.execute("INSERT INTO tagMap VALUES ((SELECT id FROM tags WHERE name=\"{}\"), (SELECT id FROM proofs WHERE name=\"{}\"))".format(elements, name))

def tagSearch(cursor): #searches for proofs matching at least one tag
    print("Type tags")
    tags = [str(x) for x in input().split()]

    command = "SELECT * FROM proofs WHERE id IN (SELECT proofID from tagMap INNER JOIN tags ON tagID = tags.id where tags.name in ("

    firstTime = 1;
    for elements in tags:
        if not firstTime:
            command += ", "
        firstTime = 0;
        command += "\'{}\'".format(elements)
    command += "))"
    cursor.execute(command)

    for rows in cursor:
        print(rows[1:])

def tagAndSearch(cursor): #searches for proofs matching all tags, this will be merged with the other tag search eventually
    print("Type tags")
    tags = [str(x) for x in input().split()]

    command = "SELECT * FROM proofs WHERE id IN " \
              "(SELECT proofID FROM tagMap WHERE tagID IN " \
              "(SELECT id FROM tags WHERE name IN ("

    firstTime = 1;
    for elements in tags:
        if not firstTime:
            command += ", "
        firstTime = 0;
        command += "\'{}\'".format(elements)

    command += ")) GROUP BY proofID HAVING COUNT(proofID) = {})".format(len(tags))
    cursor.execute(command)

    for rows in cursor:
        print(rows[1:])

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
cursor.execute("SHOW TABLES LIKE 'proofs'")
if cursor.rowcount == 0:
    cursor.execute("CREATE TABLE proofs (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, \
                    name VARCHAR(255), description TEXT)")

cursor.execute("SHOW TABLES LIKE 'tags'") #Using the unique constraint here is not ideal, results in a warning every time you insert a duplicate
if cursor.rowcount == 0:
    cursor.execute("CREATE TABLE tags (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), CONSTRAINT uniqueName UNIQUE(name))")

cursor.execute("SHOW TABLES LIKE 'tagMap'")
if cursor.rowcount == 0:
    cursor.execute("CREATE TABLE tagMap (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, tagID int, proofID int, \
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

        elif command == "search name":
            print("Type the name")
            cursor.execute("SELECT * FROM proofs WHERE name LIKE \'{}%\'".format(input()))
            for rows in cursor:
                print(rows[1:])

        elif command == "search tags":
            tagSearch(cursor)

        elif command == "search tags -and":
            tagAndSearch(cursor)

        else:
            print("Invalid Command, Try again")

sql.close()

