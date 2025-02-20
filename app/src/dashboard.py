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
from . import systemType as sysType
from . import record as r
from . import help as h
from . import locations as l
from . import classification as c
from . import record as rec
from .dao import recordDAO as rDao
import traceback
from flask import jsonify
from elasticsearch import RequestError






nodes = []
systemTypes = []

def getDashboard(user_dn, dashboard_id):
    dashboard = dashboardDAO.getDashboard(user_dn, dashboard_id)

    return dashboard



def getDashboardsDetails(user_dn):
    res = dashboardDAO.getDashboardsDetails(user_dn)

    return res


def deleteDashboard(user_dn, dashboard_id):
    dashboardDAO.deleteDashboard(user_dn, dashboard_id)
    # dashboardDAO. deleteSystems (user_dn, dashboard_id)
    return {"result": "delete" }


def deleteDashboardAndArchive(user_dn, dashboard_id):
    dashboardDAO.deleteDashboardAndArchive(user_dn, dashboard_id)
    # dashboardDA0. deleteSystems (user_dn, dashboard_id)
    return {"result": "delete"}


'''
for creating new dashboards. copy_id is the dashboard_id to use for copying a dashboard structure. copy_records is boolean to
determine if should copy the system records as well.
'''
def createDashboard(user_dn, dashboard, copy_id, copy_records):
    dashboard_json = json.loads(dashboard)
    dashboard_json["dashboard_grouping_code"] = dashboard_json["dashboard_grouping_code"].upper()

    # if dashboard_json["exercise"]:#if exercise add EX to di code
    # 	dashboard_json[" dashboard_grouping_code"] = dashboard_json["dashboard_grouping_code"] + "EX"


    if "dashboard_cycle" not in dashboard_json:
        dashboard_json["dashboard_cycle"] = ""

    dashboard_json["dashboard_smart_code"] = dashboardDAO.getDashboardGroupingCodeCount(user_dn, dashboard_json["dashboard_grouping_code"])
    dashboard_id = dashboard_json["name"] + "_" + str(uuid.uuid4())  # ES ID of dashboard
    dashboard_json["dashboard_id"] = dashboard_id

    if copy_id != "":
        # copy the dashboard
        dashboard_copy = getDashboard(user_dn, copy_id)
        dashboard_copy["dashboard_id"] = dashboard_id
        dashboard_copy["name"] = dashboard_json["name"]
        dashboard_copy["exercise"] = dashboard_json["exercise"]
        dashboard_json = dashboard_copy


        # copy systems with new system_id s.  cache the last system_id before replacing it.
        oldSystemID2newSystemID = {}
        systems = getSystems(user_dn, copy_id)
        for system in systems:
            system_id_old = system["system_id"]
            system["dashboard_id"] = dashboard_id
            system["system_id"] = str(uuid.uuid4())
            dashboardDAO.updateSystem(user_dn, system, system["system_id"])
            oldSystemID2newSystemID.update({system_id_old: system["system_id"]})
            replaceIdsForSystemCopy(dashboard_json["levels"][0], system_id_old, system["system_id"])
            #to do use the oldRSystemID2newSystemID instead

        # copy systemType systems
        systemTypes = sysType.getSystemTypes(user_dn, copy_id)
        oldSystemTypeID2newSystemTypeID = {}
        for systemType in systemTypes:
            systemType = systemType
            systemType_id_old = systemType["systemType_id"]
            del systemType["systemType_id"]
            systemType["dashboard_id"] = dashboard_id
            systemType = sysType.updateSystemType(user_dn, json.dumps(systemType))
            oldSystemTypeID2newSystemTypeID.update({systemType_id_old: systemType["systemType_id"]})
            replaceIdsForSystemTypeCopy(dashboard_json["levels"][0], systemType_id_old, systemType["systemType_id"])


        oldNodeGui2New = copyNodeAndsystemGuid(dashboard_json["levels"][0], copy_records)

        if copy_records == "true":
            recs = r.getRecords(user_dn, copy_id)
            oldRecordID2newRecordID = {}

            for record in recs["records"]:
                record = record
                record["exercise"] = True
                record["dashboard_id"] = dashboard_id
                record_id = record["record_series"] + str(uuid.uuid4())  # ES ID of record
                oldRecordID2newRecordID.update({record['record_id']: record_id})
                record["record_id"] = record_id
                if "system_id" in record:
                    record["system_id"] = oldSystemID2newSystemID[record["system_id"]]
                if "system_type_id" in record:
                    record["system_type_id"] = oldSystemTypeID2newSystemTypeID[record["system_type_id"]]
                if "guid" in record and record["guid"] in oldNodeGui2New:
                    record["guid"] = oldNodeGui2New[record["guid"]]
                if 'group_id' in record and record['group_id'] in oldNodeGui2New['old_guid_2_new']:
                    record['group_id'] = oldNodeGui2New['old_guid_2_new'][record['group_id']]

                rDao.updateRecord(user_dn, record, record_id)

            archived_recs = r.getArchiveRecords(user_dn, copy_id)
            for record in archived_recs:
                record["exercise"] = True
                record["dashboard_id"] = dashboard_id
                record_id = record["record_series"] + str(uuid.uuid4())  # ES ID of record
                record["record_id"] = record_id
                if "record_id_original" in record and record["record_id_original"] in oldRecordID2newRecordID:
                    record["record_id_original"] = oldRecordID2newRecordID[record["record_id_original"]]
                if "system_id" in record:
                    record["system_id"] = oldSystemID2newSystemID[record["system_id"]]
                if "system_type_id" in record:
                    record["system_type_id"] = oldSystemTypeID2newSystemTypeID[record["system_type_id"]]
                if "guid" in record and record["guid"] in oldNodeGui2New:
                    record["guid"] = oldNodeGui2New[record["guid"]]
                if 'group_id' in record and record['group_id'] in oldNodeGui2New['old_guid_2_new']:
                    record['group_id'] = oldNodeGui2New['old_guid_2_new'][record['group_id']]
            rDao.bulkUpdateArchiveRecords(user_dn, archived_recs)


        #copy locations
        locations = l.getLocations(user_dn, copy_id)
        for location in locations:
            location["dashboard_id"] = dashboard_id
            location_id = str(uuid.uuid4())
            location["location_id"] = location_id
            l.updateLocation(user_dn, location)

        # copy classifications
        classifications = c.getClassifications(user_dn, copy_id)
        for classification in classifications:
            classification["dashboard_id"] = dashboard_id
            classification_id = str(uuid.uuid4())
            classification[" classification_id"] = classification_id
            c.updateClassification(user_dn, classification)

        #copy helps
        helps = h.getHelps(user_dn, copy_id)
        for help in helps["helps"]:
            help["dashboard_id"] = dashboard_id
            help_id = str(uuid.uuid4())
            help["help_id"] = help_id
            h.updateHelp(user_dn, help)

    else:
        #set guid on each system/group node
        setNodeAndSystemGuid(user_dn, dashboard_json["levels"][0], nodes)

    dashboard_json = dashboardDAO.createDashboard(user_dn, dashboard_json, dashboard_id)

    # import default help
    # with open('./src/help. json') as f:
    # 	help_ json json. load (f)

    # for help in help_json:
    # 	del help['help_id']
    # 	help["dashboard_id"] = dashboard_id
    #	h.updateHelp(user_dn, json.dumps (help))

    return dashboard_json

# when copying a dashboard, replace ids with new ids or systems.  oldRSystemID2newSystemID maps old system_id to new
def replaceIdsForSystemCopy(obj, id_old, id_new):
    mapped_node_ids = []
    if "nodes" in obj:
        for node in obj["nodes"]:
            if node["type"] == "group" or node["type"] == "system":
                if node["system_id"] == id_old:
                    node["system_id"] = id_new
                    mapped_node_ids.append(node["node_id"])
            mapped_node_ids = mapped_node_ids + replaceIdsForSystemCopy(node, id_old, id_new)
    return mapped_node_ids


'''when copying a dashboard, replace itds with new ids for system types'''
def replaceIdsForSystemTypeCopy(obj, id_old, id_new):
    mapped_node_ids = []
    if "nodes" in obj:
        for node in obj["nodes"]:
            if node["type"] == "system" or node["type"] == "group":
                if "weapon_id" in node:
                    node["systemType_id"] = node["weapon_id"]
                    del node[ "weapon_id"]
                if node["type"] == "group" and "systemType_id" not in node:
                    node["systemType_id"] = None
                if node["systemType_id"] == id_old:
                    node["systemType_id"] = id_new
                    mapped_node_ids.append(node["node_id"])
            mapped_node_ids = mapped_node_ids + replaceIdsForSystemTypeCopy(node, id_old, id_new)
    return mapped_node_ids



'''copying a dashboard, replace ids with new ids for systems and systemType systems'''
def replaceGuidForSystemRecordCopy(obj, record):
    if "nodes" in obj:
        for node in obj["nodes"]:
            if node["type"] == "system":
                record["system_id"] = node["system_id"]
                if "old_guid" in node and record[ "guid"] == node["old_guid"]:
                    record[ "guid"] = node["guid"]
                    del node["old_guid"]
            elif node["type"] == "group":
                record["system_id"] = node["system_id"]
                if "old_guid" in node and record[ "guid"] == node[ "old_guid"]:
                    record["guid"] = node["guid"]
                    del node[ "old_guid"]
                replaceGuidForSystemRecordCopy(node, record)
            else:
                replaceGuidForSystemRecordCopy(node, record)


# def updateSystemGroupId (user_dn, nodes):
#   for node in nodes:
#       if node["type"] == "system":
#           record = findRecord(node["guid"])
#           record[" group_id"] = node[" guid"]

# if "nodes" in obj:
#   for node in obj[" nodes"]:
#       if node["type"] == "group":
#           if "nodes" in node:
#               for system_node in node[" nodes"]:
#                   system_record = r.getRecord (user_dn, system_node["guid"])
#                   system_record[" group_id"] = node[" guid"]
#                   if "record_id" in system_record:
#                       #rDao. updateRecord (user_dn, system_record, system_record["record_id"])
#       else:
#           updateSystemGroupId(user_dn, node)


def updateDashboard(user_dn, dashboard):
    dashboard_json = json.loads(dashboard)
    if "dashboard_cycle" not in dashboard_json:
        dashboard_json["dashboard_cycle"] = ""

    response = dashboardDAO.updateDashboard(user_dn, dashboard_json)

    return response

# look for the record in the global array
def findRecord(guid):
    res = None
    for record in records:
        if record["guid"] == guid:
            res = record
    return res

def getSystemType(systemType_id):
    for systemType in systemTypes:
        systemType = systemType
        if systemType["systemType_id"] == systemType_id:
            return systemType


def flattenHierarchy(obj):
    if "nodes" in obj:
        for node in obj["nodes"]:
            nodes.append (node)
            if node["type"] != "system":
                flattenHierarchy(node)

def updateHierarchy(user_dn, dashboard):
    global records
    global nodes
    global systemTypes
    respp = None
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
                node["guid"] = str(node["node_id"]).replace('-', '').replace('_', '') + str(uuid.uuid4()).replace('-','').replace('_', '')
            record = findRecord(node["guid"])
            if record is not None:
                if "record_static_id" in node:
                    record["record_static_id"] = node["record_static_id"]
                record["record_path"] = getPath(user_dn, dashboard_json, record["guid"])
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

    return records


'''get all the guids from the hierarchy'''
def getAllGUIDsAndSystemIds (obj, guids_and_systems):
    if "nodes" in obj:
        for node in object["nodes"]:
            if node["type"] == "system" or node["type"] == "group":
                item = {"guid": node["guid"], "system_id": node["system_id"]}
                guids_and_systems.append(item)
            getAllGUIDsAndSystemIds(node, guids_and_systems)
    return guids_and_systems

# Import CSV data into hierarchy dashboard with necessary checks
def importHierarchy(user_dn, hierarchy_upload_file):

    try:
        csv_file = pd.read_csv(hierarchy_upload_file.file, sep=",")
        hierarchys = csv_file.to_json(orient="records", date_format="epoch", force_ascii=True, date_unit="ms", default_handler=None)
        hierarchy = json.loads(hierarchys)

        errors = []
        foundTopUnit = False

        # error checking
        for index, item in enumerate(hierarchy):
            if len(item) != 7:
                errors.append(f' There was an issue with row #{index + 1}: {item} Row does not contain all seven required fields (or has more)')



            if item["id"] < 0 or item["parent_id"] < 0:
                errors.append(f' There was an issue with row #{index + 1}: {item} - The id or parent_id field is less than 0')

            if item["parent_id"] == 0 and foundTopUnit == True:
                errors.append(f' There was an issue with row #{index + 1}: {item} - Found an additional top-parent, there can only be one top-parent')

            if item["parent_id"] == 0:
                foundTopUnit = True

            if item["type"] == "unit" and ((item["system_id"] != "") or (item["systemType_id"] != "")):
                errors.append(f' There was an issue with row #{index + 1}: {item} - Units cannot have a system_id or system_type_id')

            if item["type"] == "unit" and (item["record_static_id"] != ""):
                errors.append(f' There was an issue with row #{index + 1}: {item} - A unit cannot have a record_static_id (leave this field as a dash)')

        # sort objects
        hierarchy.sort(key=lambda x: (x["id"], x["parent_id"]))

        #fail if there are errors
        if len(errors) > 0:
            print("There are problems with the imported CSV")
            return {"result": "failed", "message": "Failed with errors", "errors": errors}

        # levels to be returned
        levels = []

        currID = -1
        runThroughIDs = []
        while len(hierarchy) != 0:
            for item in hierarchy:
                # handles top level + all units, groups, and systems below it
                if item["parent_id"] == 0:
                    levels.append({"id": item["id"], "nodes":[], "title": item["name"], "type": "unit"})
                    hierarchy.remove(item)
                    currID = item["id"]
                    for item in hierarchy:
                        if item["parent_id"] == currID:
                            if item["type"].lower() == "unit":
                                levels[0]["nodes"].append({"id": item["id"], "nodes":[], "title": item["name"], "type": "unit"})
                            if item["type"].lower() == "group":
                                levels[0]["nodes"].append({"id": item["id"], "guid": "", "node_id": "", "nodes": [],
                                                           "old_guid": "", "record_static_id": item["record_static_id"],
                                                           "systemType_id": item["system_type_id"], "system_id": item["system_id"],
                                                           "title": item["name"], "item": "group"})
                            if item["type"].lower() == "system":
                                levels[0]["nodes"].append({"id": item["id"], "guid": "", "node_id": "", "nodes": [],
                                                           "old_guid": "", "record_static_id": item["record_static_id"],
                                                           "systemType_id": item["system_type_id"], "system_id": item["system_id"],
                                                           "title": item["name"], "item": "system"})

                            # the following IDs should be run through next...
                            runThroughIDs.append(item["id"])
                            # remove covered items from hierarchy list
                            hierarchy.remove(item)
                    break

                # grab t he length of runThroughIDs before more ids get added to it
                priorLength = len(runThroughIDs)

                # will house ids ran through
                tempContainer = []
                counter = 0
                for id in runThroughIDs:
                    if counter == priorLength:
                        break
                    buildUnderParentID(id, hierarchy, runThroughIDs, levels)
                    tempContainer.append(id)
                    counter += 1

                # remove ids that have been hit already
                for id in tempContainer:
                    runThroughIDs.remove(id)
                break

        deepCheckErrors = []
        # last few checks now that levels has been created
        if deepCheck(levels, False, False, deepCheckErrors) == False:
            print("There are problems with the imported CSV")
            return {"result": "failed", "message": "Failed with errors", "errors": deepCheckErrors}


        # set ids
        flattenHierarchy(levels[0])
        setNodeAndSystemGuid(user_dn, item, nodes)

        return levels
    except Exception as e:
        print(str(e))
        return {"result": "failed", "message": str(e)}

# check if there is an object with a parent_id equal to id
def buildUnderParentID(id, hierarchy, runThroughIDS, levels):
    flag = False
    for item in hierarchy:
        if item["parent_id"] == id:
            flag = True
            break

    # insert item into levels if exists
    if flag == True:
        # temporary container to house all items that've been appended into the levels list
        tempContainer = []
        for item in hierarchy:
            if item["parent_id"] == id:
                levelsInsert(item, id, levels)
                tempContainer.append(item)
                runThroughIDS.append(item["id"])

        # remove items that have been added to the levels list
        for item in tempContainer:
            hierarchy.remove(item)

# recursive function searching nested objects to add desired item from hierarchy into levels list
def levelsInsert(itemToInsert, idToInsertInto, levels):
    currID = -1
    for index in range (len(levels)):
        currID = levels [index]["id"]
        if currID == idToInsertInto and itemToInsert["parent_id"] == currID:
            if itemToInsert["type"].lower() == "unit":
                return levels[index]["nodes"]. append({"id": itemToInsert["id"], "nodes": [], "title": itemToInsert["name"], "type": "unit"})
            elif itemToInsert["type"].lower() == "group":
                return levels[index]["nodes"].append(
                    {"id": itemToInsert["id"], "guid": "", "node_id":"", "nodes": [], "old_guid": "",
                     "record_static_id": itemToInsert["record_static_id"], "systemType_id": itemToInsert["system_type_id"],
                     "system_id": itemToInsert["system_id"], "title": itemToInsert["name"], "type": "group"})
            elif itemToInsert["type"]. lower() == "system":
                return levels[index]["nodes"]. append(
                    {"id": itemToInsert["name"], "guid": "", "node_id": "", "nodes": [], "old_guid": "",
                     "record_static_id": itemToInsert["record_static_id"],
                     "systemType_id": itemToInsert["system_type_id"],
                     "system_id": itemToInsert["system_id"], "title": itemToInsert["name"], "type": "system"})
        if isinstance (levels[index]["nodes"], list):
            # if function finds levels[index]["nodes"] to be a list then search through it more
            levelsInsert(itemToInsert, idToInsertInto, levels[index]["nodes"])

def deepCheck(levels, flag1, flag2, deepCheckErrors):
    for index in range(len(levels)):
        # groups and systems cannot have a unit beneath them
        if flag1 == True and levels[index]["type"] == "unit":
            deepCheckErrors.append("Groups and systems cannot have a unit below them")
            return False
        if levels[index]["type"] == "group" or levels[index]["type"] == "system":
            flag1 = True

        # systems cannot have a group beneath them
        if flag2 == True and levels[index]["type"] == "group":
            deepCheckErrors.append("Systems cannot have a group below them")
            return False
        if levels[index]["type"] == "system":
            flag2 = True

        if isinstance(levels[index]["nodes"], list) and len(levels[index]["nodes"]) > 0:
            deepCheck(levels[index]["nodes"], flag1, flag2, deepCheckErrors)


'''
create a unique id for each system and group node (GUID). this will be attached the system record (record), so the
record knows which node it belongs to. If copying a structure, the old GUID is retained So it can be attached to the copied
system record. Also stores the path/heirarchy at each node level. Also ensures static ids are updated across records
'''
def setNodeAndSystemGuid(user_dn, dashboard, nodes):
    for node in nodes:
        if "node_id" not in node or node["node_id"] == "":
            node["node_id"] = uuid.uuid4()
        if "guid" not in node or node["guid"] == "":
            node["guid"] = str(node["node_id"]).replace('-', '').replace('_', '')+ str(uuid. uuid4()).replace('-', ''). replace('-', '')
        record = findRecord (node["guid"])
        if record is not None:
            record["record_static_id"] = node["record_static_id"]
            record["record_path"] = getPath(user_dn, dashboard, record["guid"])
            record["system_title"] = node["title"]
            record["system_id"] = node["system_id"]


# regenerate guid and node_id
def copyNodeAndsystemGuid(obj, copy_records):
    answer = {}
    if "nodes" in obj:
        for node in obj ["nodes"]:
            new_id = uuid.uuid4()
            node["node_id"] = new_id
            if "guid" in node:
                if copy_records == "true": #only create old_guid if copying records records
                    node["old_guid"] = node["guid"]
                node["guid"] = str(node["node_id"]).replace('-', '').replace('_', '') + str(uuid. uuid4()).replace('-', ''). replace('_', '')
                answer.update({node["old_guid"]: node["guid"]})
            answer.update(copyNodeAndsystemGuid(node, copy_records))
    return answer


def updateSystem(user_dn, system):
    system_json = json.loads(system)
    create = False
    if "system_id" not in system_json or system_json["system_id"] == "":
        create = True
        system_id = str(uuid.uuid4())
        system_json["system_id"] = system_id
    else:
        system_id = system_json["system_id"]

    for section in system_json["sections"]:
        for field in section["fields"]:
            field["order"] = int(field["order"])
    dashboardDAO.updateSystem(user_dn, system_json, system_id)

    if system_json["type"] == "group" and create is True:
        system_json["type"] = "system"
        system_json["name"] = system_json["name"] + "-SYSTEM"
        system_id = str(uuid.uuid4())
        system_json["system_id"] = system_id
        dashboardDAO.updateSystem(user_dn, system_json, system_id)
    return system_json


def getSystems(user_dn, dashboard_id):
    return dashboardDAO.getSystems(user_dn, dashboard_id)


def getSystem(user_dn, id):
    return dashboardDAO.getSystem(user_dn, id)


def deleteSystem (user_dn, system_id):
    records = rDao.getRecordsBySystemId(user_dn, system_id)

    if len(records) > 0:
        dashboardDAO.deleteSystem(user_dn, system_id)
        return {"result": "success", "message": "Success"}
    else:
        return {"result": "fail", "message": "System Records Exist"}



def getGroupSystems (user_dn, dashboard_id, guid):
    dashboard = dashboardDAO.getDashboard(user_dn, dashboard_id)
    group = getNodeByValue(dashboard, "guid", guid)
    return group

def getNodeByValue(obj, field, value):

    val = None
    if "levels" in obj:
        for item in obj["levels"]:
            tmp = getNodeByValue(item["nodes"], field, value)
            if val is None and tmp is not None:
                val = tmp
    else:
        for item in obj:
            if field in item:
                if item[field] == value:
                    val = item
                    return val
            if "nodes" in item:
                tmp = getNodeByValue(item["nodes"], field, value)
                if val is None and tmp is not None:
                    val = tmp
            else:
                return None
    return val


def getDashboardDetails (user_dn, dashboard_id):
    details = dashboardDAO.getDashboardDetails(user_dn, dashboard_id)
    details["time_series"] = rec.getTimeSeriesRecords (user_dn, details["dashboard_id"], details["exercise"])
    return details



def getPath (user_dn, dashboard, guid):
    global systemTypes
    path = ""
    try:
        if len(systemTypes) == 0:
            systemTypes = sysTypeDAO.getSystemTypes(user_dn, dashboard["dashboard_id"])
        path = findPath(user_dn, dashboard["levels"][0], guid, dashboard["dashboard_id"])
    except Exception as e:
        print ("FAILED TO GET PATH FOR GUID" + guid)
    return path


# find node by guid
def find_node(root_node, guid):
    if 'guid' in root_node and root_node['guid'] == guid:
        return root_node
    for n in (root_node['nodes'] if 'nodes' in root_node else []):
        if (ans := find_node(n, guid)) is not None:
            return ans
    return None


def find_node_path(root_node, path_parsed):
    if root_node['title'] != path_parsed[0]:
        return None
    if len(path_parsed) == 1 and root_node['title'] == path_parsed[0]:
        return root_node
    for n in root_node['nodes']:
        if (ans := find_node_path(n, path_parsed[1:])) is not None:
            return ans
    return None


#find the full path name from given object (dashboard.levels[0])
def findPath(user_dn, obj, guid, dashboard_id):
    global systemTypes
    if len(systemTypes) == 0:
        systemTypes = sysTypeDAO.getSystemTypes(user_dn, dashboard_id)
    path = ""
    if "nodes" in obj:
        for node in obj["nodes"]:

            if "system_id" in node and node["system_id"] is not None and "guid" in node and node["guid"] == guid:
                if node["type"] == "system" or node["type"] == "group":
                    if "systemType_id" not in node or node["systemType_id"] is None:
                        return node["title"] + "(missing system type)"
                    else:
                        systemType = getSystemType(node["systemType_id"])
                        value = ""

                        try:
                            value = node["title"] + " (" + systemType["name"] + ")"
                        except Exception as e:
                            print("FAILED TO FIND PATH FOR:")
                            print(node["title"])
                            print(systemType)
                        return value
                else:
                    return node["title"]
            else:
                res = findPath(user_dn, node, guid, dashboard_id)
                if res != "":
                    path = path + node["title"] + "/" + res


    return path



def updateSystemGroupId(nodes):
    for node in nodes:
        if node["type"] == "system":
            if "guid" in node:
                record = findRecord (node["guid"])
                if record is not None :
                    record["group_id"] = node["guid" ]



def exportDashboard(user_dn, dashboard_id):

    dashboard = dashboardDAO.getDashboard(user_dn, dashboard_id)
    dashboard["groups"] = []
    dashboard["systems"] = dashboardDAO.getSystems(user_dn, dashboard_id)
    dashboard["systemTypes"] = sysType.getSystemTypes(user_dn, dashboard_id)
    dashboard["records"] = r.getRecords(user_dn, dashboard_id)["records"]
    dashboard["locations"] = l.getLocations(user_dn, dashboard_id)
    dashboard["classifications"] = c.getClassifications(user_dn, dashboard_id)
    dashboard["helps"] = h.getHelps(user_dn, dashboard_id)["helps"]
    # dashboard["record_archive"] = r.getArchiveRecords (user_dn, dashboard_id)


    # for system in systems:
    #   system = system
    #   dashboard[" systems"]. append(system)


    # for systemType in systemTypes:
    #   systemType = systemType
    #   dashboard[" systemTypes"]. append(systemType)
    return dashboard

def upload_dashboard_original(user_dn, upload_file):
    global nodes
    global records
    try:
        dashboard = json.loads(upload_file.file)
        records = dashboard['records']
        archievd_records = dashboard['record_archive']
        systems = dashboard["systems"]
        for system in systems:
            dashboardDAO.updateSystem(user_dn, system, system["system_id"])
        system_types = dashboard["systemTypes"]
        for systemType in system_types:
            sysType.updateSystemType(user_dn, json.dumps(systemType))
        for record in archievd_records:
            if 'system_type_id' not in record:
                node = find_node_path(dashboard['levels'][0], ['TopUnit'] + record['record_path'].split('/'))
                record['system_type_id'] = node['systemType_id']

        rDao.bulkUpdateRecords(user_dn, records)
        return dashboard
    except Exception as e:
        stk = traceback.format_exc()
        print(stk)
        return {"status": "failed"}


def uploadDashboard(user_dn, upload_file):
    global nodes
    global records
    try:
        dashboard = json.load(upload_file.file)
        records = dashboard["records"].copy()
        archivedRecords = dashboard["record_archive"].copy() if "record_archive" in dashboard else []
        dashboard["name"] = dashboard["name"] + "-I"
        oldSmartCode = dashboard["dashboard_smart_code"]
        dashboard["dashboard_smart_code"] = dashboardDAO.getDashboardGroupingCodeCount(user_dn, dashboard["dashboard_grouping_code"])
        dashboard_id = dashboard["name"] + "_" + str(uuid.uuid4()) # ES ID of dashboard

        #copy the dashboard
        dashboard["dashboard_id"] = dashboard_id


        #copy systems with new system_id s. cache the last system_id before replacing it.
        oldSystemID2newSystemID = {}
        systems = dashboard["systems"]
        answer = {"nodes_translated_system_id": {"mapped": {}, "not_mapped": {}}, "node_ids_mapped": []}
        for system in systems:
            system_id_old = system["system_id"]
            system["dashboard_id"] = dashboard_id
            system["system_id"] = str(uuid.uuid4())
            dashboardDAO.updateSystem(user_dn, system, system["system_id"])
            oldSystemID2newSystemID.update({system_id_old: system["system_id"]})
            mapped_n_ids = replaceIdsForSystemCopy(dashboard["levels"][0], system_id_old, system["system_id"])
            if len(mapped_n_ids)  > 0:
                answer["node_ids_mapped"] = answer["node_ids_mapped"] + mapped_n_ids
                answer["nodes_translated_system_id"]["mapped"].update({system_id_old: system["system_id"]})
            else:
                answer["nodes_translated_system_id"]["not_mapped"].update({system_id_old: system["system_id"]})


        if "systemTypes" not in dashboard:
            systemTypes = dashboard["weapons"]
        else:
            systemTypes = dashboard["systemTypes"]

        oldSystemTypeID2newSystemTypeID = {}
        answer.update({"nodes_translated_systemType_id": {"mapped": {}, "not_mapped": {}}, "node_ids_mapped_sysTyp": []})
        for systemType in systemTypes:
            if "weapon_id" in systemType:
                systemType["systemType_id"] = systemType["weapon_id"]
                del systemType["weapon_id"]
            systemType_id_old = systemType["systemType_id"]
            systemType["systemType_id"] = str(uuid.uuid4())
            systemType["dashboard_id"] = dashboard_id
            systemType = sysType.updateSystemType(user_dn, json.dumps(systemType))
            oldSystemTypeID2newSystemTypeID.update({systemType_id_old: systemType["systemType_id"]})
            mapped_n_ids = replaceIdsForSystemTypeCopy(dashboard["levels"][0], systemType_id_old, systemType["systemType_id"])
            if len(mapped_n_ids) > 0:
                answer["node_ids_mapped_sysTyp"] = answer["node_ids_mapped_sysTyp"] + mapped_n_ids
                answer["nodes_translated_systemType_id"]["mapped"].update({systemType_id_old: systemType["systemType_id"]})
            else:
                answer["nodes_translated_systemType_id"]["not_mapped"].update({systemType_id_old: systemType["systemType_id"]})

        answer.update({"node_guid_translated":
                           copyNodeAndsystemGuid(dashboard["levels"][0], "true") })
        oldNodeGui2New = answer["node_guid_translated"]

        # pull out data
        if "locations" in dashboard:
            locations = dashboard["locations"].copy()
            del dashboard["locations"]
        else:
            locations = []

        if "classifications" in dashboard:
            classifications = dashboard["classifications"].copy()
            del dashboard["classifications"]
        else:
            classifications = []

        if "helps" in dashboard:
            helps = dashboard["helps"].copy()
            del dashboard["helps"]
        else:
            helps = []

        # dashboard must exist before adding records. cleanup and add
        del dashboard["systems"]
        if "systemTypes" in dashboard:
            del dashboard["systemTypes"]
        del dashboard["records"]
        if "record_archive" in dashboard:
            del dashboard["record_archive"]

        dashboard_json = dashboardDAO.createDashboard(user_dn, dashboard, dashboard_id)

        # wait for dashboard to be added
        time.sleep(2)

        # cache the last record id before replacing it.
        oldRecordID2newRecordID = {}

        # massage the records to put in new record_id
        record_series = r.getRecordSeries(user_dn, dashboard_id)
        answer.update({"record_system_id_translated": 0, "record_guid_translated": 0, "record_systemType_id_translated": 0 })
        for record in records:
            record["dashboard_id"] = dashboard_id
            record_id = record["record_series"] + "_" + str(uuid.uuid4())  # ES ID of record
            if len(archivedRecords) == 0:
                record["tracking_id"] = None
                record["record_version"] = 1
            oldRecordID2newRecordID.update({record["record_id"]: record_id})
            record["record_id"] = record_id
            record["record_series"] = record_series
            # replaceGuidForSystemRecordCopy replaces system_id and guid
            if "system_id" in record:
                record["system_id"] = oldSystemID2newSystemID[record["system_id"]]
                answer["record_system_id_translated"] += 1
            if "systemType_id" in record:
                record["system_type_id"] = oldSystemTypeID2newSystemTypeID[record["system_type_id"]]
                answer["record_systemType_id_translated"] += 1
            if "guid" in record and record ["guid"] in oldNodeGui2New:
                record["guid"] = oldNodeGui2New[record["guid"]]
                answer["record_guid_translated"] += 1
            if "group_id" in record and record["group_id"] in oldNodeGui2New:
                record["group_id"] = oldNodeGui2New[record["group_id"]]

            # for item in dashboard["levels"]:
            #     replaceGuidForSystemRecordCopy(item, record) replaceGuidForSystemRecordCopy IS WRONG
            # rDao.updateRecord (user_dn, record, record_id)
        rDao.bulkUpdateRecords(user_dn, records)
        answer.update({"recordsSize": len(records), "archivedRecordsSize": len(archivedRecords),
                       "archivedRecordsNotOriginalRecIDSize": 0, "dashboard": dashboard_json,
                       "records": records})

        # massage the archive to correct the original_record_id
        for rec in archivedRecords:
            rec["dashboard_id"] = dashboard_id
            rec["record_series"] = record_series
            rec["record_id"] = rec["record_series"] + "_" + str(uuid.uuid4()) # ES ID of record
            if "record_id_original" in rec and rec["record_id_original"] in oldRecordID2newRecordID:
                rec["record_id_original"] = oldRecordID2newRecordID[rec["record_id_original"]]
                answer["archivedRecordsNotOriginalRecIDSize"] += 1
            if "system_id" in rec:
                rec["system_id"] = oldSystemID2newSystemID[rec["system_id"]]
                answer["archive_record_system_id_translated"] += 1
            if "systemType_id" in rec:
                rec["system_type_id"] = oldSystemTypeID2newSystemTypeID[rec["system_type_id"]]
                answer["archive_record_systemType_id_translated"] += 1
            if "guid" in rec and rec["guid"] in oldNodeGui2New:
                rec["guid"] = oldNodeGui2New[rec["guid"]]
                answer["archive_record_guid_translated"] += 1
            if "group_id" in rec and rec["group_id"] in oldNodeGui2New:
                rec["group_id"] = oldNodeGui2New[rec["group_id"]]
        rDao.bulkUpdateArchiveRecords(user_dn, archivedRecords)

        time.sleep(1)  # wait for records to be updated
        flattenHierarchy(dashboard["levels"][0])
        updateSystemGroupId(nodes)

        # copy locations
        for location in locations:
            location["dashboard_id"] = dashboard_id
            location_id = str(uuid.uuid4())
            location["location_id"] = location_id
            l.updateLocation(user_dn, location)

        #copy classifications
        for classification in classifications:
            classification["dashboard_id"] = dashboard_id
            classification_id = str(uuid.uuid4())
            classification["classification_id"] = classification_id
            c.updateClassification(user_dn, classification)

        #copy helps
        for help in helps:
            help["dashboard_id"] = dashboard_id
            help_id = str(uuid.uuid4())
            help["help_id"] = help_id
            h.updateHelp(user_dn, help)


        return answer
    except Exception as e:
        stk = traceback.format_exc()
        print(stk)
        return {"status": "failed"}

def doCleanUp(user_dn, dashboard_id):
    dashboard = getDashboard(user_dn, dashboard_id)
    if "levels" in dashboard:
        for item in dashboard["levels"]:
            cleanupsystem_type_ids(item)
        dashboardDAO.updateDashboard(user_dn, dashboard)

    return {"result": "done"}

def cleanupsystem_type_ids(obj):
    if "nodes" in obj:
        for node in obj["nodes"]:
            if node["type"] == "system" or node["type"] == "group":
               if "weapon_id" in node:
                    node["systemType_id"] = node["weapon_id"]
                    del node["weapon_id"]

            cleanupsystem_type_ids(nodes)