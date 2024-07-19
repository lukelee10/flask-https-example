import json
import uuid
from .dao import systemTypeDAO as wDAO


def updateSystemType(user_dn, systemType):
    systemType_json = json.loads(systemType)
    if "systemType_id" not in systemType_json or systemType_json["systemType_id"] == "":
        systemType_id = str(uuid.uuid4())
        systemType_json["systemType_id"] = systemType_id
    else:
        systemType_id = systemType_json["systemType_id"]
    wDAO.updateSystemType(user_dn, systemType_json, systemType_id)
    return systemType_json


def getSystemTypes(user_dn, dashboard_id):
    return wDAO.getSystemTypes(user_dn, dashboard_id)


def getSystemType(user_dn, id):
    if id is not None:
        res = wDAO.getSystemType(user_dn, id)
    else:
        res = {"noresults": True}
    return wDAO.getSystemType(user_dn, id)


def delete(user_dn, id):
    return wDAO.deleteSystemType(user_dn, id)