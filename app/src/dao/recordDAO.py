import json
import datetime
from ..dao import esDAO as esDao
from ..dao import dashboardDAO as dashboardDAO


def bulkUpdateRecords(user_dn, records):
	docs = []

	count = 0
	for record in records:
		record["doc_type"] = "record"
		doc = {
			"_index": esDao.getESIndex(),
			"_id": record["record_id"],
			"_source": record
		}
		docs.append(doc)
		count = count + 1
		if count == 200:
			print("BULK" + str (count))
			res = esDao.bulkUpdate(user_dn, docs)
			count = 0
			docs = []
	print ("BULK" + str(count))
	res = esDao.bulkUpdate(user_dn, docs)
	return "done"


def bulkUpdateArchiveRecords(user_dn, records):
	docs = []

	count = 0
	for record in records:
		record["doc_type"] = "record"
		doc = {
			"_index": esDao.getESArchiveIndex(),
			"_id": record["record_id"],
			"_source": record
		}
		docs. append (doc)
		count = count + 1
		if count == 200:
			print("BULK" + str(count))
			res = esDao.bulkUpdate(user_dn, docs)
			count = 0
			docs = []
	print("BULK" + str(count))
	res = esDao.bulkUpdate(user_dn, docs)
	return "done"


def getRecordByRecordId(user_dn, record_id):
	query = {
		"query":  {
			"bool": {
				"must": [
					{"match":  {
						"doc_type": "record"}
					},
					{"term": {"_id": record_id}}
				]
			}
		}
	}
	res = esDao.search(user_dn, index=esDao.getESIndex(), body=query)

	if res["hits"]["total"]["value"] == 0:
		return {"noresults": True}
	else:
		return res["hits"]["hits"][0]["_source"]


def getRecordsFromIds(user_dn, record_list):
	query = {
		"size": 9999,
		"query": {
			"ids": {
				"values": record_list
			}
		}
	}

	res = esDao.search(user_dn, index=esDao.getESIndex(), body=query)

	results = {"records": [], "acm": []}
	if res["hits"]["total"] ["value"] == 0:
		results = {"records": [], "acm": []}
	else:
		for item in res["hits"] ["hits"]:
			results["records" ].append(item["_source"])
	if "acm_rollup" in res:
		results["acm"].append(res["acm_rollup"])
	return results


def getRecordsBySystemId(user_dn, system_id):
	query = {
		"query": {
			"bool": {
				"must": [
					{"match": {
						"doc_type": "record"}
					},
					{"term": {"system_id. keyword": system_id}}
				]
			}
		}
	}

	res = esDao. search (user_dn, index=esDao. getESIndex(), body=query)
	results = {"records": [], "acm": []}
	if res["hits"]["total"] ["value"] == 0:
		results = {"records": [], "acm": []}
	else:
		for item in res["hits"]["hits"]:
			results["records"] .append(item["_source"])
	results["acm"].append(res["acm_rollup"])
	return results


def getRecord(user_dn, guid):
	query = {
		"query": {
			"bool": {
				"must": [
					{"match": {
						"doc_type": "record"}
					},
					{"term": {"guid. keyword": guid}},
				]
			}
		}
	}

	res = esDao. search (user_dn, index=esDao.getESIndex(), body=query)

	if res ["hits"]["total"][ "value"] == 0:
		return {"noresults": True}
	else:
		return res["hits"]["hits" ][0]["_source"]


#
#
#
#
#
#
#
#
#
#
#
#
#
#

# res
#
#
#
#
#
#
#
#

def getRecords(user_dn, dashboard_id):
	query = {
		"size": 500,
		"query": {
			"bool": {
				"must": [
					{"match": {
						"doc_type": "record"}
					},
					{"term": {"dashboard_id.keyword": dashboard_id}}
				]
			}
		}
	}

	results = {"records": [], "acm": []}
	records = []
	# test = esDao.search(user_dn, index=esDao.getESIndex)
	resp = esDao.searchAndReturnAll(user_dn, index=esDao.getESIndex(), body=query)
	records = records + resp['hits']['hits']

	old_scroll_id = resp['_scroll_id']
	scroll_resp = resp['hits']['hits']
	if "acm_rollup" in resp:
		results["acm"].append(resp["acm_rollup"])

	while len(scroll_resp):
		# for i, r in enumerate (results):
		# # do something whih data

		result = esDao.scroll(user_dn, old_scroll_id)
		# check if there's a new scroll ID
		if old_scroll_id != result['_scroll_id']:
			print("NEW SCROLL ID:", result[' _scroll_id'])
		# keep track of pass scroll id
		old_scroll_id = result['_scroll_id']

		scroll_resp = result['hits']['hits']
		records = records + result['hits']['hits']
		if "acm_rollup" in resp:
			results["acm"].append(resp["acm_rollup"])

	for item in records:
		results["records"].append(item["_source"])
		results["acm"].append(item["_source"]["acm"])

	return results


def getLastRecord (user_dn, dashboard_id):
	query = {
		"_source": "tracking_id",
		"sort": [{"tracking_id. keyword": {"order": "desc", "unmapped_type": "keyword"}}, {"update_date": {"order": "desc"}}],
		"query": {
			"bool": {
				"must": [
					{ "match": {
						"doc_type": "record"}
					},
					{"term": {"dashboard_id. keyword": dashboard_id}},
					{"exists": {"field": "tracking_id"}}
				]
			}
		}
	}

	res = esDao.search(user_dn, index=esDao.getESArchiveIndex(), body=query)
	if res["hits"]["total"]["value"] == 0:
		return {"noresults": True}
	else:
		return res["hits"]["hits"][0]["_source"]


def getLastArchiveRecord(user_dn, dashboard_id) :
	query = {
		"sort": [{"tracking_id. keyword": {"order": "desc", "unmapped_type": "keyword"}}, {"update_date": {"order": "desc"}}],
		"_source": "tracking_id",
		"query": {
			"bool": {
				"must": [
					{"match": {
						"doc_type": "record"}
					},
					{"term": {"dashboard_id. keyword": dashboard_id}},
					{"exists": {"field": "tracking_id"}}
				]
			}
		}
	}

	res = esDao.search(user_dn, index=esDao.getESArchiveIndex(), body=query)
	if res["hits"][" total"]["value"] == 0:
		return {"noresults": True}
	else:
		return res["hits"]["hits"][0]["_source"]


def getLastUpdatedRecord(user_dn, rec_list):
	bool = []
	for sl in rec_list:
		bool.append({"match_phrase": {"record_id": sl}})
	query = {
		"sort": [ {"tracking_id.keyword": {"order": "desc", "unmapped_type": "keyword"}}, {"update_date. keyword": {"order": "desc"}}],
		"query": {
			"bool": {
				"must": [
					{"match": {
						"doc_type": "record"}
					}
				],
				"should": bool
			}
		}
	}

	res = esDao.search(user_dn, index=esDao.getESIndex(), body=query)
	if len(rec_list) == 0 or res["hits"]["total"]["value"] == 0:
		return {"noresults": True}
	else:
		return res["hits"]["hits"][0]["_source"]


def getTimeoutRecords (user_dn, dashboard_id):
	query = {
		"size": 5000,
		"_source": ["guid"],
		"query": {
			"bool": {
				"must_not": [
					{"term": {"archive": True}}
				],
				"must": [
					{"match": {
						"doc_type": "record"}
					},
					{"term": {"dashboard_id.keyword": dashboard_id}},
					{"term": {"record_state": "timeout"}}
				]
			}
		}
	}

	res = esDao.search(user_dn, index=esDao.getESIndex(), body=query)

	if res["hits"]["total"][ "value"] == 0:
		return {"timeouts": []}
	else:
		return {"timeouts": res["hits"]["hits"]}


def getTimeSeriesRecords(user_dn, dashboard_id):
	query = {
		"size": 0,
		"query": {
			"bool": {
				"must": [
					{"match": {
						"doc_type": "record"}
					},
					{"term": {
						"dashboard_id.keyword": {
							"value": dashboard_id
						}
					}},
					{"range": {
						"update_date": {
							"from": "now-1y"
						}
					}}
				]
			}
		},
		"aggs": {

			"timeline": {
				"date_histogram": {
					"field": "update_date",
					"interval": "day",
					"min_doc_count": 1
				}
			}
		}
	}

	res = esDao.search(user_dn, index="smart, smart_archive", body=query)

	return res["aggregations"]["timeline"]["buckets"]


def getFinalTimeSeriesRecords(user_dn, dashboard_id):
	query = {
		"size": 0,
		"query": {
			"bool": {
				"must": [
					{"match": {
						"doc_type": "record"}
					},
					{"term": {
						"dashboard_id.keyword": {
							"value": dashboard_id
						}
					}},
					{"match": {
						"record_state": "final"}
					}
				]
			}
		},
		"aggs": {

			"final": {
				"date_histogram": {
					"field": "update date",
					"interval": "day",
					"min_doc_count": 1
				}
			}
		}
	}

	res = esDao.search(user_dn, index="smart,smart_archive", body=query)

	return res["aggregations"]["final"]["buckets"]


def getActivatedTimeSeriesRecords(user_dn, dashboard_id):
	query = {
		"size": 0,
		"query": {
			"bool": {
				"must": [
					{"match": {
						"doc_type": "record"}
					},
					{"term": {
						"dashboard_id.keyword": {
							"value": dashboard_id
					}
					}},
					{"match": {
						"record_state": "initial"}
					}
				]
			}
		},
		"aggs": {

			"activated": {
				"date_histogram": {
					"field": "update_date",
					"interval": "day",
					"min_doc_count": 1
				}
			}
		}
	}

	res = esDao.search(user_dn, index="smart, smart_archive", body=query)

	return res["aggregations"]["activated"]["buckets"]


def updateRecord (user_dn, rec_obj, record_id):
	rec_obj["doc_type"] = "record"
	res = esDao.index(user_dn, index=esDao. getESIndex(),
						id=record_id, body=rec_obj)

	return res


def createRecord (user_dn, rec_obj, record_id) :
	rec_obj["doc_type"] = "record"
	res = esDao.create(user_dn, index=esDao. getESIndex(),
						id=record_id, body=rec_obj)
	return res


def archiveRecord(user_dn, rec_obj, record_id):
	rec_obj[" doc_type"] = "record"
	res = esDao.create(user_dn, index=esDao. getESArchiveIndex(),
						id=record_id, body=rec_obj)
	return res


def deleteRecordsByGuid(user_dn, guid):
	query = {
		"query": {
			"bool": {
				"must": [
					{"match": {
						"doc_type": "record"}
					},
					{
						"match": {
							"guid": guid
						}
					}
				]
			}
		}
	}

	esDao.delete(user_dn, index=esDao.getESIndex(), body=query)
	esDao.delete(user_dn, index=esDao.getESArchiveIndex(), body=query)
	return {"delete": "success"}


def deleteRecordById(user_dn, record_id):
	query = {
		"query": {
			"bool": {
				"must": [
					{"match": {
						"doc_type": "record"}
					 },
					{
						"match": {
							"_id": record_id
						}
					}
				]
			}
		}
	}

	esDao.delete(user_dn, index=esDao.getESIndex(), body=query)
	esDao.delete(user_dn, index=esDao.getESArchiveIndex(), body=query)
	return {"delete": "success"}


def getArchive (user_dn, record_id):
	query = {
		"size": 5000,
		"sort": [{"update_date.keyword": {"order": "desc", "unmapped_type": "date"}}],
		"query": {
			"bool": {
				"must": [
					{"match": {
						"doc_type": "record"}
					},
					{"term": {"record_id_original.keyword": record_id}}
				]
			}
		}
	}

	res = esDao.search(user_dn, index=esDao.getESArchiveIndex(), body=query)

	results = {"records": [], "acm": []}
	if res["hits"]["total"]["value"] == 0:
		results = {"records": [], "acm": []}
	else:
		for item in res["hits"]["hits"]:
			results[" records"].append(item["_source"])
	if "acm_rollup" in res:
		results["acm"].append(res["acm_rollup"])
	return results


def getArchiveHistogram(user_dn):
	query = {
		"size": 0,
		"query": {
			"bool": {
				"must": [
					{"match": {
						"doc_type": "record"}
					},
					{"match_all": {}}
				]
			}
		},
		"aggs": {
			"dashboard": {
				"terms": {
					"field": "dashboard_id.keyword"
				},
				"aggs": {
					"timeline": {
						"date_histogram": {
							"field": "update_date",
							"interval": "day",
							"min doc_count": 1
						}
					}
				}
			}
		}
	}

	res = esDao.search(user_dn, index=esDao.getESArchiveIndex(), body=query)

	results = []

	for dashboard in res["aggregations"]["dashboard"]["buckets"]:
		dashboard_details = dashboardDAO.getDashboardDetails(
			user_dn, dashboard["key"])

		if "noresults" not in dashboard_details:

			for item in dashboard["timeline"]["buckets"]:
				dsh = {
					"id": dashboard["key"],
					"name": dashboard_details["name"],
					"color": dashboard_details["color"],
					"date": item["key_as_string"],
					"count": item["doc_count"]
				}
				results.append(dsh)
	return results


def doRecordSearch(user_dn, dashboard_grouping_code, dashboard_id, record_active, exercise, record_state, tracking_id, start_date, end_date):
	query = {
		"size": 500,
		"query": {
			"bool": {
				"must": [{"match": {
					"doc_type": "record"}
				}],
				"should": [],
				"must_not": []
			}
		},
		"sort": [
			{"audit_date": "asc"},
			{"record_id.keyword": "asc"}
		]
	}

	must = query["query"]["bool"]["must"]
	must_not = query["query"]["bool"]["must_not"]

	if record_active.lower() == "true":
		must.append({"exists": {"field": "tracking_id"}})
		must_not.append({"term": {"record_state": "timeout"}})

	if dashboard_grouping_code != "":
		must.append(
			{"term": {"dashboard_grouping_code. keyword": dashboard_grouping_code}})

	if dashboard_id != "":
		must.append({"term": {"dashboard_id. keyword": dashboard_id}})
	else:
		if exercise.lower() == "true":
			must.append({"term": {"exercise": "true"}})
		else:
			must.append({"term": {"exercise": "false"}})

	if record_state != "":
		must.append({"term": {"record_state. keyword": record_state}})

	if tracking_id != "":
		if " and " in tracking_id:
			must.append({
				"query_string": {
					"default_field": "tracking_id",
					"query": tracking_id
				}})
		else:
			must.append({"term": {"tracking_id": tracking_id}})

	if start_date != "":
		if end_date == "":
			end_date = datetime.datetime.now()
		must.append(
			{"range": {"record_event_date": {"gte": start_date, "lte": str(end_date)}}})

	results = {"records": [], "acm": []}
	records = []
	resp = esDao.searchAndReturnAll(
		user_dn, index=esDao.getESIndex(), body=query)
	records = records + resp['hits']['hits']

	old_scroll_id = resp['_scroll_id']
	scroll_resp = resp['hits']['hits']
	if "acm_rollup" in resp:
		results["acm"].append(resp["acm_rollup"])

	while len(scroll_resp):
		# for i, r in enumerate (results):
		# # do something whih data

		result = esDao.scroll(user_dn, old_scroll_id)
		# check if there's a new scroll ID
		if old_scroll_id != result[' _scroll_id']:
			print("NEW SCROLL ID:", result[' _scroll_id'])
		# keep track of pass scroll _id
		old_scroll_id = result[' _scroll_id']

		scroll_resp = result['hits']['hits']
		records = records + result['hits']['hits']
		if "acm_rollup" in resp:
			results["acm"].append(resp["acm_rollup"])

	for item in records:
		results[" records"].append(item[" _source"])
