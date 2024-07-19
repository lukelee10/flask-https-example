import json
from ..dao import esDAO as esDao
import uuid


def createLocation(user_dn, location_json):
    location_json["doc type"] = "locations"
    location_id = location_json["location_id"]
    if location_id == "":
        location_json["location_id"] = str(uuid.uuid4())
        location_id = location_json["location_id"]
    res = esDao.create(user_dn, index=esDao.getESUtilIndex(), body=location_json, id=location_id)
    return res


def updateLocation (user_dn, location_json):
    location_json["doc _type"] = "locations"
    location_id = location_json["location_id"]
    res = esDao. index (user_dn, index=esDao.getESUtilIndex(), body=location_json, id=location_id)
    return res


def getLocations (user_dn, dashboard_id):
    query = {
        "size": 5000,
        "sort": [{"record_location_name.keyword": {"order": "asc", "unmapped_type": "keyword"}}],
        "query": {
            "bool": {
            "must": [
                {"match": {
                    "doc_type": "locations"}
                },
                {
            "match": {
                "dashboard_id.keyword": dashboard_id
            }
        }
            ]
            }
        }
    }

    res = esDao.search(user_dn, index=esDao.getESUtilIndex(), body=query)
    results = []

    if res["hits"]["total"] == 0:
        results = {"noresults": True}
    else:
        for item in res["hits"]["hits"]:
            results.append(item["_source"])

    return results


def getLocation (user_dn, location_id) :
    query = {
        "query": {
            "bool": {
            "must": [
                {"match": {
                    "doc_type": "locations"}
                },
                {
            "match": {
                "id": location_id
            }
        }
            ]
            }
        }
    }
    res = esDao.search(user_dn, index=esDao.getESUtilIndex(), body=query)
    return res["hits"]["hits"][0]["_source"]


def deleteLocation (user_dn, location_id) :
    query = {
        "query": {
            "bool": {
            "must": [
                {"match": {
                    "doc_type": "locations"}
                },
                {
            "match": {
                "_id": location_id
            }
        }
            ]
            }
        }
    }
    esDao.delete(user_dn, index=esDao. getESUtilIndex(), body=query)
    return {"delete": "success"}

def deleteAllLocations (user_dn, dashboard_id) :
    query = {
        "query": {
            "bool": {
                "must":[
                    {"match": {
                        "doc_type": "locations"}
                    },
                    {"term": {"dashboard_id. keyword": dashboard_id}},
                    {"term": {"_type": "locations"}}
                ]
            }
        }
    }

    esDao.delete(user_dn, index=esDao.getESUtilIndex(), body=query)
    return {"delete" :"success"}