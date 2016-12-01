from flask import Blueprint, render_template

site = Blueprint('site', __name__)
@site.route('/deneme')
def deneme():
    return render_template('homepage.html')