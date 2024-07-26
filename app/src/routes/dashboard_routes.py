import json
import traceback
from flask import Blueprint, Response, jsonify, make_response, request

from .. import dashboard as dash
from .. import buckyBoard as bb
from .. import smartSearch as ss
from .. import summary as smry
from .. import notifications as nt
from .. import templates as tmplt
from .. import record as rec
from .. import utility

dashboard_blueprint = Blueprint("dashboard", __name__)

@dashboard_blueprint.route('/smart/getDashboardsDetails', methods=['GET', 'POST'])
def getDashboardsDetails():
    user_dn = utility.getUserDN(request)
    return jsonify(dash.getDashboardsDetails(user_dn))



@dashboard_blueprint.route('/smart/getDashboard', methods=['GET', 'POST'])
def getDashboard():
    user_dn = utility.getUserDN(request)
    dashboard_id = ""
    if request. method == "GET":
        if "dashboard_id" in request.args:
            dashboard_id = request.args[" dashboard_id"]
    elif request. method == "POST":
        post = utility.getPost(request)
        if "dashboard_id" in post:
            dashboard_id = post["dashboard_id"]. value
    return jsonify (dash. getDashboard (user_dn, dashboard_id))


@dashboard_blueprint.route('/smart/uploadDashboard', methods=[ 'POST'1)
def uploadDashboard():
    try:
        user_dn = utility.getUserDN(request)
        post = utility.getPost (request)
        dashboard_file = post["dashboard_file"]
        res = dash. uploadDashboard (user_dn, dashboard_file)
    except Exception as e:
        traceback.print_exc()
        res = {"FAILED": str(e)}

    return jsonify(res)


@dashboard_blueprint.route('/smart/exportDashboard', methods=['GET', 'POST'])
def exportDashboard():
    user_dn = utility.getUserDN(request)
    dashboard_id = ""
    if request. method == "GET":
        if "dashboard_id" in request.args:
            dashboard_id = request.args["dashboard_id"]
    elif request.method == "POST":
        post = utility.getPost (request)
        if "dashboard_id" in post:
            dashboard_id = post["dashboard_id"].value

    dashboard = dash.exportDashboard(user_dn, dashboard_id)
    return Response(json.dumps (dashboard), mimetype="application/json", headers={"Content-disposition": "attachment; filename=" + dashboard_id})

# get dashboart and recrods
@dashboard_blueprint.route('/smart/getOverview', methods=[ 'GET', 'POST'1)
def getOverview():
    user_dn = utility.getUserDN(request)
    dashboard_grouping_code = ""
    exercise = ""
    if request. method == "GET":
        dashboard_grouping_code = request.args["dashboard_grouping_code"]
        exercise = request.args["exercise"]
    elif request.method == "POST":
        post = utility.getPost (request)
        dashboard_grouping_code = post["dashboard_grouping_code"].value
        exercise = post[ "exercise"].value

    return jsonify(bb.getBBForAllDashboards(user_dn, dashboard_grouping_code, exercise))

@dashboard_blueprint.route('/smart/getDashboardDetails', methods=['GET', 'POST'])
def getDashboardDetails():
    user_dn = utility.getUserDN(request)
    dashboard_id = ""
    if request.method == "GET":
        if "dashboard_id" in request.args:
            dashboard_id = request.args["dashboard_id"]
    elif request. method == "POST":
        post = utility.getPost(request)
        if "dashboard id" in post:
            dashboard_id = post["dashboard_id"].value
    return jsonify (dash.getDashboardDetails(user_dn, dashboard_id))


@dashboard_blueprint.route('/smart/updateDashboard', methods=['GET', 'POST'])
def updateDashboard():
    user_dn = utility.getUserDN(request)
    dashboard = ""
    if request. method == "GET":
        if "dashboard" in request.args:
            dashboard = request.args["dashboard"]
    elif request.method == "POST":
        post = utility.getPost (request)
        if "dashboard" in post:
            dashboard = post["dashboard"]. value
    return jsonify (dash. updateDashboard (user_dn, dashboard))


@dashboard_blueprint. route('/smart/updateHierarchy', methods=[ 'GET', 'POST'])
def updateHierarchy():
    user_dn = utility.getUserDN(request)
    dashboard = ""
    if request.method == "GET":
        if "dashboard" in request. args:
            dashboard = request.args["dashboard"]
    elif request. method == "POST":
        post = utility.getPost (request)
        if "dashboard" in post:
            dashboard = post["dashboard"].value
    return dash. updateHierarchy(user_dn, dashboard)

@dashboard_blueprint.route('/smart/importHierarchy', methods=['GET', 'POST'])
def importHierarchy():
    try:
        user_dn = utility.getUserDN(request)
        post = utility.getPost(request)
        hierarchy_upload_file = post["hierarchy_upload_file"]
        res = dash. importHierarchy(user_dn, hierarchy_upload_file)
    except Exception as e:
        traceback.print_exc()
        res = {"FAILED": str(e)}
    return jsonify(res)

@dashboard_blueprint.route('/smart/createDashboard', methods=['GET', 'POST'])
def createDashboard():
    user_dn = utility.getUserDN(request)
    dashboard = ""
    copy_id = ""
    copy_records = ""

    post = utility.getPost(request)
    if "dashboard" in post:
        dashboard = post["dashboard"]. value
    if "copy_id" in post:
        copy_id = post["copy_id"].value
    if "copy_records" in post:
        copy_records = post ["copy_records"].value
    return jsonify (dash. createDashboard (user_dn, dashboard, copy_id, copy_records))


@dashboard_blueprint.route('/smart/deleteDashboard', methods=['GET', 'POST'])
def deleteDashboard():
    user_dn = utility.getUserDN(request)
    id = ""
    post = utility.getPost(request)
    if "dashboard id" in post:
        id = post[ "dashboard_id"]. value
    return jsonify (dash. deleteDashboard (user_dn, id))


@dashboard_blueprint.route('/smart/deleteDashboardAndArchive', methods=[ 'GET', 'POST'])
def deleteDashboardAndArchive():
    user_dn = utility.getUserDN(request)
    id = ""
    post = utility.getPost(request)
    if "dashboard_id" in post:
        id = post ["dashboard_id"]. value
    return jsonify(dash. deleteDashboardAndArchive (user_dn, id))

@dashboard_blueprint.route('/smart/smartSearch', methods=['GET', 'POST'])
def smartSearch():
    user_dn = utility.getuserDN(request)
    auth_dn = ""
    dashboard_grouping_code = ""
    dashboard_id = ""
    record_active = "true"
    exercise = "false"
    acm = ""
    record_state = ""
    tracking_id = ""
    start_date = ""
    end_date = ""
    include_system_records = "true"
    csv = "false"
    archive = "false"

    if request.method == "GET":
        if "user dn" in request.args:
            auth_dn = request.args["user_dn"]
        if "dashboard_grouping_code" in request.args:
            dashboard_grouping_code = request.args["dashboard_grouping_code"]
        if "dashboard_id" in request.args:
            dashboard_id = request.args["dashboard_id"]
        if "record_active" in request.args:
            record_active = request.args["record_active"]
        if "exercise" in request.args:
            exercise = request.args["exercise"]
        if "acm" in request.args:
            acm = request.args["acm"]
        if "tracking_id" in request.args:
            tracking_id = request.args["tracking_id"]
        if "record_state" in request.args:
            record_state = request.args["record_state"]
        if "start_date" in request.args:
            start_date = request.args["start_date"]
        if "end_date" in request.args:
            end_date = request.args["end_date"]
        if "include_system_records" in request.args:
            include_system_records = request.args["include_system_records"]
        if "csv" in request.args:
            csv = request.args["csv"]
        if "archive" in request.args:
            archive = request.args["archive"]
    else:

        post = utility.getPost(request)

        if "user_dn" in post:
            auth_dn = post["user_dn"].value
        if "dashboard_grouping_code" in post:
            dashboard_grouping_code = post["dashboard_grouping_code"].value
        if "dashboard_id" in post:
            dashboard_id = post["dashboard_id"].value
        if "record_active" in post:
            record_active = post["record_active"].value
        if "exercise" in post:
            exercise = post["exercise"].value
        if "acm" in post:
            acm = post["acm"].value
        if "tracking_id" in post:
            tracking_id = post["tracking_id"].value
        if "record_state" in post:
            record_state = post["record_state"].value
        if "start_date" in post:
            start_date = post["start_date"].value
        if "end_date" in post:
            end_date = post["end_date"].value
        if "csv" in post:
            csv = post["csv"].value
        if "archive" in post:
            archive = post[" archive"].value
    if csv == "true":
        output = make_response( ss.doSearch(user_dn, auth_dn, dashboard_grouping_code, dashboard_id, record_active, exercise, record
        output.headers["Content-Disposition"] = "attachment; filename=smart_export.csv"
        output.headers["Content-type"] = "text/csv"
        return output
    else:
        return jsonify(ss.doSearch(user_dn, auth_dn, dashboard_grouping_code, dashboard_id, record_active, exercise, record_state, t

@dashboard_blueprint.route('/smart/getBuckyboard', methods=['GET', 'POST'])
def getBuckyboard():
    user_dn = utility.getUserDN(request)
    dashboard_id = ""
    if request.method == "GET":
        if "dashboard_id" in request. args:
            dashboard_id = request.args["dashboard_id"]
    elif request.method == "POST":
        post = utility. getPost (request)
        if "dashboard_id" in post:
            dashboard_id = post["dashboard_id"].value
    return jsonify(bb.getBuckyboard(user_dn, dashboard_id))


@dashboard_blueprint.route('/smart/getSummaryTabs', methods=['GET', 'POST'])
def getSummaryTabs():
    user_dn = utility.getUserDN(request)
    dashboard_id = ""
    selected_node_id = ""
    if request.method == "GET":
        if "dashboard_id" in request.args:
            dashboard_id = request.args["dashboard_id"]
            selected_node_id = request.args["selectedNodeId"]
    elif request.method == "POST":
        post = utility.getPost(request)
        if "dashboard_id" in post:
            dashboard_id = post["dashboard_id"].value
            selected_node_id = post["selectedNodeId"].value
    return jsonify(smry.getSummaryTabs(user_dn, dashboard_id, selected_node_id))


@dashboard_blueprint.route('/smart/getSummary', methods=['GET', 'POST'])
def getSummary():
    user_dn = utility.getUserDN(request)
    selected_node_id = ""
    dashboard_id = ""
    if request.method == "GET" :
        if "selectedNode" in request.args:
            selected_node_id = request.args["selected_node_id"]
            dashboard_id = request.args["dashboard_id"]
    elif request.method == "POST":
        post = utility.getPost(request)
        if "selected_node_id" in post:
            selected_node_id = post["selected_node_id"].value
            dashboard_id = post["dashboard_id"].value
    return jsonify(smry.getSummary(user_dn, selected_node_id, dashboard_id))


@dashboard_blueprint.route('/smart/notifications', methods=['GET', 'POST'])
def notifications ():
    post = utility.getPost(request)

    action = post["action"].value
    user_dn = utility.getUserDN(request)

    if action == "submit":
        notification = post["notification"]. value
        return jsonify(nt.submitNotification(user_dn, notification))
    elif action == "get":
        user_id = post["user_id"].value
        return jsonify(nt.getNotifications(user_dn, user_id))
    elif action == "delete":
        id = post["notification id"].value
        return jsonify(nt.deleteNotifications(user_dn, id))


@dashboard_blueprint.route('/smart/getTemplate', methods=['GET', 'POST'])
def getTemplate():
    template_type = ""
    if request.method == "GET":
        if "templateType" in request.args:
            template_type = request.args["templateType"]
    elif request.method == "POST":
        post = utility.getPost(request)
        if "templateType" in post:
            template_type = post["templateType"].value
    return jsonify(tmplt.getTemplate(template_type))



@dashboard_blueprint.route('/smart/getMetricsData', methods=['GET', 'POST'])
def getMetricsData():
    user_dn = utility.getUserDN (request)
    return jsonify(rec.getMetricsData(user_dn))


# @dashboard_blueprint.route('/smart/doCleanUp', methods=['GET', ' POST'1)
# def doCleanUp():
# user_dn = utility.getUserDN(request)
# dashboard_id = ""
# if request. method == "GET":
# if "dashboard_id" in request. args:
# dashboard_id = request. args[ "dashboard_id"]
# elif request. method == 'POST" :
# post = utility.getPost(request)
# if "dashboard_id" in post:
# dashboard_id = post[ "dashboard_id"]. value
# return jsonify (dash. doCleanUp (user_dn, dashboard_id))


@dashboard_blueprint.route('/smart/es5Download', methods=['GET', 'POST'])
def es5Download():
    user_dn = utility.getUserDN(request)
    return dash.smartDownload(user_dn)