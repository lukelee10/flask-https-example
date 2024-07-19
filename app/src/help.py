import json
import uuid
from .dao import helpDAO as hDAO


def updateHelp(user_dn, help):
    if type(help) == str:
        help = json.loads(help)
    if "help_id" not in help or help["help_id"] == "":
        help_id = str(uuid.uuid4())
        help["help_id"] = help_id
    else:
        help_id = help["help_id"]
    hDAO.updateHelp(user_dn, help, help_id)
    return help

def uploadHelps (user_dn, dashboard_id, help_file):
    help_upload_status = ['']
    help_json = json.load(help_file.file)
    for help in help_json:
        del help['help_id']
        help["dashboard_id"] = dashboard_id
        res = updateHelp(user_dn, json.dumps(help))
        help_upload_status.append(res)
    return {"result": "success"}

# def exportHelp(user_dn):


def getHelp(user_dn, id):
    return hDAO.getHelps(user_dn, id)

def getHelps(user_dn, dashboard_id):
    return hDAO.getHelps(user_dn, dashboard_id)

def getHelpItems(user_dn, dashboard_id):
    return hDAO.getHelpItems(user_dn, dashboard_id)

def delete(user_dn, id):
    return hDAO.deleteHelp(user_dn, id)

def deleteAllHelp(user_dn, dashboard_id):
    return hDAO.deleteAllHelp(user_dn, dashboard_id)


def searchHelp(user_dn, dashboard_id, terms, view):

    return hDAO.searchHelp(user_dn,dashboard_id, terms, view)