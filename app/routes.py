from app import app
from .dao import esDAO


@app.route('/')
@app.route('/index')
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

@app.route('/update')
def update():
    return esDAO.update({"default": {"key3": ""}})

@app.route('/get')
def get():
    return esDAO.get()