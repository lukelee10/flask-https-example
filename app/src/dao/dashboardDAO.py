import json
import datetime
from ..dao import esDAO as esDao
from ..dao import dashboardDAO

def getDashboardDetails(user_dn, dashboard_id):
    return {"dashboard_emails_to": "johndoe@dia.gov"}

def updateDashboard(user_dn, dashboard_json):
    return {"ok": True}