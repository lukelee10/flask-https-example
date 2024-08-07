import json
import datetime
from ..dao import esDAO as esDao
from ..dao import dashboardDAO

def getDashboardDetails(user_dn, dashboard_id):
    return {"dashboard_emails_to": "johndoe@dia.gov"}

def updateDashboard(user_dn, dashboard_json):
    return {"ok": True}

def getSystem(user_dn, system_id):
    return {"dashboard_id": 5677, "system_id": 100011}

def getSystems(user_dn, system_id):
    return []

def updateSystem(user_dn, system, system_id):
    return True

def getDashboard(user_dn, system):
    return {"dashboard_id": 5677}

def deleteDashboard(user_dn, dashboard_id):
    return {"dashboard_id": 5677}


def deleteDashboardAndArchive(user_dn, dashboard_id):
    return {"dh": 444}


def getDashboardGroupingCodeCount(user_dn, dashboard_id):
    return "AB"

def createDashboard(user_dn, dashboard_json, dashboard_id):
    return {}