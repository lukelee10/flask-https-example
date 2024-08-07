from io import StringIO
import numpy as np

from app.src.dao import dashboardDAO as dDao
from app.src.dao import recordDAO as rDao
from app.src.dao import locationsDAO as lDao
from app.src.dao import classificationsDAO as cDao
from app.src.dao import helpDAO as hDao
from app.src import dashboard as d
from app.src.dao import systemTypeDAO
from mockito import when, unstub, any
import json
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

class MockCGIFieldStorage(object):
	pass
def test_uploadDashboard():
	when(dDao).getDashboardGroupingCodeCount("user_dn", any).thenReturn("AB")
	when(dDao).updateSystem("user_dn", any, any).thenReturn(None)
	when(systemTypeDAO).updateSystemType("user_dn", any, any)

	upload = MockCGIFieldStorage()
	with open('dashboard.json', 'r') as file:
		x = file.read()
		upload.file = StringIO(x)

	when(dDao).createDashboard ("user_dn", any, any).thenReturn(json.loads(x))
	when(dDao).getDashboardDetails ("user_dn", any).thenReturn(json.loads(x))
	when(rDao).bulkUpdateRecords ("user_dn", any).thenReturn("done")
	when(rDao).bulkUpdateArchiveRecords ("user_dn", any).thenReturn("done")
	when(lDao).updateLocation ("user_dn", any).thenReturn({"location_id": "xyz"})
	when(cDao).updateClassification("user_dn", any, any).thenReturn({" record_id":"xyz"})
	when(hDao).updateHelp("user_dn", any, any).thenReturn(True)
	# classification, classification_id)

	response = d.uploadDashboard("user_dn", upload)
	A = [r["system_id"] for r in response["records"]]
	B = [r["system_id"] for r in response["dashboard"]["records"]]

	unstub()
	assert not np.array_equal(A, B)

def test_uploadDashboardMore():
	when(dDao).getDashboardGroupingCodeCount("user_dn", any).thenReturn("AB")
	when(dDao).updateSystem("user_dn", any, any).thenReturn(None)
	when(systemTypeDAO).updateSystemType("user_dn", any, any)

	upload = MockCGIFieldStorage()
	with open('dashboard_more.json', 'r') as file:
		x = file.read()
		upload.file = StringIO(x)

	when(dDao).createDashboard ("user_dn", any, any).thenReturn(json.loads(x))
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

	when(dDao).createDashboard("user_dn", any, any).thenReturn(json.loads(x))
	when(dDao).getDashboardDetails("user_dn", any).thenReturn(json.loads(x))
	when(rDao).bulkUpdateRecords("user_dn", any).thenReturn("done")
	when(rDao).bulkUpdateArchiveRecords("user_dn", any).thenReturn("done")
	when(lDao).updateLocation("user_dn", any).thenReturn({"location_id": "xyz"})
	# take off the classificationDao updateHelp mockito..will expect error.
	# classification, classification_id)

	response = d.uploadDashboard("user_dn", upload)
	assert response == {"status": "failed"}
