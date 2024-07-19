import json
from . import esDAO as esDao


def updateClassification(user_dn, classification_json, classification_id):
    classification_json["doc_type"] = "classifications"
    res = esDao.index (user_dn, index=esDao. getESIndex(), body=classification_json, id=classification_id)

    return res


def getClassifications(user_dn, dashboard_id):
    query = {
        "size": 5000,
        "sort": [{"order.keyword": {"order": "asc", "unmapped_type" : "keyword" }}],
        "query": {
            "bool": {
                "must": [
                    {"match": {
                        "doc_type": "classifications"}
                    },
                    {
                        "match": {
                            "dashboard_id. keyword": dashboard_id
                        },
                    }
                ]
            }
        }
    }

    res = esDao.search(user_dn, index=esDao.getESIndex(), body=query)
    results = []
    if res["hits"]["total"] == 0:
        results = {"noresults": True}
    else:
        for item in res["hits"]["hits"]:
            results.append(item["_source"])

    return results


def getClassification (user_dn, classification_id):
    query = {
        "query": {"match": {
        "_id": classification_id
        }}
    }
    res = esDao.search(user_dn, index=esDao.getESIndex(), body=query)
    if res["hits"]["total"] > 0:
        return res["hits"]["hits"][0]["_source"]
    else:
        return {"noresults": True}


def deleteClassification(user_dn, classification_id):
    query = {
        "query": {
            "match": {
                "_id": classification_id
            }
        }
    }
    esDao.delete(user_dn, index=esDao.getESIndex(), body=query)
    return {"delete": "success"}