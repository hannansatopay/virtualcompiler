import sqlite3

conn = sqlite3.connect('data.db')
print("Opened database successfully");

##conn.execute('''CREATE TABLE USER
##         (EMAIL TEXT PRIMARY KEY NOT NULL,
##          PASSWORD TEXT NOT NULL,
##          ROLE TEXT NOT NULL,
##          NAME TEXT,
##          SEMESTER TEXT,
##          STORAGE TEXT);''')

##conn.execute('''CREATE TABLE ASSIGNMENT
##         (ID TEXT PRIMARY KEY NOT NULL,
##          TEACHER TEXT NOT NULL,
##          SEMESTER TEXT NOT NULL,
##          SUBJECT TEXT NOT NULL,
##          STORAGE TEXT NOT NULL);''')

conn.execute('''CREATE TABLE SUBMISSION
         (ID TEXT PRIMARY KEY NOT NULL,
          STUDENT TEXT NOT NULL,
          TEACHER TEXT NOT NULL,
          SUBJECT TEXT NOT NULL,
          STORAGE TEXT NOT NULL,
          SCORE NUMBER);''')

print("Table created successfully");

conn.close()
