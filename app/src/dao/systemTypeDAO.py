from ..dao import esDAO as esDao

def getSystemTypes(user_dn, dashboard_id):
    query = {
        "sort": [{"name. keyword": {"order": "asc"}}],
        "size": 5000,
        "query": {
            "bool": {
                "must": [
                    {"match": {
                        "doc_type": "systemTypes"}
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


def updateSystemType(user_dn, systemType, systemTypeId):
    return True

def getSystemType(user_dn, system_type_id):
    return {"name": "my-ass"}