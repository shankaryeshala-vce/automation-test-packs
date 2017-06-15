#!/usr/bin/env python
import json
import pytest
import pika
import sys
import logging
import requests
import os
import re
import af_support_tools
#import httplib2 as http
#from collections import Counter



@pytest.fixture(scope="module", autouse=True)
def load_test_data():
    global path
    path = "/home/autouser/PycharmProjects/auto-framework/test_suites/continuous-integration-deploy-suite/rcm-fitness-ci-cd/restLevelTests/rcmDefinitionByUUID/"
    ensurePathExists(path)
    purgeOldOutput(path, "rcmDef")

    global ssl_options
    ssl_options = {"ca_certs":"/etc/rabbitmq/certs/testca/cacert.pem","certfile":"/etc/rabbitmq/certs/certs/client/cert.pem","keyfile":"/etc/rabbitmq/certs/certs/client/key.pem","cert_reqs":"ssl.CERT_REQUIRED","ssl_version":"ssl.PROTOCOL_TLSv1_2"}

    # Set config ini file name
    global env_file
    env_file = 'env.ini'

    global host
    host = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='hostname')

    ensurePathExists(path)
    purgeOldOutput(path, "rcmDefinition")



def ensurePathExists(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

def purgeOldOutput(dir, pattern):
    for f in os.listdir(dir):
        if re.search(pattern, f) and f.endswith(".json"):
            os.remove(os.path.join(dir, f))
            print("Old output files successfully deleted.")
        else:
            print('Unable to locate output files to remove.')

def getRCMDefinition(family, model):
        # print(data)
    contentIndex = 0
    fileList = []
    fileHash = []
    option = "ORIGINAL"
    optionAdd = "ADDENDUM"
    optionManu = "MANUFACTURING"
    #model = "340"
    exception = "No rcm definitions for system family"
    urlInventory = 'http://' + host + ':19080/rcm-fitness-api/api/rcm/inventory/vxrack/FLEX/9.2'

    #print(url)
    respInventory = requests.get(urlInventory)
    dataInventory = json.loads(respInventory.text)
    UUID = dataInventory["rcmInventoryItems"][0]["uuid"]
    print("UUID: %s" % UUID)

    url = 'http://' + host + ':19080/rcm-fitness-api/api/rcm/definition/' + UUID
    resp = requests.get(url)
    data = json.loads(resp.text)
    rcm = data["rcmDefinition"]
    assert resp.status_code == 200, "Request has not been acknowledged as expected."

    if data != "":
        if data["message"] == None:
            #print(data)
# #            if
            with open(path + 'rcmDefinitionByUUID.json', 'a') as outfile:
                json.dump(data, outfile, sort_keys=True, indent=4, ensure_ascii=False)
#
            print("\nStarting to verify a sample of the returned data....")
            #print(url)

            assert data["message"] == None
            assert len(rcm) > 0
            lastRCM = len(rcm)
            midRCM = (len(rcm))/2
            print("Option: %s" % rcm["viewOption"])
            assert rcm["systemModelFamily"] == model
            assert rcm["systemProductFamily"] == family
            assert (rcm["viewOption"] == option) or (rcm["viewOption"] == optionAdd) or (rcm["viewOption"] == optionManu)
            prod = rcm["systemProductFamily"]
            mod = rcm["systemModelFamily"]
            train = rcm["rcmTrain"]
            version = rcm["rcmVersion"]
            combo = prod + '/' + mod + '/' + train + '/'  + version
            print("RCM returned for: %s" % combo)

            while contentIndex < len(data["rcmDefinition"]["rcmContents"]):
                if "versionFileName" in data["rcmDefinition"]["rcmContents"][contentIndex]:
                    assert "versionFileHash" in data["rcmDefinition"]["rcmContents"][contentIndex]
                    assert data["rcmDefinition"]["rcmContents"][contentIndex]["versionFileName"] != "", "No filename specified in definition."
                    assert data["rcmDefinition"]["rcmContents"][contentIndex]["versionFileHash"] != "", "No filename specified in definition."
                    versFileName = data["rcmDefinition"]["rcmContents"][contentIndex]["versionFileName"]
                    versFileHash = data["rcmDefinition"]["rcmContents"][contentIndex]["versionFileHash"]
                    fileList.append(versFileName)
                    fileHash.append(versFileHash)
                contentIndex += 1
            print("List of filenames:", fileList)
            print("List of filehashes:", fileHash)
            #contentndex = 0

        else:
            combo = str(family + "/" + model + "/")
            print("\nNo RCMs found for product/model combination: %s" % combo)
            print(data["message"])
            assert exception in data["message"], ("No RCMs not returned for model:" + model)


        print("\nReturned data has completed all defined checks successfully......")

def getRCMDefinition_Invalid(UUID, family, model):
        # print(data)

    option = "ORIGINAL"
    optionAdd = "ADDENDUM"
    optionManu = "MANUFACTURING"

    exception = "No rcm definitions for system family"
    url = 'http://' + host + ':19080/rcm-fitness-api/api/rcm/definition/' + UUID
    print("Requested UUID: %s" % UUID, "\n")
    resp = requests.get(url)
    data = json.loads(resp.text)
    rcm = data["rcmDefinition"]
    print(data, "\n")
    print(data["message"])

    assert resp.status_code == 200, "Request has not been acknowledged as expected."

    if ("message") in data.keys():
        assert ('RFCA101') in (data["message"]), "Returned Error Message does not reflect missing correlation ID."

    print("\nReturned data has completed all defined checks successfully......")


def getRCMDefinition_Null(rcmUUID):
    url = 'http://' + host + ':19080/rcm-fitness-api/api/rcm/inventory/' + rcmUUID + '/'
    print(url, "\n")
    resp = requests.get(url)

    print("Requesting a NULL rcmUUID ....")
    print(resp.status_code)
    assert resp.status_code == 404, "Request has not been acknowledged as expected."

@pytest.mark.rcm_fitness_mvp_extended
def test_getRCMDef1():
    getRCMDefinition("VxRack", "FLEX")

@pytest.mark.rcm_fitness_mvp_extended
def test_getRCMDef2():
    getRCMDefinition_Invalid("12345678-1234-1234-1234-12347b7370a2", "VxRack", "FLEX")

@pytest.mark.rcm_fitness_mvp_extended
def test_getRCMDef3():
    getRCMDefinition_Invalid("----", "VxRack", "FLEX")

@pytest.mark.rcm_fitness_mvp_extended
def test_getRCMDef4():
    getRCMDefinition_Invalid("1-1-1-1-1", "VxRack", "FLEX")
@pytest.mark.rcm_fitness_mvp_extended
def test_getRCMDef5():
    getRCMDefinition_Null("")


#@pytest.mark.TC546562_Vxblock
#def test_getRCMDef5():
#    getRCMDefinition_Invalid("", "Vblock", "340")

# getRCMDefinition("0ef9b082-0d9f-479b-9934-ff0f7b7370a2", "Vblock", "340")
# getRCMDefinition("12345678-1234-1234-1234-12347b7370a2", "Vblock", "340")
# getRCMDefinition("----", "Vblock", "340")
# getRCMDefinition("1-1-1-1-1", "Vblock", "340")
# getRCMDefinition("", "Vblock", "340")
#getRCMDefinition()
#getAvailableRCMs("Block")
#getRCMDefinition()
