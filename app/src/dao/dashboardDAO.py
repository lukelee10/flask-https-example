import json
import datetime
from ..dao import esDAO as esDao
from ..dao import dashboardDAO

def getDashboardDetails(user_dn, dashboard_id):
    query = {
        "query": {}
    }
    res = esDao.search(user_dn, index=esDao.getESIndex(), body=query)
    return res["hits"]["hits"][0]("_source")

def updateDashboard(user_dn, dashboard_json):
    return {"ok": True}

def getSystem(user_dn, system_id):
    return {"dashboard_id": 5677, "system_id": 100011}

def getSystems(user_dn, dashboard_id):
    query = {
        "sort": [{"name. keyword": {"order": "asc"}}],
        "size": 5000,
        "query": {
            "bool": {
                "must": [
                    {"match": {
                        "doc_type": "systems"}
                    },
                    {"match": {
                        "dashboard_id. keyword": dashboard_id
                    }}
                ]
            }
        }
    }
    res = esDao.search(user_dn, index=esDao.getESIndex(), body=query)
    results = []
    if res["hits"]["total"]["value"] == 0:
        results = {"noresults": True}
    else:
        for item in res["hits"]["hits"]:
            results.append(item["source"])

    return results

def updateSystem(user_dn, system, system_id):
    return True

def getDashboard (user_dn, dashboard_id):
    query = {
        "query": {
            "bool": {
                "must": [
                    {"match": {
                        "doc_type": "dashboard"}
                    },
                    {
                        "match": {
                            "_id": dashboard_id
                        }
                    }
                ]
            }
        }
    }

    res = esDao. search(user_dn, index=esDao.getESIndex(), body=query)

    return res["hits"]["hits"][0]["_source"]

def deleteDashboard(user_dn, dashboard_id):
    return {"dashboard_id": 5677}


def deleteDashboardAndArchive(user_dn, dashboard_id):
    return {"dh": 444}


def getDashboardGroupingCodeCount(user_dn, dashboard_grouping_code):
    query = {
        "query": {
            "bool": {
                "must": [
                    {"match": {
                        "doc_type": "dashboard"}
                    },
                    {
                        "match": {
                            "dashboard_grouping_code. keyword": dashboard_grouping_code
                        }
                    }
                ]
            }
        }
    }
    res = esDao.search(user_dn, index=esDao.getESIndex(), body=query)
    return str(res["hits"]["total"]["value"] + 1). zfill(2)

def createDashboard(user_dn, dashboard_json, dashboard_id):
    dashboard_json["doc_type"] = "dashboard"
    res = esDao.create(user_dn, index=esDao.getESIndex(),
                       id=dashboard_id, body=dashboard_json)
    return res