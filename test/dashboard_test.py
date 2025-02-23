from io import StringIO
import numpy as np
import traceback
import copy

from app.src.dao import dashboardDAO as dDao
from app.src.dao import recordDAO as rDao
from app.src.dao import locationsDAO as lDao
from app.src.dao import classificationsDAO as cDao
from app.src.dao import helpDAO as hDao
from app.src import dashboard as d
from app.src.dao import systemTypeDAO
from mockito import when, unstub, any, patch
import json
import uuid
def test_getDashboard():
	when (dDao) \
		.getDashboard("user_dn", "dashboard_id") \
		.thenReturn(True)

	response = d.getDashboard("user_dn", "dashboard_id")

	assert response == True

def test_getDashboardDetails():
	when(dDao) \
		.getDashboardDetails("user_dn", "dashboard_id") \
		.thenReturn(True)

	response = d. getDashboardDetails ("user_dn", "dashboard_id")
	assert response == True


def test_deleteDashboard():
	when(dDao) \
		.deleteDashboard("user_dn", "dashboard_id") \
		.thenReturn(True)

	response = d.deleteDashboard("user_dn", "dashboard_id")["result"]
	assert response == "delete"

def test_deleteDashboardAndArchive():
	when(dDao)\
		.deleteDashboardAndArchive("user_dn", "dashboard_id") \
		.thenReturn(True)

	response = d. deleteDashboardAndArchive("user_dn", "dashboard_id" )["result"]
	assert response == "delete"

def test_getSystems():
	when (dDao) \
		.getSystems("user_dn", "dashboard_id") \
		.thenReturn([])

	response = d.getSystems ("user_dn", "dashboard_id")
	assert response == []

def test_getSystem():
	when (dDao) \
		.getSystem("user_dn", "dashboard_id") \
		.thenReturn(True)

	response = d.getSystem("user_dn", "dashboard_id")
	assert response == True

# def test_deleteSystem():
# when (rDao)
# .getRecordsBySystemId("user_dn", "system_id") \
# thenReturn([])
# response = .deleteSystem("user_dn", "system_id")
# assert response == {"result": "fail", "message": "System Records Exist"}

# def test getGroupSystems():
# 	when (dDao)\
#		.getDashboard(' user_dn', "dashboard_id")
# 		.getNodeByValue ("dashboard", "guid", 'guid") \
# 		.thenReturn(True)

# response = d. getGroupSystems ("user_dn", "dashboard_id", "guid")
# assert response == True

def test_getDashboardDetails():
	when(dDao) \
		.getDashboardDetails("user_dn", "dashboard_id") \
		.thenReturn({"dashboard_id": "dashboard_id", "exercise": "false"})

	when(rDao) \
		.getTimeSeriesRecords ("user_dn", "dashboard_id") \
		.thenReturn([])

	when(rDao) \
		.getFinalTimeSeriesRecords ("user_dn", "dashboard_id") \
		.thenReturn([])

	when (rDao) \
		.getActivatedTimeSeriesRecords("user_dn", "dashboard_id") \
		.thenReturn([])

	when(dDao) \
		.getDashboard("user_dn", "dashboard_id") \
		.thenReturn({"dashboard_id": "dashboard_id", "name": "name", "color": "color"})

	response = d.getDashboardDetails("user_dn", "dashboard_id")
	unstub()

	assert len(response) == 3

# def test_getPath():
# response = d.getPath("user_dn", "dashboard_id", "guid")
# return response

tugged_dash = [None]
# copied the first part of  uploadDashboard
def save_dashboard(x, dashboard, y):
	tugged_dash[0] = dashboard
	return dashboard


def get_saved_dashboard(user_dn, dashboard_id):
	return tugged_dash[0]

tugged_records =[[]]
def save_record(x, record, record_id):
	tugged_records[0].append(record)


tugged_systems = [[]]
def save_system(x, system, system_id):
	tugged_systems[0].append(system)

tugged_system_types = [[]]
def save_system_type(x, systemType, systemTypeId):
	tugged_system_types[0].append(systemType)

tugged_locations = [[]]
def save_location(x, location_json):
	tugged_locations[0].append(location_json)

def get_leaves(obj_list, attribute_name):
	ans = []
	for r in obj_list:
		if attribute_name in r:
			ans.append(r[attribute_name])
		ans = ans + get_leaves(r["nodes"], attribute_name)
	return ans

def traverse(obj_list):
	ans = []
	for r in obj_list:
		ans.append({ k: v for k, v in r.items() if k != 'nodes' })
		ans = ans + traverse(r["nodes"])
	return ans

class MockCGIFieldStorage(object):
	pass


original_dash = [None]
original_systems = [None]
original_system_types = [None]
original_records = [None]
original_locations = [None]
original_record_archive = [None]


def prepare_base():
	x = open("dashboard.json").read()
	orig_dash = json.loads(x)
	original_systems[0] = orig_dash["systems"]
	original_system_types[0] = orig_dash["systemTypes"]
	original_records[0] = {"records": orig_dash["records"]}
	original_locations[0] = orig_dash["locations"]
	original_record_archive[0] = orig_dash["record_archive"]
	for fd_name in ["systems", "systemTypes", "records", "locations","record_archive"]:
		del orig_dash[fd_name]
	original_dash[0] = orig_dash
	return x


def test_createDashboard():
	x = prepare_base()
	when(dDao).getDashboardGroupingCodeCount("user_dn", any).thenReturn(23)
	when(dDao).getDashboard("user_dn", any).thenReturn(copy.deepcopy(original_dash[0]))
	when(rDao).getRecords("user_dn", any).thenReturn(copy.deepcopy(original_records[0])) # use the records key inside the orginal_dash.  the rest please ignore it
	patch(rDao, "updateRecord", save_record) # saves the new records back into ES
	when(lDao).getLocations("user_dn", any).thenReturn(original_locations[0])
	patch(lDao, "updateLocation", save_location)
	when(cDao).getClassifications("user_dn", any).thenReturn(original_dash[0]["classifications"])
	when(cDao).updateClassification("user_dn", any, any).thenReturn({"record_id": "xyz"})
	when(hDao).getHelps("user_dn", any).thenReturn({"helps": original_dash[0]["helps"]}) # use the helps key inside the orginal_dash.  the rest please ignore it
	when(hDao).updateHelp("user_dn", any, any).thenReturn(True)
	patch(dDao, "createDashboard", save_dashboard)
	when(dDao).getSystems("user_dn", any).thenReturn(copy.deepcopy(original_systems[0]))
	patch(dDao, "updateSystem", save_system)
	when(systemTypeDAO).getSystemTypes("user_dn", any).thenReturn(copy.deepcopy(original_system_types[0]))
	patch(systemTypeDAO, "updateSystemType", save_system_type)
	try:
		response = d.createDashboard("user_dn", x, "ABC country-fleet 123", "true")
	except Exception as e:
		stk = traceback.format_exc()
		print(stk)

	target_composite_dash = copy.deepcopy(tugged_dash[0])
	target_composite_dash.update({"systemTypes": tugged_system_types[0], "systems": tugged_systems[0], "locations": tugged_locations[0], "records": tugged_records[0]})
	# make sure dashboard change dashboard_id, and levels(nodes) various ids are changed;
	# system id and systemType id are changed
	assert [k for k, v in original_dash[0].items() if v != tugged_dash[0][k] and k != "levels"] == ['dashboard_id']
	for x,y in zip(traverse(original_dash[0]["levels"]), traverse(tugged_dash[0]["levels"])):
		diff = [k for k,v in x.items() if v != y[k]]  # check each node node_id, guid, system_id, and system type id different
		assert diff == [] or diff == ['node_id', 'guid'] or diff == ['system_id', 'systemType_id', 'node_id', 'guid']
	for i in range(len(original_systems[0])):
		assert [k for k, v in original_systems[0][i].items() if v != tugged_systems[0][i][k]] == ["dashboard_id", "system_id"]
	for i, sys_type in enumerate(original_system_types[0]):
		assert [k for k, v in sys_type.items() if v != tugged_system_types[0][i][k]] == ['dashboard_id', 'systemType_id']
	for i, rec in enumerate(original_records[0]["records"]):
		diff2 = [k for k, v in rec.items() if v != tugged_records[0][i][k]]
		# supposed to have 'dashboard_id', 'exercise', 'record_id', 'system_id' AND systemType_id AND guid different
		assert (diff2 == ['dashboard_id', 'exercise','guid', 'record_id', 'system_id', 'system_type_id']),\
			(('record at ' + str(i) + ' differs' + str(diff2)) + ' instead of dashboard_id, exercise, guid, record_id, system_id')
	validate_dashboard(target_composite_dash)
	unstub()


# should have matching records, or no orphaned records
def validate_dashboard(dashboard_json):
	ans = {}
	nodes = traverse(dashboard_json["levels"])
	system_ids = nodes
	rec_guids = [r['guid'] for r in dashboard_json["records"]]

	if len(set(rec_guids)) < len(dashboard_json["records"]):
		tally = dict((i, rec_guids.count(i)) for i in rec_guids)
		extra_guids = [k for k, v in tally.items() if v > 1]
		ans.update({'records have duplicate guid': extra_guids})
	duplicated_rec_guids = []
	orphaned_rec_guids = []
	unmatched_recs = []
	for r in dashboard_json["records"]:
		matched_nodes = [n for n in nodes if 'guid' in n and n['guid'] == r['guid']]
		if len(matched_nodes) > 1:
			duplicated_rec_guids.append(r['guid'])
		elif len(matched_nodes) < 1:
			orphaned_rec_guids.append(r['guid'])
		elif (matched_nodes[0]['system_id'] != r['system_id'] or
			 matched_nodes[0]['systemType_id'] != r['system_type_id']):
			unmatched_recs.append(r['guid'])
	if len(duplicated_rec_guids) > 0 or len(orphaned_rec_guids) > 0 or len(unmatched_recs) > 0:
		ans.update({'duplicated_rec_guids':duplicated_rec_guids,
					'orphaned_rec_guids':orphaned_rec_guids, 'unmatched_recs':unmatched_recs})
	return ans


def test_upload_dashboard_ori():
	upload = MockCGIFieldStorage()
	with open('dashboard.json', 'r') as file:
		x = file.read()
		upload.file = x

	response = d.upload_dashboard_original("user_dn", upload)
	assert 'failed' in response

def test_uploadDashboard():
	when(dDao).getDashboardGroupingCodeCount("user_dn", any).thenReturn("AB")
	when(dDao).updateSystem("user_dn", any, any).thenReturn(None)
	when(systemTypeDAO).updateSystemType("user_dn", any, any)

	upload = MockCGIFieldStorage()
	with open('dashboard.json', 'r') as file:
		x = file.read()
		upload.file = StringIO(x)

	patch(dDao, "createDashboard", save_dashboard)
	patch(dDao, "getDashboardDetails", get_saved_dashboard)
	when(rDao).bulkUpdateRecords ("user_dn", any).thenReturn("done")
	when(rDao).bulkUpdateArchiveRecords ("user_dn", any).thenReturn("done")
	when(lDao).updateLocation ("user_dn", any).thenReturn({"location_id": "xyz"})
	when(cDao).updateClassification("user_dn", any, any).thenReturn({"record_id":"xyz"})
	when(hDao).updateHelp("user_dn", any, any).thenReturn(True)
	# classification, classification_id)

	original_dash = json.loads(x)
	response = d.uploadDashboard("user_dn", upload)
	A = get_leaves(original_dash["levels"], "guid")
	B = get_leaves(response["dashboard"]["levels"], "guid")
	assert not np.array_equal(A, B)

	A = [response["node_guid_translated"][guid] for guid in get_leaves (original_dash["levels"], "guid")]
	B = get_leaves(response["dashboard"]["levels"], "guid")
	assert np.array_equal(A, B)

	# guid old
	A = get_leaves(original_dash["levels"], "old_guid")
	B = get_leaves(response["dashboard"]["levels"], "old_guid")
	assert np. array_equal(A, B)
	A = get_leaves(original_dash["levels"], "system_id")
	B = get_leaves(response["dashboard"]["levels"], "system_id")
	assert not np. array_equal(A, B)
	A = get_leaves(original_dash["levels"], "systemType_id")
	B = get_leaves(response["dashboard" ]["levels"], "systemType_id")
	assert not np. array_equal(A, B)

	A = [r["system_id"] for r in original_dash["records"]]
	B = [r["system_id"] for r in response["records"]]
	assert not np. array_equal(A, B)
	# get the mapped system ID to make sure it's mapped over to records
	A = [response["nodes_translated_system_id"]["mapped"][rec["system_id"]] for rec
	in original_dash["records"]]
	B = [r["system_id"] for r in response["records"]]
	assert np. array_equal(A, B)

	A = [r["systemType_id" ] for r in original_dash["records"]]
	B = [r["systemType_id"] for r in response["records"]]
	assert not np.array_equal(A, B)
	# get the mapped system ID to make sure it's mapped over to records
	A = [response["nodes_translated_system_id"]["mapped"][rec["system_id"]] for rec
	in original_dash["records"]]
	B = [r["system_id"] for r in response[ "records"]]
	assert np. array_equal(A, B)
	unstub()

def test_uploadDashboardMore():
	when(dDao).getDashboardGroupingCodeCount("user_dn", any).thenReturn("AB")
	when(dDao).updateSystem("user_dn", any, any).thenReturn(None)
	when(systemTypeDAO).updateSystemType("user_dn", any, any)

	upload = MockCGIFieldStorage()
	with open('dashboard_more.json', 'r') as file:
		x = file.read()
		upload.file = StringIO(x)

	patch(dDao, "createDashboard", massage_dashboard)
	when(dDao).getDashboardDetails ("user_dn", any).thenReturn(json.loads(x))
	when(rDao).bulkUpdateRecords ("user_dn", any).thenReturn("done")
	when(rDao).bulkUpdateArchiveRecords ("user_dn", any).thenReturn("done")
	when(lDao).updateLocation ("user_dn", any).thenReturn({"location_id": "xyz"})
	when(cDao).updateClassification("user_dn", any, any).thenReturn({" record_id":"xyz"})
	# classification, classification_id)

	response = d.uploadDashboard("user_dn", upload)
	A = [r["system_id"] for r in response["records"]]
	B = [r["system_id"] for r in response["dashboard"]["records"]]
	unstub()
	assert not np.array_equal(A, B)

def test_uploadDashboardError():
	when(dDao).getDashboardGroupingCodeCount("user_dn", any).thenReturn("AB")
	when(dDao).updateSystem("user_dn", any, any).thenReturn(None)
	when(systemTypeDAO).updateSystemType("user_dn", any, any)

	upload = MockCGIFieldStorage()
	with open('dashboard.json', 'r') as file:
		x = file.read()
		upload.file = StringIO(x)

	patch(dDao, "createDashboard", massage_dashboard)
	when(dDao).getDashboardDetails("user_dn", any).thenReturn(json.loads(x))
	when(rDao).bulkUpdateRecords("user_dn", any).thenReturn("done")
	when(rDao).bulkUpdateArchiveRecords("user_dn", any).thenReturn("done")
	when(lDao).updateLocation("user_dn", any).thenReturn({"location_id": "xyz"})
	# take off the classificationDao updateHelp mockito..will expect error.
	# classification, classification_id)

	response = d.uploadDashboard("user_dn", upload)
	assert response == {"status": "failed"}
