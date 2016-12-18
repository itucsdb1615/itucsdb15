import datetime
import json
import os
import psycopg2 as dbapi2
import re

from flask import Flask
from flask import redirect
from flask import render_template
from flask.helpers import url_for

from flask import flash

from flask import Blueprint, redirect, render_template, url_for
from flask import current_app, request

from passlib.apps import custom_app_context as pwd_context

from branch_operations import site
from profile import *
from search import *
from faculty import *
from classes import *

#from user import get_user
from flask_login import LoginManager
from flask_login.utils import login_required, login_user, current_user,\
    logout_user
lm = LoginManager()

@lm.user_loader
def load_user(userName):
    return get_user(userName)

def get_user(user_id):
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()
        query = """SELECT * FROM USERS WHERE USERNAME = %s"""
        cursor.execute(query, [user_id])
        result = cursor.fetchall()
        password = result[0][3]
        user = User(result[0][0], result[0][1], result[0][2], result[0][3], result[0][4], result[0][5], result[0][6]) if password else None
#    if user is not None:
#        user.is_admin = user.username in current_app.config['ADMIN_USERS']
    return user
def create_app():
    app = Flask(__name__)
    app.register_blueprint(site)
    return app
app =create_app()
lm.init_app(app)
lm.login_view = 'signin'

from user import User #user model
from post import Post #post model

#hashed = pwd_context.encrypt('leblebi')
#currentUser = User('Mertcan', 'mcanyasakci', 'yasakci@itu.edu.tr', hashed)
#post_01 = Post(25,"mcanyasakci","Lorem ipsum",0)

def get_elephantsql_dsn(vcap_services):
    """Returns the data source name for ElephantSQL."""
    parsed = json.loads(vcap_services)
    uri = parsed["elephantsql"][0]["credentials"]["uri"]
    match = re.match('postgres://(.*?):(.*?)@(.*?)(:(\d+))?/(.*)', uri)
    user, password, host, _, port, dbname = match.groups()
    dsn = """user='{}' password='{}' host='{}' port={}
             dbname='{}'""".format(user, password, host, port, dbname)
    return dsn

#****
#    Simple and low level sing in is done
# It has many security vulnerabilities. It takes the email and password and
# it will check if the hashed password in the database will match the given password.
# If so, it will set the currentUser's information to new obtained ones
# Vulnerabilities:
#    currentUser is global variable and not private
#    it will always takes the hashed password from database
#    Unauthorized users can reach the different html files
#    Only one user can log in at once
#
# To Do:
#    Log out is not handled
#    if the email is not correct site will crash
#
# And many more
#****
@app.route('/', methods=['GET', 'POST'])
def home_page():
    now = datetime.datetime.now()
    if request.method == 'POST':
        email=request.form['inputEmail']
        password=request.form['inputPassword']

        #hashing the password
        hashed = pwd_context.encrypt(password)

        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT USERNAME FROM USERS WHERE MAIL = %s"""
            cursor.execute(query, [email])
            data = cursor.fetchall()
            connection.commit()

        user = get_user(data[0][0])
        if user is not None:
            if pwd_context.verify(password, user.password):
                login_user(user)
                #flash('You have logged in.')
                next_page = request.args.get('next', url_for('site.profile_page'))
                return redirect(next_page)
        #flash('Invalid credentials.')
    else:
        return render_template('homepage.html', current_time=now.ctime())

@app.route('/initdb')
def initialize_database():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()

        query = """DROP TABLE IF EXISTS COUNTER CASCADE"""        #DROP TABLE COMMANDS
        cursor.execute(query)
        query=  """DROP TABLE IF EXISTS STUDENTBRANCHES_CASTING CASCADE """
        cursor.execute(query)
        query=  """DROP TABLE IF EXISTS STUDENTBRANCHES CASCADE"""
        cursor.execute(query)
        query = """DROP TABLE IF EXISTS DEPARTMENTLIST CASCADE"""
        cursor.execute(query)
        query = """DROP TABLE IF EXISTS LOST CASCADE"""
        cursor.execute(query)
        query = """DROP TABLE IF EXISTS FOUND CASCADE"""
        cursor.execute(query)
        query = """DROP TABLE IF EXISTS USERS CASCADE"""
        cursor.execute(query)
        query = """DROP TABLE IF EXISTS CLASSES CASCADE"""
        cursor.execute(query)
        query = """DROP TABLE IF EXISTS CRNS CASCADE"""
        cursor.execute(query)
        query = """DROP TABLE IF EXISTS CLASSPOSTS CASCADE"""
        cursor.execute(query)
        query = """DROP TABLE IF EXISTS CLASSPOSTCONTENT CASCADE"""
        cursor.execute(query)
        query = """DROP TABLE IF EXISTS FEED CASCADE"""
        cursor.execute(query)
        query = """DROP TABLE IF EXISTS POST CASCADE"""
        cursor.execute(query)
        query = """DROP TABLE IF EXISTS FOLLOW CASCADE"""
        cursor.execute(query)
        query = """DROP TABLE IF EXISTS HOTTITLES CASCADE"""
        cursor.execute(query)
        query = """DROP TABLE IF EXISTS HOTTITLECAST CASCADE"""
        cursor.execute(query)
        query = """DROP TABLE IF EXISTS FACULTYFEED CASCADE"""
        cursor.execute(query)
        query = """DROP TABLE IF EXISTS DEPARTMENTS CASCADE"""
        cursor.execute(query)
        query = """DROP TABLE IF EXISTS BRANCHFEEDS CASCADE"""
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

        query = """INSERT INTO CRNS (CRN, LECTURENAME, LECTURERNAME) VALUES (11909, 'Database Management Systems', 'Hayri Turgut Uyar')"""
        cursor.execute(query)

                                            #USERS TABLE
        query = """CREATE TABLE USERS (
                    NAME VARCHAR(80) NOT NULL,
                    USERNAME VARCHAR(20) PRIMARY KEY,
                    MAIL VARCHAR(80) NOT NULL,
                    PASSWORD VARCHAR(120) NOT NULL,
                    DESCRIPTION VARCHAR(100) DEFAULT 'No information given.',
                    FOLLOWER_COUNT INTEGER DEFAULT 0,
                    FOLLOWING_COUNT INTEGER DEFAULT 0)"""
        cursor.execute(query)

        password = "leblebi"
        hashed = pwd_context.encrypt(password)
        query = """INSERT INTO USERS (NAME, USERNAME, MAIL, PASSWORD) VALUES ('Mertcan', 'mcanyasakci', 'yasakci@itu.edu.tr', %s)"""
        cursor.execute(query, [hashed])

        password = "deneme"
        hashed = pwd_context.encrypt(password)
        query = """INSERT INTO USERS (NAME, USERNAME, MAIL, PASSWORD) VALUES ('ismail', 'namdar', 'namdar@yahoo.com', %s)"""
        cursor.execute(query, [hashed])

        query = """CREATE TABLE LOST (
                    USERNAME VARCHAR (20) REFERENCES USERS ON DELETE CASCADE,
                    ITEMID SERIAL PRIMARY KEY,
                    NAME VARCHAR(80) NOT NULL,
                    DESCRIPTION VARCHAR(80) NOT NULL)"""
        cursor.execute(query)
        query = """CREATE TABLE FOUND (
                    USERNAME VARCHAR (20) REFERENCES USERS ON DELETE CASCADE,
                    ITEMID SERIAL PRIMARY KEY,
                    NAME VARCHAR(80) NOT NULL,
                    DESCRIPTION VARCHAR(80) NOT NULL)"""
        cursor.execute(query)

                                            #CLASSES TABLE
        query = """CREATE TABLE CLASSES (
                    CRN INTEGER REFERENCES CRNS(CRN),
                    USERNAME VARCHAR (20) REFERENCES USERS ON DELETE CASCADE,
                    PRIMARY KEY(CRN, USERNAME))"""
        cursor.execute(query)

        query = """INSERT INTO CLASSES (CRN, USERNAME) VALUES (11909, 'mcanyasakci')"""
        cursor.execute(query)

                                                    #CLASS POSTS' CONTENTS TABLE
        query = """CREATE TABLE CLASSPOSTCONTENT (
                    POSTID SERIAL PRIMARY KEY UNIQUE,
                    USERNAME VARCHAR (20) REFERENCES USERS ON DELETE CASCADE,
                    CONTENT VARCHAR(500) NOT NULL,
                    LIKES INT DEFAULT 0)"""
        cursor.execute(query)

        query = """INSERT INTO CLASSPOSTCONTENT(POSTID, USERNAME, CONTENT, LIKES) VALUES (0, 'mcanyasakci', 'hello camera', 0)"""
        cursor.execute(query)

                                            #CLASS POSTS TABLE
        query = """CREATE TABLE CLASSPOSTS (
                    GROUPID INTEGER REFERENCES CRNS(CRN),
                    USERNAME VARCHAR (20) REFERENCES USERS ON DELETE CASCADE,
                    POSTID INTEGER PRIMARY KEY REFERENCES CLASSPOSTCONTENT(POSTID))"""
        cursor.execute(query)

        query = """INSERT INTO CLASSPOSTS(GROUPID, USERNAME, POSTID) VALUES (11909, 'mcanyasakci', 0)"""
        cursor.execute(query)


                                            #POST TABLE
        query = """CREATE TABLE POST (
                    POSTID SERIAL PRIMARY KEY,
                    USERNAME VARCHAR(20) REFERENCES USERS(USERNAME) ON DELETE CASCADE,
                    CONTENT VARCHAR(500) NOT NULL,
                    LIKES INT DEFAULT 0)"""
        cursor.execute(query)

        query = """INSERT INTO POST (POSTID, USERNAME, CONTENT, LIKES) VALUES (25, 'mcanyasakci', 'Lorem ipsum', 0 )"""
        cursor.execute(query)
        query = """INSERT INTO POST (POSTID, USERNAME, CONTENT, LIKES) VALUES (10, 'mcanyasakci', 'deneme', 0 )"""
        cursor.execute(query)


                                            #POSTLIST TABLE
        query = """CREATE TABLE FEED (
                    USERNAME VARCHAR(20) REFERENCES USERS(USERNAME) ON DELETE CASCADE,
                    POSTID INTEGER REFERENCES POST(POSTID) ON DELETE CASCADE ,
                    PRIMARY KEY(USERNAME, POSTID))"""
        cursor.execute(query)

        query = """INSERT INTO FEED (USERNAME, POSTID) VALUES ('mcanyasakci', 10)"""
        cursor.execute(query)

        query = """INSERT INTO FEED (USERNAME, POSTID) VALUES ('mcanyasakci', 25)"""
        cursor.execute(query)

        query = """CREATE TABLE FACULTYFEED (
                    SENDER VARCHAR(20) REFERENCES USERS(USERNAME) ON DELETE CASCADE,
                    READER VARCHAR(20) REFERENCES USERS(USERNAME) ON DELETE CASCADE,
                    POSTID INTEGER REFERENCES POST(POSTID) ON DELETE CASCADE ,
                    PRIMARY KEY(READER, POSTID))"""
        cursor.execute(query)

        query = """CREATE TABLE DEPARTMENTS (
                    FACULTYNO INTEGER PRIMARY KEY,
                    NAME VARCHAR(80))"""   #DEPARTMENTS TABLE
        cursor.execute(query)

        query = """INSERT INTO DEPARTMENTS (FACULTYNO, NAME) VALUES (01, 'Faculty of Civil Engineering')"""
        cursor.execute(query)

        query = """INSERT INTO DEPARTMENTS (FACULTYNO, NAME) VALUES (15, 'Faculty of Computer and Informatics')"""
        cursor.execute(query)
        query = """INSERT INTO DEPARTMENTS (FACULTYNO, NAME) VALUES (02, 'Faculty of Architecture')"""
        cursor.execute(query)
        query = """INSERT INTO DEPARTMENTS (FACULTYNO, NAME) VALUES (03, 'Faculty of Mechanical Engineering')"""
        cursor.execute(query)

        query = """INSERT INTO DEPARTMENTS (FACULTYNO, NAME) VALUES (04, 'Faculty of Electrical and Electronics Engineering')"""
        cursor.execute(query)

        query = """INSERT INTO DEPARTMENTS (FACULTYNO, NAME) VALUES (05, 'Faculty of Mines')"""
        cursor.execute(query)
        query = """INSERT INTO DEPARTMENTS (FACULTYNO, NAME) VALUES (06, 'Faculty of Chemical and Metallurgical Engineering')"""
        cursor.execute(query)

        query = """INSERT INTO DEPARTMENTS (FACULTYNO, NAME) VALUES (07, 'Faculty of Management')"""
        cursor.execute(query)
        query = """INSERT INTO DEPARTMENTS (FACULTYNO, NAME) VALUES (08, 'Faculty of Naval Architecture and Ocean Engineering')"""
        cursor.execute(query)

        query = """INSERT INTO DEPARTMENTS (FACULTYNO, NAME) VALUES (09, 'Faculty of Science and Letters')"""
        cursor.execute(query)
        query = """INSERT INTO DEPARTMENTS (FACULTYNO, NAME) VALUES (10, 'Faculty of Aeronautics and Astronautics')"""
        cursor.execute(query)

        query = """INSERT INTO DEPARTMENTS (FACULTYNO, NAME) VALUES (11, 'Turkish Music State Conservatory')"""
        cursor.execute(query)
        query = """INSERT INTO DEPARTMENTS (FACULTYNO, NAME) VALUES (12, 'Maritime Faculty')"""
        cursor.execute(query)

        query = """INSERT INTO DEPARTMENTS (FACULTYNO, NAME) VALUES (13, 'Faculty of Textile Technologies and Design ')"""
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
                    STUDENTBRANCH_ID INTEGER REFERENCES STUDENTBRANCHES(ID),
                    PERSON_NAME VARCHAR(20) REFERENCES USERS(USERNAME) ON DELETE CASCADE,
                    UNIQUE(STUDENTBRANCH_ID, PERSON_NAME)
        ) """
        cursor.execute(query)

        query = """INSERT INTO STUDENTBRANCHES_CASTING(STUDENTBRANCH_ID, PERSON_NAME) VALUES (1,'mcanyasakci') """
        cursor.execute(query)

        query= """CREATE TABLE DEPARTMENTLIST (
                    USERNAME VARCHAR(20) PRIMARY KEY REFERENCES USERS(USERNAME) ON DELETE CASCADE,
                    FACULTYNO INTEGER REFERENCES DEPARTMENTS(FACULTYNO) ,
                    UNIQUE (USERNAME , FACULTYNO) )"""
        cursor.execute(query)
        query = """INSERT INTO DEPARTMENTLIST (USERNAME, FACULTYNO ) VALUES ('mcanyasakci', 15)"""
        cursor.execute(query)

        query= """CREATE TABLE FOLLOW (
                    ID SERIAL PRIMARY KEY,
                    FOLLOWER VARCHAR(20) REFERENCES USERS(USERNAME),
                    FOLLOWING VARCHAR(20) REFERENCES USERS(USERNAME),
                    UNIQUE(FOLLOWER, FOLLOWING))"""
        cursor.execute(query)

        query= """CREATE TABLE HOTTITLES (
                    ID SERIAL PRIMARY KEY,
                    TOPIC VARCHAR(20) NOT NULL,
                    USERNAME VARCHAR(20) REFERENCES USERS(USERNAME),
                    UNIQUE(TOPIC) )"""
        cursor.execute(query)

        query= """CREATE TABLE HOTTITLECAST (
                    ID SERIAL PRIMARY KEY,
                    HOTTITLEID INTEGER REFERENCES HOTTITLES(ID),
                    POSTID INTEGER REFERENCES POST(POSTID) ON DELETE CASCADE,
                    UNIQUE(HOTTITLEID, POSTID) )"""
        cursor.execute(query)

        query = """INSERT INTO HOTTITLES ( TOPIC, USERNAME ) VALUES ('beeHive is awesome!', 'namdar')"""
        cursor.execute(query)
        query = """INSERT INTO HOTTITLES ( TOPIC, USERNAME ) VALUES ('Database', 'namdar')"""
        cursor.execute(query)
        query = """ 
                CREATE TABLE BRANCHFEEDS(
                ID SERIAL PRIMARY KEY, 
                BRANCH_ID INTEGER REFERENCES STUDENTBRANCHES(ID),
                USER_NAME VARCHAR(20) REFERENCES USERS(USERNAME),
                CONTENT VARCHAR(200) NOT NULL
                )
                """
        cursor.execute(query)

        query = """ INSERT INTO
                     BRANCHFEEDS (BRANCH_ID, USER_NAME,CONTENT) VALUES 
                     (1,'namdar', 'This is awesome branch, keep in touch for news !!!') """
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

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        nameSurname=request.form['inputNameSurname']
        username=request.form['inputUsername']
        email=request.form['inputEmail']
        password=request.form['inputPassword']

        #hashing the password
        hashed = pwd_context.encrypt(password)

        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()

            query = """INSERT INTO USERS (NAME, USERNAME, MAIL, PASSWORD) VALUES ('%s', '%s', '%s', '%s')""" %(nameSurname,username,email,hashed)
            cursor.execute(query)

            user = User(nameSurname, username,email,hashed,"No information given.",0,0)


            connection.commit()

            login_user(user)
            #flash('You have logged in.')
            #next_page = request.args.get('next', url_for('profile_page'))
            #    (next_page)
        return redirect(url_for('site.profile_page'))

    else:
        return render_template('signup.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email=request.form['inputEmail']
        password=request.form['inputPassword']

        #hashing the password
        hashed = pwd_context.encrypt(password)

        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT USERNAME FROM USERS WHERE MAIL = %s"""
            cursor.execute(query, [email])
            data = cursor.fetchall()
            connection.commit()

        user = get_user(data[0][0])
        if user is not None:
            if pwd_context.verify(password, user.password):
                login_user(user)
                #flash('You have logged in.')
                next_page = request.args.get('next', url_for('site.profile_page'))
                return redirect(next_page)
        #flash('Invalid credentials.')
        next = flask.request.args.get('next')
        return flask.redirect(next or url_for('site.profile_page'))
    else:
        return render_template('signin.html')


@app.route('/forgottenpassword')
def forgotten_password():
    return render_template('forgotten_password.html')
    pass
@app.route('/About')
def about_page():
    return render_template('about_page.html')
@app.route('/departments')
@login_required
def departments():
    return render_template('departments.html')
@app.route('/privacypolicy')
def privacy_policy():
    return render_template('privacy_policy.html')

@app.route('/titles/<titleid>', methods=['GET', 'POST'])
@login_required
def title_cfg(titleid):
    if request.method == 'POST':
        if request.form['action'] == 'sendPost':
            postContent = request.form['postContent']
            username = current_user.userName
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()

                query = """INSERT INTO POST(USERNAME, CONTENT) VALUES(%s, %s)"""
                cursor.execute(query,(username, postContent))

                query = """SELECT POSTID FROM POST WHERE (USERNAME = %s and CONTENT = %s)"""
                cursor.execute(query,(username, postContent))
                postid = cursor.fetchall()

                query = """INSERT INTO FEED(USERNAME, POSTID) VALUES(%s, %s)"""
                cursor.execute(query,(username, postid[0][0]))

                query = """INSERT INTO HOTTITLECAST(HOTTITLEID, POSTID) VALUES(%s, %s)"""
                cursor.execute(query,(titleid[0], postid[0][0]))
                print(postid[0][0])
                print(titleid)
                connection.commit()
            return redirect(url_for('title_cfg', titleid = titleid))
        elif request.form['action'] == 'updateTitle':
            updateContent = request.form['titleUpdate']
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()

                query = """UPDATE HOTTITLES SET TOPIC = %s WHERE ID = %s"""
                cursor.execute(query,(updateContent, titleid[0]))

                connection.commit()
            return redirect(url_for('title_cfg', titleid = titleid))
        elif request.form['action'] == 'deleteTitle':
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()

                query = """DELETE FROM HOTTITLECAST WHERE HOTTITLEID = %s"""
                cursor.execute(query, [titleid[0]])

                query = """DELETE FROM HOTTITLES WHERE ID = %s"""
                cursor.execute(query, [titleid[0]])

                connection.commit()
            return redirect(url_for('site.profile_page'))
        else:
            return render_template('title_cfg.html', titleid = titleid)
    else:
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()

            query = """SELECT POSTID FROM HOTTITLECAST WHERE HOTTITLEID = %s"""
            cursor.execute(query, titleid[0])

            postids = cursor.fetchall()
            print(postids)
            query = """SELECT * FROM HOTTITLES WHERE ID = %s"""
            cursor.execute(query, titleid[0])
            print(titleid[0])
            titles = cursor.fetchall()
            posts = []
            for id in postids:
                query = """SELECT * FROM POST WHERE POSTID = %s"""
                cursor.execute(query, [id[0]])
                posts.append(cursor.fetchall())
                print([id[0]])

            print(posts)
            connection.commit()
        return render_template('title_cfg.html', posts = posts, user = current_user, titles = titles)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home_page'))

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings_page():
    if request.method == 'POST':
        if request.form['action'] == 'deleteUser':
            username=current_user.userName
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()

                query = """DELETE FROM USERS WHERE ( USERNAME=%s )"""
                cursor.execute(query, ([username]))

                query = """SELECT * FROM LOST WHERE ( USERNAME=%s )"""
                cursor.execute(query, ([current_user.userName]))
                items=cursor.fetchall()

                connection.commit()
            logout_user()
            return redirect(url_for('home_page'))
        elif request.form['action'] == 'updateUser':
            nameSurname=request.form['inputNameSurname']
            username=current_user.userName
            email=request.form['inputEmail']
            password=request.form['inputPassword']
            hashed = pwd_context.encrypt(password)

            execute=[]
            query="""UPDATE USERS SET """
            if len(nameSurname)!=0:
                current_user.fullName=nameSurname
                execute+=[str(nameSurname)]
                query+="""NAME=%s"""
            if len(email)!=0:
                current_user.email=email
                execute+=[str(email)]
                if len(nameSurname)!=0:
                    query+=""", """
                query+="""MAIL=%s"""
            if len(password)!=0:
                current_user.password=hashed
                execute+=[str(hashed)]
                if len(nameSurname)!=0 or len(email)!=0:
                    query+=""", """
                query+="""PASSWORD=%s"""
            if len(nameSurname)==0 and len(email)==0 and len(password)==0:
                return render_template('settings_page.html', messageU="Could not update.")

            query+=""" WHERE (USERNAME=%s)"""

            execute+=[username]

            print(execute)
            print(query)

            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()

                #query = """UPDATE USERS SET NAME=%s, MAIL=%s, PASSWORD=%s WHERE (USERNAME=%s)"""
                cursor.execute(query, execute)

                connection.commit()
            return render_template('settings_page.html', messageU="Updated user %s" %(username))
        elif request.form['action'] == 'searchUser':
            username=request.form['inputUsername']
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()

                query = """SELECT * FROM USERS WHERE ( USERNAME=%s )"""
                cursor.execute(query, [username])

                datas=cursor.fetchall()

                query = """SELECT * FROM LOST WHERE ( USERNAME=%s )"""
                cursor.execute(query, ([current_user.userName]))
                items=cursor.fetchall()

                connection.commit()
            return render_template('settings_page.html', result=datas, items=items)

    else:
        return render_template('settings_page.html')

@app.route('/lost_found', methods=['GET', 'POST'])
@login_required
def lostfound_page():
    if request.method == 'POST':
        if request.form['action'] == 'createLostItem':
            username=current_user.userName
            itemName=request.form['inputItemName']
            description=request.form['inputDescription']
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()

                query = """INSERT INTO LOST (USERNAME, NAME, DESCRIPTION) VALUES (%s, %s, %s)"""
                cursor.execute(query, (username,itemName,description))

                connection.commit()
            return redirect(url_for('lostfound_page'))
        elif request.form['action'] == 'deleteLostItem':
            username=current_user.userName
            value = request.form.get('itemSelected')
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()

                query = """DELETE FROM LOST WHERE ( USERNAME=%s AND ITEMID=%s )"""
                cursor.execute(query, (username, value))

                connection.commit()
            return redirect(url_for('lostfound_page'))
        elif request.form['action'] == 'updateLostItem':
            username=current_user.userName
            value = request.form.get('itemSelected')
            itemName=request.form['inputItemName']
            description=request.form['inputDescription']
            go=0
            if len(itemName)==0 and len(description)==0:
                go=0
            elif len(itemName)==0:
                go=1
            elif len(description)==0:
                go=2

            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()

                if go==1:
                    print(str(go) + "girdi")
                    query = """UPDATE LOST SET DESCRIPTION=%s WHERE (USERNAME=%s AND ITEMID=%s)"""
                    cursor.execute(query, (description, username, value))
                elif go==2:
                    print(str(go) + "girdi")
                    query = """UPDATE LOST SET NAME=%s WHERE (USERNAME=%s AND ITEMID=%s)"""
                    cursor.execute(query, (itemName, username, value))
                else:
                    query = """UPDATE LOST SET NAME=%s, DESCRIPTION=%s WHERE (USERNAME=%s AND ITEMID=%s)"""
                    cursor.execute(query, (itemName, description, username, value))


                connection.commit()
            return redirect(url_for('lostfound_page'))
        elif request.form['action'] == 'createFoundItem':
            username=current_user.userName
            itemName=request.form['inputItemName']
            description=request.form['inputDescription']
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()

                query = """INSERT INTO FOUND (USERNAME, NAME, DESCRIPTION) VALUES (%s, %s, %s)"""
                cursor.execute(query, (username,itemName,description))

                connection.commit()
            return redirect(url_for('lostfound_page'))
        elif request.form['action'] == 'deleteFoundItem':
            username=current_user.userName
            value = request.form.get('itemSelected')
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()

                query = """DELETE FROM FOUND WHERE ( USERNAME=%s AND ITEMID=%s )"""
                cursor.execute(query, (username, value))

                connection.commit()
            return redirect(url_for('lostfound_page'))
        elif request.form['action'] == 'updateFoundItem':
            username=current_user.userName
            value = request.form.get('itemSelected')
            itemName=request.form['inputItemName']
            description=request.form['inputDescription']
            go=0
            if len(itemName)==0 and len(description)==0:
                go=0
            elif len(itemName)==0:
                go=1
            elif len(description)==0:
                go=2

            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()

                if go==1:
                    print(str(go) + "girdi")
                    query = """UPDATE FOUND SET DESCRIPTION=%s WHERE (USERNAME=%s AND ITEMID=%s)"""
                    cursor.execute(query, (description, username, value))
                elif go==2:
                    print(str(go) + "girdi")
                    query = """UPDATE FOUND SET NAME=%s WHERE (USERNAME=%s AND ITEMID=%s)"""
                    cursor.execute(query, (itemName, username, value))
                else:
                    query = """UPDATE FOUND SET NAME=%s, DESCRIPTION=%s WHERE (USERNAME=%s AND ITEMID=%s)"""
                    cursor.execute(query, (itemName, description, username, value))


                connection.commit()
            return redirect(url_for('lostfound_page'))
    else:
        username=current_user.userName
        with dbapi2.connect(app.config['dsn']) as connection:
            cursor = connection.cursor()

            query = """SELECT * FROM LOST"""
            cursor.execute(query)
            lostitems=cursor.fetchall()

            query = """SELECT * FROM LOST WHERE( USERNAME = %s )"""
            cursor.execute(query, [username])
            userlostitems=cursor.fetchall()

            query = """SELECT * FROM FOUND"""
            cursor.execute(query)
            founditems=cursor.fetchall()

            query = """SELECT * FROM FOUND WHERE( USERNAME = %s )"""
            cursor.execute(query, [username])
            userfounditems=cursor.fetchall()

            connection.commit()
        return render_template('lost_found.html', lostitems=lostitems, userlostitems=userlostitems, founditems=founditems, userfounditems=userfounditems)


@app.route('/department_page', methods=['GET', 'POST'])
@login_required
def department_page():
    if request.method == 'POST':
        if request.form['action'] == 'addFaculty':
            userName= request.form['inputUsername']
            faculty = request.form['selectFaculty']
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()

                query = """INSERT INTO DEPARTMENTLIST (USERNAME, FACULTYNO ) VALUES (%s, %s)"""
                cursor.execute(query, (userName,faculty))
                test = 'test'
                connection.commit()

            return render_template('department_page.html', resultInsert=test)

        elif request.form['action'] == 'updateFaculty':
            userName= request.form['inputUsername']
            faculty = request.form['selectFaculty']
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()

                query = """UPDATE DEPARTMENTLIST SET FACULTYNO=%s WHERE (USERNAME=%s)"""
                cursor.execute(query, (faculty,userName))
                test='test'
                connection.commit()

            return render_template('department_page.html', resultUpdate=test)

        elif request.form['action'] == 'deleteFaculty':
            userName= request.form['inputUsername']
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()

                query = """DELETE FROM DEPARTMENTLIST WHERE ( USERNAME=%s )"""
                cursor.execute(query,[userName])
                test='test'
                connection.commit()

            return render_template('department_page.html', resultDelete=test)

        elif request.form['action'] == 'searchFaculty':
            userName= request.form['inputUsername']
            with dbapi2.connect(app.config['dsn']) as connection:
                cursor = connection.cursor()

                query = """SELECT * FROM DEPARTMENTLIST WHERE ( USERNAME=%s )"""
                cursor.execute(query, [userName])
                datas=cursor.fetchall()

                query = """SELECT D.NAME FROM DEPARTMENTS AS D INNER JOIN DEPARTMENTLIST AS L ON D.FACULTYNO =L.FACULTYNO  WHERE L.USERNAME = %s"""
                cursor.execute(query, [userName])
                faculty = cursor.fetchall()

                connection.commit()
            return render_template('department_page.html', resultSearch=datas ,faculty=faculty)

    else:

        return render_template('department_page.html')

if __name__ == '__main__':
    app.secret_key = 'super secret key'
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
