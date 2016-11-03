import datetime
import json
import os
import psycopg2 as dbapi2
import re

from flask import Flask
from flask import redirect
from flask import render_template
from flask.helpers import url_for

from flask import Blueprint, redirect, render_template, url_for
from flask import current_app, request

from passlib.apps import custom_app_context as pwd_context

app = Flask(__name__)

# User and Post classes, static for now
class User:
   fullName = "Unknown"
   userName = "noname"
   email = "nomail@nomail.com"

   def __init__(self, fullName, userName, eMail):
      self.fullName = fullName
      self.userName = userName
      self.email = eMail

class Post:
   id = -1
   userName = ""
   content = ""
   likes = 0

   def __init__(self, id, userName, content, likes):
      self.id = id
      self.userName = userName
      self.content = content
      self.likes = likes

currentUser = User("Mertcan","mcanyasakci","yasakci@itu.edu.tr")
post_01 = Post(25,"mcanyasakci","Lorem ipsum",0)

def get_elephantsql_dsn(vcap_services):
    """Returns the data source name for ElephantSQL."""
    parsed = json.loads(vcap_services)
    uri = parsed["elephantsql"][0]["credentials"]["uri"]
    match = re.match('postgres://(.*?):(.*?)@(.*?)(:(\d+))?/(.*)', uri)
    user, password, host, _, port, dbname = match.groups()
    dsn = """user='{}' password='{}' host='{}' port={}
             dbname='{}'""".format(user, password, host, port, dbname)
    return dsn

@app.route('/')
def home_page():
    now = datetime.datetime.now()
    return render_template('homepage.html', current_time=now.ctime())

@app.route('/initdb')
def initialize_database():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()

        query = """DROP TABLE IF EXISTS COUNTER CASCADE"""        #DROP TABLE COMMANDS
        cursor.execute(query)
        query=  """DROP TABLE IF EXISTS STUDENTBRANCHES_CASTING CASCADE """
        cursor.execute(query)
        query=  """DROP TABLE IF EXISTS  STUDENTBRANCHES CASCADE"""
        cursor.execute(query)
        query = """DROP TABLE IF EXISTS DEPARTMENTLIST CASCADE"""
        cursor.execute(query)
        query = """DROP TABLE IF EXISTS USERS CASCADE"""
        cursor.execute(query)
        query = """DROP TABLE IF EXISTS CRNLIST CASCADE"""
        cursor.execute(query)
        query = """DROP TABLE IF EXISTS CRNS CASCADE"""
        cursor.execute(query)
        query = """DROP TABLE IF EXISTS POSTLIST CASCADE"""
        cursor.execute(query)
        query = """DROP TABLE IF EXISTS POST CASCADE"""
        cursor.execute(query)
        query = """DROP TABLE IF EXISTS DEPARTMENTS CASCADE"""
        cursor.execute(query)

        query = """CREATE TABLE COUNTER (N INTEGER)"""            #COUNTER TABLE
        cursor.execute(query)

        query = """INSERT INTO COUNTER (N) VALUES (0)"""
        cursor.execute(query)


                                            #CRNS TABLE
        query = """CREATE TABLE CRNS (
                    CRN INTEGER PRIMARY KEY NOT NULL,
                    LECTURENAME VARCHAR(150),
                    LECTURERNAME VARCHAR(50))"""
        cursor.execute(query)

        query = """INSERT INTO CRNS (CRN, LECTURENAME, LECTURERNAME) VALUES (11909, 'Database Managament Systems', 'Hayri Turgut Uyar')"""
        cursor.execute(query)

                                            #USERS TABLE
        query = """CREATE TABLE USERS (
                    NAME VARCHAR(80) NOT NULL,
                    USERNAME VARCHAR(20) PRIMARY KEY,
                    MAIL VARCHAR(80) NOT NULL,
                    PASSWORD VARCHAR(20) NOT NULL)"""
        cursor.execute(query)

        query = """INSERT INTO USERS (NAME, USERNAME, MAIL, PASSWORD) VALUES ('Mertcan', 'mcanyasakci', 'yasakci@itu.edu.tr', 'leblebi')"""
        cursor.execute(query)

                                            #CRNLIST TABLE
        query = """CREATE TABLE CRNLIST (
                    USERNAME VARCHAR(20) REFERENCES USERS ON DELETE CASCADE,
                    CRN INTEGER REFERENCES CRNS(CRN),
                    PRIMARY KEY(USERNAME, CRN))"""
        cursor.execute(query)

        query = """INSERT INTO CRNLIST (USERNAME, CRN) VALUES ('mcanyasakci', 11909)"""
        cursor.execute(query)

                                            #POST TABLE
        query = """CREATE TABLE POST (
                    POSTID SERIAL PRIMARY KEY,
                    USERNAME VARCHAR(20) REFERENCES USERS ON DELETE CASCADE,
                    CONTENT VARCHAR(500) NOT NULL,
                    LIKES INT DEFAULT 0)"""
        cursor.execute(query)

        query = """INSERT INTO POST (POSTID, USERNAME, CONTENT, LIKES) VALUES (25, 'mcanyasakci', 'Lorem ipsum', 0 )"""
        cursor.execute(query)
        query = """INSERT INTO POST (POSTID, USERNAME, CONTENT, LIKES) VALUES (10, 'mcanyasakci', 'Lorem ipsum', 0 )"""
        cursor.execute(query)


                                            #POSTLIST TABLE
        query = """CREATE TABLE POSTLIST (
                    USERNAME VARCHAR(20) REFERENCES USERS ON DELETE CASCADE,
                    POSTID INTEGER,
                    PRIMARY KEY(USERNAME, POSTID))"""
        cursor.execute(query)

        query = """INSERT INTO POSTLIST (USERNAME, POSTID) VALUES ('mcanyasakci', 10)"""
        cursor.execute(query)


        query = """CREATE TABLE DEPARTMENTS (
                    FACULTYNO INTEGER PRIMARY KEY,
                    NAME VARCHAR(40))"""   #DEPARTMENTS TABLE
        cursor.execute(query)

        query = """INSERT INTO DEPARTMENTS (FACULTYNO, NAME) VALUES (01, 'Faculty of Civil Engineering')"""
        cursor.execute(query)

        query = """INSERT INTO DEPARTMENTS (FACULTYNO, NAME) VALUES (15, 'Faculty of Computer and Informatics')"""
        cursor.execute(query)

        query = """CREATE TABLE STUDENTBRANCHES(
                    ID SERIAL PRIMARY KEY,
                    NAME VARCHAR(20),
                    DESCRIPTION VARCHAR(50)
        ) """
        cursor.execute(query)

        query = """INSERT INTO STUDENTBRANCHES(NAME, DESCRIPTION) VALUES ('COMPUTER SOCIETY','lorem ipsum lorem ipsum') """
        cursor.execute(query)
        query = """CREATE TABLE STUDENTBRANCHES_CASTING(
                    STUDENTBRANCH_ID INTEGER,
                    PERSON_NAME VARCHAR(20),
                    UNIQUE(STUDENTBRANCH_ID, PERSON_NAME)

        ) """
        cursor.execute(query)
        query= """CREATE TABLE DEPARTMENTLIST (
                    USERNAME VARCHAR(20) PRIMARY KEY REFERENCES USERS ON DELETE CASCADE,
                    FACULTYNO INTEGER,
                    UNIQUE (USERNAME , FACULTYNO) )"""
        cursor.execute(query)
        query = """INSERT INTO DEPARTMENTLIST (USERNAME, FACULTYNO ) VALUES ('mcanyasakci', 15)"""
        cursor.execute(query)

        connection.commit()
    return redirect(url_for('home_page'))

@app.route('/count')
def counter_page():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()

        query = "UPDATE COUNTER SET N = N + 1"
        cursor.execute(query)
        connection.commit()

        query = "SELECT N FROM COUNTER"
        cursor.execute(query)
        count = cursor.fetchone()[0]
    return "This page was accessed %d times." % count

@app.route('/profile', methods=['GET', 'POST'])
def profile_page():
    if request.method == 'POST':
        if request.form['action'] == 'sendPost':
            postContent = request.form['postContent']
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()

                query = """INSERT INTO POST(USERNAME, CONTENT) VALUES('%s', '%s')""" %(currentUser.userName, postContent)
                cursor.execute(query)

                connection.commit()
            return render_template('post_cfg.html')
        else:
            return render_template('post_cfg.html')
    else:
        return render_template('profile_page.html')

@app.route('/post_cfg', methods=['GET', 'POST'])
def post_cfg():
    if request.method == 'POST':
        if request.form['action'] == 'updatePost':
            postContent = request.form['postContent']
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()

                query = """UPDATE POST SET CONTENT='%s' WHERE (POSTID='%s')""" %(postContent, post_01.id)

                cursor.execute(query)

                connection.commit()
            return render_template('post_cfg.html', messageU="Updated post to %s" %(postContent))
        elif request.form['action'] == 'deletePost':
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()

                query = """DELETE FROM POST WHERE ( POSTID='%d' )""" %(post_01.id)
                cursor.execute(query)

                connection.commit()
            return render_template('post_cfg.html')
        elif request.form['action'] == 'searchPost':
            postContent=request.form['search-content']
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()

                query = """SELECT * FROM POST WHERE ( CONTENT='%s' )""" %(postContent)
                cursor.execute(query)

                datas=cursor.fetchall()
                connection.commit()
            return render_template('post_cfg.html', result=datas)
        else:
            return render_template('post_cfg.html')
    else:
        return render_template('post_cfg.html')

@app.route('/branches', methods=['GET', 'POST'])
def student_branches():
    if request.method =='POST':

        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            if request.form['action'] == 'update':
                branch_name = request.form['branch-name']
                new_branch_name = request.form['new-branch-name']
                branch_desc = request.form['branch-desc']
                query = """ UPDATE STUDENTBRANCHES SET NAME = '%s' , DESCRIPTION='%s' WHERE (NAME = '%s')"""%(new_branch_name, branch_desc, branch_name)

            elif request.form['action'] == 'delete':
                branch_name = request.form['delete-branch-name']
                query = """DELETE FROM STUDENTBRANCHES WHERE (NAME = '%s')"""%(branch_name)

            elif request.form['action'] == 'add':
                branch_name = request.form['add-branch-name']
                new_branch_desc = request.form['add-branch-desc']
                query = """INSERT INTO STUDENTBRANCHES(NAME, DESCRIPTION) VALUES ('%s','%s') """%(branch_name, new_branch_desc)
            elif request.form['action'] == 'search':
                 branch_name = request.form['search-branch-name']
                 query = """SELECT * FROM STUDENTBRANCHES WHERE (NAME = '%s')""" %(branch_name)
                 cursor.execute(query)
                 result = cursor.fetchall()
                 print(result)
                 connection.commit()
                 return render_template('student_branches.html', result=result)


            cursor.execute(query)
            connection.commit()


    return render_template('student_branches.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        nameSurname=request.form['inputNameSurname']
        username=request.form['inputUsername']
        email=request.form['inputEmail']
        password=request.form['inputPassword']

        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()

            query = """INSERT INTO USERS (NAME, USERNAME, MAIL, PASSWORD) VALUES ('%s', '%s', '%s', '%s')""" %(nameSurname,username,email,password)
            cursor.execute(query)

            connection.commit()
        return redirect(url_for('profile_page'))

    else:
        return render_template('signup.html')

@app.route('/signin')
def signin():
    return render_template('signin.html')

@app.route('/lectures', methods=['GET', 'POST'])
def lectures():
    if request.method == 'POST':
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            if request.form['action'] == 'addtoUser':
                userName=request.form['username']
                adding=request.form['addCRN']
                query = """INSERT INTO CRNLIST (USERNAME, CRN) VALUES ('%s', '%s')""" %(userName, adding)

            elif request.form['action'] == 'addtoLectures':
                adding=request.form['addCRN']
                lecturesName=request.form['LecturesName']
                lecturersName=request.form['LecturerSName']
                query = """INSERT INTO CRNS (CRN, LECTURENAME, LECTURERNAME) VALUES ('%s', '%s', '%s')""" %(adding, lecturesName, lecturersName)

            elif request.form['action'] == 'delete':
                userName=request.form['username']
                deleted=request.form['deleteCRN']
                query = """DELETE FROM CRNLIST WHERE ((USERNAME = '%s') AND (CRN='%s'))""" %(userName, deleted)
                cursor.execute(query)
                connection.commit()

            elif request.form['action'] == 'update':
                userName=request.form['username']
                oldcrn=request.form['oldCRN']
                newcrn=request.form['newCRN']
                query = """UPDATE CRNLIST SET CRN='%s' WHERE ((USERNAME='%s') AND (CRN='%s'))""" %(newcrn, userName, oldcrn)


            elif request.form['action'] == 'select':
                selected=request.form['selectCRN']
                query = """SELECT * FROM CRNS WHERE ( CRN='%s' )""" %(selected)
                cursor.execute(query)
                result=cursor.fetchall()
                print(result)
                connection.commit()
                return render_template('crn_edit.html', result=result)

        cursor.execute(query)
        connection.commit()
        return redirect(url_for('profile_page'))

    else:
        return render_template('crn_edit.html')

@app.route('/forgottenpassword')
def forgotten_password():
    return render_template('forgotten_password.html')
    pass
@app.route('/About')
def about_page():
    return render_template('about_page.html')
@app.route('/departments')
def departments():
    return render_template('departments.html')
@app.route('/privacypolicy')
def privacy_policy():
    return render_template('privacy_policy.html')

@app.route('/settings', methods=['GET', 'POST'])
def settings_page():
    if request.method == 'POST':
        if request.form['action'] == 'deleteUser':
            username=request.form['inputUsername']
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()

                query = """DELETE FROM USERS WHERE ( USERNAME='%s' )""" %(username)
                cursor.execute(query)

                connection.commit()
            return render_template('settings_page.html')
        elif request.form['action'] == 'updateUser':
            nameSurname=request.form['inputNameSurname']
            username=request.form['inputUsername']
            email=request.form['inputEmail']
            password=request.form['inputPassword']
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()

                query = """UPDATE USERS SET NAME='%s', MAIL='%s', PASSWORD='%s' WHERE (USERNAME='%s')""" %(nameSurname, email, password, username)
                cursor.execute(query)

                connection.commit()
            return render_template('settings_page.html', messageU="Updated user %s" %(username))
        elif request.form['action'] == 'searchUser':
            username=request.form['inputUsername']
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()

                query = """SELECT * FROM USERS WHERE ( USERNAME='%s' )""" %(username)
                cursor.execute(query)

                datas=cursor.fetchall()

                connection.commit()
            return render_template('settings_page.html', result=datas)

    else:
        return render_template('settings_page.html')

@app.route('/department_page', methods=['GET', 'POST'])
def department_page():
    if request.method == 'POST':
        if request.form['action'] == 'addFaculty':
            userName= request.form['inputUsername']
            faculty = request.form['selectFaculty']
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()

                query = """INSERT INTO DEPARTMENTLIST (USERNAME, FACULTYNO ) VALUES ('%s', '%s')""" %(userName,faculty)
                cursor.execute(query)
                test = 'test'
                connection.commit()

            return render_template('department_page.html', resultInsert=test)

        elif request.form['action'] == 'updateFaculty':
            userName= request.form['inputUsername']
            faculty = request.form['selectFaculty']
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()

                query = """UPDATE DEPARTMENTLIST SET FACULTYNO='%s' WHERE (USERNAME='%s')""" %(faculty,userName)
                cursor.execute(query)
                test='test'
                connection.commit()

            return render_template('department_page.html', resultUpdate=test)

        elif request.form['action'] == 'deleteFaculty':
            userName= request.form['inputUsername']
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()

                query = """DELETE FROM DEPARTMENTLIST WHERE ( USERNAME='%s' )""" %(userName)
                cursor.execute(query)
                test='test'
                connection.commit()

            return render_template('department_page.html', resultDelete=test)

        elif request.form['action'] == 'searchFaculty':
            userName= request.form['inputUsername']
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()

                query = """SELECT * FROM DEPARTMENTLIST WHERE ( USERNAME='%s' )""" %(userName)
                cursor.execute(query)
                datas=cursor.fetchall()

                connection.commit()
            return render_template('department_page.html', resultSearch=datas)

    else:

        return render_template('department_page.html')

if __name__ == '__main__':
    VCAP_APP_PORT = os.getenv('VCAP_APP_PORT')
    if VCAP_APP_PORT is not None:
        port, debug = int(VCAP_APP_PORT), False
    else:
        port, debug = 5000, True

    VCAP_SERVICES = os.getenv('VCAP_SERVICES')
    if VCAP_SERVICES is not None:
        app.config['dsn'] = get_elephantsql_dsn(VCAP_SERVICES)
    else:
        app.config['dsn'] = """user='vagrant' password='vagrant'
                               host='localhost' port=5432 dbname='itucsdb'"""

    app.run(host='0.0.0.0', port=port, debug=debug)
