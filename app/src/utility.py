import os
import cgi
from . import users
from .dao import esDAO
import traceback

def getPost(request):
    post_env = request.environ.copy()
    post_env['QUERY_STRING'] = ''
    post = cgi.FieldStorage(
        fp=request.environ['wsgi.input'],
        environ=post_env,
        keep_blank_values=True
    )
    return post

def getCredentials(request):
    if "User-Dn" in request.headers:
        user_dn = request.headers['User-Dn']
        user_dict = dict(x.split('=') for x in user_dn.split(',') if '=' in x)
        user_obj = {"user_cn": "", "user_dn": user_dn, "role": "read_only"}
        user_obj['user_cn'] = user_dict['CN']
        try:
            user_obj = users.getUser(user_dn, user_obj)
        except Exception as e:
            print("FAILED TO GET USER")
            traceback.print_exc()
        return user_obj
    else:  # USED FOR TEST RUNNING NON-SSL
        print("GETTING DEV USER DN")
        user_dn = os.getenv('DEV_USER_DN')
        user_dict = dict(x.split('=') for x in user_dn.split(',') if '=' in x)
        user_obj = {"user_cn": "", "user_dn": user_dn, "role": "read_only"}
        user_obj['user_c'] = user_dict['CN']
        user_obj = users.getUser(user_dn, user_obj)
        return user_obj


def getUserDN(request):
    try:

        user_dn = request. headers[' User-Dn']
        print ("LOG: " + user_dn + " is accessing " + request. url)
        return user_dn
    except Exception as e:
        print ("FAILED TO GET USER_DN. TRYING TO GET DEV DN")
        user_dn = os. getenv('DEV_USER_DN')
        print("LOG: DEV USER DN " + user_dn + " is accessing " + request.url)
        return user_dn

def reIndexer(keyName, data, userDN):
    if keyName == "dashboards":
        for object in data:
            esDAO.index(user_dn=userDN, index=esDAO.getESIndex(), body=object, id=object["dashboard_id"])
    elif keyName == "users":
        for object in data:
            esDAO.index(user_dn=userDN, index=esDAO.getESUtilIndex(), body=object, id=object["id"])
    elif keyName == "holidays":
        for object in data:
            esDAO.index(user_dn=userDN, index=esDAO.getESIndex(), body=object, id=object["holiday_id"])
    elif keyName == "locations":
        for object in data:
            esDAO.index(user_dn=userDN, index=esDAO.getESUtilIndex(), body=object, id=object["location_id"])
    elif keyName == "system_types":
        for object in data:
            object["doc_type"] = "systemTypes"
            esDAO.index(user_dn=userDN, index=esDAO.getESIndex(), body=object, id=object["systemType_id"])
    elif keyName == "classifications":
        for object in data:
            esDAO.index(user_dn=userDN, index=esDAO.getESIndex(), body=object, id=object["classification_id"])
    elif keyName == "notifications":
        for object in data:
            esDAO.index(user_dn=userDN, index=esDAO.getESIndex(), body=object)
    elif keyName == "helps":
        for object in data:
            esDAO.index(user_dn=userDN, index=esDAO.getESUtilIndex(), body=object, id=object["help_id"])
    elif keyName == "records_archive":
        for object in data:
            esDAO.index(user_dn=userDN, index=esDAO.getESArchiveIndex(), body=object, id=object["record_id"])
    elif keyName == "records":
        for object in data:
            esDAO.index(user_dn=userDN, index=esDAO.getESIndex(), body=object, id=object["record_id"])
    elif keyName == "systems":
        for object in data:
            esDAO.index(user_dn=userDN, index=esDAO.getESIndex(), body=object, id=object["system_id"])