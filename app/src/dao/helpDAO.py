import json
from . import esDAO as esDao


def updateHelp(user_dn, help_json, help_id):
    help_json["doc_type"] = "help"
    res = esDao. index (user_dn, index=esDao.getESUtilIndex(), body=help_json, id=help_id)
    return res

def getHelpItems (user_dn, dashboard_id):
    query = {
        "size": 9999,
        "query": {
            "bool": {
                "must": [
                    {"match": {
                        "doc_type": "help"}
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

    result = []

    res = esDao.search(user_dn, index=esDao.getESUtilIndex(), doc_type="help", body=query)
    for item in res["hits"]["hits"]:
        result.append(item["_source"])
    return result



def getHelps (user_dn, dashboard_id):
    query = {
        "size": 9999,
        "sort": [
            {"view.keyword": {"order": "asc", "unmapped_type": "keyword"}},
            {"section.keyword": {"order": "asc", "unmapped_type" : "keyword"}}
        ],
        "query": {
            "bool": {
                "must": [
                    {"match": {
                        "doc type": "help"}
                    },
                    {
                        "match": {
                            "dashboard_id.keyword": dashboard_id
                        }
                    }
                ]
            }
        },
        "aggs": {
            "views": {
                "terms": {
                    "field": "view.keyword",
                    "min_doc_count": 1,
                    "size": 9999,
                    "order": {
                        "_term": "asc"
                    }
                },
                "aggs": {
                    "section": {
                        "terms": {
                            "field": "section.keyword",
                            "min_doc_count": 1,
                            "size" :9999,
                            "order": {
                                "_term": "asc"
                            }
                        }
                    }
                }
            }
        }
    }

    result = {"helps": [], "buckets": []}

    res = esDao.search(user_dn, index=esDao.getESUtilIndex(), body=query)
    for item in res["hits"]["hits"]:
        result["helps"].append(item ["_source"])
    result["buckets"] = res["aggregations"]["views"]["buckets"]
    return result


def getHelp(user_dn, help_id):
    query = {
        "query": {"match": {
                "_id": help_id
        }}
    }
    res = esDao.search(user_dn, index=esDao.getESUtilIndex(), body=query)
    if res["hits" ]["total"] > 0:
        return res["hits"]["hits"][0]["_source"]
    else:
        return {"noresults": True}


def deleteHelp(user_dn, help_id):
    query = {
        "query": {
            "match": {
                "_id": help_id
            }
        }
    }
    esDao.delete(user_dn, index=esDao.getESUtilIndex(), body=query)
    return {"delete": "success"}


def deleteAllHelp(user_dn, dashboard_id):
    query = {
        "query": {
            "bool": {
                "must": [
                    {"match": {
                        "doc_type": "help"}
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
    esDao.delete(user_dn, index=esDao.getESUtilIndex(), body=query)
    return {"delete": "success"}


def searchHelp(user_dn, dashboard_id, terms, view):
    query = {
        "size": 9999,
        "sort": [
            {"view.keyword": {"order": "asc", "unmapped_type" : "keyword"}},
            {"section.keyword": {"order": "ase", "unmapped_type" : "keyword"}}
        ],
        "query": {
            "bool": {
                "must":[
                    {"match": {
                        "doc_type": "help"}
                    },
                    {
                        "match": {
                            "dashboard_id.keyword": dashboard_id
                        }
                    }
                ]
            }
        },
        "aggs": {
            "views": {
            "terms": {
                "field": "view.keyword"
            }
            , "ages": {
                "section": {
                "terms": {
                    "Field": "section.keyword"
                }
                }
            }
            }
        }
    }

    query_bool = query["query"]["bool"]

    if terms != "":
        query_bool["must"].append({
            "multi_match": {
            "query": terms,
            "Fields": ["text", "title", "section", "view"]
            }
        })

    if view != "all":
        query_bool["must"].append({"match": {"view.keyword": view}})

    result = {"helps": [], "buckets":[]}

    res = esDao.search(user_dn, index=esDao.getESUtilIndex(), body=query)
    for item in res["hits"]["hits"]:
        result["helps"].append(item["_source"])
    result["buckets"] = res["aggregations"]["views"]["buckets"]
    return result