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


                return render_template('search.html', results = datas)

        elif request.form['action'] == 'searchUser':
            username = request.form['search-user']
            with dbapi2.connect(flask.current_app.config['dsn']) as connection:
                cursor = connection.cursor()

                query = """SELECT * FROM USERS WHERE USERNAME= %s """
                cursor.execute(query, (username,))

                datas=cursor.fetchall()

                connection.commit()
            return render_template('search.html', foundUser = datas)

        elif request.form['action'] == 'follow':
            username = request.form['foundUser']
            flag = False
            if current_user.userName == username:
                message = "Follow yourself but only in real life :)"
                return render_template('search.html', message = message)

            with dbapi2.connect(flask.current_app.config['dsn']) as connection:
                cursor = connection.cursor()

                query = """SELECT * FROM FOLLOW WHERE FOLLOWER = %s AND FOLLOWING = %s"""
                cursor.execute(query, (current_user.userName, username,))

                result = cursor.fetchall()

                if result:
                    return render_template('search.html', message = "User couldn't added to following list. Possible reason: User is already in the list.")

                else:
                    query = """INSERT INTO FOLLOW(FOLLOWER, FOLLOWING) VALUES(%s, %s)"""
                    cursor.execute(query, (current_user.userName, username,))
                    query = """UPDATE USERS SET FOLLOWER_COUNT = (FOLLOWER_COUNT+1) WHERE USERNAME = %s"""
                    cursor.execute(query, (username,))
                    query = """UPDATE USERS SET FOLLOWING_COUNT = (FOLLOWING_COUNT+1) WHERE USERNAME = %s"""
                    cursor.execute(query, (current_user.userName,))
                    connection.commit()
                    return render_template('search.html', message = "User added to following list.")

        else:
            return render_template('search.html')
    else:
        return render_template('search.html')