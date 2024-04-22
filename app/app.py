from flask import Flask, Blueprint
from flask_cors import CORS, cross_origin
from flask_mail import Mail

from app.src.routes import routes

index_blueprint = Blueprint("index", __name__)

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

mail = Mail(app)

app.register_blueprint(index_blueprint)
app.register_blueprint(routes.user_blueprint)

app.debug = True


if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0")
    except Exception:
        app.logger.exception("Failed")