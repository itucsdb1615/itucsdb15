from flask import Blueprint, render_template
from flask_login import LoginManager
from flask_login.utils import login_required, login_user, current_user
from flask import current_app, request
from jinja2 import TemplateNotFound
import psycopg2 as dbapi2
import flask

from flask import Flask
from flask import redirect
from flask import render_template
from flask.helpers import url_for

from branch_operations import site


@site.route('/classes', methods=['GET', 'POST'])
@login_required
def classes():
    if request.method == 'GET':
        with dbapi2.connect(flask.current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            username = current_user.userName

            query="""SELECT * FROM CRNS AS C INNER JOIN CLASSES AS D ON C.CRN=D.CRN WHERE D.USERNAME=%s"""
            cursor.execute(query, [username])
            myCRNs = cursor.fetchall()

            connection.commit()
        return render_template('classes.html', user = current_user, lectures=myCRNs)


    elif request.method == 'POST':
        with dbapi2.connect(flask.current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            if request.form['action'] == 'add':
                username = current_user.userName
                crn=request.form['CRN']
                lectureName=request.form['lecture']
                lecturerName=request.form['lecturer']
                query = """INSERT INTO CRNS (CRN, LECTURENAME, LECTURERNAME) VALUES (%s, %s,%s)"""
                cursor.execute(query,(crn, lectureName, lecturerName))
                textMessage = 'Lecture is successfully added to current lectures'

            elif request.form['action'] == 'delete':
                username = current_user.userName
                delete=request.form['CRN']
                query = """DELETE FROM CRNS WHERE (CRN=%s)"""
                cursor.execute(query,[delete])
                textMessage = 'Lecture is successfully deleted'

            elif request.form['action'] == 'update':
                username = current_user.userName
                update=request.form['CRN']
                lecturename=request.form['nlecture']
                lecturername=request.form['nlecturer']
                query = """UPDATE CRNS SET LECTURENAME=%s WHERE CRN=%s"""
                cursor.execute(query,(lecturename, update))
                query = """UPDATE CRNS SET LECTURERNAME=%s WHERE CRN=%s"""
                cursor.execute(query,(lecturername, update))
                textMessage = 'Lecture information is successfully updated'

            elif request.form['action'] == 'enter':
                username = current_user.userName
                add=request.form['CRN']
                query = """INSERT INTO CLASSES (CRN, USERNAME) VALUES (%s, %s)"""
                cursor.execute(query,(add, username))
                textMessage = 'Have a good time in your new class!'

            elif request.form['action'] == 'leave':
                username = current_user.userName
                left=request.form['CRN']
                query = """DELETE FROM CLASSES WHERE (CRN=%s AND USERNAME=%s)"""
                cursor.execute(query,(left, username))
                textMessage = 'You successfully left the class'

            elif request.form['action'] == 'updateClass':
                username = current_user.userName
                oldcrn=request.form['oldCRN']
                newcrn=request.form['newCRN']
                query = """UPDATE CLASSES SET CRN=%s WHERE ((CRN=%s) AND (USERNAME=%s))"""
                cursor.execute(query, (newcrn, oldcrn, username))
                textMessage = 'Your current classes are successfully updated'
        connection.commit()
        return redirect(url_for('site.classes'))
    else:
        return render_template('site.classes', message=textMessage)


@site.route('/classes/<lectureid>', methods=['GET', 'POST'])
def lecture_cfg(lectureid):
    if request.method == 'POST':
        if request.form['action'] == 'sendPost':
            postContent = request.form['postContent']
            username = current_user.userName
            with dbapi2.connect(flask.current_app.config['dsn']) as connection:
                cursor = connection.cursor()

                query = """INSERT INTO POST(USERNAME, CONTENT) VALUES(%s, %s)"""
                cursor.execute(query,(username, postContent))

                query = """SELECT POSTID FROM POST WHERE (USERNAME = %s and CONTENT = %s)"""
                cursor.execute(query,(username, postContent))
                postid = cursor.fetchall()

                query = """INSERT INTO FEED(USERNAME, POSTID) VALUES(%s, %s)"""
                cursor.execute(query,(username, [postid]))

                query = """INSERT INTO CLASSPOSTS(GROUPID, POSTID) VALUES(%s, %s)"""
                cursor.execute(query,(lectureid, [postid]))
                print(postid[0][0])
                print(lectureid)
                connection.commit()
            return redirect(url_for('site.lecture_cfg', lectureid = lectureid))

        elif request.form['action'] == 'updatePost':
            postContent = request.form['postContent']
            with dbapi2.connect(flask.current_app.config['dsn']) as connection:
                cursor = connection.cursor()

                query = """UPDATE POST SET CONTENT= %s WHERE (POSTID= %s)"""

                cursor.execute(query, (postContent, postid))

                connection.commit()
            return redirect(url_for('site.lecture_cfg', postid = postid))

        elif request.form['action'] == 'deletePost':
            with dbapi2.connect(flask.current_app.config['dsn']) as connection:
                cursor = connection.cursor()

                query = """DELETE FROM FEED WHERE (POSTID= %s)"""
                cursor.execute(query, [postid])

                query = """DELETE FROM CLASSPOSTS WHERE (GROUPID= %s AND POSTID=%s)"""
                cursor.execute(query, [lectureid], [postid])

                query = """DELETE FROM POST WHERE (POSTID= %s)"""
                cursor.execute(query, [postid])

                connection.commit()
            return render_template('lecture_cfg.html', message = 'Post is successfully deleted')

        elif request.form['action'] == 'searchPost':
            postContent=request.form['search-content']
            with dbapi2.connect(flask.current_app.config['dsn']) as connection:
                cursor = connection.cursor()

                query = """SELECT * FROM POST WHERE CONTENT = %s"""
                cursor.execute(query, [postContent])

                datas=cursor.fetchall()
                connection.commit()
            return render_template('lecture_cfg.html', result=datas)

        else:
            return render_template('lecture_cfg.html')
    else:
        with dbapi2.connect(flask.current_app.config['dsn']) as connection:
            cursor = connection.cursor()

            query = """SELECT * FROM CRNS WHERE CRN = %s"""
            cursor.execute(query, [lectureid])
            lecture = cursor.fetchall()

            query = """SELECT * FROM POST WHERE POSTID = %s"""
            cursor.execute(query, [lectureid])
            post = cursor.fetchall()

            query="""SELECT USERNAME FROM CLASSES WHERE CRN=%s"""
            cursor.execute(query, [lectureid])
            students = cursor.fetchall()

            connection.commit()
        return render_template('lecture_cfg.html', post = post, lecture=lecture, students=students)