from app.src.dao import dashboardDAO as dDao
from app.src.dao import recordDAO as rDao
from app.src.dao import systemTypeDAO as sTDao
from app.src import record as r
from app.src import dashboard as d
from mockito import when
import datetime

# def test_removeRecordAttribute():
# when (rDao) \
#    getRecordsBySystemId("user_dn", "system_id")
#    thenReturn([])

#    response = r. removeRecordAttribute("user_dn", "system_id", "attribute_name") ["results"]
#    assert response == "0 records updated"

def test_convertDMStoDecimal():
    when(r) \
        .convertDMStoDecimal("record") \
        .thenReturn(True)

    response = r.convertDMStoDecimal("record")
    assert response == True

# in theory, fix mail. send
def test_emailRecord():
    when(r) \
        .getRecordForEdit ("user_dn", "system_id", "guid", "") \
        .thenReturn({"record": {"dashboard_cycle": "", "dashboard_grouping_code": "", "record_path": "", "record_type": ""}, "recordwww":33})

    when(r) \
        .emailRecord("mail", "user_dn", "dashboard_id", "system_id", "guid", "exercise") \
        .thenReturn(True)

    when(dDao) \
        .getDashboardDetails("user_dn", "dashboard_id") \
        .thenReturn({"dashboard_emails_to": "johndoe@dia.gov"})

    response = r.emailRecord("mail", "user_dn", "dashboard_id", "system_id", "guid", "exercise")
    assert response == True

def test_getAcrhive():
    when(rDao) \
        .getArchive("user_dn", "record_id") \
        .thenReturn([])

    response = r.getArchive ("user_dn", "record_id") ["record_form"]
    assert response == None

def test_uploadRecord():
    when (r) \
        .uploadRecord("user_dn", "upload_file", "file_type") \
        .thenReturn(True)

    response = r.uploadRecord ("user_dn", "upload_file", "file_type")
    assert response == True

def test_export ():
    when (r) \
        .export ("user_dn", "rec_list") \
        .thenReturn(True)

    response = r. export ("user_dn", "rec_list")
    assert response == True

# def test_deleteRecordsByGuid():
# when (rDao)
#    .deleteRecordsByguid("user_dn", "guid")
#    .thenReturn(True)

# response = r. deleteRecordsByGuid("user_dn", "guid")
# assert response == True

# def test deleteRecordByid():
# when (rDao)
#   .deleteRecordByid("user_dn", "record_id") \ #
#   .thenReturn(True)

# response = r.deleteRecordById ("user_dn", "record_id")
# assert response == True

def test_getRecordSeries():
    when(dDao) \
        .getDashboardDetails("user_dn", "dashboard_id") \
        .thenReturn({"dashboard_grouping_code": "TEST", "dashboard_smart_code": "TEST"})

    response = r.getRecordSeries("user_dn", "dashboard_id")

    assert response == "TEST" + str(datetime.datetime.now().year)[-2:] + "TEST"

def test_getTimeoutRecords():
    when (rDao) \
        .getTimeoutRecords ("user_dn", "dashboard_id") \
        .thenReturn(True)

    response = r.getTimeoutRecords ("user_dn", "dashboard_id")
    assert response == True

def test_getLastUpdatedRecord():
    when (r) \
        .getLastUpdatedRecord ("user_dn", "rec_list") \
        .thenReturn(True)

    response = r. getLastUpdatedRecord("user_dn", "rec_list")
    assert response == True

def test_getNextTrackingId():
    when(r) \
        .getRecordSeries("user_dn", "dashboard_id") \
        .thenReturn("TEST")

    when (rDao) \
        .getLastRecord ("user_dn", "dashboard_id") \
        .thenReturn(["noresults"])

    response = r. getNextTrackingId("user_dn", "dashboard_id")
    assert response == "TEST0001"

def test_getMetricsData():
    when (rDao) \
        .getArchiveHistogram("user_dn") \
        .thenReturn([])

    response = r. getMetricsData("user_dn")
    assert response == {"histogram": {"dashboards": [], "data": []}}

# def test_getArchiveRecords():
# when (rDao) \
# •getArchiveRecords("user_dn", "dashboard_id") \
# .thenReturn(True)

# response = r. getArchiveRecords ("user_dn", "dashboard_id")
# assert response == True

def test_getRecords():
    when (rDao) \
        .getRecords ("user_dn", "dashboard_id") \
        .thenReturn(True)

    response = r. getRecords("user_dn", "dashboard_id")
    assert response == True

def test_createArchive():
    when(r) \
        .createArchive ("user_dn", "record") \
        .thenReturn(True)

    response = r.createArchive("user_dn", "record")
    assert response == True

def test_updateSystemsOfGroup():
    when(d) \
        .getGroupSystems("user_dn", "group_record", "group_record") \
        .thenReturn ( {"nodes": []})

    when (r) \
        .updateSystems0fGroup ("user_dn", "action", "group_record", "selected_systems", "set_default") \
        .thenReturn(True)

    response = r.updateSystemsOfGroup("user_dn", "action", "group_record", "selected_systems", "set_default")
    assert response == True

def test_setDefaultRecord():
    response = r.setDefaultRecord({"default_values":[]})
    assert response == {"default_values": {}}

# TODO FIX LATER
def test_updateRecord():
    when(dDao) \
        .getSystem("user_dn", 0) \
        .thenReturn({"dashboard_id": 0, "name": "test"})

    when(dDao) \
        .getDashboard("user_dn", 0) \
        .thenReturn({"levels": [[]]})

    when(r) \
        .getSystemType([], 0) \
        .thenReturn(0)

    # get system types for dashboard 0
    when(sTDao) \
        .getSystemTypes("user_dn", 0) \
        .thenReturn({"name": "test"})
    # # #
    when(r) \
        .convertDMStoDecimal({'system_id': 0, 'guid': 0, 'record_event_date': None, 'record_source_date': None, 'audit_date': None}) \
        .thenReturn({"record_series": "test", "record_id": 0})

    when(rDao) \
        .createRecord("user_dn", "record", "test") \
        .thenReturn(True)
    # # *
    when(r) \
        .updateSystemsOfGroup("user_dn", "action",
                              {'system_id': 0, 'guid': 0, 'record_event_date': None, 'record_source_date': None},
                              [], False) \
        .thenReturn(True)

    response = r.updateRecord("user_dn", "create", "update_group", "set_default",
                              {'system_id': 0, 'guid': 0, 'record_event_date': 0}, True)
    assert response == True

def test_getSystemType():
    response = r. getSystemType({"nodes": []}, "guid")
    assert response == None

def test_getTimeSeriesRecords():
    when(dDao) \
        .getDashboard("user_dn", "dashboard_id") \
        .thenReturn({" dashboard_id" : "test", "name": "test", "color": "test"})

    when(rDao) \
        .getTimeSeriesRecords ("user_dn", "test") \
        .thenReturn([])

    response = r.getTimeSeriesRecords("user_dn", "dashboard_id", "false")
    assert len(response) == 2

def test_getActiveRecords():
    when(rDao) \
        .getRecordsFromIds("user_dn", 0) \
        .thenReturn(True)

    response = r.getActiveRecords("user_dn", str({}))
    assert response == True

def test_getRecordsFromList():
    when (rDao) \
        .getRecordsFromIds("user_dn", {}) \
        .thenReturn({"records": []})

    response = r. getRecordsFromList("user_dn", str({}))
    assert response == {"records": []}

def test_getRecord():
    when(rDao) \
        .getRecord("user_dn", "guid") \
        .thenReturn(True)

    response = r. getRecord ("user_dn", "guid")
    assert response == True

# def test getRecordById):
# when (rDao) l
#   .getRecordByrecordId("user_dn", "record_id") \
#   .thenReturn(True)

# response = r.getRecordById ("user_dn", "record_id")
# assert response == True

def test_getRecordForEdit():
    when(dDao) \
        .getSystem("user_dn", "system_id") \
        .thenReturn ({"dashboard_id": 0, "system_id": 0, "sections": []})

    when(dDao) \
        .getDashboardDetails ("user_dn", 0) \
        .thenReturn({})

    when(rDao) \
        .getRecord ("user_dn", "guid") \
        .thenReturn({" system_id": 0, "record_type": "test"})

    when(d) \
        .getPath ("user_dn", 0, "guid") \
        .thenReturn(True)

    response = r.getRecordForEdit("user_dn", "system_id", "guid", "" )
    assert len (response) == 2