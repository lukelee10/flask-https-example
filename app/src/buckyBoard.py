import copy
import math
import traceback

systems = []
records = []
system_types = []
def getSystem (system_id):
    for system in systems:
        system = system
        if system["system_id"] == system_id:
            return system


def getSystemType(system_type_id):
    for system_type in system_types:
        system_type = system_type
        if system_type["systemType_id"] == system_type_id:
            return copy.deepcopy(system_type)
def getRecord(guid):
    found = False
    found_sl = {"noresults": True}
    for record in records:
        if record ["guid"] == guid:
            found_sl = record
            break
    return found_sl


def get_paragraph_item(name, title, selected, system_type_id, count):
    return {"name": name, "title": title, "selected": selected, "systemType": system_type_id, "count": count}


def get_paragraph_item_r(rollup, system_type_id, record):
    try:
        count = int(record[rollup["field"]])
    except Exception as e:
        count = 0
    selected_flag = rollup["items"]["sum"]["selected"]
    return get_paragraph_item(rollup["field"], rollup["title"], selected_flag, system_type_id, count)


# given rollups directives, a record, and the 2 flags and system_type_id, make an initial paragraph for the given record
def makeParagraph(rollups, record, rollup_total_ob, rollup_oob, systemType_id):
    paragraph = []
    if rollup_total_ob is True:
        paragraph.append(get_paragraph_item("total_ob",  "Total OB",True, systemType_id,1))
    if rollup_oob is True:  # determine oob
        paragraph.append(
            get_paragraph_item("oob", '00B', True, systemType_id,
                               1 if "record_operational" in record and record["record_operational"] == "yes" else 0))
    for rollup in rollups:  # get other rollups
        if rollup["type"] == "integer":  # if type is integer then sum up all the values from the records
            para_item = get_paragraph_item_r(rollup, systemType_id, record)
            if para_item not in paragraph:
                paragraph.append(para_item)
        else:  # if not integer then only tally the number of instances
            for value, item in rollup["items"].items():
                rollup_item = {"name": rollup["field"], "title": rollup["title"],
                               "selected": item["selected"], "systemType": systemType_id}
                rollup_item["name"] = rollup_item["name"] + "_" + value
                rollup_item["title"] = rollup_item["title"] + " (" + value + ")"
                if rollup["field"] in record and record[rollup["field"]] == value:
                    rollup_item["count"] = 1
                else:
                    rollup_item["count"] = 0

                if rollup_item not in paragraph:
                    paragraph.append(rollup_item)

    return paragraph


# obj has nodes (more like tree of nodes)
# group_in_rollup is a boolean
# rollups are user directives on which fields to roll up or not.
def setBBValues(user_dn, obj, rollups, group_in_rollup, rollup_oob, rollup_total_ob, alerts):
    # map of system_type names mapped to the rollup-items.  equate system_type being 
    rollup_map = {}  # the paragraph header.  and the paragraph being the rollup-itmes
    record_ids_has_system = []  # collect corresponding records' record_id in given nodes (from obj)
    record_ids_has_trk_id = []  # subset of above and has tracking_id. aka active records

    for node in (obj["nodes"] if "nodes" in obj else []):
        record = None
        if "guid" in node and "system_id" in node:
            record = getRecord(node["guid"])
            if getSystem(node["system_id"]) is not None and "record_id" in record:
                record_ids_has_system. append(record["record_id"])
                if "tracking_id" in record and record["tracking_id"] is not None:
                    record_ids_has_trk_id.append(record["record_id"])

        # set systemTypesystem values and merge
        if node["type"] == "system" or (node["type"] == "group" and group_in_rollup):
            if record is not None and "noresults" not in record:
                systemType_id = node["systemType_id"] if "systemType_id" in node else None
                system_type_name = getSystemType(systemType_id)["name"] if systemType_id is not None else "missing system type in hierarchy"
                if system_type_name not in rollup_map:  # initialize the paragraph (rollup items)
                    paragraph = makeParagraph(rollups, record, rollup_total_ob, rollup_oob, systemType_id)
                    rollup_map[system_type_name] = {"type": node["type"], "rollups": paragraph}
                else:

                    for rollup_item in rollup_map[system_type_name]["rollups"]:
                        if rollup_item["name"] == "oob":
                            if "record_operational" in record and record["record_operational"] == "yes":
                                rollup_item["count"] = rollup_item["count"] + 1
                        elif rollup_item["name"] == "total_ob":
                            rollup_item["count"] = rollup_item["count"] + 1
                        else:
                            worked = []
                            for rollup in rollups:
                                if rollup["type"] == "integer":  # if type is integer, then sum up values
                                    if rollup_item["name"] == rollup["field"] and rollup["field"] not in worked:
                                        if rollup["field"] in record:
                                            value = 0
                                            try:
                                                value = int(record[rollup["field"]])
                                            except Exception as e:
                                                value = 0
                                            rollup_item["count"] = rollup_item["count"] + value
                                            worked.append(value)
                                else:  # tally up number of instances

                                    for value, item in rollup["items"].items():
                                        rollup_item_name = rollup["field"] + "_" + value
                                        if rollup_item["name"] == rollup_item_name and value not in worked:
                                            if rollup["field"] in record and record[rollup["field"]] == value:
                                                rollup_item["count"] = rollup_item["count"] + 1
                                                worked.append(value)

        if node["type"] != "system": #not at the
            incoming_rollup_list = setBBValues(user_dn, node, rollups, group_in_rollup, rollup_oob, rollup_total_ob, alerts)
            # merge incoming rollup_map with current rollup_map
            record_ids_has_system = record_ids_has_system + node["records"]
            record_ids_has_trk_id = record_ids_has_trk_id + node["active_records"]

            for in_name, in_sys_type in incoming_rollup_list.items():

                if in_name not in rollup_map:
                    rollup_map[in_name] = in_sys_type
                else:
                    for in_rollup in in_sys_type["rollups"]:
                        for s_rollup in rollup_map[in_name]["rollups"]:
                            if in_rollup["name"] == s_rollup["name"]:
                                s_rollup["count"] = s_rollup["count"] + in_rollup["count"]

    obj["records"] = record_ids_has_system
    obj["active_records"] = record_ids_has_trk_id
    obj["rollup"] = copy.deepcopy(rollup_map)  # need to copy the node other same objects gets changed
    alerts = copy.deepcopy(alerts)
    # set calculations for alerts
    obj["alerts"] = []
    for alert in alerts:
        calculation = ""
        for calc in alert["calculations"]:
            if calc["type"] == "field" or calc["type"] == "rollup_options":
                rollup_total = 0
                for value in obj["rollup"].values():
                    rollup_total += sum([r["count"] for r in value["rollups"] if ["name"] == calc["value"]])
                calculation += str(rollup_total)
            else:
                calculation += calc["value"] + " "
        try:
            alert["total"] = math.ceil(eval(calculation))
        except Exception as e:
            # bad expretion or divide by zero
            alert["total"] = 0
        levels = alert["thresholds"].split(",")

        if alert["total"] <= int(levels[0]):
            alert["total_class"] = "alert-lt-green"
            alert["total_description"] = "low"
            alert["total_color"] = "alert-1g-count-color"
        elif alert["total"] >= (int(levels[0]) + 1) and alert["total"] <= int(levels[1]):
            alert["total_class"] = "alert-lt-yellow"
            alert["total_description"] = "moderate"
            alert["total_color"] = "alert-1g-count-color"
        else:
            alert["total_class"] = "alert-lt-red"
            alert["total_description"] = "high"
            alert["total_color"] = "alert-1g-count-color"


        obj["alerts"].append(alert)

    return rollup_map








