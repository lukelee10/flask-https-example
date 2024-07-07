import zipfile
import json, os
from src import utility
from flask import Blueprint, Flask, send_file, render_template, jsonify, request
from flask_cors import CORS, cross_origin
from flask_mail import Mail
from src import users as users
from src.routes import routes, record_routes

index_blueprint = Blueprint("index", __name__)

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

mail = Mail(app)

app.register_blueprint(index_blueprint)
# app.register_blueprint(routes.user_blueprint)
app.register_blueprint(record_routes.record_blueprint)

app.debug = True

@app.route("/")
@cross_origin()
def index():
    return send_file("templates/index.html")

# upload zip file
@app.route("/dataUpload")
def uploadData():
    return render_template('upload.html')

@app.route("/test")
def test():
    return render_template('test.html')

# reindex data (after running the elastic7_sestup.py file twice)
@app.route('/uploader', methods = ['POST'])
def extractData():
    with zipfile.ZipFile(request.files["file"], 'r') as ref:
        for index in range(len(ref.infolist())):
            with ref.open(ref.infolist()[index], "r") as jsonData:
                keyName = str(str(ref.namelist()[index].split("/")[1]).split(".")[0])
                utility.reIndexer(keyName, json.load(jsonData), utility.getUserDN(request))

    return jsonify("success")




if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0")
    except Exception:
        app.logger.exception("Failed")