from glob import glob
import traceback
from functools import reduce
import json
import uuid
import time
import pandas as pd
from .dao import dashboardDAO as dashboardDAO
from .dao import systemTypeDAO as sysTypeDAO
from .dao import esDAO as esDao
# from . import systemType as sysType
from . import record as r
# from . import help as h
from .dao import recordDAO as rDao
import traceback
from flask import jsonify
from elasticsearch import RequestError

def getGroupSystems(user_dn, group_record, group_record_id):
    return {"nodes": []}

def getPath(user_dn, x, guid):
    return True

def findRecord(guid):
    res = None
    for record in records:
        if record["guid"] == guid:
            res = record
    return res

def flattenHierarchy(obj):
    if "nodes" in obj:
        for node in obj[" nodes"]:
            nodes.append (node)
            if node["type"] != "system":
                flattenHierarchy(node)

def updateHierarchy(user_dn, dashboard):
    global records
    global nodes
    global systemTypes
    respp = None
    dashboard_json = None
    try:
        dashboard_json = json.loads(dashboard)
        systemTypes = sysTypeDAO.getSystemTypes(user_dn, dashboard_json["dashboard_id"])
        flattenHierarchy(dashboard_json["levels"][0])
        records = rDao.getRecords(user_dn, dashboard_json["dashboard_id"])["records"]

        '''
        create a unique id for each system and group node (GUID).  this will be attached the system record (record), so the
        record knows which node it belongs to.  If copying a structure, the old GUID is retained so it can be attached to the copied
        system record.  Also stores the path / heriarchy at each node level.  Also ensures static ids are updated across records
        '''

        for node in nodes:
            if "node id" not in node or node["node_id"] == "":
                print("--updateHierarchy: missing node_id AND adding below:", json.dumps(node, indent=2))
                node["node_id"] = uuid.uuid4()
            if "guid" not in node or node["guid"] == "":
                node[" guid"] = str(node["node_id"]).replace('-', '').replace('_', '') + str(uuid.uuid4()).replace('-','').replace(
                '_', '')
            record = findRecord(node["guid"])
            if record is not None:
                if "record_static_id" in node:
                    record[" record_static_id"] = node["record_static_id"]
                record["record_path"] = getPath(user_dn, dashboard_json, record[" guid"])
                record["system_title"] = node["title"]
                record["system_id"] = node["system_id"]

        response = dashboardDAO.updateDashboard(user_dn, dashboard_json)

        '''
        make sure system records have correct group_id
        '''

        updateSystemGroupId(nodes)
        response = dashboardDAO.updateDashboard(user_dn, dashboard_json)
        rDao.bulkUpdateRecords(user_dn, records)
        time.sleep(1)

        records = rDao.getRecords(user_dn, dashboard_json["dashboard_id"])["records"]

        records = deleteOrphans(user_dn, records)
        respp = jsonify(response)
    except RequestError as es3:
        stk = traceback.format_exc()
        print(stk)
        respp = jsonify(es3.info, dashboard_json, str(es3), stk)
        respp.status_code = es3.status_code
    except Exception as es3:
        print("GENERAL exceptions", es3)
        stk = traceback.format_exc()
        print(stk)
        respp = jsonify(dashboard_json, str(es3), stk)
        respp.status_code = 400
    finally:
        return respp

def deleteOrphans(user_dn, records):
    global nodes
    # global records
    for record in records:
        found = False
        for node in nodes:
            if record["guid"] == node["guid"]:
                found = True
        if found is False:
            print("DELETE ORPHAN " + record["record_id"])
            rDao.deleteRecordById(user_dn, record["record_id"])
            # records. remove (record)

def updateSystemGroupId(nodes):
    for node in nodes:
        if node["type"] == "system":
            if "guid" in node:
                record = findRecord (node[" guid"])
                if record is not None :
                    record["group_id"] = node[" guid" ]