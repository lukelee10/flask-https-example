from ..dao import esDAO as esDao
import configparser
import os
import traceback

def setupES(user_dn):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ELASTICSEARCH_INDEX = os. getenv('ELASTICSEARCH_INDEX')

    if esDao. indexExists (user_dn, ELASTICSEARCH_INDEX):
        print ("run me again")
        # try:
        # print ("delete old index")
        # esDao. deleteIndex (user_dn, ELASTICSEARCH_INDEX)
        # except Exception as e:
        #
        traceback.print_exc()
        # try:
        #   print ("delete old index")
        #
        #   esDao. deleteIndex(user_dn, ELASTICSEARCH_INDEX + "_archive")
        # except Exception as e:
        #   traceback.print_exc()

        # try:
        #   print ("delete old index")
        #   esDao. deleteIndex (user_dn, ELASTICSEARCH_INDEX + "_util")
        # except Exception as e:
        #   traceback.print_exc()
    else:
        try:
            print("creating indexes")
            settings_filepath = BASE_DIR + "/dao/settings/settings.json"
            with open (settings_filepath) as infile:
                settings = infile.read()
            esDao.createIndex(user_dn, ELASTICSEARCH_INDEX, settings)
            esDao.createIndex(user_dn, ELASTICSEARCH_INDEX, "_archive", settings)
            esDao.createIndex(user_dn, ELASTICSEARCH_INDEX, "_util", settings)
        except Exception as e:
            traceback.print_exc()

    print("DONE")