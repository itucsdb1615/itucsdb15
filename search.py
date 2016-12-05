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

@site.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        if request.form['action'] == 'searchPost':
                postContent=request.form['search-content']
                with dbapi2.connect(flask.current_app.config['dsn']) as connection:
                    cursor = connection.cursor()

                    query = """SELECT * FROM POST WHERE CONTENT = %s"""
                    cursor.execute(query, [postContent])

                    datas=cursor.fetchall()
                    connection.commit()


                return render_template('search.html', result = datas)
        else:
            return render_template('search.html')
    else:
        return render_template('search.html')