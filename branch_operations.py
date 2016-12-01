from flask import Blueprint, render_template
from flask_login import LoginManager
from flask_login.utils import login_required, login_user, current_user
from flask import current_app, request
from jinja2 import TemplateNotFound

site = Blueprint('site', __name__,template_folder='templates', static_folder='static')
@site.route('/deneme')
def deneme():
    return render_template('homepage.html')

@site.route('/add_students_to_branches', methods =['GET','POST'])
def add_students_to_branches():
    if request.method =='POST':
        with dbapi2.connect(site.config['dsn']) as connection:
            cursor = connection.cursor()
            if request.form['action'] == 'add':
                student_name = request.form['student_name']
                branch_name = request.form['branch_name']

                query = """SELECT * FROM STUDENTBRANCHES WHERE  NAME = %s """
                cursor.execute(query,[branch_name])
                result = cursor.fetchall()
                message =""
                if len(result) == 0:#there is no such a user
                    query = """INSERT INTO STUDENTBRANCHES(NAME, DESCRIPTION) VALUES (%s,%s) """
                    cursor.execute(query,[branch_name,"not entered yet"])
                    message = "new student branch added(this branch created now )"


                query = """SELECT * FROM USERS WHERE  NAME = %s """
                cursor.execute(query,[student_name])
                result = cursor.fetchall()
                if len(result) ==0:
                    message += "There is no such a user"
                   # there is no such a user so that this operation can not be done
                else:#adding to casting table if user is exist
                    query = """SELECT STUDENTBRANCH_ID FROM STUDENTBRANCHES WHERE NAME =%s """
                    cursor.execute(query,[student_branch])
                    branch_id = cursor.fetchall()[0]
                    message += "User added to the branch succesfully"
                    query = """INSERT INTO STUDENTBRANCHES_CASTING(STUDENTBRANCH_ID, PERSON_NAME) VALUES (%s,%s) """
                    cursor.execute(query, [branch_id, student_name])
            connection.commit()
            #return render_template('add_students_to_branches.html',message = message)
            if request.form['action'] == 'remove':
                message =""
                print(request.form)
                student_name = request.form['student_name']
                branch_name = request.form['branch_name']

                query = """SELECT * FROM USERS WHERE  NAME = %s """
                cursor.execute(query,[student_name])
                result = cursor.fetchall()
                if len(result) ==0:
                    message += "There is no such a user"
                    return render_template('add_students_to_branches.html',message = message)

                query = """SELECT * FROM STUDENTBRANCHES WHERE  NAME = %s """
                cursor.execute(query,[branch_name])
                result = cursor.fetchall()
                if len(result) == 0:#there is no such a user
                    message += "There is no such a user"
                    return render_template('add_students_to_branches.html',message = message)

                query = """SELECT STUDENTBRANCH_ID FROM STUDENTBRANCHES WHERE NAME =%s """
                cursor.execute(query,[student_branch])
                branch_id = cursor.fetchall()[0]

                message += "User removed from the branch succesfully"

                query = """DELETE FROM STUDENTBRANCHES_CASTING WHERE STUDENTBRANCH_ID = %s AND PERSON_NAME = %s """
                cursor.execute(query, [branch_id, student_name])
            connection.commit()
            return render_template('add_students_to_branches.html',message = message)


    else:
        return render_template('add_students_to_branches.html')
    pass


@login_required
@site.route('/branches', methods=['GET', 'POST'])
def student_branches():
    if request.method =='POST':

        with dbapi2.connect(site.config['dsn']) as connection:
            cursor = connection.cursor()
            if request.form['action'] == 'update':
                branch_name = request.form['branch-name']
                new_branch_name = request.form['new-branch-name']
                branch_desc = request.form['branch-desc']
                query = """ UPDATE STUDENTBRANCHES SET NAME = %s , DESCRIPTION='%s' WHERE (NAME = %s)"""#,(new_branch_name, branch_desc, branch_name,)
                cursor.execute(query,(new_branch_name, branch_desc, branch_name,))

            elif request.form['action'] == 'delete':
                branch_name = request.form['delete-branch-name']
                query = """DELETE FROM STUDENTBRANCHES WHERE (NAME = %s)"""#,(branch_name,)
                cursor.execute(query,(branch_name,))
            elif request.form['action'] == 'add':
                branch_name = request.form['add-branch-name']
                new_branch_desc = request.form['add-branch-desc']
                query = """INSERT INTO STUDENTBRANCHES(NAME, DESCRIPTION) VALUES (%s,%s) """#,(branch_name, new_branch_desc,)
                cursor.execute(query,(branch_name, new_branch_desc,))
            elif request.form['action'] == 'search':
                 branch_name = request.form['search-branch-name']
                 query = """SELECT * FROM STUDENTBRANCHES WHERE (NAME = %s)""" #,(branch_name)
                 cursor.execute(query,(branch_name,) )
                 result = cursor.fetchall()
                 print(result)
                 connection.commit()
                 return render_template('student_branches.html', results=result)
    else:
        return render_template('student_branches.html')

