
from xml.dom import UserDataHandler
from flask import Blueprint, Response, jsonify, request, current_app
# from importlib_metadata import method_cache

from ..dao import recordDAO
from ..dao import esDAO

from .. import utility
from .. import record as rec
from flask_mail import Mail
from elasticsearch import RequestError
import traceback

from ..dao import elastic_setup

record_blueprint = Blueprint("record", __name__)

@record_blueprint.route('/smart/getRecordById', methods=['GET', 'POST' ])
def getRecordById():
	user_dn = utility.getUserDN(request)
	record_id = ""
	if request. method == "GET":
		if "record id" in request.args:
			record_id = request.args["record_id"]
	elif request .method == "POST":
		post = utility.getPost (request)
		if "record_id" in post:
			record_id = post["record_id"]. value
	return jsonify (rec.getRecordById (user_dn, record_id))


@record_blueprint. route('/smart/getRecordForEdit', methods=['GET', 'POST'])
def getRecordForEdit():
	resp = None
	try:
		post = utility.getPost (request)
		user_dn = utility.getUserDN(request)
		guid = post.getvalue("guid", "")
		system_id = post.getvalue("system_id", "")
		exercise = post.getvalue("exercise", "")
		if (guid == "" or system_id == "" or exercise == ""):
			stk = traceback.format_exc()
			resp = jsonify(errorInfo="missing parameters", system_id=system_id, guid=guid, exer=exercise, stacktrc=stk)
			resp.status_code = 403
		else:
			resp = jsonify(rec. getRecordForEdit (user_dn, system_id, guid, exercise))
	except RequestError as es3:
		stk = traceback.format_exc()
		print(stk, "system_id="+system_id+", guid="+guid+", exer="+exercise)
		resp = jsonify(errorInfo=es3.info, system_id=system_id, guid=guid, exer=exercise, errStg=str(es3), stacktrc=stk)
		resp.status_code = es3.status_code
	except Exception as es3:
		print ("GENERAL exceptions", es3, "system_id="+system_id+", guid="+guid+", exer="+exercise)
		stk = traceback.format_exc()
		print(stk)
		resp = jsonify(system_id=system_id, guid=guid, exer=exercise, errStg=str(es3), stacktrc=stk)
		resp.status_code = 400
	finally:
		return resp

# given dashboard ID, get all the records.
@record_blueprint.route('/smart/getRecords', methods=['POST'])
def getRecords():
	post = utility.getPost (request)
	user_dn = utility.getUserDN(request)
	guid = post["guid"].value
	return jsonify(rec.getRecords (user_dn, guid))

@record_blueprint.route('/smart/getTimeSeriesRecords', methods=['GET', 'POST'])
def getTimeSeriesRecords():

	user_dn = utility.getUserDN (request)
	dashboard_id = ""
	exercise = False
	if request.method == "GET":
		if "dashboard id" in request. args:
			dashboard_id = request.args[ "dashboard_id"]
		if "exercise" in request. args:
			exercise = request.args["exercise"]
	elif request.method == "POST":
		post = utility.getPost (request)
		if "dashboard_id" in post:
			dashboard_id = post["dashboard_id"]. value
		if "exercise" in post:
			exercise = post["exercise"]. value
	return jsonify(rec.getTimeSeriesRecords(user_dn, dashboard_id, exercise))


@record_blueprint.route('/smart/getActiveRecords', methods=['GET', 'POST'])
def getActiveRecords():
	post = utility.getPost (request)
	user_dn = utility.getUserDN(request)
	rec_list = post["rec_list"]. value
	return jsonify(rec.getActiveRecords(user_dn, rec_list))


@record_blueprint.route('/smart/getRecordsFromList', methods=['GET', 'POST'])
def getRecordsFromList():
	post = utility.getPost (request)
	user_dn = utility.getUserDN(request)
	rec_list = post["rec_list"]. value
	return jsonify(rec.getRecordsFromList(user_dn, rec_list))

@record_blueprint.route('/smart/exportRecords', methods=['GET', 'POST'])
def exportRecords():
	post = utility.getPost (request)
	user_dn = utility.getUserDN(request)
	rec_list = post["rec_list"]. value
	return Response(rec .export (user_dn, rec_list), mimetype="text/csv", headers={" Content-disposition": "attachment; filename=SMART_Export.csv"})


@record_blueprint. route('/smart/deleteRecord', methods=['GET', 'POST'])
def deleteRecord():
	post = utility.getPost (request)
	user_dn = utility.getUserDN(request)
	if "record id" in post:
		record_id = post["record_id"].value
		return jsonify(rec.deleteRecordById(user_dn, record_id))
	elif "guid" in post:
		guid = post[" guid"]. value
	return jsonify(rec.deleteRecordsByGuid(user_dn, guid))


@record_blueprint.route('/smart/unlockRecord', methods=['GET', 'POST'])
def unlockRecord():
	post = utility.getPost(request)
	user_dn = utility.getUserDN (request)
	id = post[" tracking_id"]. value
	return jsonify(rec. unlockRecord (user_dn, id))

@record_blueprint.route('/smart/getTimeoutRecords', methods=['GET', 'POST'])
def getTimeoutRecords():
	post = utility.getPost (request)
	user_dn = utility.getUserDN(request)
	dashboard_id = post["dashboard id"].value
	return jsonify(rec.getTimeoutRecords (user_dn, dashboard_id))


@record_blueprint.route('/smart/getLastUpdatedRecord', methods=['GET', 'POST'])
def getLastUpdatedRecord():
	post = utility.getPost (request)
	user_dn = utility. getUserDN(request)
	rec_list = post["rec_list"]. value
	return jsonify(rec. getLastUpdatedRecord(user_dn, rec_list))

@record_blueprint. route('/smart/getArchive', methods=['GET', 'POST'])
def getArchive():
	post = utility.getPost (request)
	user_dn = utility. getUserDN(request)
	record_id = post["record_id" ].value
	return jsonify(rec.getArchive(user_dn, record_id))


@record_blueprint. route('/smart/emailRecord', methods=[' GET', 'POST'])
def emailRecord():
	post = utility.getPost (request)
	user_dn = utility.getUserDN(request)
	dashboard_id = post["dashboard id"] .value
	guid = post[" guid"]. value
	system_id = post ["system_id"]. value
	exercise = post["exercise"]. value
	with current_app. app_context():
		mail = Mail()
	return jsonify(rec. emailRecord (mail, user_dn, dashboard_id, system_id, guid, exercise))

@record_blueprint.route('/smart/updateRecord', methods=['GET', ' POST'])
def updateRecord():
	post = utility.getPost (request)
	user_dn = utility.getUserDN(request)
	action = post["action"]. value
	update_group = post["update_group"]. value
	create_tracking_id = post["create_tracking_id"]. value
	set_default = "false"
	if "set_default" in post:
		set_default = post["set_default"]. value
	record = post["record"]. value
	return rec. updateRecord (user_dn, action, update_group, set_default, record, create_tracking_id)

# @record_blueprint.route('/smart/modifyRecord', methods=['GET', ' POST'1)
# def modifyRecord():
# 	post = utility.getPost (request)
#	user_dn = utility.getUserDN(request)
# 	#record = post[" record"]. value
#	update_group = post["update_group"].value
#	return jsonify(rec. updateRecord(user_dn, "modify", update_group, "false", record, "no"))

@record_blueprint .route('/smart/recordUpload', methods=['GET', 'POST'])
def recordUpload():
	post = utility.getPost (request)

	user_dn = utility.getUserDN(request)

	file = post["file"]
	file_type = post ["file_type"] .value
	return jsonify(rec.uploadRecord(user_dn, file, file_type))


@record_blueprint.route('/smart/removeRecordAttribute', methods=['GET', 'POST'])
def removeRecordAttribute():
	user_dn = utility. getUserDN(request)
	system_id = ""
	attribute_name = ""
	if request. method == "GET":
		if "dashboard_id" in request. args:
			system_id = request.args["system_id"]
			attribute_name = request.args["attribute_name"]
	elif request. method == "POST":
		post = utility.getPost (request)
		if "system_id" in post:
			system_id = post["system_id"].value
			attribute_name = post ["attribute_name"]. value
	return jsonify(rec. removeRecordAttribute (user_dn, system_id, attribute_name))

@record_blueprint.route('/smart/finalAllRecords', methods=[ 'GET', 'POST'])
def finalAllRecords():
	post = utility. getPost (request)
	user_dn = utility. getUserDN(request)
	dashboard_id = post[" dashboard_id"]. value
	return jsonify(rec.finalAllRecords(user_dn, dashboard_id))

@record_blueprint.route('/smart/setup', methods=['GET'])
def setup():
	user_dn = utility.getUserDN(request)
	elastic_setup.setupES(user_dn)
	return jsonify({"result": 'good'})