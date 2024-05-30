import json
import datetime
from ..dao import esDAO as esDao
from ..dao import dashboardDAO

def getRecords(user_dn, dashboard_id):
    return {"records": []}

def bulkUpdateRecords(user_dn, records):
    return None

def deleteRecordById(user_dn, record_id):
    return None
