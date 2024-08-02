import json
import uuid
from .dao import classificationsDAO as cDAO


def updateClassification (user_dn, classification):
    if type (classification) == str:
        classification = json.loads(classification)
    if "classification_id" not in classification or classification["classification_id"] == "":
        classification_id = str(uuid.uuid4())
        classification["classification_id"] = classification_id
    else:
        classification_id = classification["classification_id"]
    cDAO.updateClassification(user_dn, classification, classification_id)
    return classification


def getClassifications(user_dn, dashboard_id):
    return cDAO.getClassifications(user_dn, dashboard_id)


def getClassification(user_dn, id):
    return cDAO.getClassification(user_dn, id)


def delete(user_dn, id):
    return cDAO.deleteClassification(user_dn, id)