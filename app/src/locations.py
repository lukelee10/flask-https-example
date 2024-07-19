import traceback
import json
import pandas as pd
from .dao import locationDAO as lDAO
import re
import uuid


def updateLocation (user_dn, location):
    if type(location) == str:
        location = json.loads(location)

    if "record_location_name" not in location or location["record_location_name"] == "":
        location["record_location_name"] = "UNKNOWN"


    if location["location_id"] == "":
        location["location_id"] = str(uuid.uuid4())
        res = lDAO.createLocation (user_dn, location)
    else:
        res = lDAO.updateLocation(user_dn, location)

    return res


def getLocations(user_dn, dashboard_id):
    return lDAO.getLocations(user_dn, dashboard_id)


def getLocation (user_dn, id):
    return lDAO.getLocation(user_dn, id)


def delete (user_dn, id, dashboard_id):
    if id == "all":
        return lDAO.deleteAllLocations (user_dn, dashboard_id)
    else:
        return lDAO.deleteLocation (user_dn, id)


'''
upload a CSV
'''
def uploadLocations(user_dn, dashboard_id, upload_file):
    try:
        csv_file = pd.read_csv(upload_file.file, sep=", ")
        locs = csv_file.to_json(orient="records", date_format="epoch", force_ascii=True, date_unit="ms", default_handler=None)
        locs_json = json.loads(locs)
        line_count = 0

        for loc in locs_json:
            line_count = line_count + 1
            if "." in loc["latitude"]:
                lat = loc["latitude"][:loc["latitude"].find(".")] + loc["latitude"][-1:]
                lng = loc["longitude"][:loc["longitude"].find(".")] + loc["longitude"][-1:]
            else:
                lat = loc["latitude"]
                lng = loc["longitude"]

            lat = lat.strip()
            lng = lng.strip()

            if (re.search("^.{5}$", loc["osuffix"])== None):
                print("FAILED OSSUFIX")
                print(loc)
                return {"result": "failed", "message": "Osuffix not valid: line " + str(line_count)}

            if (re.search("^\d{6}[N|S]{1}$", lat) == None):
                print("FAILED LAT")
                print(loc)
                return {"result": "failed", "message": "latitude not valid: line " + str(line_count)}
            if (re.search("^\d{7}[E]w]{1}$", lng) == None):
                print("FAILED LONG")
                print(loc)
                return {"result": "failed", "message": "longitude not valid: line " + str(line_count)}

            new_loc = {
                "location_id": str(uuid.uuid4()),
                "dashboard_id": dashboard_id,
                "record location_name": loc["name"],
                "record_location_benumber": loc["be_number"],
                "record_location_osuffix": loc["osuffix"],
                "record_location_latitude": lat,
                "record_location_longitude": lng,
                "record_location_catcode": loc["catcode"],

                "record_location_semi_major": loc["semi_major"],
                "record_location_semi_minor": loc["semi_minor"],
                "record_location_radius": loc["radius"],
                "record_location_orient": loc["orient"]
            }

            if "elevation" in loc:
                new_loc["record_location_elevation"] = loc["elevation"]

            try:
                lDAO.updateLocation(user_dn, new_loc)
            except Exception as ese:
                print(str(ese))
                print(new_loc)


        #{...}
        return {"result": "success"}
    except Exception as e:
        print(str(e))