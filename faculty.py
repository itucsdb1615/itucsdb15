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


@site.route('/faculty', methods=['GET', 'POST'])
@login_required
def faculty():


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

                query = """SELECT USERNAME FROM DEPARTMENTLIST WHERE (FACULTYNO = ( SELECT FACULTYNO FROM DEPARTMENTLIST WHERE USERNAME=%s )) AND USERNAME!= %s """
                cursor.execute(query,(username,username))
                departmentalFriends = cursor.fetchall()

                query = """INSERT INTO FACULTYFEED VALUES(%s, %s, %s)"""
                cursor.execute(query,(username,username, postid[0]))
                query = """INSERT INTO FEED(USERNAME, POSTID) VALUES (%s, %s)"""
                cursor.execute(query,(username, postid[0]))

                for friend in departmentalFriends:
                    query = """INSERT INTO FACULTYFEED VALUES (%s, %s,%s)"""
                    cursor.execute(query,(username,friend[0], postid[0]))
                    query = """INSERT INTO FEED(USERNAME, POSTID) VALUES (%s, %s)"""
                    cursor.execute(query,(friend[0], postid[0]))



                connection.commit()
            return render_template('faculty.html', user = current_user)
        elif request.form['action'] == 'addFaculty':
            username = current_user.userName
            faculty = request.form['selectFaculty']
            with dbapi2.connect(flask.current_app.config['dsn']) as connection:
                cursor = connection.cursor()

                query = """INSERT INTO DEPARTMENTLIST (USERNAME, FACULTYNO ) VALUES (%s, %s)"""
                cursor.execute(query, (username,faculty))
                test = 'test'
                connection.commit()

            return render_template('faculty.html', resultInsert=test,user = current_user)

        elif request.form['action'] == 'updateFaculty':
            username = current_user.userName
            faculty = request.form['selectFaculty']
            with dbapi2.connect(flask.current_app.config['dsn']) as connection:
                cursor = connection.cursor()

                query = """UPDATE DEPARTMENTLIST SET FACULTYNO=%s WHERE (USERNAME=%s)"""
                cursor.execute(query , (faculty, username))
                test='test'
                connection.commit()

            return render_template('faculty.html', resultUpdate=test,user = current_user)

        elif request.form['action'] == 'deleteFaculty':
            username = current_user.userName
            with dbapi2.connect(flask.current_app.config['dsn']) as connection:
                cursor = connection.cursor()

                query = """DELETE FROM DEPARTMENTLIST WHERE ( USERNAME=%s )"""
                cursor.execute(query, [username])
                test='test'
                connection.commit()

            return render_template('faculty.html', resultDelete=test,user = current_user)

        elif request.form['action'] == 'searchFaculty':
            username = current_user.userName
            with dbapi2.connect(flask.current_app.config['dsn']) as connection:
                cursor = connection.cursor()

                query = """SELECT * FROM DEPARTMENTLIST WHERE ( USERNAME=%s )"""
                cursor.execute(query, [username])
                datas=cursor.fetchall()

                query = """SELECT D.NAME FROM DEPARTMENTS AS D INNER JOIN DEPARTMENTLIST AS L ON D.FACULTYNO =L.FACULTYNO  WHERE L.USERNAME = %s"""
                cursor.execute(query, [username])
                faculty = cursor.fetchall()

                connection.commit()
            return render_template('faculty.html', resultSearch=datas, faculty= faculty,user = current_user)

    else:
        with dbapi2.connect(flask.current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            username = current_user.userName

            ## posts
            query = """SELECT POSTID FROM FACULTYFEED WHERE READER = %s ORDER BY POSTID DESC"""
            cursor.execute(query, [username])
            postids = cursor.fetchall()

            posts = []
            for id in postids:
                query = """SELECT F.SENDER,P.USERNAME,P.CONTENT FROM POST AS P NATURAL JOIN FACULTYFEED AS F   WHERE P.POSTID = %s ORDER BY POSTID DESC"""
                cursor.execute(query, [id[0]])
                posts.append(cursor.fetchall())

        return render_template('faculty.html', user = current_user,posts =posts)