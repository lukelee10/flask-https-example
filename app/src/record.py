
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
from flask_mail import Message
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

        for section in system["sections"]:
            for field in section ["fields"]:
                if "default_value" in field:
                    record[field["name"]] = field["default_value"]
                elif field["type"] == "date":
                    record[field["name"]] = None
                else:
                    record[field["name"]] = ""

        record["system_id"] = system["system_id"]
        record[" guid"] = guid
        record["update_date"] = datetime.datetime.now()
        record["dashboard_id"] = system[" dashboard_id"]
        record["dashboard_grouping_code"] = dashboard["dashboard_grouping_code"]
        record["exercise"] = exercise
        record["record_series"] = record_series
        record["record_classification"] = None
        record["record_version"] = 1
        record["update_version"] = 1
        record["dashboard_cycle"] = dashboard["dashboard_cycle"]
        record["record_type"] = system["type"]
        record["tracking_id"] = None
        # brand new record.  copy the classification from default
        record["classification"] = system["classification"]

    if "record_classification" not in record:
        record["record_classification"] = None
    # record["record_path"] = dsh.getPath(user_dn, dashboard_id, guid)

    for section in system["sections"]:
        for field in section ["fields"]:
            if field["name"] + "_classification" not in record:
                record[field["name"] + "_classification"] = field["classification"]

    resp = {"record": record, "record_form": system}

    # if group get systems for select "group" updates
    if record["record_type"] == "group":
        systems = dsh.getGroupSystems(user_dn, record["dashboard_id"], guid)
        if systems is not None:
            resp[" systems"] = systems["nodes"]

    return resp

def getRecordById(user_dn, record_id) :
    return rDao.getRecordByRecordId(user_dn, record_id)

def getRecord(user_dn, guid):
    # get the strat lead if it exists
    record = rDao.getRecord(user_dn, guid)

    resp = record

    return resp


'''
return records from a list of record_ids
'''
def getRecordsFromList(user_dn, rec_list):
    rec_list = json.loads(rec_list)

    resp = {"records": []}

    resp = rDao.getRecordsFromIds(user_dn, rec_list)
    return resp



def getActiveRecords(user_dn, rec_list):
    rec_list = json.loads(rec_list)

    return rDao.getRecordsFromIds(user_dn, rec_list)


def getTimeSeriesRecords(user_dn, dashboard_id, exercise):
    if exercise == "false":
        exercise = False
    elif exercise == "true":
        exercise = True
    dashboard = dashboardDAO.getDashboard(user_dn, dashboard_id)

    results = {"groups":[], "activity":[], "activated":[], "final": []}

    group = {
        "id": 1,
        "name": "Activity",
        "color": "green"
    }
    results["groups"].append(group)

    group = {
        "id": 2,
        "name": "Activated",
        "color": "red"
    }
    results["groups"].append(group)

    group = {
        "id": 3,
        "name": "Final",
        "color": "blue"
    }
    results["groups"].append (group)

    items = rDao.getTimeSeriesRecords(user_dn, dashboard["dashboard_id"])
    for item in items:
        item["group_1d"] = 1
        results["activity"].append(item)

    items = rDao.getActivatedTimeSeriesRecords(user_dn,dashboard["dashboard_id"])
    for item in items:
        item["group_1d"] = 2
        results["activated"].append(item)

    items = rDao.getFinalTimeSeriesRecords(user_dn, dashboard["dashboard_id"])
    for item in items:
        item["group_id"] = 3
        results["final"].append(item)

    return results




def getSystemType(obj, guid):
    guid_found = None
    for node in obj["nodes"]:
        if "guid" in node and node["guid"] ==  guid:
            guid_found = node["systemType_id"]
        if "node" in node and guid_found == None:
            guid_found = getSystemType(node, guid)

    return guid_found

def updateRecord(user_dn, action, update_group, set_default, record, create_tracking_id):
    if type(record) == str:
        record = json.loads(record)

    # audit_date tracks datetime of any changes
    print("record:updateRecord.", action, update_group, set_default, create_tracking_id, sep=" | ")
    record["audit_date"] = datetime.datetime.now()
    record["last_updated_by"] = user_dn

    #update system name and system type
    system = dashboardDAO.getSystem(user_dn, record["system_id"])
    dashboard = dashboardDAO.getDashboard(user_dn, system["dashboard_id"])
    record["system_name"] = system["name"]
    system_type_id = getSystemType(dashboard["levels"][0], record["guid"])
    record["system_type_id"] = system_type_id
    system_type = systemTypeDAO.getSystemType(user_dn, system_type_id)
    record["system_type"] = system_type["name"]

    # convert date string to date obj for ES
    if record["record_event_date"] == "Invalid date":
        record["record_event_date"] = None
    if record["record_event_date"] is not None:
        dt = parser.parse(record["record_event_date"])
        record["record_event_date"] = dt

    if record["record_source_date"] == "Invalid date":
        record["record_source_date"] = None
    if record["record_source_date"] is not None:
        dt = parser.parse(record["record_source_date"])
        record["record_source_date"] = dt


    #create archive of record
    if action != "create" and action != "modify" and action != "timeout":
        original_record = rDao.getRecord(user_dn, record["guid"])
        createArchive(user_dn, original_record, True)

    # add decimal values for DMS lat/long
    record = convertDMStoDecimal(record)

    # determine state
    if action == "create":
        record["record_state"] = "create"
    elif action == "update" or action == "update_to_group":
        record["record_state"] = "update"
    elif action == "timeout":
        record["record_state"] = "timeout"
        record["record_found"] = "no"
    elif action == "final":
        record["record_state"] = "final"
    if "tracking_id" not in record:
        record["tracking_id"] = None
    if action == "update_to_group":
        group_record = rDao.getRecord(user_dn, record["group_id"])
        new_system_record = copy.deepcopy(group_record)
        new_system_record["group_id"] = record["group_id"]
        new_system_record["record_type"] = record["record_type"]
        new_system_record["timeout_level"] = 0
        new_system_record["system_id"] = record["system_id"]
        new_system_record["guid"] = record["guid"]
        new_system_record["record_id"] = record["record_id"]
        new_system_record["record_static_id"] = record["record_static_id"]
        new_system_record["record_version"] = record["record_version"] + 1
        new_system_record["update_version"] = record["update_version"] + 1
        new_system_record["update_date"] = datetime.datetime.now()
        rDao.updateRecord(user_dn, new_system_record, new_system_record["record_1d"])

    else:
        # if an update, or final, create record_version and archive record
        if action == "update":
            record["timeout_level"] = 0
            record["record_version"] = int(record["record_version"]) + 1  # up record_version
            if "update_version" not in record:
                record["update_version"] = record["record_version"]
            else:
                record["update_version"] = int(record["update_version"]) + 1  # up update_version
            record["update_date"] = datetime.datetime.now()

            # if "record_static_id" not in record or record["record_static_id"] == "":
            #   record["record_static_id"] = record["record_id"]

            if create_tracking_id == "yes":
                # if record["tracking_id"] == None or record["tracking_id"] == "":
                record["tracking_id"] = getNextTrackingId(user_dn, record["dashboard_id"])
                record["record_state"] = "initial"  # set to initial if first time setting tracking id
            # #create new startled id if lat and long are different
            # if record["record_type"] == "system":
            #   if "group_id" in record:
            #       group_record = rDao.getRecord(user_dn, record["group_id"])
            #       if create_tracking_id == "yes":
            #           record["tracking_id"] = getNextTrackingId(user_dn, record[" dashboard_id"

            # check to see that the record tracking id exists, if it does, make sure its not null or empty
            # ./


            if set_default == "true":
                record = setDefaultRecord(record)

            rDao.updateRecord(user_dn, record, record["record_id"])
        elif action == "final":
            record["timeout_level"] = 0
            record["record_event_date"] = None
            record["record_source_date"] = None
            if "default_values" in record:
                for key, value in record["default_values"].items():
                    record[key] = value

            record["comments"] = ""
            record["record_version"] = 0  # up record_version
            record["update_date"] = datetime.datetime.now()
            if "tracking_id" in record:
                record["tracking_id"] = None
            # replace record classification with system's classification
            record["classification"] = system["classification"]
            for section in system["sections"]:
                for field in section["fields"]:
                    record[field["name"] + "_classification"] = field["classification"]
            rDao.updateRecord(user_dn, record, record["record_id"])
        elif action == "create":
            record_id = record["record_series"] + "_" + str(uuid.uuid4())  # ES ID of record
            record["record_id"] = record_id
            # record["record_static_id"] = record_id
            record["timeout_level"] = 0
            record["update_date"] = datetime.datetime.now()

            rDao.createRecord(user_dn, record, record_id)
        elif action == "timeout": # do not create archive or record_version
            record["timeout_level"] = 1
            rDao.updateRecord(user_dn, record, record["record_id"])
        elif action == "modify": # do not create archive or record_version
            if set_default == "true":
                record = setDefaultRecord(record)
            rDao.updateRecord(user_dn, record, record["record_id"])

        updateSystemsOfGroup(user_dn, action, record, json.loads(update_group), set_default)



    return record


#creates a default copy of the record within the record for setting default values when status is set to final
def setDefaultRecord(record):
    if "default_values" in record:
        del (record["default_values"])
    record[" default_values"] = {}
    for key, value in record.items():
        if "record_" in key or "comment" == key or "classification" == key:
            if key != "record_id" and key != "record_version" and key != "record_type" and key != "record_state":
                record["default_values" ][key] = value

    return record

def updateSystemsOfGroup (user_dn, action, group_record, selected_systems, set_default):
    '''
    copy group record and create for each system. delete record if there is one
    '''
    dashboard = dashboard = dashboardDAO.getDashboard(user_dn, group_record["dashboard_id"])
    systems = dsh.getGroupSystems(user_dn, group_record["dashboard_id"], group_record[" guid"])
    for system in systems["nodes"]:

        if system["guid"] in selected_systems:
            system_record = rDao.getRecord(user_dn, system["guid"])
            if "noresults" in system_record or action == "create":
                record = copy.deepcopy(group_record)
                record["record_type"] = system["type"]
                # record["record_path"] = dsh.getPath(user_dn, dashboard, system["guid"])
                record["system_id"] = system["system_id"]
                record["group_id"] = group_record["guid"]
                record["guid"] = system["guid"]
                record_id = group_record["record_series"] + "_" + str(uuid.uuid4())
                record["record_id"] = record_id
                # record["record_static_id"] = record_id
                #update system name and system type
                system_obj = dashboardDAO.getSystem(user_dn, record["system_id"])
                dashboard = dashboardDAO.getDashboard(user_dn, system_obj["dashboard_id"])
                record["system_name"] = system_obj["name"]
                system_type_id = getSystemType(dashboard["levels"][0], record["guid"])
                record["system_type_id"] = system_type_id
                system_type = systemTypeDA0.getSystemType(user_dn, system_type_id)
                record["system_type"] = system_type["name"]

                rDao.createRecord(user_dn, record, record_id)

            elif action == "update":
                createArchive(user_dn, system_record, True)

                new_system_record = copy.deepcopy(group_record)
                # update system name and system type
                system_obj = dashboardDAO.getsystem(user_dn, system_record["system_id"])
                dashboard = dashboardDAO.getDashboard(user_dn, system_record["dashboard_id"])
                system_type_id = getSystemType(dashboard["levels"][0], system_record["guid"])
                new_system_record["system_name"] = system_obj["name"]
                new_system_record["system_type_1d"] = system_type_id
                system_type = systemTypeDAO.getSystemType(user_dn, system_type_id)
                new_system_record["system_type"] = system_type["name"]

                new_system_record["group_id"] = group_record["guid"]
                new_system_record["record_type"] = system["type"]
                new_system_record["timeout_level"] = 0
                new_system_record["system id"] = system["system_id"]
                new_system_record["guid"] = system["guid"]

                # reset system specific data
                new_system_record["record_id"] = system_record["record_id"]
                if "record_static_id" in system_record and system_record["record_static_id"] != "":
                    new_system_record["record_static_id"] = system_record["record static_id"]

                new_system_record["record path"] = system_record["record_path"]

                new_system_record["record_version"] = system_record["record_version"] + 1
                if "update_version" not in system_record:
                    new_system_record["update_version"] = system_record["record_version"]
                else:
                    new_system_record["update_version"] = system_record["update_version"] + 1
                new_system_record["update_date"] = datetime.datetime.now()

                # undo any fields marked as DO NOT update from group
                system = dashboardDAO.getSystem(user_dn, system_record[" system_id"])
                for section in system["sections"]:
                    for field in section["fields"]:
                        if "disable_group_edit" in field and field["disable_group_edit"] == True:
                            new_system_record[field["name"]] = system_record[field["name"]]
                            if field["name"] + "_classification" in system_record:
                                new_system_record[field["name"] + "_classification"] = system_record[field["name"] + "_classification"]

                if set_default == "true":
                    new_system_record = setDefaultRecord(new_system_record)
                else:
                    if "default_values" in system_record:
                        if "default_values" in new_system_record:
                            del(new_system_record["default_values"])
                        new_system_record["default_values"] = system_record["default_values"]
                rDao.updateRecord(user_dn, new_system_record, new_system_record["record_id"])
            elif action == "final":
                createArchive(user_dn, system_record, True)

                if "default_values" in system_record:
                    for key, value in system_record["default_values"].items():
                        system_record[key] = value
                    new_system_record = system_record
                    print("updateSystemsOfGroup: has default_values", new_system_record)
                else:
                    new_system_record = copy.deepcopy(group_record)
                    new_system_record["group_id"] = group_record["guid"]
                    new_system_record["record_type"] = system["type"]
                    new_system_record["timeout_level"] = 0
                    new_system_record["system_id"] = system["system_id"]
                    new_system_record["guid"] = system["guid"]
                    new_system_record["record_id"]: system_record["record_id"]
                    new_system_record["record_static_id"] = system_record["record_static_id"]
                    new_system_record["update_date"] = datetime.datetime.now()
                    print("updateSystemsOfGroup: NO default_values", new_system_record)

                new_system_record["record version"] = 0
                new_system_record["record_state"] = "final"
                if "update_version" not in new_system_record:
                    new_system_record["update_version"] = new_system_record["record_version"]
                else:
                    new_system_record["update_version"] = int(new_system_record["update_version"]) + 1  # up update_version None
                new_system_record["record_event_date"] = None
                new_system_record["record_source_date"] = None
                if "tracking_id" in new_system_record:
                    new_system_record["tracking_id"] = None
                rDao.updateRecord(user_dn, new_system_record, new_system_record["record_id"])

            elif action == "timeout":   # do not create archive or record_version
                system_record["record _state"] = "timeout"
                system_record["record_found"] = "no"
                system_record["timeout_level"] = 1

                rDao.updateRecord(user_dn, system_record, system_record["record_id"])




def createArchive (user_dn, record, save):
    archive_copy = copy.deepcopy(record)
    archive_copy["record_id_original"] = archive_copy["record_id"]
    new_record_id = archive_copy["record_series"] + "_" + str(uuid.uuid4())
    archive_copy["record_id"] = new_record_id
    archive_copy["audit_date"] = datetime.datetime.now()
    if save is True:
        rDao.archiveRecord(user_dn, archive_copy, new_record_id)
    else:
        return archive_copy



def getRecords(user_dn, dashboard_id) :
    return rDao.getRecords(user_dn, dashboard_id)

def getArchiveRecords(user_dn, dashboard_id) :
    return rDao.getArchiveRecords(user_dn, dashboard_id)

def getMetricsData(user_dn):
    metrics = {"histogram": {"dashboards": [], "data": []}}
    metrics ["histogram"]["data"] = rDao.getArchiveHistogram(user_dn)
    for item in metrics[ "histogram" ]["data"]:
        dashboard = {"id": item["id"], "color": item["color"], "name": item[" name"]}
        if dashboard not in metrics["histogram"][" dashboards"]:
            metrics["histogram"]["dashboards"].append(dashboard)
    return metrics


def getNextTrackingId(user_dn, dashboard_id):
    record_series = getRecordSeries(user_dn, dashboard_id)
    last_sl = rDao.getLastRecord(user_dn, dashboard_id)
    if "noresults" in last_sl:
        tracking_id = record_series + "0001"

    else:
        last_id = last_sl["tracking_id"]
        last_archive = rDao. getLastArchiveRecord (user_dn, dashboard_id)
        if "noresults" in last_archive:
            archive_count = 0
        else:
            last_archive_id = last_archive["tracking_id"]
            print("record: getNextTrackingId. (last_id) (last_archive_id)", last_id, last_archive_id, sep=" | ")
            archive_count = int(last_archive_id[-4:])
        count = int(last_id[-4:])
        count = count + 1

        if count > archive_count :
            count = str(count).zfill(4)
        else:
            count = archive_count + 1
            count = str(count).zfill(4)

        tracking_id = record_series + count

    return tracking_id


def getLastUpdatedRecord(user_dn, rec_list):

    rec_list = json.loads(rec_list)
    last_sl = rDao.getLastUpdatedRecord(user_dn, rec_list)

    if "noresults" in last_sl:
        res = {"cao": "not available"}

    else:
        res = {"cao": last_sl["update_date"]}

    return res


def getTimeoutRecords(user_dn, dashboard_id):
    return rDao.getTimeoutRecords(user_dn, dashboard_id)

def getRecordSeries (user_dn, dashboard_id):
    now = datetime.datetime.now()
    year = str(now.year)[-2:]
    dashboard = dashboardDAO.getDashboardDetails(user_dn, dashboard_id)
    dashboard_grouping_code = dashboard["dashboard_grouping_code"]
    smart_code = dashboard["dashboard_smart_code"]

    record_series = smart_code + year + dashboard_grouping_code

    return record_series



def deleteRecordById (user_dn, record_id):
    return rDao. deleteRecordByid (user_dn, record_id)


def deleteRecordsByGuid(user_dn, guid):
    return rDao. deleteRecordsByGuid (user_dn, guid)


'''
export records to CSV from a list of record_ids
'''
def export(user_dn, rec_list):
    rec_list = json.loads(rec_list)
    resp = []

    for record_id in rec_list:
        record = rDao.getRecordByRecordId(user_dn, record_id)
        resp.append(record)

    df = json_normalize(resp)
    csv_str = io.StringIO()
    df.to_csv(csv_str)
    print("LOG: " + user_dn + "exported a list of records.")
    return csv_str.getvalue()


'''
upload a json array of records
'''
def uploadRecord (user_dn, upload_file, file_type):
    # TODO: add update by, audit date, update date

    records_upload = None
    try:
        if file_type == "file":
            records_upload = json.load(upload_file.file)
        elif file_type == "text":
            records_upload = json.loads(upload_file)
    except Exception as e:
        return {"result": "failed", "messages": ["failed to load json file: " + str(e)]}

    result = {"result": "success", "messages":[], "records": []}

    # checks to make sure the input is good
    for record in records_upload:
        existing_record = None
        if "record_version" not in record:
            result = {"result": "failed", "message": "record_version attribute was not found"}
            return result
        if "record_id" in record:
            record_id = record["record_id"]
            existing_record = rDao.getRecordByrecordId(user_dn, record_id)
        else:
            result = {"result": "failed", "message": "record_id attribute was not found"}
            return result

        if "noresults" in existing_record:
            result = {"result": "failed", "message": "could not find record_id: " + record_id}
            return result
        if existing_record["record_version"] != record["record_version"]:
            result = {"result": "failed", "message": "record versions do not match for record_id: " + record_id}
            return result
        if "record_type" in record:
            del record["record_type"]

    # start actual processing
    for record in records_upload:
        record_id = record["record id"]
        existing_record = rDao.getRecordByrecordId(user_dn, record_id)
        fields_excluded = ["record_id", "tracking_id", "record_static_id", "record_type", "record_version", "record_state", "record_ser"]
        #check the fields
        for key, value in record.items():
            if "record_" in key or key == "comments":
                if key in existing_record and key not in fields_excluded:
                    existing_record[key] = value
                else:
                    result["messages"].append("INGORING THE ATTRIBUTE: " + record_id + ": " + key)

        # create a tracking ID
        if "update_tracking_id" in record and record["update_tracking_id"] == True:
            updateRecord(user_dn, "update", "[]", "false", existing_record, "yes")
        elif "final_record" in record and record["final_record"] == True:
            updateRecord(user_dn, "final", "[]", "false", existing_record, "no")
        elif "update_system_to_group" in record and record["update_system_to_group"] == True:
            updateRecord(user_dn, "update_to_group", "[]", "false", existing_record, "no")
        else:
            updateRecord(user_dn, "update", "[]","false", existing_record, "no")

        # update the systems of the group
        if "update_systems" in record:
            updateSystemsOfGroup(user_dn, "update", existing_record, record[" update_systems"], "false")
            # TODO: add back in later to check for valid guid
            # for system_record in record[" update_systems"]: #
            #   existing_record[" systems"] = []
            #   # if group get systems for select
            #   if existing_record["record_type"] == "group":
            #       systems = dsh.get_group_systems(user_dn, existing_record["dashboard_id"], existing_record[" guid"])
            #       if systems is not None:
            #           for system in systems["nodes"]:
            #               existing_record["systems"].append(system[" guid"])



        result["records"].append(existing_record)

    return result


def getArchive(user_dn, record_id):

    records = rDao.getArchive(user_dn, record_id)
    if len (records) > 0:
        system = dashboardDAO.getSystem(user_dn, records["records" ][0]["system_id"])
    else:
        system = None

    resp = {"records": records[ "records"], "record_form": system}
    return resp


def emailRecord (mail, user_dn, dashboard_id, system_id, guid, exercise):
    if exercise == "true":
        exercise = "EXERCISE EXERCISE EXERCISE"
    else:
        exercise = ""
    resp = getRecordForEdit (user_dn, system_id, guid, exercise)
    record = resp["record"]
    record_form = resp["record_form"]
    body = io.StringIO()

    body.write("=======================================\n")
    body.write ("" + record_form["name"] + "\n")
    body.write("=======================================\n")
    if "tracking_id" in record and record["tracking_id"] is not None:
        body.write ("Tracking ID: " + record["tracking_id"] + "\n")
    else:
        body.write("Tracking ID: " + "\n")
    if record[" dashboard_cycle"] != "":
        body.write("Cycle: " + record ["dashboard_cycle"] + "\n")
    body.write("Grouping Code: " + record["dashboard_grouping_code"] + "\n")
    body.write("Path: " + record["record_path"] + "\n")
    for section in record_form[ "sections"]:
        body.write("---------------------------------------\n")
        body.write("" + section["title"]. upper() + "\n")
        body.write("---------------------------------------\n")
        for field in section[ "fields"]:
            if field["name"] in record and record[field["name"]] is not None:
                body.write(field["title"] + ":" + str (record[field[" name"]]) + "\n")
            else:
                body.write(field["title"] + ": " + "\n")


    if record["record_type"] == "group":
        systems = dsh.getGroupSystems(user_dn, record["dashboard_id"], record["guid"])
        for system in systems["nodes"]:
            system_id = system["system id"]
            guid = system["guid"]
            resp = getRecordForEdit(user_dn, system_id, guid, exercise)
            record = resp["record"]
            record_form = resp["record_form"]
            body.write("\n\n=========================================\n")
            body.write("" + record_form[" name"] + "\n")
            body.write("======================================\n")
            if "tracking_id" in record and record["tracking_id"] is not None:
                body.write ("Tracking ID: " + record["tracking_id"] + "\n")
            else:
                body.write("Tracking ID: " + "\n")
            for section in record_form["sections"]:
                body.write("——————————————\n")
                body.write("" + section["title"].upper() + "\n")
                body.write("——————————————\n")
                for field in section["fields"]:
                    if field["name"] in record and record[field["name"]] is not None:
                        body.write(field["title"] + ": " + str(record[field["name"]]) + "\n")
                    else:
                        body.write(field["title"] + ": " + "\n")

    dashbaord_details = dashboardDAO.getDashboardDetails(user_dn, dashboard_id)
    email_to = dashbaord_details["dashboard_emails_to"].split(";")

    msg = Message(subject="SMART Update " + exercise, sender= "SMART@coe.ic.gov", recipients = email_to, body = body.getvalue())
    mail.send(msg)
    return {"email": "success"}


def convertDMStoDecimal(record):
    lat = record["record_location_latitude"]
    lng = record["record_location_longitude"]

    if lat != "":
        d_lat = 0
        d_lng = 0

        if lng.startswith("0") == False and lng.startswith("1") == False:
            lng = "0" + lng



        lng_degrees = int(lng[0:3])
        lng_minutes = int(lng[3:5])
        lng_seconds = int(lng[5:len(lng) - 1])
        lng_direction = lng[len(lng) - 1: len(lng)]

        lat_degrees = int(lat[0:2])
        lat_minutes = int(lat[2:4])
        lat_seconds = int(lat[4: len(lat) - 1])
        lat_direction = lat[len(lat) - 1: len(lat)]

        # convert lng
        d_lng = lng_degrees + (lng_minutes / 60) + (lng_seconds / (60 * 60))
        if lng_direction.upper() == "W":
            d_lng = d_lng * -1


        # convert lat
        d_lat = lat_degrees + (lat_minutes/60) + (lat_seconds/(60*60))
        if lat_direction.upper() == "S":
            d_lat = d_lat * -1

        record["record_location_latitude_degrees"] = d_lat
        record["record_location_longitude_degrees"] = d_lng


    return record



def removeRecordAttribute(user_dn, system_id, attribute_name):
    records = rDao.getRecordsBySystemId(user_dn, system_id)
    count = 0

    for record in records["records"]:
        if attribute_name in record:
            del record[attribute_name]
            if attribute_name + "_classification" in record:
                del record[attribute_name + "_classification"]
            rDao.updateRecord(user_dn, record, record["record_id"])
            count = count + 1

    return {"results": str(count) + " records updated"}



def finalAllRecords(user_dn, dashboard_id):
    records = rDao.getRecords(user_dn, dashboard_id)["records"]
    archives = []

    try:
        for record in records:
            # updateRecord(user_dn, "final", "[]", "false", record, "no")
            record_archive = createArchive(user_dn, record, False)
            archives.append(record_archive)
            record["record_state"] = "final"
            record["timeout_level"] = 0
            record["record_event_date"] = None
            record["record_source_date"] = None
            if "default_values" in record:
                for key, value in record["default_values"].items():
                    record[key] = value

            record["comments"] = ""
            record["record_version"] = 0  # up record_version
            record["update_date"] = datetime.datetime.now()
            if "tracking_id" in record:
                record["tracking_id"] = None

        rDao.bulkUpdateRecords(user_dn, records)
        rDao.bulkUpdateArchiveRecords(user_dn, archives)

    except Exception as e:
        print("FAILED TO FINAL ALL RECORDS")
        traceback.print_exc()
        return {"status": "failed"}
