#!/usr/bin/env python
import json
import requests
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
path = '/home/autouser/PycharmProjects/auto-framework/test_suites/continuousIntegration/complianceDataDevice/'

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
purgeOldOutput(path, "complianceDataDevice")

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

            #print("\nExtracting UUID from response....\n")
            global systemUUID
            systemUUID = data["systems"][0]["uuid"]
        else:
            print("\nNo System UUID returned in REST response")
            print(data["message"])

    print("\nDefined SystemUUID: %s\n" % systemUUID)
    return systemUUID

def getComplianceDataNEXUS(product, model, subModel, subcomponents, deviceType, type, filename):
    subIndex = 0
    compIndex = 0
    versionIndex = 0
    getSystemDefinition()

    url = 'http://' + host + ':19080/rcm-fitness-api/api/system/definition/' + systemUUID + '/component/'

    resp = requests.get(url)
    data = json.loads(resp.text)

    assert resp.status_code == 200, "Request has not been acknowledged as expected."
    print(model + ": Requesting latest discovered f/w version from Compliance Data service...\n")

    totalComponents = len(data["components"])

    try:
        if data != "" and totalComponents > 0:
            while compIndex < totalComponents:

                if "modelFamily" in data["components"][compIndex]["definition"] and data["components"][compIndex]["definition"]["modelFamily"] == model:

                    global compUUID
                    compUUID = data["components"][compIndex]["uuid"]
                    print("Component UUID: %s" % compUUID)

                    compURL = 'http://' + host + ':19080/rcm-fitness-api/api/compliance/data/device/' + compUUID

                    compResp = requests.get(compURL)
                    compData = json.loads(compResp.text)

                    assert compResp.status_code == 200, "Request has not been acknowledged as expected."

                    with open(filename, 'a') as outfile:
                        json.dump(compData, outfile, sort_keys=True, indent=4, ensure_ascii=False)

                    if len(compData["device"]["uuid"]) != "":
                        assert "parentGroupUuids" in compData["device"], "Response not detail Parent Group UUID."
                        assert "elementData" in compData["device"], "Response not detail Element Data."
                        assert "auditData" in compData["device"], "Response not detail Audit Data."
                        assert "versionDatas" in compData["device"], "Response not detail Version Datas."
                        assert "product" in compData["device"]["elementData"], "Response not detail Product."
                        assert "modelFamily" in compData["device"]["elementData"], "Response not detail Family."
                        assert "model" in compData["device"]["elementData"], "Response not detail Model."
                        assert "elementType" in compData["device"]["elementData"], "Response not detail Element Type."
                        assert "ipAddress" in compData["device"]["elementData"], "Response not detail IP Address."
                        assert "serialNumber" in compData["device"]["elementData"], "Response not detail Serial No."

                        assert "collectedTime" in compData["device"]["auditData"], "Response not detail Collected Time."
                        assert "collectionSentTime" in compData["device"]["auditData"], "Response not detail Collection Sent Time."
                        assert "messageReceivedTime" in compData["device"]["auditData"], "Response not detail Received Time."

                        assert "uuid" in compData["groups"][0], "Response not detail component Groups."

                        assert compData["device"]["elementData"]["product"] == product
                        assert model in compData["device"]["elementData"]["modelFamily"]
                        assert compData["device"]["elementData"]["elementType"] == deviceType

                    print("Key and Value assertions concluded.")

                    assert len(compData["subComponents"]) == subcomponents, "Incomplete list of sumComponents."

                    while subIndex < len(compData["subComponents"]):
                        assert "elementType" in compData["subComponents"][subIndex]["elementData"], "Response not detail Element Type for each SubComponent."
                        assert compData["systems"][0]["systemUuid"] == systemUUID, "Response not detail the expected System UUID."
                        if "model" in compData["subComponents"][subIndex]["elementData"]:
                            if model in (compData["subComponents"][subIndex]["elementData"]["model"]) and (compData["subComponents"][subIndex]["elementData"]["elementType"] == type):
                                while versionIndex < len(compData["subComponents"][subIndex]["versionDatas"]):
                                    if (compData["subComponents"][subIndex]["versionDatas"][versionIndex]["type"]) == "FIRMWARE":
                                        global nexusFWversionComponent
                                        nexusFWversionComponent = (compData["subComponents"][subIndex]["versionDatas"][versionIndex]["version"])
                                        print("Discovered firmware version: %s" % nexusFWversionComponent)
                                    versionIndex += 1
                                versionIndex = 0
                        subIndex += 1
                    print("SubComponent Key and Value assertions concluded.\n")
                    subIndex = 0
                compIndex += 1
            compIndex = 0
        else:
            raise Exception("Empty response or an empty list of Components returned.")

    except Exception as e:
        print("Unexpected error: " + str(e))
        #print(response)
        traceback.print_exc()
        raise Exception(e)

def getComplianceDataMDS(product, model, subModel, subcomponents, deviceType, type, filename):
    subIndex = 0
    compIndex = 0
    versionIndex = 0
    getSystemDefinition()

    url = 'http://' + host + ':19080/rcm-fitness-api/api/system/definition/' + systemUUID + '/component/'

    resp = requests.get(url)
    data = json.loads(resp.text)

    assert resp.status_code == 200, "Request has not been acknowledged as expected."
    print(product + " " + subModel + ": Requesting latest discovered f/w version from Compliance Data service...\n")

    totalComponents = len(data["components"])

    if data != "":
        while compIndex < totalComponents:
            if "modelFamily" in data["components"][compIndex]["definition"] and model in data["components"][compIndex]["definition"]["modelFamily"]:
                global compUUID
                compUUID = data["components"][compIndex]["uuid"]
                print("Component UUID: %s" % compUUID)

                compURL = 'http://' + host + ':19080/rcm-fitness-api/api/compliance/data/device/' + compUUID

                compResp = requests.get(compURL)
                compData = json.loads(compResp.text)

                assert compResp.status_code == 200, "Request has not been acknowledged as expected."

                with open(filename, 'a') as outfile:
                    json.dump(compData, outfile, sort_keys=True, indent=4, ensure_ascii=False)

                if len(compData["device"]["uuid"]) != 0:
                    assert "parentGroupUuids" in compData["device"], "Response not detail Parent Group UUID."
                    assert "elementData" in compData["device"], "Response not detail Element Data."
                    assert "auditData" in compData["device"], "Response not detail Audit Data."
                    assert "versionDatas" in compData["device"], "Response not detail Version Datas."
                    assert "product" in compData["device"]["elementData"], "Response not detail Product."
                    assert "modelFamily" in compData["device"]["elementData"], "Response not detail Family."
                    assert "model" in compData["device"]["elementData"], "Response not detail Model."
                    assert "elementType" in compData["device"]["elementData"], "Response not detail Element Type."
                    assert "ipAddress" in compData["device"]["elementData"], "Response not detail IP Address."
                    assert "serialNumber" in compData["device"]["elementData"], "Response not detail Serial No."

                    assert "collectedTime" in compData["device"]["auditData"], "Response not detail Collected Time."
                    assert "collectionSentTime" in compData["device"]["auditData"], "Response not detail Collection Sent Time."
                    assert "messageReceivedTime" in compData["device"]["auditData"], "Response not detail Received Time."

                    assert "uuid" in compData["groups"][0], "Response not detail component Groups."

                    assert compData["device"]["elementData"]["product"] == product
                    assert model in compData["device"]["elementData"]["modelFamily"]
                    assert subModel in compData["device"]["elementData"]["model"]
                    assert compData["device"]["elementData"]["elementType"] == deviceType

                print("Key and Value assertions concluded.")

                assert len(compData["subComponents"]) == subcomponents, "Incomplete list of sumComponents."

                while subIndex < len(compData["subComponents"]):

                    assert "elementType" in compData["subComponents"][subIndex]["elementData"], "Response not detail Element Type for each SubComponent."
                    assert compData["systems"][0]["systemUuid"] == systemUUID, "Response not detail the expected System UUID."

                    if "model" in compData["subComponents"][subIndex]["elementData"]:
                        if subModel in (compData["subComponents"][subIndex]["elementData"]["model"]) and (compData["subComponents"][subIndex]["elementData"]["elementType"] == type):
                            while versionIndex < len(compData["subComponents"][subIndex]["versionDatas"]):
                                if (compData["subComponents"][subIndex]["versionDatas"][versionIndex]["type"]) == "FIRMWARE":
                                    global mdsFWversionComponent
                                    mdsFWversionComponent = (compData["subComponents"][subIndex]["versionDatas"][versionIndex]["version"])
                                    print("Discovered firmware version: %s" % mdsFWversionComponent)
                                versionIndex += 1
                            versionIndex = 0
                    subIndex += 1
                print("SubComponent Key and Value assertions concluded.\n")
                subIndex = 0
            compIndex += 1
        compIndex = 0

def getComplianceData_INVALID(compUUID):
    subIndex = 0
    compIndex = 0
    versionIndex = 0
    getSystemDefinition()

    url = 'http://' + host + ':19080/rcm-fitness-api/api/compliance/data/device/' + compUUID

    resp = requests.get(url)
    print(resp)
    data = json.loads(resp.text)

    print(data)

    if not data["device"]:
        if "message" in data.keys():
            if ('RFCA1025E') in data["code"]:
                assert resp.status_code == 500, "Request has not been acknowledged as expected."
                print(data["message"])
                print("Message A")
                assert ('RCDS1004E Error retrieving device compliance data') in (data["message"]), "Returned Error Message does not reflect expected Error Code."
                assert (compUUID) in (data["message"]), "Returned Error Message does not include expected compUUID."

            if ('RFCA1024I') in data["code"]:
                print(data["message"])
                print("Message B")
                assert resp.status_code == 200, "Request has not been acknowledged as expected."
                assert ('RFCA1024I No compliance data was found') in (data["message"]), "Returned Error Message does not reflect expected Error Code."
                assert (compUUID) in (data["message"]), "Returned Error Message does not include expected compUUID."

#    if "message" in data.keys():
#        print (data["message"])
#        assert ('RFCA1025E') in (data["message"]), "Returned Error Message does not reflect expected Error Code."

    print("\nReturned data has completed all defined checks successfully......")

def getComplianceData_SPACES(compUUID):
    subIndex = 0
    compIndex = 0
    versionIndex = 0
    getSystemDefinition()

    url = 'http://' + host + ':19080/rcm-fitness-api/api/compliance/data/device/' + compUUID + '/'

    resp = requests.get(url)
    print(resp.text)
    #data = json.loads(resp.text)

    #print(data)
    assert resp.status_code == 500, "Request has not been acknowledged as expected."

    assert ('RFCA1025E') in (resp.text), "Returned Error Message does not reflect expected Error Code."
    assert ('[' + compUUID + ']') in (resp.text), "Returned Error Message does not include expected compUUID."
    assert ('RCDS1004E Error retrieving device compliance data') in (resp.text), "Returned Error Message does not include expected text."

    print("\nReturned data has completed all defined checks successfully......")



def getComplianceData_NULL():
    print("Verifying 404 returned if no component UUID provided.")

    url = 'http://' + host + ':19080/rcm-fitness-api/api/compliance/data/device/'
    resp = requests.get(url)
    assert resp.status_code == 404, "Request has not been acknowledged as expected."

    url = 'http://' + host + ':19080/rcm-fitness-api/api/compliance/data/device//'
    resp = requests.get(url)
    assert resp.status_code == 404, "Request has not been acknowledged as expected."

    print("\nReturned response codes are as expected.")


@pytest.mark.rcm_fitness_mvp
def test_getComplianceDataDevice1():
    af_support_tools.mark_defect(defect_id='DE12419', user_id='toqeer.akhtar@vce.com', comments='hal layer')
    getComplianceDataNEXUS("NEXUS", "N5K", "C5548", 7, "SWITCH", "FIXEDMODULE", path + "complianceDataDeviceNEXUS5k.json")
@pytest.mark.rcm_fitness_mvp
def test_getComplianceDataDevice2():
    af_support_tools.mark_defect(defect_id='DE12419', user_id='toqeer.akhtar@vce.com', comments='hal layer')
    getComplianceDataNEXUS("NEXUS", "N3K", "C3048", 3, "SWITCH", "FIXEDMODULE", path + "complianceDataDeviceNEXUS3k.json")
@pytest.mark.rcm_fitness_mvp
def test_getComplianceDataDevice3():
    getComplianceDataMDS("MDS", "MDS9K", "C9148", 3, "SWITCH", "FIXEDMODULE", path + "complianceDataDeviceMDS.json")
@pytest.mark.rcm_fitness_mvp
def test_getComplianceDataDevice4():
    af_support_tools.mark_defect(defect_id='DE12419', user_id='toqeer.akhtar@vce.com', comments='hal layer')
    getComplianceDataNEXUS("NEXUS", "N9K", "C9396", 5, "SWITCH", "FIXEDMODULE", path + "complianceDataDeviceNEXUS9k.json")
@pytest.mark.rcm_fitness_mvp
def test_getComplianceDataDevice5():
    af_support_tools.mark_defect(defect_id='DE12419', user_id='toqeer.akhtar@vce.com', comments='hal layer')
    getComplianceData_INVALID(compUUID[:8])
@pytest.mark.rcm_fitness_mvp
def test_getComplianceDataDevice6():
    getComplianceData_INVALID("----")
@pytest.mark.rcm_fitness_mvp
def test_getComplianceDataDevice7():
    getComplianceData_INVALID("0-0-0-0")
@pytest.mark.rcm_fitness_mvp
def test_getComplianceDataDevice8():
    getComplianceData_INVALID("<>")
@pytest.mark.rcm_fitness_mvp
def test_getComplianceDataDevice9():
    getComplianceData_INVALID("  ")
@pytest.mark.rcm_fitness_mvp
def test_getComplianceDataDevice10():
    getComplianceData_NULL()
