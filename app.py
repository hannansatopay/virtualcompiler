import flask
import os
from flask import jsonify
import random
import time
import sqlite3
import sys
from werkzeug import secure_filename
import json
import subprocess
from flask import url_for
from os.path import join, dirname, realpath
from flask import send_from_directory

UPLOAD_FOLDER = join(dirname(realpath(__file__)), 'static/uploads/')

app = flask.Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
port = int(os.getenv("PORT", 9099))

@app.route('/')
def home():
	return flask.render_template('login.html')

@app.route('/login', methods= ['POST'])
def login():
        email = flask.request.form['email']
        password = flask.request.form['password']
        conn = sqlite3.connect('data.db')
        for row in conn.execute(f"SELECT * FROM USER WHERE email = '{email}';"):
            variable = row[1]
            role = row[2]
            if (variable == password):
                    variable = 1
                    break
            else:
                    variable = 0
                    break
        else:
            variable = -1
        conn.commit()
        conn.close()
        return jsonify(data = variable, role = role)

@app.route('/create', methods= ['POST'])
def create():
        email = flask.request.form['email']
        name = flask.request.form['name']
        password = flask.request.form['password']
        semester = flask.request.form['semester']
        conn = sqlite3.connect('data.db')
        conn.execute(f"INSERT INTO USER (EMAIL, NAME, PASSWORD, SEMESTER) VALUES ('{email}', '{name}', '{password}', '{semester}');")
        conn.commit()
        conn.close()
        return "Added"

@app.route('/updatepassword', methods= ['POST'])
def updatepassword():
        email = flask.request.form['email']
        password = flask.request.form['password']
        conn = sqlite3.connect('data.db')
        conn.execute(f"UPDATE USER SET PASSWORD = '{password}';")
        conn.commit()
        conn.close()
        return "Updated Password"

@app.route('/adduser')
def adduser():
	return flask.render_template('adduser.html')

@app.route('/addassignment')
def addassignment():
	return flask.render_template('addassignment.html')

@app.route('/dashboard')
def dashboard():
	return flask.render_template('dashboard.html')

@app.route('/fetchdashboard', methods= ['POST'])
def fetchdashboard():
	semester = flask.request.form['semester']
	email = flask.request.form['email']
	conn = sqlite3.connect('data.db')
	for row in conn.execute(f"SELECT * FROM USER WHERE email = '{email}';"):
		s = json.loads(row[5])
		break
	for row in conn.execute(f"SELECT * FROM ASSIGNMENT WHERE semester = '{semester}';"):
		if (row[0] not in s):
			d = json.loads(row[4])
			break
	conn.commit()
	conn.close()
	data = ""
	for element in d:
		if element[1] == "java" or element[1] == "c" or element[1] == "cpp" or element[1] == "python":
			data = data + '''<div class="typecode"><label>'''+element[0]+" ("+element[1]+")"+'''</label> <textarea form ="assignmentform" rows="10" cols="90" id="question"></textarea><button type="button" id="run">Run</button><textarea form ="assignmentform" rows="2" cols="90" id="answer" disabled></textarea></div>'''
		else:
			data = data + '''<div class="document"><label>'''+element[0]+'''</label> <input id="fileinput" form ="assignmentform" type="file" name="file" style="padding-bottom: 10px;"/></div>'''
	return jsonify(data)

@app.route('/createassignment', methods= ['POST'])
def createassignment():
    teacher = flask.request.form['teacher']
    semester = flask.request.form['semester']
    subject = flask.request.form['subject']
    data = flask.request.form['storage']
    id = ''.join(random.choice('0123456789ABCDEF') for i in range(16))
    conn = sqlite3.connect('data.db')
    conn.execute(f"INSERT INTO ASSIGNMENT (ID, TEACHER, SEMESTER, SUBJECT, STORAGE) VALUES ('{id}', '{teacher}', '{semester}', '{subject}', '{data}');")
    conn.commit()
    conn.close()
    return "1"

@app.route('/profile')
def profile():
	return flask.render_template('profile.html')

@app.route('/runcode', methods= ['POST'])
def runcode():
	code = flask.request.form['code']
	f = open("demo.py","w+")
	f.write(code)
	f.close()
	command = subprocess.run(["python","demo.py"], shell=True, stdout=subprocess.PIPE, text=True)
	return str(command.stdout)

@app.route('/upload')
def upload_file():
   return flask.render_template('upload.html')

@app.route('/submitassignment', methods = ['POST'])
def submitassignment():
	question = flask.request.form.getlist("question")
    conn = sqlite3.connect('data.db')
    #conn.execute(f"INSERT INTO SUBMISSION (ID, STUDENT, TEACHER, SUBJECT, STORAGE, SCORE) VALUES ('{id}', '{teacher}', '{semester}', '{subject}', 0);")
    conn.commit()
    conn.close()
	#print(question, file=sys.stderr)
	files = flask.request.files.getlist("file")
	for file in files:
		filename = secure_filename(file.filename)
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		#print(url_for('uploaded_file', filename=filename),  file=sys.stderr)
	return "1"

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
