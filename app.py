import flask
import os
from flask import jsonify
import random
import time
import sqlite3
import sys
from werkzeug.utils import secure_filename
import json
import subprocess
from flask import url_for
from os.path import join, dirname, realpath
from flask import send_from_directory
import pandas as pd
from datetime import datetime

UPLOAD_FOLDER = join(dirname(realpath(__file__)), 'static/uploads/')

app = flask.Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
port = int(os.getenv("PORT", 9099))


@app.route('/')
def home():
    return flask.render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    email = flask.request.form['email']
    password = flask.request.form['password']
    conn = sqlite3.connect('data.db')
    for row in conn.execute(f"SELECT * FROM USER WHERE email = '{email}';"):
        db_password = row[1]
        role = row[2]
        semester = row[4]
        classgroup = row[5]
        if (db_password == password):
            variable = 1
            break
        else:
            variable = 0
            break
    else:
        variable = -1
    conn.commit()
    conn.close()
    return jsonify(data=variable, role=role, semester=semester, classgroup=classgroup)


@app.route('/adduser')
def adduser():
    return flask.render_template('adduser.html')


@app.route('/create', methods=['POST'])
def create():
    email = flask.request.form['email']
    name = flask.request.form['name']
    role = flask.request.form['role']
    password = flask.request.form['password']
    semester = flask.request.form['semester']
    classgroup = flask.request.form['classgroup']
    conn = sqlite3.connect('data.db')
    if role == "teacher":
        query = f"INSERT INTO USER (EMAIL, PASSWORD, ROLE, NAME, STORAGE) VALUES ('{email}', '{password}', '{role}', '{name}', '[]');"
    else:
        query = f"INSERT INTO USER (EMAIL, PASSWORD, ROLE, NAME, SEMESTER, CLASSGROUP, STORAGE) VALUES ('{email}', '{password}', '{role}', '{name}', '{semester}', '{classgroup}', '[]');"
    conn.execute(query)
    conn.commit()
    conn.close()
    return "1"


@app.route('/profile')
def profile():
    return flask.render_template('profile.html')


@app.route('/updatepassword', methods=['POST'])
def updatepassword():
    email = flask.request.form['email']
    password = flask.request.form['password']
    oldpassword = flask.request.form['oldpassword']
    conn = sqlite3.connect('data.db')
    for row in conn.execute(f"SELECT * FROM USER WHERE email = '{email}';"):
        p = row[1]
        if (p == oldpassword):
            conn.execute(
                f"UPDATE USER SET PASSWORD = '{password}' WHERE email = '{email}';")
            variable = "1"
            break
        else:
            variable = "0"
            break
    else:
        variable = "-1"
    conn.commit()
    conn.close()
    return variable


@app.route('/addassignment')
def addassignment():
    return flask.render_template('addassignment.html')


@app.route('/createassignment', methods=['POST'])
def createassignment():
    teacher = flask.request.form['teacher']
    semester = flask.request.form['semester']
    subject = flask.request.form['subject']
    classgroup = flask.request.form['classgroup']
    data = flask.request.form['storage']
    id = ''.join(random.choice('0123456789ABCDEF') for i in range(16))
    conn = sqlite3.connect('data.db')
    conn.execute(
        f"INSERT INTO ASSIGNMENT (ID, TEACHER, SEMESTER, CLASSGROUP, SUBJECT, STORAGE) VALUES ('{id}', '{teacher}', '{semester}', '{classgroup}', '{subject}', '{data}');")
    conn.commit()
    conn.close()
    return "1"


@app.route('/dashboard')
def dashboard():
    return flask.render_template('dashboard.html')


@app.route('/fetchdashboard', methods=['POST'])
def fetchdashboard():
    semester = flask.request.form['semester']
    classgroup = flask.request.form['classgroup']
    email = flask.request.form['email']
    conn = sqlite3.connect('data.db')
    for row in conn.execute(f"SELECT * FROM USER WHERE EMAIL = '{email}';"):
        s = json.loads(row[6])
        break
    for row in conn.execute(f"SELECT * FROM ASSIGNMENT WHERE SEMESTER = '{semester}' AND CLASSGROUP = '{classgroup}';"):
        if (row[0] not in s):
            d = json.loads(row[5])
            t = row[1]
            s = row[4]
            assignmentid = row[0]
            break
    conn.commit()
    conn.close()
    data = ""
    try:
        d
    except NameError:
        d = None
    if(d is None):
        return jsonify("<div style='text-align: center;'>Wohoo! No more assignments to complete.</div>")
    for element in d:
        if element[1] == "java" or element[1] == "c" or element[1] == "cpp" or element[1] == "python":
            data = data + '''<div class="typecode"><label>''' + \
                element[0] + " (" + element[1] + ")" + '''</label> <textarea form ="assignmentform" rows="10" cols="90" id="question"></textarea><button type="button" id="run">Run</button><textarea form ="assignmentform" rows="2" cols="90" id="answer" disabled></textarea></div>'''
        else:
            data = data + '''<div class="document"><label>''' + \
                element[0] + '''</label> <input id="fileinput" form ="assignmentform" type="file" name="file" style="padding-bottom: 10px;"/></div>'''
    data = data + '<input form="assignmentform" type="submit" value="Submit Assignment">'
    data = data + '''<span id="assignmentid" style="display:none;">''' + assignmentid + '''</span>''' + \
        '''<span id="teacher" style="display:none;">''' + t + '''</span>''' + \
        '''<span id="subject" style="display:none;">''' + s + '''</span>'''
    return jsonify(data)


@app.route('/runcode', methods=['POST'])
def runcode():
    code = flask.request.form['code']
    language = flask.request.form['language']
    language = language.split("(")[-1].split(")")[0]

    if language == "python":
        f = open("demo.py", "w+")
        f.write(code)
        f.close()
        try:
            command = subprocess.run(["python3 demo.py"], shell=True,
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return str(command.stdout, "utf-8")
        except subprocess.CalledProcessError as e:
            return str(e.stderr, "utf-8")

    if language == "java":
        f = open("HelloWorld.java", "w+")
        f.write(code)
        f.close()
        try:
            subprocess.run(["javac HelloWorld.java"], shell=True)
            command = subprocess.run(["java HelloWorld"], shell=True,
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return str(command.stdout, "utf-8")
        except subprocess.CalledProcessError as e:
            return str(e.stderr, "utf-8")
    if language == "c":
        f = open("demo.c", "w+")
        f.write(code)
        f.close()
        try:
            subprocess.run(["cc demo.c -o demo"], shell=True)
            command = subprocess.run(["./demo"], shell=True,
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return str(command.stdout, "utf-8")
        except subprocess.CalledProcessError as e:
            return str(e.stderr, "utf-8")
    if language == "cpp":
        f = open("demo.C", "w+")
        f.write(code)
        f.close()
        try:
            subprocess.run(["g++ demo.C -o demo"], shell=True)
            command = subprocess.run(["./demo"], shell=True,
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return str(command.stdout, "utf-8")
        except subprocess.CalledProcessError as e:
            return str(e.stderr, "utf-8")        


@app.route('/submitassignment', methods=['POST'])
def submitassignment():
    question = flask.request.form.getlist("question")
    id = ''.join(random.choice('0123456789ABCDEF') for i in range(16))
    student = flask.request.form.getlist('student')
    teacher = flask.request.form.getlist('teacher')
    subject = flask.request.form.getlist('subject')
    classgroup = flask.request.form.getlist('classgroup')
    assignmentid = flask.request.form.getlist('assignmentid')
    conn = sqlite3.connect('data.db')
    conn.execute(f"INSERT INTO SUBMISSION (ID, STUDENT, TEACHER, SUBJECT, CLASSGROUP, STORAGE, TIMESTAMP, SCORE) VALUES ('{id}', '{student[0]}', '{teacher[0]}', '{subject[0]}', '{classgroup[0]}', '{json.dumps(question)}', '{round(time.time())}', '0');")
    conn.commit()
    conn.close()
    conn = sqlite3.connect('data.db')
    for row in conn.execute(f"SELECT * FROM USER WHERE email = '{student[0]}';"):
        s = json.loads(row[6])
        break
    s.append(assignmentid[0])
    conn.execute(f"UPDATE USER SET STORAGE = '{json.dumps(s)}';")
    conn.commit()
    conn.close()
    files = flask.request.files.getlist("file")
    for file in files:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return "1"


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/evaluate')
def evaluate():
    return flask.render_template('evaluate.html')


@app.route('/fetchassignment', methods=['POST'])
def fetchassignment():
    email = flask.request.form['email']
    conn = sqlite3.connect('data.db')
    for row in conn.execute(f"SELECT * FROM USER WHERE EMAIL = '{email}';"):
        s = json.loads(row[6])
        break
    for row in conn.execute(f"SELECT * FROM SUBMISSION WHERE TEACHER = '{email}';"):
        if (row[0] not in s):
            d = json.loads(row[5])
            assignmentid = row[0]
            timestamp = str(datetime.fromtimestamp(int(row[6])))
            student = conn.execute(f"SELECT NAME FROM USER WHERE EMAIL = '{row[1]}';").fetchone()
            subject = row[3]
            break
    conn.commit()
    conn.close()
    try:
        d
    except NameError:
        d = None
    if(d is None):
        return jsonify("<div style='text-align: center;'>No more assignments to check.</div>")
    for element in d:
        data = "<div><table><tr><th>Name: "+student[0]+"</th><th>Subject: "+subject+"</th><th>TIMESTAMP: "+timestamp+"</th></tr></table></div>"
        q = element.split(",")
        if(len(q) == 3):
            data = data + '''<div class="typecode"><label>''' + q[0] + '''</label> <textarea form ="assignmentform" rows="10" cols="90" id="question" disabled>''' + \
                q[1] + '''</textarea><textarea form ="assignmentform" rows="2" cols="90" id="answer" disabled>''' + \
                q[2] + '''</textarea></div>'''
        else:
            data = data + '''<div class="document"><label>''' + \
                q[0] + '''</label><div><a style="padding-bottom: 10px;" target="_blank" href="/uploads/''' + \
                q[1] + '''">View Document</a></div></div>'''
    data = data + '<h3>Add Score:</h3>'
    data = data + '<input type="number" id="score1" min="0" value="0"><input type="number" id="score2" min="0" value="0"><input type="number" id="score3" min="0" value="0"><input type="number" id="score4" min="0" value="0"><input type="number" id="score5" min="0" value="0"><input disabled type="number" id="totalscore" value="0">'
    data = data + '<input form="assignmentform" type="submit" value="Grade Assignment">'
    data = data + '''<span id="assignmentid" style="display:none;">''' + \
        assignmentid + '''</span>'''
    return jsonify(data)


@app.route('/submitevaluation', methods=['POST'])
def submitevaluation():
    assignmentid = flask.request.form['assignmentid']
    score = flask.request.form['score']
    email = flask.request.form['email']
    conn = sqlite3.connect('data.db')
    conn.execute(f"UPDATE SUBMISSION SET SCORE = '{score}' WHERE ID = '{assignmentid}';")
    conn.commit()
    conn.close()
    conn = sqlite3.connect('data.db')
    for row in conn.execute(f"SELECT * FROM USER WHERE email = '{email}';"):
        s = json.loads(row[6])
        break
    s.append(assignmentid)
    conn.execute(f"UPDATE USER SET STORAGE = '{json.dumps(s)}';")
    conn.commit()
    conn.close()
    return "1"


@app.route('/studentreport')
def studentreport():
    return flask.render_template('studentreport.html')


@app.route('/studentreportrender', methods=['POST'])
def studentreportrender():
    email = flask.request.form['email']
    conn = sqlite3.connect('data.db')
    ##query = f"SELECT SUBJECT, SUM (SCORE) FROM SUBMISSION WHERE STUDENT='{email}' GROUP BY SUBJECT;"
    query = f"SELECT ID, SUBJECT, SCORE FROM SUBMISSION WHERE STUDENT='{email}';"
    df = pd.read_sql_query(query, conn)
    df.columns = ['ID', 'SUBJECT', 'SCORE']
    conn.close()
    return jsonify(df.to_html(index=False))


@app.route('/teacherreport')
def teacherreport():
    return flask.render_template('teacherreport.html')


@app.route('/teacherreportrender', methods=['POST'])
def teacherreportrender():
    email = flask.request.form['email']
    subject = flask.request.form['subject']
    classgroup = flask.request.form['classgroup']
    conn = sqlite3.connect('data.db')
    query = f"SELECT ID, STUDENT, SCORE FROM SUBMISSION WHERE TEACHER='{email}' AND SUBJECT='{subject}' AND CLASSGROUP='{classgroup}';"
    df = pd.read_sql_query(query, conn)
    df.columns = ['ID', 'STUDENT', 'SCORE']
    conn.close()
    return jsonify(df.to_html(index=False))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
