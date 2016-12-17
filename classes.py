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
    if request.method == 'POST':
        with dbapi2.connect(flask.current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            if request.form['action'] == 'addNewLecture':
                username = current_user.userName
                entering=request.form['enter']
                query = """INSERT INTO CLASSES (CRN, USERNAME) VALUES (%s, %s)"""
                cursor.execute(query,(entering, username))

            elif request.form['action'] == 'leftAclass':
                username = current_user.userName
                leave=request.form['left']
                query = """DELETE FROM CLASSES WHERE ((CRN=%s) AND (USERNAME=%s))"""
                cursor.execute(query,(leave, username))

            elif request.form['action'] == 'updateAclass':
                username = current_user.userName
                oldcrn=request.form['oldCRN']
                newcrn=request.form['newCRN']
                query = """UPDATE CLASSES SET CRN=%s WHERE ((CRN=%s) AND (USERNAME=%s))"""
                cursor.execute(query, (newcrn, oldcrn, username))

            elif request.form['action'] == 'findLecture':
                found=request.form['find']
                query = """SELECT * FROM CRNS WHERE (CRN=%s) """
                cursor.execute(query, [found])
                results=cursor.fetchall()
                print(results)
                connection.commit()
                return render_template('classes.html', result=results)

            elif request.form['action'] == 'listClass':
                classCRN=request.form['CRNofClass']
                query = """SELECT USERNAME FROM CLASSES WHERE (CRN=%s) """
                cursor.execute(query, [classCRN])
                theList=cursor.fetchall()
                print(theList)
                connection.commit()
                return render_template('classes.html', listClass=theList)
        connection.commit()
        return redirect(url_for('site.profile_page'))
    else:
        return render_template('classes.html', user = current_user)
