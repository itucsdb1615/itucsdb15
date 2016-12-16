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

        if request.form['action'] == 'addFaculty':
            username = current_user.userName
            faculty = request.form['selectFaculty']
            with dbapi2.connect(flask.current_app.config['dsn']) as connection:
                cursor = connection.cursor()

                query = """INSERT INTO DEPARTMENTLIST (USERNAME, FACULTYNO ) VALUES (%s, %s)"""
                cursor.execute(query, (username,faculty))
                test = 'test'
                connection.commit()

            return render_template('faculty.html', resultInsert=test)

        elif request.form['action'] == 'updateFaculty':
            username = current_user.userName
            faculty = request.form['selectFaculty']
            with dbapi2.connect(flask.current_app.config['dsn']) as connection:
                cursor = connection.cursor()

                query = """UPDATE DEPARTMENTLIST SET FACULTYNO=%s WHERE (USERNAME=%s)"""
                cursor.execute(query , (faculty, username))
                test='test'
                connection.commit()

            return render_template('faculty.html', resultUpdate=test)

        elif request.form['action'] == 'deleteFaculty':
            username = current_user.userName
            with dbapi2.connect(flask.current_app.config['dsn']) as connection:
                cursor = connection.cursor()

                query = """DELETE FROM DEPARTMENTLIST WHERE ( USERNAME='%s' )""" %(username)
                cursor.execute(query)
                test='test'
                connection.commit()

            return render_template('faculty.html', resultDelete=test)

        elif request.form['action'] == 'searchFaculty':
            username = current_user.userName
            with dbapi2.connect(flask.current_app.config['dsn']) as connection:
                cursor = connection.cursor()

                query = """SELECT * FROM DEPARTMENTLIST WHERE ( USERNAME='%s' )""" %(username)
                cursor.execute(query)
                datas=cursor.fetchall()

                connection.commit()
            return render_template('faculty.html', resultSearch=datas)

    else:

        return render_template('faculty.html')