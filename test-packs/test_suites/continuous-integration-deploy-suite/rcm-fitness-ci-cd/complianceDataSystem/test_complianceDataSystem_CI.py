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
path = '/home/autouser/PycharmProjects/auto-framework/test_suites/continuousIntegration/complianceDataSystem/'

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
purgeOldOutput(path, "complianceDataSystem")

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

def getComplianceDataSystem(filename):
    subIndex = 0
    compIndex = 0
    groupIndex = 0
    deviceIndex = 0

    getSystemDefinition()

    url = 'http://' + host + ':19080/rcm-fitness-api/api/system/definition/' + systemUUID + '/component/'

    resp = requests.get(url)
    data = json.loads(resp.text)

    assert resp.status_code == 200, "Request has not been acknowledged as expected."
    print("Requesting system details from Compliance Data Service.\n")

    totalComponents = len(data["components"])

    compURL = 'http://' + host + ':19080/rcm-fitness-api/api/compliance/data/system/' + systemUUID

    compResp = requests.get(compURL)
    compData = json.loads(compResp.text)

    assert compResp.status_code == 200, "Request has not been acknowledged as expected."

    with open(filename, 'a') as outfile:
        json.dump(compData, outfile, sort_keys=True, indent=4, ensure_ascii=False)


    if len(compData["devices"]) != "":

        assert not compData["message"], "Expected message field to be NULL."
        assert compData["convergedSystem"]["systemUuid"] == systemUUID
        assert "product" in compData["convergedSystem"], "Response not detail Product."
        assert "model" in compData["convergedSystem"], "Response not detail Model."
        assert "modelFamily" in compData["convergedSystem"], "Response not detail Family."
        assert "identifier" in compData["convergedSystem"], "Response not detail Identifier."
        assert "serialNumber" in compData["convergedSystem"], "Response not detail Serial Number."

        print("Verifying Converged System....")
        totalGroups = len(compData["groups"])
        assert totalGroups > 0, "response not including a list of Groups."
        totalDevices = len(compData["devices"])
        assert totalDevices > 0, "response not including a list of Devices."
        totalSubComponents = len(compData["subComponents"])
        assert totalSubComponents > 0, "response not including a list of Devices."

        while groupIndex < totalGroups:
            assert compData["groups"][groupIndex]["uuid"] != "", "Response detailed an empty group UUID."
            assert "parentGroupUuids" in compData["groups"][groupIndex], "Response not detail parent Group UUID."
            assert compData["groups"][groupIndex]["parentSystemUuids"][0] == systemUUID, "Response not detail parent System UUID."
            assert compData["groups"][groupIndex]["type"] == "STORAGE" or "NETWORK" or "COMPUTE"
            groupIndex += 1
        print("Verifying groups....")

        while deviceIndex < totalDevices:
            assert compData["devices"][deviceIndex]["uuid"] != "", "Response detailed an empty group UUID."
            assert compData["devices"][deviceIndex]["parentGroupUuids"][0] != "", "Response not detail parent Group UUID."
            assert "modelFamily" in compData["devices"][deviceIndex]["elementData"], "Response not detail Model Family."
            assert "model" in compData["devices"][deviceIndex]["elementData"], "Response not detail Model."
            assert "identifier" in compData["devices"][deviceIndex]["elementData"], "Response not detail Identifier."
            assert compData["devices"][deviceIndex]["auditData"]["collectedTime"] != "", "Response not detail Collection Time."
            assert compData["devices"][deviceIndex]["auditData"]["collectionSentTime"] != "", "Response not detail Collection Sent Time."
            assert compData["devices"][deviceIndex]["auditData"]["messageReceivedTime"] != "", "Response not detail Received Time."
            deviceIndex += 1
        print("Verifying devices....")

        while subIndex < totalSubComponents:
            assert compData["subComponents"][subIndex]["uuid"] != "", "Response detailed an empty group UUID."
            assert compData["subComponents"][subIndex]["parentDeviceUuid"] != "", "Response not detail parent Group UUID."
            assert "elementType" in compData["subComponents"][subIndex]["elementData"], "Response not detail Element Type."
            assert "identifier" in compData["subComponents"][subIndex]["elementData"], "Response not detail Identifier."
            assert compData["subComponents"][subIndex]["auditData"]["messageReceivedTime"] != "", "Response not detail Received Time."
            subIndex += 1
        print("Verifying subComponents....")

def getComplianceDataSystemSWITCH(product, family, elementType, subType, identifier, sysDefFilename, compDataFilename):
    subIndex = 0
    compIndex = 0
    groupIndex = 0
    deviceIndex = 0

    getSystemDefinition()

    url = 'http://' + host + ':19080/rcm-fitness-api/api/system/definition/' + systemUUID

    resp = requests.get(url)
    data = json.loads(resp.text)

    assert resp.status_code == 200, "Request has not been acknowledged as expected."
    print("Requesting system details from Compliance Data Service.\n")

    with open(sysDefFilename, 'w') as outfile:
        json.dump(data, outfile, sort_keys=True, indent=4, ensure_ascii=False)

    compURL = 'http://' + host + ':19080/rcm-fitness-api/api/compliance/data/system/' + systemUUID

    compResp = requests.get(compURL)
    compData = json.loads(compResp.text)

    assert compResp.status_code == 200, "Request has not been acknowledged as expected."

    with open(compDataFilename, 'w') as outfile:
        json.dump(compData, outfile, sort_keys=True, indent=4, ensure_ascii=False)

    assert compData["convergedSystem"]["model"] == data["system"]["definition"]["model"], "Unexpected Model returned."
    assert compData["convergedSystem"]["product"] == data["system"]["definition"]["product"], "Unexpected Product returned."
    assert compData["convergedSystem"]["modelFamily"] == data["system"]["definition"]["modelFamily"], "Unexpected UUID returned."

    if len(compData["devices"]) != "":
        totalSubComponents = len(compData["subComponents"])
        totalDevices = len(compData["devices"])
        print(totalDevices)
        while deviceIndex < totalDevices:
            #print("Starting devices: %d" % deviceIndex)
            if compData["devices"][deviceIndex]["elementData"]["modelFamily"] == family:
                assert compData["devices"][deviceIndex]["elementData"]["elementType"] == elementType, "Response not detail Element Type."
                assert family in compData["devices"][deviceIndex]["elementData"]["modelFamily"], "Response not detail Family."
                assert identifier in compData["devices"][deviceIndex]["elementData"]["model"], "Response not detail Model."
                assert compData["devices"][deviceIndex]["elementData"]["product"] == product, "Response not detail Product."
                assert compData["devices"][deviceIndex]["elementData"]["serialNumber"] != "", "Response not detail Serial Number."
                assert compData["devices"][deviceIndex]["uuid"] != "", "Response detailed an empty group UUID."
                assert compData["devices"][deviceIndex]["parentGroupUuids"][0] != "", "Response not detail parent Group UUID."
                assert compData["devices"][deviceIndex]["auditData"]["collectedTime"] != "", "Response not detail Collection Time."
                assert compData["devices"][deviceIndex]["auditData"]["collectionSentTime"] != "", "Response not detail Collection Sent Time."
                assert compData["devices"][deviceIndex]["auditData"]["messageReceivedTime"] != "", "Response not detail Received Time."
                print(compData["devices"][deviceIndex]["elementData"]["modelFamily"])
                print(compData["devices"][deviceIndex]["elementData"]["elementType"])
                print("Done Device Index: %d\n" % deviceIndex)
            deviceIndex += 1
        deviceIndex = 0
        print("Verifying Devices completed....\n")

        print("Total subComponents: %d" % totalSubComponents)
        while subIndex < totalSubComponents:
            #print("Starting subComps: %d" % subIndex)
            if identifier in compData["subComponents"][subIndex]["elementData"]["identifier"]:
                if subType in compData["subComponents"][subIndex]["elementData"]["elementType"]:
                    assert compData["subComponents"][subIndex]["elementData"]["serialNumber"] != "", "Response not detail Serial Number."
                    assert subType in compData["subComponents"][subIndex]["elementData"]["elementType"], "Response returns incorrect Element Type."
                    assert identifier in compData["subComponents"][subIndex]["elementData"]["identifier"], "Response returns incorrect Identifier."
                    print(compData["subComponents"][subIndex]["elementData"]["model"])
                    print(compData["subComponents"][subIndex]["elementData"]["elementType"])
                    print(compData["subComponents"][subIndex]["elementData"]["identifier"])
                    print(compData["subComponents"][subIndex]["elementData"]["serialNumber"])
                    print("Done SubComps Index: %d\n" % subIndex)
            subIndex += 1
        subIndex = 0
        print("Verifying subComponents completed....")

def getComplianceDataSystem_INVALID(sysUUID):
    subIndex = 0
    compIndex = 0
    versionIndex = 0
    getSystemDefinition()

    url = 'http://' + host + ':19080/rcm-fitness-api/api/compliance/data/system/' + sysUUID

    resp = requests.get(url)
    data = json.loads(resp.text)

    #assert resp.status_code == 200, "Request has not been acknowledged as expected."

    if not data["convergedSystem"]:
        if "message" in data.keys():
            if ('RFCA1003E') in data["code"]:
                assert resp.status_code == 500, "Request has not been acknowledged as expected."
                print("Message: %s" % data["message"])
                assert ('RCDS1006E Error retrieving system compliance data') in (data["message"]), "Returned Error Message text not as expected."
                #assert ('RFCA1005I') in (data["code"]), "Returned Error Message does not reflect expected Error Code."
                assert (sysUUID) in (data["message"]), "Returned Error Message does not include expected compUUID."

            if ('RFCA1005I') in (data["code"]):
                assert resp.status_code == 200, "Request has not been acknowledged as expected."
                print("Message: %s" % data["message"])
                assert ('RFCA1005I No compliance data was found') in (data["message"]), "Returned Error Message text not as expected."
                #assert ('RFCA1005I') in (data["code"]), "Returned Error Message does not reflect expected Error Code."
                assert (sysUUID) in (data["message"]), "Returned Error Message does not include expected compUUID."

    print("\nReturned data has completed all defined checks successfully......")

def getComplianceDataSystem_NULL():
    print("Verifying 404 returned if no component UUID provided.")

    url = 'http://' + host + ':19080/rcm-fitness-api/api/compliance/data/system/'
    resp = requests.get(url)
    assert resp.status_code == 404, "Request has not been acknowledged as expected."

    url = 'http://' + host + ':19080/rcm-fitness-api/api/compliance/data/system//'
    resp = requests.get(url)
    assert resp.status_code == 404, "Request has not been acknowledged as expected."

    print("\nReturned response codes are as expected.")

@pytest.mark.rcm_fitness_mvp
def test_getComplianceDataSystem1():
    #af_support_tools.mark_defect(defect_id='DE12419', user_id='toqeer.akhtar@vce.com', comments='hal layer', date_marked='04/04/2017')
    getComplianceDataSystem(path + "complianceDataSystem.json")
@pytest.mark.rcm_fitness_mvp
def test_getComplianceDataSystem2():
    #af_support_tools.mark_defect(defect_id='DE12419', user_id='toqeer.akhtar@vce.com', comments='hal layer', date_marked='04/04/2017')
    getComplianceDataSystemSWITCH("NEXUS", "N3K", "SWITCH", "NETWORKCHASSIS", "3048", path + "rcmSystemDefinition.json", path + "complianceDataSystemNEXUS3K.json")
@pytest.mark.rcm_fitness_mvp
def test_getComplianceDataSystem3():
    #af_support_tools.mark_defect(defect_id='DE12419', user_id='toqeer.akhtar@vce.com', comments='hal layer', date_marked='04/04/2017')
    getComplianceDataSystemSWITCH("NEXUS", "N5K", "SWITCH", "NETWORKCHASSIS", "5548", path + "rcmSystemDefinition.json", path + "complianceDataSystemNEXUS5K.json")
@pytest.mark.rcm_fitness_mvp
def test_getComplianceDataSystem4():
    #af_support_tools.mark_defect(defect_id='DE12419', user_id='toqeer.akhtar@vce.com', comments='hal layer', date_marked='04/04/2017')
    getComplianceDataSystemSWITCH("MDS", "MDS9K", "SWITCH", "NETWORKCHASSIS", "9148", path + "rcmSystemDefinition.json", path + "complianceDataSystemMDS9K.json")
@pytest.mark.rcm_fitness_mvp
def test_getComplianceDataSystem5():
    #af_support_tools.mark_defect(defect_id='DE12419', user_id='toqeer.akhtar@vce.com', comments='hal layer', date_marked='04/04/2017')
    getComplianceDataSystemSWITCH("NEXUS", "N9K", "SWITCH", "NETWORKCHASSIS", "9396", path + "rcmSystemDefinition.json", path + "complianceDataSystemNEXUS9K.json")
@pytest.mark.rcm_fitness_mvp
def test_getComplianceDataSystem6():
    #af_support_tools.mark_defect(defect_id='DE12419', user_id='toqeer.akhtar@vce.com', comments='hal layer', date_marked='04/04/2017')
    getComplianceDataSystem_INVALID(systemUUID[:8])
@pytest.mark.rcm_fitness_mvp
def test_getComplianceDataSystem7():
    getComplianceDataSystem_INVALID("----")
@pytest.mark.rcm_fitness_mvp
def test_getComplianceDataSystem8():
    getComplianceDataSystem_INVALID(" ")
@pytest.mark.rcm_fitness_mvp
def test_getComplianceDataSystem9():
    getComplianceDataSystem_NULL()
