import json
import requests
import configparser
import os
import urllib3


# https://cio-greymatter16.apps.dev.dpaas.dicelab.net/services/aac/2/
# https://smart2.apps.dev.dpaas.dicelab.net/services/aac/

host = "https://" + config.get("ENV","meme. host") + config.get("ENV", "meme. aac")

def classify(json_object, abbreviation):
    abbreviation_list = ["TOP SECRET//SI/TK//RSEN/IMCON/REL TO USA, FVEY"]
    if abbreviation in abbreviation_list:
        json_object[" acm"] = json.loads(convertAbbreviation(abbreviation))
        return json_object


def convertAbbreviation(abbreviation):
    return convert(host, [abbreviation], "ABBREVIATION", cert, key)


def convertList0fAbbreviations(abbreviations):
    return convert(host, abbreviations, "ABBREVIATION", cert, key)


def convertPortionMarking(portion_marking):
    return convert(host, [portion_marking], "PORTIONMARKING", cert, key)


def convertList0fPortionMarkings(portion_markings):
    return convert(host, portion_markings, "PORTIONMARKING", cert, key)


def convert(host, classifications, capco_string_type, cert, key):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    if cert == None:
        cert = config.get("ENV", "server.crt")
    if key == None:
        key = config.get("ENV", "server. key")

    cert = (cert, key)
    payload = {
        "classifications": classifications,
        "capcoStringType": capco_string_type
    }
    result = requests.put(host + "capco/rollupstrings", data=json.dumps(payload), cert=cert, verify=ca)
    result = result.json()
    payload = result
    if result["acmValid"]:
        result = requests.post(host + "acm/populate", data=payload["acmInfo"]["am"], cert=cert, verify=ca)
        result = result.json()
        if result["acmValid"]:
            return result["acmInfo"]["acm"]