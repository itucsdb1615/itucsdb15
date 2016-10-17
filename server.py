import datetime
import os

from flask import Flask
from flask import render_template


app = Flask(__name__)


@app.route('/')
def home_page():
    now = datetime.datetime.now()
    return render_template('homepage.html', current_time=now.ctime())

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signin')
def signin():
    return render_template('signin.html')

@app.route('/lectures')
def lectures():
    return render_template('lectures.html')

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

if __name__ == '__main__':
    VCAP_APP_PORT = os.getenv('VCAP_APP_PORT')
    if VCAP_APP_PORT is not None:
        port, debug = int(VCAP_APP_PORT), False
    else:
        port, debug = 5000, True
    app.run(host='0.0.0.0', port=port, debug=debug)
