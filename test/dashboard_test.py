from io import StringIO
import numpy as np

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
def massage_dashboard(x, dashboard, y):
	tugged_dash[0] = dashboard
	return dashboard


def get_massaged_dashboard(user_dn, dashboard_id):
	return tugged_dash[0]

def get_leaves(obj_list, attribute_name):
	ans = []
	for r in obj_list:
		if attribute_name in r:
			ans.append(r[attribute_name])
		ans = ans + get_leaves(r["nodes"], attribute_name)
	return ans

class MockCGIFieldStorage(object):
	pass


def test_createDashboard():
	x = open("dashboard.json").read()
	response = d.createDashboard("user_dn", x, "ABC country-fleet 123", "true")
	assert response != None


def test_uploadDashboard():
	when(dDao).getDashboardGroupingCodeCount("user_dn", any).thenReturn("AB")
	when(dDao).updateSystem("user_dn", any, any).thenReturn(None)
	when(systemTypeDAO).updateSystemType("user_dn", any, any)


	with open('dashboard.json', 'r') as file:
		x = file.read()


	patch(dDao, "createDashboard", massage_dashboard)
	patch(dDao, "getDashboardDetails", get_massaged_dashboard)
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
