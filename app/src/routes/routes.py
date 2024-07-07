from flask import Blueprint

from ..dao import esDAO

user_blueprint = Blueprint('user', __name__)

@user_blueprint.route('/', methods=['GET', 'POST'])
@user_blueprint.route('/index')
def index():
    user = {'username': 'Miguel'}
    return '''
<html>
    <head>
        <title>Home Page - Microblog</title>
    </head>
    <body>
        <h1>Hello, ''' + user['username'] + '''!</h1>
    </body>
</html>'''

@user_blueprint.route('/update')
def update():
    return esDAO.update({"default": {"key3": ""}})

@user_blueprint.route('/get')
def get():
    return esDAO.get()