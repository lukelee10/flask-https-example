
import copy
from distutils import file_util
import json
import datetime
from dateutil.parser import *
import uuid
from .dao import dashboardDAO as dashboardDAO
from .dao import recordDAO as rDao
from .dao import systemTypeDAO as systemTypeDAO
from . import dashboard as dsh
from pandas import json_normalize
import pandas as pd
import io

import traceback


'''
gets record to edit and locks it
'''

def getRecordForEdit (user_dn, system_id, guid, exercise):
    #get the system that will be used to create the form and output fields
    system = dashboardDAO.getSystem(user_dn, system_id)
    dashboard = dashboardDAO.getDashboard(user_dn, system["dashboard_id"])

    if "dashboard_cycle" not in dashboard:
        dashboard[" dashboard_cycle"] = ""

    #get the strat lead if it exists
    record = rDao.getRecord(user_dn, guid)
    record["system id"] = system["system_id"]

    if "noresults" in record: # record does not exist
        record = {}
        record_series = getRecordSeries(user_dn, system["dashboard_id"])


def getRecordSeries (user_dn, dashboard_id):
    now = datetime.datetime.now()
    year = str(now.year) [-2:]
    dashboard = dashboardDAO.getDashboardDetails(user_dn, dashboard_id)
    dashboard_grouping_code = dashboard["dashboard_grouping_code"]
    smart_code = dashboard["dashboard_smart_code"]

    record_series = smart_code + year + dashboard_grouping_code

    return record_series
