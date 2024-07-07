from app.src import dashboard as d

def test_updateHierarchy():
    when(r) \
        .convertDMStoDecimal("record") \
        .thenReturn(True)

    response = d.updateHierarchy("record")
    assert response == True