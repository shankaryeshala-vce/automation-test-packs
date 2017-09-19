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

def getRCMDefinition(family, model, train, version):
        # print(data)
    contentIndex = 0
    fileIndex = 0
    fileList = []
    fileHash = []
    option = "ORIGINAL"
    optionAdd = "ADDENDUM"
    optionManu = "MANUFACTURING"
    #model = "340"
    exception = "No rcm definitions for system family"
    urlInventory = 'http://' + host + ':10000/rcm-fitness-paqx/rcm-fitness-api/api/rcm/inventory/vxrack/1000 FLEX/' + train + '/' + version + '/'

    #print(url)
    respInventory = requests.get(urlInventory)
    dataInventory = json.loads(respInventory.text)
    UUID = dataInventory["rcmInventoryItems"][0]["uuid"]
    print("UUID: %s" % UUID)

    url = 'http://' + host + ':10000/rcm-fitness-paqx/rcm-fitness-api/api/rcm/definition/' + UUID
    resp = requests.get(url)
    data = json.loads(resp.text)
    rcm = data["rcmDefinition"]
    rcmContent = data["rcmDefinition"]["rcmContents"]
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
            assert rcm["rcmTrain"] == train
            assert rcm["rcmVersion"] == version
            assert rcm["initialReleaseDate"] != ""
            assert rcm["lastModificationDate"] != ""
            assert rcm["endOfLifeDate"] != ""
            assert (rcm["viewOption"] == option) or (rcm["viewOption"] == optionAdd) or (rcm["viewOption"] == optionManu)
            prod = rcm["systemProductFamily"]
            mod = rcm["systemModelFamily"]
            train = rcm["rcmTrain"]
            version = rcm["rcmVersion"]
            combo = prod + '/' + mod + '/' + train + '/' + version
            print("RCM returned for: %s" % combo)

            while contentIndex < len(data["rcmDefinition"]["rcmContents"]):
                print("Loop: %d" % contentIndex)
                assert "uuid" in rcmContent[contentIndex] and rcmContent[contentIndex]["uuid"] != "", "No UUID returned in rcmContents."
                assert "category" in rcmContent[contentIndex] and rcmContent[contentIndex]["category"] != "", "No category returned in rcmContents."
                assert "component" in rcmContent[contentIndex] and rcmContent[contentIndex]["component"] != "", "No component returned in rcmContents."
                #assert "option" in rcmContent[contentIndex] and rcmContent[contentIndex]["option"] != "", "No option returned in rcmContents."
                assert "option" in rcmContent[contentIndex], "No option returned in rcmContents."
                assert "priorVersion" in rcmContent[contentIndex], "No priorVersion returned in rcmContents."
                assert "priorComponent" in rcmContent[contentIndex], "No priorComponent returned in rcmContents."
                assert "subType" in rcmContent[contentIndex], "No subType returned in rcmContents."
                assert "type" in rcmContent[contentIndex] and rcmContent[contentIndex]["type"] != "", "No type returned in rcmContents."
                assert "version" in rcmContent[contentIndex] and rcmContent[contentIndex]["version"] != "", "No version returned in rcmContents."
                assert "remediationFiles" in rcmContent[contentIndex] and rcmContent[contentIndex]["remediationFiles"] != "", "No remediationFiles returned in rcmContents."

                if "Compute" in rcmContent[contentIndex]["type"]:
                    assert rcmContent[contentIndex]["type"] == "Compute" or "Compute - Dell (R630/R730)"

                if "Management" in rcmContent[contentIndex]["type"]:
                    assert rcmContent[contentIndex]["type"] == "Management" or "Management - Dell (R630)"


                print(len(rcmContent[contentIndex]["remediationFiles"]))
                print("Component level checks complete.")

                if len(rcmContent[contentIndex]["remediationFiles"]) > 0:
                    print("Deep")
                    while fileIndex < len(rcmContent[contentIndex]["remediationFiles"]):
                        print("Deeper still")
                        print("File Loop: %d" % fileIndex)
                        assert "uuid" in rcmContent[contentIndex]["remediationFiles"][fileIndex], "No file UUID returned in remediationFiles."
                        assert rcmContent[contentIndex]["remediationFiles"][fileIndex]["uuid"] != "", "Unexpected file UUID returned in remediationFiles."
                        assert "filename" in rcmContent[contentIndex]["remediationFiles"][fileIndex], "No file name returned in remediationFiles."
                        assert rcmContent[contentIndex]["remediationFiles"][fileIndex]["filename"] != "", "Unexpected file name returned in remediationFiles."
                        assert "platform" in rcmContent[contentIndex]["remediationFiles"][fileIndex], "No platform returned in remediationFiles."
                        assert rcmContent[contentIndex]["remediationFiles"][fileIndex]["platform"] != "", "Unexpected platform returned in remediationFiles."
                        assert rcmContent[contentIndex]["remediationFiles"][fileIndex]["operatingSystem"] != "", "Unexpected operatingSystem returned in remediationFiles."
                        assert rcmContent[contentIndex]["remediationFiles"][fileIndex]["osArchitecture"] != "", "Unexpected osArchitecture returned in remediationFiles."
                        assert rcmContent[contentIndex]["remediationFiles"][fileIndex]["fileVersion"] != "", "Unexpected fileVersion returned in remediationFiles."
                        assert rcmContent[contentIndex]["remediationFiles"][fileIndex]["fileType"] != "", "Unexpected fileType returned in remediationFiles."
                        assert len(rcmContent[contentIndex]["remediationFiles"][fileIndex]["fileHash"]) > 16, "Unexpected fileHash returned in remediationFiles."
                        assert rcmContent[contentIndex]["remediationFiles"][fileIndex]["hashType"] == "SHA256" or "MD5", "Unexpected hash type returned in remediationFiles."
                        assert "/VxRack_1000_FLEX/Component/" in rcmContent[contentIndex]["remediationFiles"][fileIndex]["cdnPath"], "Unexpected path returned in remediationFiles."
                        versFileName = rcmContent[contentIndex]["remediationFiles"][fileIndex]["filename"]
                        versFileHash = rcmContent[contentIndex]["remediationFiles"][fileIndex]["fileHash"]
                        fileList.append(versFileName)
                        fileHash.append(versFileHash)
                        print("File level checks complete.")
                        fileIndex += 1
                    #contentIndex += 1
                fileIndex = 0
                contentIndex += 1


            print("List of filenames:", fileList)
            print("List of filehashes:", fileHash)



            print("\nReturned data has completed all defined checks successfully......")
            return


    assert False, "No RCMs not returned for model:" + model


def getRCMDefinition_Invalid(UUID, family, model):
        # print(data)

    option = "ORIGINAL"
    optionAdd = "ADDENDUM"
    optionManu = "MANUFACTURING"

    exception = "No rcm definitions for system family"
    url = 'http://' + host + ':10000/rcm-fitness-paqx/rcm-fitness-api/api/rcm/definition/' + UUID
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
    url = 'http://' + host + ':10000/rcm-fitness-paqx/rcm-fitness-api/api/rcm/inventory/' + rcmUUID + '/'
    print(url, "\n")
    resp = requests.get(url)

    print("Requesting a NULL rcmUUID ....")
    print(resp.status_code)
    assert resp.status_code == 404, "Request has not been acknowledged as expected."

@pytest.mark.rcm_fitness_mvp_extended
def test_getRCMDef1():
    getRCMDefinition("VxRack", "1000 FLEX", "9.2", "9.2.2")

@pytest.mark.rcm_fitness_mvp_extended
def test_getRCMDef2():
    getRCMDefinition("VxRack", "1000 FLEX", "9.2", "9.2.1")

@pytest.mark.rcm_fitness_mvp_extended
def test_getRCMDef3():
    getRCMDefinition_Invalid("12345678-1234-1234-1234-12347b7370a2", "VxRack", "FLEX")

@pytest.mark.rcm_fitness_mvp_extended
def test_getRCMDef4():
    getRCMDefinition_Invalid("----", "VxRack", "1000 FLEX")

@pytest.mark.rcm_fitness_mvp_extended
def test_getRCMDef5():
    getRCMDefinition_Invalid("1-1-1-1-1", "VxRack", "1000 FLEX")
@pytest.mark.rcm_fitness_mvp_extended
def test_getRCMDef6():
    getRCMDefinition_Null("")

