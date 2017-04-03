#!/usr/bin/env python
import json
import traceback
import requests
from collections import Counter
import pytest
import os
import re
import af_support_tools

try:
    env_file = 'env.ini'
    host = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='hostname')

except:
    print('Possible configuration error')

#host = '10.3.8.54'
path = '/home/autouser/PycharmProjects/auto-framework/test_suites/continuousIntegration/rcmComplianceScan/'

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

ensurePathExists(path)
purgeOldOutput(path, "rcm")

#open(path + "rcmSystemDefinition.json", 'w').close()

def getSystemDefinition():
    url = 'http://' + host + ':19080/rcm-fitness-api/api/system/definition/'
    resp = requests.get(url)
    data = json.loads(resp.text)

    print("Requesting UUID from System Definition....")
    assert resp.status_code == 200, "Request has not been acknowledged as expected."

    if data != "":
        if data["systems"][0]["uuid"] != "":
            with open(path + 'rcmSystemDefinition.json', 'w') as outfile:
                json.dump(data, outfile, sort_keys=True, indent=4, ensure_ascii=False)

            print("\nExtracting UUID from response....\n")
            global systemUUID
            systemUUID = data["systems"][0]["uuid"]
            print(systemUUID)
        else:
            print("\nNo System UUID returned in REST response")
            print(data["message"])

    print("Defined SystemUUID: %s" % systemUUID)
    return systemUUID

def getComplianceDataNexus(model, type, filename):
    subIndex = 0
    compIndex = 0
    versionIndex = 0
    url = 'http://' + host + ':19080/rcm-fitness-api/api/system/definition/' + systemUUID + '/component/'

    resp = requests.get(url)
    data = json.loads(resp.text)

    assert resp.status_code == 200, "Request has not been acknowledged as expected."
    print("Requesting latest discovered f/w version from Compliance Data service...")

    totalComponents = len(data["components"])

    assert data["message"] == None, "Error response returned unexpectedly."


    if data != "":
        #print("1")

        while compIndex < totalComponents:
            if "modelFamily" in data["components"][compIndex]["definition"] and data["components"][compIndex]["definition"]["modelFamily"] == model:
                print(data["components"][compIndex]["definition"]["modelFamily"])
                #print("4")
                global compUUID
                compUUID = data["components"][compIndex]["uuid"]
                print(compUUID)
                compURL = 'http://' + host + ':19080/rcm-fitness-api/api/compliance/data/device/' + compUUID

                compResp = requests.get(compURL)
                compData = json.loads(compResp.text)

                assert compResp.status_code == 200, "Request has not been acknowledged as expected."
                assert compData["message"] is None, "Error response returned unexpectdely."
                print("Message: %s" % compData["message"])
                with open(filename, 'a') as outfile:
                    json.dump(compData, outfile, sort_keys=True, indent=4, ensure_ascii=False)

                while subIndex < len(compData["subComponents"]):
                    print("1")
                    if "model" in compData["subComponents"][subIndex]["elementData"]:
                        print("2")
                        if model in (compData["subComponents"][subIndex]["elementData"]["model"]) and (compData["subComponents"][subIndex]["elementData"]["elementType"] == type):
                            print("3")
                            while versionIndex < len(compData["subComponents"][subIndex]["versionDatas"]):
                                print("4")
                                if (compData["subComponents"][subIndex]["versionDatas"][versionIndex]["type"]) == "FIRMWARE":
                                    print("5")
                                    global nexusFWversionComponent
                                    nexusFWversionComponent = (compData["subComponents"][subIndex]["versionDatas"][versionIndex]["version"])
                                    print("\n\nComponent requested: %s" % compUUID)
                                    print("\nDiscovered firmware version: %s\n\n" % nexusFWversionComponent)
                                versionIndex += 1
                    subIndex += 1
                subIndex = 0
            compIndex += 1
        compIndex = 0

def getComplianceDataMDS(model, type, filename):
    subIndex = 0
    compIndex = 0
    versionIndex = 0
    url = 'http://' + host + ':19080/rcm-fitness-api/api/system/definition/' + systemUUID + '/component/'

    resp = requests.get(url)
    data = json.loads(resp.text)

    assert resp.status_code == 200, "Request has not been acknowledged as expected."
    print("Requesting latest discovered f/w version from Compliance Data service...")

    totalComponents = len(data["components"])

    assert data["message"] == None, "Error response returned unexpectedly."


    if data != "":
        #print("1")

        while compIndex < totalComponents:
            if "modelFamily" in data["components"][compIndex]["definition"] and data["components"][compIndex]["definition"]["model"] == model:
                print(data["components"][compIndex]["definition"]["model"])
                #print("4")
                global compUUID
                compUUID = data["components"][compIndex]["uuid"]
                print(compUUID)
                compURL = 'http://' + host + ':19080/rcm-fitness-api/api/compliance/data/device/' + compUUID

                compResp = requests.get(compURL)
                compData = json.loads(compResp.text)

                assert compResp.status_code == 200, "Request has not been acknowledged as expected."
                assert compData["message"] is None, "Error response returned unexpectdely."
                print("Message: %s" % compData["message"])
                with open(filename, 'a') as outfile:
                    json.dump(compData, outfile, sort_keys=True, indent=4, ensure_ascii=False)

                while subIndex < len(compData["subComponents"]):
                    print("1")
                    if "model" in compData["subComponents"][subIndex]["elementData"]:
                        print("2")
                        if model in (compData["subComponents"][subIndex]["elementData"]["model"]) and (compData["subComponents"][subIndex]["elementData"]["elementType"] == type):
                            print("3")
                            while versionIndex < len(compData["subComponents"][subIndex]["versionDatas"]):
                                print("4")
                                if (compData["subComponents"][subIndex]["versionDatas"][versionIndex]["type"]) == "FIRMWARE":
                                    print("5")
                                    global nexusFWversionComponent
                                    nexusFWversionComponent = (compData["subComponents"][subIndex]["versionDatas"][versionIndex]["version"])
                                    print("\n\nComponent requested: %s" % compUUID)
                                    print("\nDiscovered firmware version: %s\n\n" % nexusFWversionComponent)
                                versionIndex += 1
                    subIndex += 1
                subIndex = 0
            compIndex += 1
        compIndex = 0

def getComplianceDataSystem():
    subIndex = 0
    compIndex = 0
    versionIndex = 0
    url = 'http://' + host + ':19080/rcm-fitness-api/api/system/definition/' + systemUUID + '/component/'

    resp = requests.get(url)
    data = json.loads(resp.text)

    assert resp.status_code == 200, "Request has not been acknowledged as expected."
    print("Requesting latest discovered f/w version from Compliance Data service...")

    totalComponents = len(data["components"])

    if data != "":
        while compIndex < totalComponents:
            if "modelFamily" in data["components"][compIndex]["definition"]:
                if data["components"][compIndex]["definition"]["modelFamily"] == model:
                    global compUUID
                    compUUID = data["components"][compIndex]["uuid"]

                    systemURL = 'http://' + host + ':19080/rcm-fitness-api/api/compliance/data/system/' + systemUUID

                    systemResp = requests.get(systemURL)
                    systemData = json.loads(systemResp.text)

                    assert systemResp.status_code == 200, "Request has not been acknowledged as expected."
                    with open(filename, 'a') as outfile:
                        json.dump(compData, outfile, sort_keys=True, indent=4, ensure_ascii=False)

                    while subIndex < len(systemData["subComponents"]):
                        if "model" in systemData["subComponents"][subIndex]["elementData"]:
                            if model in (systemData["subComponents"][subIndex]["elementData"]["model"]) and (systemData["subComponents"][subIndex]["elementData"]["elementType"] == type):
                                while versionIndex < len(compData["subComponents"][subIndex]["versionDatas"]):
                                    if (compData["subComponents"][subIndex]["versionDatas"][versionIndex]["type"]) == "FIRMWARE":
                                        global nexusFWversionSystem
                                        nexusFWversionSystem = (compData["subComponents"][subIndex]["versionDatas"][versionIndex]["version"])
                                        assert nexusFWversionSystem == nexusFWversionComponent
                                        print("\n\nComponent requested: %s" % compUUID)
                                        print("\nDiscovered firmware version: %s\n\n" % nexusFWversionSystem)
                                    versionIndex += 1
                        subIndex += 1
            compIndex += 1
            #compIndex = 0

def getAvailableRCMs(family, model, train, version, filename):
        # print(data)
    numRCMs = 0
    rcmIndex = 0
    option = "ORIGINAL"
    optionAdd = "ADDENDUM"
    optionManu = "MANUFACTURING"

    exception = "No RCM definition systems for system family"
    url = 'http://' + host + ':19080/rcm-fitness-api/api/rcm/inventory/' + family + "/" + model + "/" + train + "/" + version
    print(url)
    resp = requests.get(url)
    data = json.loads(resp.text)

    assert resp.status_code == 200, "Request has not been acknowledged as expected."
    print("Requesting a list of available RCMs for the specific version: %s" % version)
    if data != "":
        if data["message"] == None:
            with open(filename, 'a') as outfile:
                json.dump(data, outfile, sort_keys=True, indent=4, ensure_ascii=False)

            print("\nStarting to verify a sample of the returned data....\n")

            assert len(data["rcmInventoryItems"]) > 0
            assert data["rcmInventoryItems"][0]["systemModelFamily"] == model
            assert data["rcmInventoryItems"][0]["systemProductFamily"] == family
            assert data["rcmInventoryItems"][0]["rcmTrain"] == train
            assert data["rcmInventoryItems"][0]["rcmVersion"] == version

            assert (data["rcmInventoryItems"][0]["viewOption"] == option) or (data["rcmInventoryItems"][0]["viewOption"] == optionAdd) or (data["rcmInventoryItems"][0]["viewOption"] == optionManu)
        else:
            combo = str(family + "/" + model + "/" + train + "/" + version)
            print("\nNo RCMs found for product/train/model combination: %s" % combo)
            print(data["message"])
            assert exception in data["message"], "No RCMs not returned for train:" + train

    while numRCMs < len(data["rcmInventoryItems"]):
        if (data["rcmInventoryItems"][numRCMs]["viewOption"]) == option:
            global rcmUUID
            rcmUUID = (data["rcmInventoryItems"][numRCMs]["uuid"])
            print("Requested rcmUUID: %s" % rcmUUID)
        numRCMs += 1

def getRCMDefinition(component, filename):
    contentIndex = 0
    url = 'http://' + host + ':19080/rcm-fitness-api/api/rcm/definition/' + rcmUUID
    print(url)
    resp = requests.get(url)
    data = json.loads(resp.text)

    assert resp.status_code == 200, "Request has not been acknowledged as expected."

    print("\nStarting to verify a sample of the returned data....")
    if data != "":
        if data["message"] == None:

            with open(filename, 'a') as outfile:
                json.dump(data, outfile, sort_keys=True, indent=4, ensure_ascii=False)
            if data["rcmDefinition"]["viewOption"] == "ORIGINAL":
                while contentIndex < len(data["rcmDefinition"]["rcmContents"]):
                    if component in (data["rcmDefinition"]["rcmContents"][contentIndex]["component"]):
                        firmwareVersion = (data["rcmDefinition"]["rcmContents"][contentIndex]["version"])
                        print("\n\nExpected version: %s" % firmwareVersion)
                    contentIndex += 1

def getRCMEvaluation(product, model, filename):

    url = 'http://' + host + ':19080/rcm-fitness-api/api/rcm/evaluation/'
    payload = {'systemUuid': systemUUID, 'rcmUuid': rcmUUID}
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    resp = requests.post(url, data=json.dumps(payload), headers=headers)
    data = json.dumps(payload)

    print("Returned status code: %d" % resp.status_code)
    print("SystemUUID:" + systemUUID)
    print("rcmUUID:" + rcmUUID)
    response = json.loads(resp.text)
    assert resp.status_code == 200, "Request has not been acknowledged as expected."

    numResults = 0
    count = 0

    with open(filename, 'a') as outfile:
        json.dump(response, outfile, sort_keys=True, indent=4, ensure_ascii=False)


    while numResults < len(response["rcmEvaluationResults"]):
        if response["rcmEvaluationResults"][numResults]["evaluatedRcmDatum"]["product"] == product:
            if (response["rcmEvaluationResults"][numResults]["evaluatedRcmDatum"]["model"]) == model:
                versionFound = (response["rcmEvaluationResults"][numResults]["actualValue"])
                versionExpected = (response["rcmEvaluationResults"][numResults]["expectedValues"][0])
                if versionFound == versionExpected:
                    print(model)
                    print(response["rcmEvaluationResults"][numResults]["evaluationResult"])
                    assert (response["rcmEvaluationResults"][numResults]["evaluationResult"]) == "match", "Expected a match to be returned, not the case."

                else:
                    print(model)
                    print(response["rcmEvaluationResults"][numResults]["evaluationResult"])
                    assert (response["rcmEvaluationResults"][numResults]["evaluationResult"]) == "mismatch", "Expected a mismatch to be returned, not the case."
                print("Version found: %s" % versionFound)
                print("Version expected: %s" % versionExpected)


        numResults += 1

#@pytest.mark.TC546466
@pytest.mark.rcm_fitness_mvp
def test_getSysDef1():
    getSystemDefinition()
@pytest.mark.rcm_fitness_mvp
def test_getComplianceData1():
    pytest.skip('Disable for harness stability')
    getComplianceDataNexus("N3K", "FIXEDMODULE", path + "rcmComplianceData-N3k.json")
@pytest.mark.rcm_fitness_mvp
def test_getAvailableRCM1():
    getAvailableRCMs("Vblock", "340", "6.0", "6.0.11", path + "rcmAvailableRCMs-N3k.json")
@pytest.mark.rcm_fitness_mvp
def test_getRCMDefinition1():
    getRCMDefinition("Nexus 3048", path + "rcmRCMDefinitionDetails-N3k.json")
@pytest.mark.rcm_fitness_mvp
def test_getRCMEval1():
    getRCMEvaluation("Nexus", "3048", path + "rcmEvaluationDetails-N3k.json")
@pytest.mark.rcm_fitness_mvp
def test_getComplianceData2():
    pytest.skip('Disable for harness stability')
    getComplianceDataNexus("N5K", "FIXEDMODULE", path + "rcmComplianceData-N5k.json")
@pytest.mark.rcm_fitness_mvp
def test_getAvailableRCM2():
    getAvailableRCMs("Vblock", "340", "6.0", "6.0.11", path + "rcmAvailableRCMs-N5k.json")
@pytest.mark.rcm_fitness_mvp
def test_getRCMDefinition2():
    getRCMDefinition("Nexus 55xx", path + "rcmRCMDefinitionDetails-N5k.json")
@pytest.mark.rcm_fitness_mvp
def test_getRCMEval2():
    getRCMEvaluation("Nexus", "55xx", path + "rcmEvaluationDetails-N5k.json")
@pytest.mark.rcm_fitness_mvp
def test_getComplianceData3():
    getComplianceDataMDS("9148", "FIXEDMODULE", path + "rcmComplianceData-MDS9k.json")
@pytest.mark.rcm_fitness_mvp
def test_getAvailableRCM3():
    getAvailableRCMs("Vblock", "340", "6.0", "6.0.10", path + "rcmAvailableRCMs-MDS9k.json")
@pytest.mark.rcm_fitness_mvp
def test_getRCMDefinition3():
    getRCMDefinition("MDS 9148", path + "rcmRCMDefinitionDetails-MDS9k.json")
@pytest.mark.rcm_fitness_mvp
def test_getRCMEval3():
    getRCMEvaluation("MDS", "9148", path + "rcmEvaluationDetails-MDS9k.json")
@pytest.mark.rcm_fitness_mvp
def test_getComplianceData4():
    pytest.skip('Disable for harness stability')
    getComplianceDataNexus("N3K", "FIXEDMODULE", path + "rcmComplianceData-N3k-Mismatch.json")
@pytest.mark.rcm_fitness_mvp
def test_getAvailableRCM4():
    getAvailableRCMs("Vblock", "340", "5.0", "5.0.4", path + "rcmAvailableRCMs-N3k-Mismatch.json")
@pytest.mark.rcm_fitness_mvp
def test_getRCMDefinition4():
    getRCMDefinition("Nexus 3048", path + "rcmRCMDefinitionDetails-N3k-Mismatch.json")
@pytest.mark.rcm_fitness_mvp
def test_getRCMEval4():
    getRCMEvaluation("Nexus", "3048", path + "rcmEvaluationDetails-N3k-Mismatch.json")
@pytest.mark.rcm_fitness_mvp
def test_getComplianceData5():
    pytest.skip('Disable for harness stability')
    getComplianceDataNexus("N5K", "FIXEDMODULE", path + "rcmComplianceData-N5k-Mismatch.json")
@pytest.mark.rcm_fitness_mvp
def test_getAvailableRCM5():
    getAvailableRCMs("Vblock", "340", "5.0", "5.0.7", path + "rcmAvailableRCMs-N5k-Mismatch.json")
@pytest.mark.rcm_fitness_mvp
def test_getRCMDefinition5():
    getRCMDefinition("Nexus 55xx", path + "rcmRCMDefinitionDetails-N5k-Mismatch.json")
@pytest.mark.rcm_fitness_mvp
def test_getRCMEval5():
    getRCMEvaluation("Nexus", "55xx", path + "rcmEvaluationDetails-N5k-Mismatch.json")
@pytest.mark.rcm_fitness_mvp
def test_getComplianceData6():
    getComplianceDataMDS("9148", "FIXEDMODULE", path + "rcmComplianceData-MDS9k-Mismatch.json")
@pytest.mark.rcm_fitness_mvp
def test_getAvailableRCM6():
    getAvailableRCMs("Vblock", "340", "6.0", "6.0.1", path + "rcmAvailableRCMs-MDS9k-Mismatch.json")
@pytest.mark.rcm_fitness_mvp
def test_getRCMDefinition6():
    getRCMDefinition("MDS 9148", path + "rcmRCMDefinitionDetails-MDS9k-Mismatch.json")
@pytest.mark.rcm_fitness_mvp
def test_getRCMEval6():
    getRCMEvaluation("MDS", "9148", path + "rcmEvaluationDetails-MDS9k-Mismatch.json")
