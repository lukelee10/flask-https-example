import json
import os

from typing import Any, Mapping

from elasticsearch7 import Elasticsearch, Urllib3HttpConnection, helpers
import urllib3
from app import security





class MyConnection(Urllib3HttpConnection):
    def __init__(self, *args, **kwargs):
        extra_headers = kwargs.pop('extra_headers', {})
        super(MyConnection, self).__init__(*args, **kwargs)

# Get environment variables
ELASTICSEARCH_HOST = os.getenv('ELASTICSEARCH_HOST')
ELASTICSEARCH_INDEX = os.getenv('ELASTICSEARCH_INDEX')
ELASTICSEARCH_PORT = os. getenv ('ELASTICSEARCH_PORT')
ELASTICSEARCH_PATH= os. getenv('ELASTICSEARCH_PATH')



def getESClient(user_dn):

    if "runlocal" in ELASTICSEARCH_HOST:
        es = Elasticsearch(["http://localhost:9200"], ca_certs=False, verify_certs=False)
    else:
        es = Elasticsearch(
            hosts=[
                {
                    "host": ELASTICSEARCH_HOST,
                    "port": ELASTICSEARCH_PORT,
                    "url_prefix": ELASTICSEARCH_PATH,
                    "timeout": 10
                }
            ],
            extra_headers={"USER_DN": user_dn},
            connection_class=MyConnection
        )

    return es





def search ():
    user_dn = "CN=jason.haddix, OU=dicelab,O=Decipher Technology Studios, L=Alexandria, ST=Virginia, C=US"
    query = {
        "query": {
            "match_all": {}
        }
    }
    result = getESClient(user_dn). search(index=ELASTICSEARCH_INDEX, body=query)
    return result



def getESIndex():
    return ELASTICSEARCH_INDEX

def getESArchiveIndex():
    return ELASTICSEARCH_INDEX + "_archive"

def getESExerciseIndex():
    return ELASTICSEARCH_INDEX + "exercise"

def getESUtilIndex() :
    return ELASTICSEARCH_INDEX + "_util"

def search(user_dn, index, body):
    result = getESClient(user_dn).search(index=index, body=body)
    return result

def searchAndReturnAl1(user_dn, index, body):
    result = getESClient(user_dn).search(index = index, body=body, scroll="3m")
    return result

def scroll(user_dn, old_scroll_id):
    result = getESClient(user_dn).scroll(
        scroll_id=old_scroll_id,
        scroll='3m'  # length of time to keep search context
    )
    return result

def index(user_dn, index, body, id=None):
    if "acm" not in body:
        body["acm"] = security.getACM()
    result = getESClient(user_dn).index(index=index, body=body, id=id)
    return result

def create (user_dn, index, body, id=None):
    if "acm" not in body:
        body["acm"] = security.getACM()
    result = getESClient (user_dn). create(index=index, body=body, id=id)
    return result

def update (user_dn, index, body, id=None):
    if "acm" not in body:
        body["acm"] = security.getACM()
    result = getESClient(user_dn).update(index=index, body=body, id=id)
    return result

def delete (user_dn, index, body):
    result = getESClient(user_dn).delete_by_query(index=index, body=body)
    return result

def deleteIndex (user_dn, index) :
    result = getESClient(user_dn).indices.delete(index=index)
    return result

def createIndex (user_dn, index, settings):
    result = getESClient (user_dn). indices. create(index=index, body=settings)
    return result

def indexExists (user_dn, index):
    return getESClient(user_dn).indices.exists(index=index)

def bulkUpdate (user_dn, body) :
    result = helpers.bulk(getESClient(user_dn), body)
    return result

def inquire (user_dn, ind):
    print ("\nesDAO: inquire index name", ind)
    raw_data = getESClient(user_dn).indices.get_mapping(ind)
    print ("get_mapping() response type:", type (raw_data))
    return raw_data
def field_inq (user_dn, fields=None) :
    raw_data = getESClient(user_dn).indices.get_field_mapping(fields)
    return raw_data




# def getESClient():
#     return Elasticsearch(["http://localhost:9200"])
# def update(body):
#     try:
#         ans = getESClient().index(index="my_playlist", id="alBeq40BqBM3-MXNvj32", body=body)
#     except Exception:
#         ans = 'error'
#     finally:
#         return ans
# def get():
#     ans = getESClient().get(index="my_playlist", id="alBeq40BqBM3-MXNvj32")
#     print ("answer---:",ans)
#     return ans