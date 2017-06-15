#!/usr/bin/env python
import json
import traceback
import requests
from collections import Counter
import pytest
import os
import re
import af_support_tools

@pytest.fixture(scope="module", autouse=True)
def load_test_data():
    global path
    path = '/home/autouser/PycharmProjects/auto-framework/test_suites/continuous-integration-deploy-suite/rcm-fitness-ci-cd/restLevelTests/rcmComplianceScan/'
    ensurePathExists(path)
    purgeOldOutput(path, "rcm")

    global ssl_options
    ssl_options = {"ca_certs":"/etc/rabbitmq/certs/testca/cacert.pem","certfile":"/etc/rabbitmq/certs/certs/client/cert.pem","keyfile":"/etc/rabbitmq/certs/certs/client/key.pem","cert_reqs":"ssl.CERT_REQUIRED","ssl_version":"ssl.PROTOCOL_TLSv1_2"}

    # Set config ini file name
    global env_file
    env_file = 'env.ini'

    global host
    host = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='hostname')

    getSystemDefinition()
    
#path = '/home/autouser/PycharmProjects/auto-framework/test_suites/continuousDeployment/restLevelTests/rcmComplianceScan/'

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


fileList = []
fileHash = []

def getSystemDefinition():
    url = 'http://' + host + ':19080/rcm-fitness-api/api/system/definition/'
    resp = requests.get(url)
    data = json.loads(resp.text)

    print("Requesting UUID from System Definition....")
    assert resp.status_code == 200, "Request has not been acknowledged as expected."

    if data != "":
        if data["systems"][0]["uuid"] != "":
            with open(path + 'rcmSystemDefinition-VxRack.json', 'w') as outfile:
                json.dump(data, outfile, sort_keys=True, indent=4, ensure_ascii=False)

            #print("\nExtracting UUID from response....\n")
            global systemUUID
            global secondSystemUUID
            systemUUID = data["systems"][0]["uuid"]
            if len(data["systems"]) > 1:
                secondSystemUUID = data["systems"][1]["uuid"]

        else:
            print("\nNo System UUID returned in REST response")
            print(data["message"])

    print("\nDefined SystemUUID: %s\n" % systemUUID)
    return systemUUID

def getListCompUUIDs(sysUUID):
    subIndex = 0
    compIndex = 0
    versionIndex = 0
    compList = []
    #getSystemDefinition()

    url = 'http://' + host + ':19080/rcm-fitness-api/api/system/definition/' + sysUUID + '/component/'

    resp = requests.get(url)
    data = json.loads(resp.text)

    assert resp.status_code == 200, "Request has not been acknowledged as expected."

    totalComponents = len(data["components"])

    try:
        if data != "" and totalComponents > 0:
            while compIndex < totalComponents:
                global compUUID
                # fb422b4b-d372-49fa-8b11-4e04ee37a2f9
                compUUID = data["components"][compIndex]["uuid"]
                compList.append(compUUID)
                compIndex += 1

        print("\nList of Component UUIDs:")
        for i in compList:
            print(i)
        return compList

    except Exception as e:
        print("Unexpected error: " + str(e))
        #print(response)
        traceback.print_exc()
        raise Exception(e)

def getComplianceData(model, type, filename, sysUUID):
    subIndex = 0
    compIndex = 0
    versionIndex = 0
    url = 'http://' + host + ':19080/rcm-fitness-api/api/system/definition/' + sysUUID + '/component/'

    resp = requests.get(url)
    data = json.loads(resp.text)

    assert resp.status_code == 200, "Request has not been acknowledged as expected."
    print("Requesting latest discovered f/w version from Compliance Data service...")

    totalComponents = len(data["components"])

    assert data["message"] == None, "Error response returned unexpectedly."

    if data != "":
        while compIndex < totalComponents:
            if "modelFamily" in data["components"][compIndex]["definition"] and data["components"][compIndex]["definition"]["modelFamily"] == model:
                print(data["components"][compIndex]["definition"]["modelFamily"])
                global compUUID
                compUUID = data["components"][compIndex]["uuid"]
                print("Component UUID: %s" % compUUID)
                compURL = 'http://' + host + ':19080/rcm-fitness-api/api/compliance/data/device/' + compUUID

                compResp = requests.get(compURL)
                compData = json.loads(compResp.text)

                assert compResp.status_code == 200, "Request has not been acknowledged as expected."
                assert compData["message"] is None, "Error response returned unexpectdely."

                with open(filename, 'a') as outfile:
                    json.dump(compData, outfile, sort_keys=True, indent=4, ensure_ascii=False)

                while subIndex < len(compData["subComponents"]):
                    if "model" in compData["subComponents"][subIndex]["elementData"]:
                        if model in (compData["subComponents"][subIndex]["elementData"]["model"]) and (compData["subComponents"][subIndex]["elementData"]["elementType"] == "RAID"):
                            while versionIndex < len(compData["subComponents"][subIndex]["versionDatas"]):
                                if (compData["subComponents"][subIndex]["versionDatas"][versionIndex]["type"]) == "FIRMWARE":
                                    global raidFWversionComponent
                                    raidFWversionComponent = (compData["subComponents"][subIndex]["versionDatas"][versionIndex]["version"])
                                    print("\nRAID Component requested: %s" % compData["subComponents"][subIndex]["uuid"])
                                    print("Discovered firmware version: %s" % raidFWversionComponent)
                                versionIndex += 1
                            versionIndex = 0
                        if model in (compData["subComponents"][subIndex]["elementData"]["model"]) and (compData["subComponents"][subIndex]["elementData"]["elementType"] == "BIOS"):
                            while versionIndex < len(compData["subComponents"][subIndex]["versionDatas"]):
                                if (compData["subComponents"][subIndex]["versionDatas"][versionIndex]["type"]) == "FIRMWARE":
                                    global biosFWversionComponent
                                    biosFWversionComponent = (compData["subComponents"][subIndex]["versionDatas"][versionIndex]["version"])
                                    print("\nBIOS Component requested: %s" % compData["subComponents"][subIndex]["uuid"])
                                    print("Discovered firmware version: %s" % biosFWversionComponent)
                                versionIndex += 1
                            versionIndex = 0
                        if model in (compData["subComponents"][subIndex]["elementData"]["model"]) and (compData["subComponents"][subIndex]["elementData"]["elementType"] == "NIC"):
                            while versionIndex < len(compData["subComponents"][subIndex]["versionDatas"]):
                                if (compData["subComponents"][subIndex]["versionDatas"][versionIndex]["type"]) == "FIRMWARE":
                                    global nicFWversionComponent
                                    nicFWversionComponent = (compData["subComponents"][subIndex]["versionDatas"][versionIndex]["version"])
                                    print("\nNIC Component requested: %s" % compData["subComponents"][subIndex]["uuid"])
                                    print("Discovered firmware version: %s" % nicFWversionComponent)
                                versionIndex += 1
                            versionIndex = 0
                    subIndex += 1
                subIndex = 0
            compIndex += 1
        compIndex = 0

def getComplianceDataSystem(model, filename, sysUUID):
    subIndex = 0
    compIndex = 0
    versionIndex = 0
    url = 'http://' + host + ':19080/rcm-fitness-api/api/system/definition/' + sysUUID + '/component/'

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

                    systemURL = 'http://' + host + ':19080/rcm-fitness-api/api/compliance/data/system/' + sysUUID

                    systemResp = requests.get(systemURL)
                    systemData = json.loads(systemResp.text)

                    assert systemResp.status_code == 200, "Request has not been acknowledged as expected."
                    with open(filename, 'a') as outfile:
                        json.dump(systemData, outfile, sort_keys=True, indent=4, ensure_ascii=False)

                    while subIndex < len(systemData["subComponents"]):
                        if "model" in systemData["subComponents"][subIndex]["elementData"] and systemData["subComponents"][subIndex]["elementData"]["elementType"] == "RAID" or "BIOS" or "NIC":
                            if model in (systemData["subComponents"][subIndex]["elementData"]["model"]):
                                while versionIndex < len(systemData["subComponents"][subIndex]["versionDatas"]):
                                    if (systemData["subComponents"][subIndex]["versionDatas"][versionIndex]["type"]) == "FIRMWARE":
                                        global fwVersionSystem
                                        fwVersionSystem = (systemData["subComponents"][subIndex]["versionDatas"][versionIndex]["version"])
                                        #assert nexusFWversionSystem == nexusFWversionComponent
                                        print("\n\nComponent requested: %s" % compUUID)
                                        print("Element Type: %s" % systemData["subComponents"][subIndex]["elementData"]["elementType"])
                                        print("\nDiscovered firmware version: %s\n\n" % fwVersionSystem)
                                    versionIndex += 1
                                versionIndex = 0
                        subIndex += 1
                    subIndex = 0
            compIndex += 1
        compIndex = 0




def getAvailableRCMs(family, model, train, version, option, filename):
    numRCMs = 0
    rcmIndex = 0

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
        if data["rcmInventoryItems"][numRCMs]["viewOption"] == option:
            global rcmUUID
            rcmUUID = (data["rcmInventoryItems"][numRCMs]["uuid"])
            print("Requested rcmUUID: %s" % rcmUUID)
            print("Requested version: %s" % data["rcmInventoryItems"][0]["rcmVersion"])
        numRCMs += 1
    numRCMs = 0
#    getRCMDefinition("Dell BIOS Firmware", path + "rcmRCMDefinitionDetails-VxRack.json")
def getRCMDefinition(component, filename, option):
    contentIndex = 0

    url = 'http://' + host + ':19080/rcm-fitness-api/api/rcm/definition/' + rcmUUID
    print(url)
    resp = requests.get(url)
    data = json.loads(resp.text)
    assert resp.status_code == 200, "Request has not been acknowledged as expected."

    global versionRCM
    versionRCM = data["rcmDefinition"]["rcmVersion"]
    global optionRCM
    optionRCM = data["rcmDefinition"]["viewOption"]
    print("\nStarting to verify a sample of the returned data....")
    if data != "":
        if data["message"] == None:
            with open(filename, 'a') as outfile:
                json.dump(data, outfile, sort_keys=True, indent=4, ensure_ascii=False)
            if data["rcmDefinition"]["viewOption"] == option:
                while contentIndex < len(data["rcmDefinition"]["rcmContents"]):
                    if (data["rcmDefinition"]["rcmContents"][contentIndex]["component"]) == component:
                        assert "version" in data["rcmDefinition"]["rcmContents"][contentIndex], "No version attribute returned for specified component."
                        firmwareVersion = (data["rcmDefinition"]["rcmContents"][contentIndex]["version"])
                        if "versionFileName" in data["rcmDefinition"]["rcmContents"][contentIndex]:
                            assert "versionFileHash" in data["rcmDefinition"]["rcmContents"][contentIndex]
                            assert data["rcmDefinition"]["rcmContents"][contentIndex]["versionFileName"] != "", "No filename specified in definition."
                            assert data["rcmDefinition"]["rcmContents"][contentIndex]["versionFileHash"] != "", "No filename specified in definition."
                            versFileName = data["rcmDefinition"]["rcmContents"][contentIndex]["versionFileName"]
                            versFileHash = data["rcmDefinition"]["rcmContents"][contentIndex]["versionFileHash"]
                            fileList.append(versFileName)
                            fileHash.append(versFileHash)
                        print("List of filenames:", fileList)
                        print("List of filehashes:", fileHash)

                        print("\nComponent: %s" % data["rcmDefinition"]["rcmContents"][contentIndex]["component"])
                        print("Expected version: %s" % firmwareVersion)
                    contentIndex += 1


def getRCMEvaluation(component, identifier, productFamily, modelFamily, vendor, product, model, filename, sysUUID):

    url = 'http://' + host + ':19080/rcm-fitness-api/api/rcm/evaluation/'
    payload = {'systemUuid': sysUUID, 'rcmUuid': rcmUUID}
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    resp = requests.post(url, data=json.dumps(payload), headers=headers)
    data = json.dumps(payload)

    print("Returned status code: %d" % resp.status_code)
    print("SystemUUID:" + sysUUID)
    print("rcmUUID:" + rcmUUID)
    print("\nRCM Version: %s" % versionRCM)
    response = json.loads(resp.text)
    assert resp.status_code == 200, "Request has not been acknowledged as expected."

    numResults = 0
    count = 0

    with open(filename, 'a') as outfile:
        json.dump(response, outfile, sort_keys=True, indent=4, ensure_ascii=False)

    while numResults < len(response["rcmEvaluationResults"]):
        if response["rcmEvaluationResults"][numResults]["evaluatedRcmDatum"]["product"] == product and response["rcmEvaluationResults"][numResults]["evaluatedRcmDatum"]["component"] == component:
            #identifier in response["rcmEvaluationResults"][numResults]["evaluatedVersionDatum"]["identity"]["identifier"]:
            if response["rcmEvaluationResults"][numResults]["evaluatedVersionDatum"]["definition"]["model"] == model:
                versionFound = (response["rcmEvaluationResults"][numResults]["actualValue"])
                versionExpected = (response["rcmEvaluationResults"][numResults]["expectedValues"][0])
                print("Product Family: %s" % response["rcmEvaluationResults"][numResults]["evaluatedRcmDatum"]["systemProductFamily"])
                print("Model Family: %s" % response["rcmEvaluationResults"][numResults]["evaluatedRcmDatum"]["systemModelFamily"])
                print("Vendor: %s" % response["rcmEvaluationResults"][numResults]["evaluatedRcmDatum"]["vendor"])
                print("Component: %s" % response["rcmEvaluationResults"][numResults]["evaluatedRcmDatum"]["component"])
                print("Identifier: %s" % response["rcmEvaluationResults"][numResults]["evaluatedVersionDatum"]["identity"]["identifier"])
                print("Returned result: %s" % response["rcmEvaluationResults"][numResults]["evaluationResult"])
                assert productFamily in response["rcmEvaluationResults"][numResults]["evaluatedRcmDatum"]["systemProductFamily"]
                assert modelFamily in response["rcmEvaluationResults"][numResults]["evaluatedRcmDatum"]["systemModelFamily"]
                assert vendor in response["rcmEvaluationResults"][numResults]["evaluatedRcmDatum"]["vendor"]

                if versionFound == versionExpected:
                    assert (response["rcmEvaluationResults"][numResults]["evaluationResult"]) == "match", "Expected a match to be returned, not the case."
                    assert response["rcmEvaluationResults"][numResults]["expectedValues"][0] == response["rcmEvaluationResults"][numResults]["actualValue"]

                else:
                    assert (response["rcmEvaluationResults"][numResults]["evaluationResult"]) == "mismatch", "Expected a mismatch to be returned, not the case."
                    assert response["rcmEvaluationResults"][numResults]["expectedValues"][0] not in response["rcmEvaluationResults"][numResults]["actualValue"]
                print("Version found: %s" % versionFound)
                print("Version expected: %s" % versionExpected)
                assert response["rcmEvaluationResults"][numResults]["evaluatedRcmDatum"]["component"] == component, "Unexpected component value returned."
                if "versionFileName" in response["rcmEvaluationResults"][numResults]["evaluatedRcmDatum"]:
                    assert "versionFileHash" in response["rcmEvaluationResults"][numResults]["evaluatedRcmDatum"]
                    assert response["rcmEvaluationResults"][numResults]["evaluatedRcmDatum"]["versionFileName"] in fileList, "No filename specified in definition."
                    assert response["rcmEvaluationResults"][numResults]["evaluatedRcmDatum"]["versionFileHash"] in fileHash, "No filename specified in definition."
                    print(response["rcmEvaluationResults"][numResults]["evaluatedRcmDatum"]["versionFileName"])
                    print(response["rcmEvaluationResults"][numResults]["evaluatedRcmDatum"]["versionFileHash"])
                else:
                    print("Expected filename not returned.")
                    #continue
              #  numResults += 1
            else:
                print("Incorrect model family returned.")
                #continue
           # numResults += 1
        else:
            print("Either product or identifier returned are not as expected.")
            #continue
        numResults += 1
        
 

@pytest.mark.rcm_fitness_mvp_extended
def test_getSysDef1():
    getSystemDefinition()
@pytest.mark.rcm_fitness_mvp_extended
def test_getListCompUUIDs2():
    getListCompUUIDs(systemUUID)
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceData3():
    getComplianceData("730", "RAID", path + "rcmComplianceData-VxRack.json", systemUUID)
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataSystem4():
    getComplianceDataSystem("730", path + "rcmComplianceDataSystem-VxRack.json",systemUUID)
@pytest.mark.rcm_fitness_mvp_extended
def test_getAvailableRCM5():
    getAvailableRCMs("VxRack", "FLEX", "9.2", "9.2.33", "ORIGINAL", path + "rcmAvailableRCMs-VxRack.json")
@pytest.mark.rcm_fitness_mvp_extended
def test_getRCMDefinition6():
    getRCMDefinition("Dell BIOS Firmware", path + "rcmRCMDefinitionDetails-VxRack.json", "ORIGINAL")
@pytest.mark.rcm_fitness_mvp_extended
def test_getRCMEval7():
    getRCMEvaluation("Dell BIOS Firmware", "BIOS", "VxRack", "FLEX", "DELL", "POWEREDGE", "R730XD", path + "rcmEvaluationDetails-VxRack.json", systemUUID)
@pytest.mark.rcm_fitness_mvp_extended
def test_getRCMDefinition8():
    getRCMDefinition("Dell iDRAC / Lifecycle Controller Firmware", path + "rcmRCMDefinitionDetails-VxRack2.json", "ORIGINAL")
@pytest.mark.rcm_fitness_mvp_extended
def test_getRCMEval9():
    getRCMEvaluation("Dell iDRAC / Lifecycle Controller Firmware", "Integrated Remote Access Controller", "VxRack", "FLEX", "DELL", "POWEREDGE", "R730XD", path + "rcmEvaluationDetails-VxRack.json", systemUUID)
@pytest.mark.rcm_fitness_mvp_extended
def test_getRCMDefinition10():
    getRCMDefinition("Dell Ethernet X520 NDCi350/X520/X540 Firmware", path + "rcmRCMDefinitionDetails-VxRack2.json", "ORIGINAL")
@pytest.mark.rcm_fitness_mvp_extended
def test_getRCMEval11():
    getRCMEvaluation("Dell Ethernet X520 NDCi350/X520/X540 Firmware", "2P X520 Adapter", "VxRack", "FLEX", "DELL", "POWEREDGE", "R730XD", path + "rcmEvaluationDetails-VxRack.json", systemUUID)
@pytest.mark.rcm_fitness_mvp_extended
def test_getRCMDefinition12():
    getRCMDefinition("Dell PERC H730P Firmware", path + "rcmRCMDefinitionDetails-VxRack2.json", "ORIGINAL")
@pytest.mark.rcm_fitness_mvp_extended
def test_getRCMEval13():
    getRCMEvaluation("Dell PERC H730P Firmware", "PERC H730P Mini", "VxRack", "FLEX", "DELL", "POWEREDGE", "R730XD", path + "rcmEvaluationDetails-VxRack.json", systemUUID)
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceData14():
    getComplianceData("730", "SERVER", path + "rcmComplianceData-N3k-Mismatch.json", systemUUID)
@pytest.mark.rcm_fitness_mvp_extended
def test_getAvailableRCM15():
    getAvailableRCMs("VxRack", "FLEX", "9.2", "9.2.33.1", "ADDENDUM", path + "rcmAvailableRCMs-VxRack-Mismatch.json")
@pytest.mark.rcm_fitness_mvp_extended
def test_getRCMDefinition16():
    getRCMDefinition("Dell BIOS Firmware", path + "rcmRCMDefinitionDetails-VxRack.json", "ADDENDUM")
@pytest.mark.rcm_fitness_mvp_extended
def test_getRCMEval17():
    getRCMEvaluation("Dell BIOS Firmware", "BIOS", "VxRack", "FLEX", "DELL", "POWEREDGE", "R730XD", path + "rcmEvaluationDetails-VxRack.json", systemUUID)
@pytest.mark.rcm_fitness_mvp_extended
def test_getRCMDefinition18():
    getRCMDefinition("Dell iDRAC / Lifecycle Controller Firmware", path + "rcmRCMDefinitionDetails-VxRack2.json", "ADDENDUM")
@pytest.mark.rcm_fitness_mvp_extended
def test_getRCMEval19():
    getRCMEvaluation("Dell iDRAC / Lifecycle Controller Firmware", "Integrated Remote Access Controller", "VxRack", "FLEX", "DELL", "POWEREDGE", "R730XD", path + "rcmEvaluationDetails-VxRack.json", systemUUID)
@pytest.mark.rcm_fitness_mvp_extended
def test_getRCMDefinition20():
    getRCMDefinition("Dell Ethernet X520 NDCi350/X520/X540 Firmware", path + "rcmRCMDefinitionDetails-VxRack2.json", "ADDENDUM")
@pytest.mark.rcm_fitness_mvp_extended
def test_getRCMEval21():
    getRCMEvaluation("Dell Ethernet X520 NDCi350/X520/X540 Firmware", "4P X520/I350 rNDC", "VxRack", "FLEX", "DELL", "POWEREDGE", "R730XD", path + "rcmEvaluationDetails-VxRack.json", systemUUID)
@pytest.mark.rcm_fitness_mvp_extended
def test_getRCMDefinition22():
    getRCMDefinition("Dell PERC H730P Firmware", path + "rcmRCMDefinitionDetails-VxRack2.json", "ADDENDUM")
@pytest.mark.rcm_fitness_mvp_extended
def test_getRCMEval23():
    getRCMEvaluation("Dell PERC H730P Firmware", "PERC H730P Mini", "VxRack", "FLEX", "DELL", "POWEREDGE", "R730XD", path + "rcmEvaluationDetails-VxRack.json", systemUUID)
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceData24():
    getComplianceData("630", "RAID", path + "rcmComplianceData-VxRack.json", systemUUID)
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataSystem25():
    getComplianceDataSystem("630", path + "rcmComplianceDataSystem-VxRack.json",systemUUID)
@pytest.mark.rcm_fitness_mvp_extended
def test_getAvailableRCM26():
    getAvailableRCMs("VxRack", "FLEX", "9.2", "9.2.33", "ORIGINAL", path + "rcmAvailableRCMs-VxRack.json")
@pytest.mark.rcm_fitness_mvp_extended
def test_getRCMDefinition27():
    getRCMDefinition("Dell BIOS Firmware", path + "rcmRCMDefinitionDetails-VxRack.json", "ORIGINAL")
@pytest.mark.rcm_fitness_mvp_extended
def test_getRCMEval28():
    getRCMEvaluation("Dell BIOS Firmware", "BIOS", "VxRack", "FLEX", "DELL", "POWEREDGE", "R630", path + "rcmEvaluationDetails-VxRack.json", systemUUID)
@pytest.mark.rcm_fitness_mvp_extended
def test_getRCMDefinition29():
    getRCMDefinition("Dell iDRAC / Lifecycle Controller Firmware", path + "rcmRCMDefinitionDetails-VxRack2.json", "ORIGINAL")
@pytest.mark.rcm_fitness_mvp_extended
def test_getRCMEval30():
    getRCMEvaluation("Dell iDRAC / Lifecycle Controller Firmware", "Integrated Remote Access Controller", "VxRack", "FLEX", "DELL", "POWEREDGE", "R630", path + "rcmEvaluationDetails-VxRack.json", systemUUID)
@pytest.mark.rcm_fitness_mvp_extended
def test_getRCMDefinition31():
    getRCMDefinition("Dell Ethernet X520 NDCi350/X520/X540 Firmware", path + "rcmRCMDefinitionDetails-VxRack2.json", "ORIGINAL")
@pytest.mark.rcm_fitness_mvp_extended
def test_getRCMEval132():
    getRCMEvaluation("Dell Ethernet X520 NDCi350/X520/X540 Firmware", "2P X520 Adapter", "VxRack", "FLEX", "DELL", "POWEREDGE", "R630", path + "rcmEvaluationDetails-VxRack.json", systemUUID)
@pytest.mark.rcm_fitness_mvp_extended
def test_getRCMDefinition33():
    getRCMDefinition("Dell PERC H730P Firmware", path + "rcmRCMDefinitionDetails-VxRack2.json", "ORIGINAL")
@pytest.mark.rcm_fitness_mvp_extended
def test_getRCMEval34():
    getRCMEvaluation("Dell PERC H730P Firmware", "PERC H730P Mini", "VxRack", "FLEX", "DELL", "POWEREDGE", "R630", path + "rcmEvaluationDetails-VxRack.json", systemUUID)
