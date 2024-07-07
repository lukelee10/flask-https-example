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
					{"term": {"dashboard_id. keyword": dashboard_id}}
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
		old_scroll_id = result[' _scroll_id']

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