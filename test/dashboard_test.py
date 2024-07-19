from app.src.dao import dashboardDAO as dDao
from app.src.dao import recordDAO as rDao
from app.src import dashboard as d
from mockito import when, unstub
def test_getDashboard():
	when (dDao) \
		.getDashboard("user_dn", "dashboard_id") \
		.thenReturn(True)

	response = d.getDashboard ("user_dn", "dashboard id")

	assert response == True

def test_getDashboardDetails():
	when (dDao)
		.getDashboardDetails("user_dn", "dashboard_ id") \
		.thenReturn(True)

	response = d. getDashboardDetails ("user_dn", "dashboard_id")
	assert response == True

def test_deleteDashboard():
	when (dDao) \
		.deleteDashboard("user_dn", "dashboard_id") \
		.thenReturn(True)

	response = d. deleteDashboard ("user_dn", "dashboard_id")[" result"]
	assert response == "delete"

def test_deleteDashboardAndArchive():
	when(dDao)\
		.deleteDashboardAndArchive("user_dn", "dashboard_id") \
		.thenReturn(True)

	response = d. deleteDashboardAndArchive("user_dn", "dashboard_id" )["result"]
	assert response == "delete"

def test_getSystems():
	when (dDao) \
		.getSystems ("user_dn", "dashboard_id") \
		.thenReturn(True)

	response = d.getSystems ("user_dn", "dashboard_id")
	assert response == True

def test_getSystem():
	when (dDao) \
		.getSystem(" user_dn", "dashboard_id") \
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
	when(dDao)
		.getDashboardDetails("user_dn", "dashboard_id") \
		.thenReturn({"dashboard_id": "dashboard_id", "exercise": "false"})

	when(rDao) \
		.getTimeSeriesRecords ("user_dn", "dashboard id") \
		.thenReturn([])

	when(rDao) \
		.getFinalTimeSeriesRecords ("user_dn", "dashboard_id") \
		.thenReturn([])

	when (rDao)
		.getActivatedTimeSeriesRecords("user_dn", "dashboard_id") \
		.thenReturn([])

	when(dDao)
		.getDashboard("user_dn", "dashboard_id")
		.thenReturn(("dashboard_id": "dashboard_id", "name": "name", "color": "color"})

	response = d.getDashboardDetails("user_dn", "dashboard_id")
	unstub()

	assert len(response) == 3

# def test_getPath():
# response = d.getPath("user_dn", "dashboard_id", "guid")
# return response