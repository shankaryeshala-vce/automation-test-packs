#!/usr/bin/env python
import json
import requests
import pytest
import os
import re
import af_support_tools

@pytest.fixture(scope="module", autouse=True)
def load_test_data():
    global path
    path = '/home/autouser/PycharmProjects/auto-framework/test_suites/continuous-integration-deploy-suite/rcm-fitness-ci-cd/restLevelTests/complianceDataDevice/'
    global ssl_options
    ssl_options = {"ca_certs":"/etc/rabbitmq/certs/testca/cacert.pem","certfile":"/etc/rabbitmq/certs/certs/client/cert.pem","keyfile":"/etc/rabbitmq/certs/certs/client/key.pem","cert_reqs":"ssl.CERT_REQUIRED","ssl_version":"ssl.PROTOCOL_TLSv1_2"}

    # Set config ini file name
    global env_file
    env_file = 'env.ini'

    global host
    host = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='hostname')

    ensurePathExists(path)
    purgeOldOutput(path, "complianceDataDevice")

    getSystemDefinition()
    
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
            print("\nDefined SystemUUID: %s\n" % systemUUID)
            if len(data["systems"]) > 1:
                secondSystemUUID = data["systems"][1]["uuid"]
                print("\nDefined SystemUUID: %s\n" % secondSystemUUID)
        else:
            print("\nNo System UUID returned in REST response")
            print(data["message"])


    return systemUUID



#("VxRack", "1000 FLEX", "R730XD", "POWEREDGE", "SERVER", path + "complianceDataDevicePOWEREDGE.json")

def getComplianceData(product, family, model, deviceProduct, deviceType, filename, sysUUID, minSubCount, maxSubCount):
    subIndex = 0
    compIndex = 0
    versionIndex = 0
    totalComponents = 0
    totalSubComponents = 0
    i = 0

    url = 'http://' + host + ':19080/rcm-fitness-api/api/system/definition/' + sysUUID + '/component/'

    resp = requests.get(url)
    data = json.loads(resp.text)

    assert resp.status_code == 200, "Request has not been acknowledged as expected."

    url = 'http://' + host + ':19080/rcm-fitness-api/api/system/definition/' + sysUUID

    resp = requests.get(url)
    sysData = json.loads(resp.text)

    assert resp.status_code == 200, "Request has not been acknowledged as expected."
    print(model + ": Requesting latest discovered f/w version from Compliance Data service...\n")

    #data = sysData["system"]
    totalComponents = len(data["components"])
    print("Total Comps: %d" % totalComponents)
    try:
        if data != "":
            while compIndex < totalComponents:
                print("You are here now...")
                if "modelFamily" in data["components"][compIndex]["definition"] and data["components"][compIndex]["definition"]["model"] == model:
                    print("You are right here now......")
                    i = 0
                    global compUUID
                    compUUID = data["components"][compIndex]["uuid"]
                    print("Component UUID: %s" % compUUID)
                    newComp = compUUID[:8]
                    print(newComp)
                    compURL = 'http://' + host + ':19080/rcm-fitness-api/api/compliance/data/device/' + compUUID

                    compResp = requests.get(compURL)
                    compData = json.loads(compResp.text)

                    assert compResp.status_code == 200, "Request has not been acknowledged as expected."

                    totalSubComponents = len(compData["subComponents"])
                    assert totalSubComponents == minSubCount or maxSubCount, "Unexpected number of subcomponents returned."

                    with open(filename, 'a') as outfile:
                        json.dump(compData, outfile, sort_keys=True, indent=4, ensure_ascii=False)

                    if compData["device"]["uuid"] != "":
                        print("You are right here now again......")
                        if compData["device"]["uuid"] == data["components"][i]["uuid"]:

                            print(i)
                            assert compData["device"]["uuid"] == data["components"][i]["uuid"], "response does not detail Component UUID."

                            assert "parentGroupUuids" in compData["device"], "Response not detail Parent Group UUID."
                            assert compData["device"]["parentGroupUuids"] == data["components"][i]["parentGroupUuids"], "Response not detail Parent Group UUID."

                            assert "elementData" in compData["device"], "Response not detail Element Data."
                            assert "auditData" in compData["device"], "Response not detail Audit Data."
                            assert "versionDatas" in compData["device"], "Response not detail Version Datas."
                            #assert "productFamily" in compData["device"]["elementData"], "Response not detail Product Family."

                            assert "modelFamily" in compData["device"]["elementData"], "Response not detail Family."
                            assert compData["device"]["elementData"]["modelFamily"] == data["components"][i]["definition"]["modelFamily"], "Response not detail Family."

                            assert "model" in compData["device"]["elementData"], "Response not detail Model."
                            assert compData["device"]["elementData"]["model"] == model, "Response not detail Model."
                            assert compData["device"]["elementData"]["model"] == data["components"][i]["definition"]["model"], "Response not detail Model."

                            assert "productFamily" in compData["device"]["elementData"], "Response not detail Model."
                            assert compData["device"]["elementData"]["productFamily"] == deviceProduct, "Response not detail Model."
                            assert compData["device"]["elementData"]["productFamily"] == data["components"][i]["definition"]["productFamily"], "Response not detail Model."

                            assert "elementType" in compData["device"]["elementData"], "Response not detail Element Type."
                            assert compData["device"]["elementData"]["elementType"] == deviceType, "Response not detail Type."
                            assert compData["device"]["elementData"]["elementType"] == data["components"][i]["identity"]["elementType"], "Response not detail Type."

                            assert "identifier" in compData["device"]["elementData"], "response not detail Identifier."
                            assert compData["device"]["elementData"]["identifier"] == data["components"][i]["identity"]["identifier"], "Response not detail Identifier."

                            #assert "ipAddress" in compData["device"]["elementData"], "Response not detail IP Address."
                            #assert compData["device"]["elementData"]["identifier"] == data["components"][0]["identity"]["identifier"], "Response not detail IP Address."

                            #assert "serialNumber" in compData["device"]["elementData"], "Response not detail Serial No."
                            #assert compData["device"]["elementData"]["serialNumber"] == data["components"][0]["identity"]["serialNumber"], "Response not detail Serial Number."

                            assert "collectedTime" in compData["device"]["auditData"], "Response not detail Collected Time."
                            assert "collectionSentTime" in compData["device"]["auditData"], "Response not detail Collection Sent Time."
                            assert "messageReceivedTime" in compData["device"]["auditData"], "Response not detail Received Time."

                            assert "uuid" in compData["groups"][0], "Response not detail component Groups."
                            assert compData["groups"][0]["uuid"] == sysData["system"]["groups"][0]["uuid"], "Response not detail component Groups."

                            assert "parentGroupUuids" in compData["groups"][0], "Response not detail Parent Groups."
                            assert compData["groups"][0]["parentGroupUuids"] == sysData["system"]["groups"][0]["parentGroupUuids"], "Response not detail Parent Group."

                            assert "parentSystemUuids" in compData["groups"][0], "Response not detail Parent System."
                            assert compData["groups"][0]["parentSystemUuids"][0] == sysData["system"]["groups"][0]["parentSystemUuids"][0], "Response not detail Parent System."

                            assert "type" in compData["groups"][0], "Response not detail component Groups."
                            assert compData["groups"][0]["type"] == sysData["system"]["groups"][0]["type"], "Response not detail Type."

                            assert "systemUuid" in compData["systems"][0], "Response not detail System UUID."
                            assert compData["systems"][0]["systemUuid"] == sysData["system"]["uuid"], "Response not detail Type."

                            assert "product" in compData["systems"][0], "Response not detail System UUID."
                            assert compData["systems"][0]["product"] == product, "1 Response not detail Product."
                            assert compData["systems"][0]["product"] == sysData["system"]["definition"]["product"], "2 Response not detail Product."

                            assert "modelFamily" in compData["systems"][0], "Response not detail System UUID."
                            assert compData["systems"][0]["modelFamily"] == family, "Response not detail Family."
                            assert compData["systems"][0]["modelFamily"] == sysData["system"]["definition"]["modelFamily"], "Response not detail Family."

                            assert "model" in compData["systems"][0], "Response not detail System UUID."
                            assert compData["systems"][0]["model"] == sysData["system"]["definition"]["model"], "Response not detail Model."

                            assert "identifier" in compData["systems"][0], "Response not detail System UUID."
                            assert compData["systems"][0]["identifier"] == sysData["system"]["identity"]["identifier"], "Response not detail Identifier."

                            assert "serialNumber" in compData["systems"][0], "Response not detail System UUID."
                            assert compData["systems"][0]["serialNumber"] == sysData["system"]["identity"]["serialNumber"], "Response not detail Serial Number."

                            #assert "productFamily" in compData["systems"][0], "Response not detail Product Family."
                            #assert compData["systems"][0]["productFamily"] == sysData["system"]["definition"]["productFamily"], "Response not detail Serial Number."

                            assert compData["device"]["elementData"]["elementType"] == deviceType
                            i += 1
                    print("Key and Value assertions concluded.")

                compIndex += 1
            compIndex = 0

    except Exception as e:
        print("Unexpected error: " + str(e))
        #print(response)
        traceback.print_exc()
        raise Exception(e)


def getComplianceDataDeviceSubComps(elementType, identifier, sysDefFilename, compDataFilename, sysUUID):
    subIndex = 0
    totalSubComponents = 0
    getSystemDefinition()

    url = 'http://' + host + ':19080/rcm-fitness-api/api/system/definition/' + sysUUID

    resp = requests.get(url)
    data = json.loads(resp.text)

    assert resp.status_code == 200, "Request has not been acknowledged as expected."
    print("Requesting system details from Compliance Data Service.\n")

    with open(sysDefFilename, 'w') as outfile:
        json.dump(data, outfile, sort_keys=True, indent=4, ensure_ascii=False)

    compURL = 'http://' + host + ':19080/rcm-fitness-api/api/compliance/data/device/' + compUUID

    compResp = requests.get(compURL)
    compData = json.loads(compResp.text)

    assert compResp.status_code == 200, "Request has not been acknowledged as expected."

    with open(compDataFilename, 'w') as outfile:
        json.dump(compData, outfile, sort_keys=True, indent=4, ensure_ascii=False)

#("NIC", "Ethernet 10G", )

    if len(compData["subComponents"]) != "":
        totalSubComponents = len(compData["subComponents"])
        while subIndex < totalSubComponents:
            #print("Starting subComps: %d" % subIndex)
            if identifier in compData["subComponents"][subIndex]["elementData"]["identifier"]:
                assert "uuid" in compData["subComponents"][subIndex], "Response detailed an empty group UUID."
                assert "parentDeviceUuid" in compData["subComponents"][subIndex], "Response not detail parent Group UUID."
                assert "elementType" in compData["subComponents"][subIndex]["elementData"], "Response not detail Element Type."
                assert "identifier" in compData["subComponents"][subIndex]["elementData"], "Response not detail Identifier."
                assert "modelFamily" in compData["subComponents"][subIndex]["elementData"], "Response not detail Family."
                assert "model" in compData["subComponents"][subIndex]["elementData"], "Response not detail Model."
                assert "messageReceivedTime" in compData["subComponents"][subIndex]["auditData"], "Response not detail Received Time."
                assert "type" in compData["subComponents"][subIndex]["versionDatas"][0], "Response not detail Type."
                assert "version" in compData["subComponents"][subIndex]["versionDatas"][0], "Response not detail Version."

                assert compData["subComponents"][subIndex]["uuid"] != "", "Response not detail subcomponent UUID."
                assert compData["subComponents"][subIndex]["elementData"]["elementType"] == elementType, "Response returns incorrect Type."
                #assert identifier in compData["subComponents"][subIndex]["elementData"]["identifier"], "Response returns incorrect Identifier."
                assert compData["subComponents"][subIndex]["parentDeviceUuid"] == compData["device"]["uuid"], "Response not detail parent Group UUID."
                assert compData["subComponents"][subIndex]["auditData"]["messageReceivedTime"] != "", "No timestamp included."
                assert compData["subComponents"][subIndex]["versionDatas"][0]["type"] == "FIRMWARE"
                assert compData["subComponents"][subIndex]["versionDatas"][0]["version"] != ""
                print(compData["subComponents"][subIndex]["elementData"]["model"])
                print(compData["subComponents"][subIndex]["elementData"]["elementType"])
                print(compData["subComponents"][subIndex]["elementData"]["identifier"])
                print(compData["subComponents"][subIndex]["elementData"]["modelFamily"])
                if compData["subComponents"][subIndex]["elementData"]["elementType"] == "NIC":
                    macAddress = compData["subComponents"][subIndex]["elementData"]["identifier"]
                    countColon = macAddress.count(":")
                    assert countColon == 5, "Unexpected MAC address format returned in Identifier value."

                print("Done SubComp: %s\n" % elementType)
            subIndex += 1


def getComplianceData_INVALID(compUUID):
    subIndex = 0
    compIndex = 0
    versionIndex = 0
    getSystemDefinition()
    print(compUUID)
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
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataDevice1():
    getComplianceData("VXRACK", "FLEX", "R730XD", "POWEREDGE", "SERVER", path + "complianceDataDevicePOWEREDGE.json", systemUUID, 5, 5)
@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataDevice2():
    getComplianceDataDeviceSubComps("NIC", "Ethernet 10G 2P", path + "rcmSystemDefinition-VxRack.json", path + "complianceDataDevicePOWEREDGE.json", systemUUID)
@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataDevice3():
    getComplianceDataDeviceSubComps("NIC", "Ethernet 10G 4P", path + "rcmSystemDefinition-VxRack.json", path + "complianceDataDevicePOWEREDGE.json", systemUUID)
@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataDevice4():
    getComplianceDataDeviceSubComps("BIOS", "BIOS", path + "rcmSystemDefinition-VxRack.json", path + "complianceDataDevicePOWEREDGE.json", systemUUID)
@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataDevice5():
    getComplianceDataDeviceSubComps("iDRAC", "Remote Access", path + "rcmSystemDefinition-VxRack.json", path + "complianceDataDevicePOWEREDGE.json", systemUUID)
@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataDevice6():
    getComplianceDataDeviceSubComps("RAID", "PERC H730", path + "rcmSystemDefinition-VxRack.json", path + "complianceDataDevicePOWEREDGE.json", systemUUID)
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataDevice7():
    getComplianceData("VXRACK", "FLEX", "R630", "POWEREDGE", "SERVER", path + "complianceDataDevicePOWEREDGE.json", systemUUID, 5, 5)
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataDevice8():
    getComplianceDataDeviceSubComps("NIC", "Ethernet 10G 2P", path + "rcmSystemDefinition-VxRack.json", path + "complianceDataDevicePOWEREDGE.json", systemUUID)
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataDevice9():
    getComplianceDataDeviceSubComps("NIC", "Ethernet 10G 4P", path + "rcmSystemDefinition-VxRack.json", path + "complianceDataDevicePOWEREDGE.json", systemUUID)
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataDevice10():
    getComplianceDataDeviceSubComps("BIOS", "BIOS", path + "rcmSystemDefinition-VxRack.json", path + "complianceDataDevicePOWEREDGE.json", systemUUID)
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataDevice11():
    getComplianceDataDeviceSubComps("iDRAC", "Remote Access", path + "rcmSystemDefinition-VxRack.json", path + "complianceDataDevicePOWEREDGE.json", systemUUID)
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataDevice12():
    getComplianceDataDeviceSubComps("RAID", "PERC H730", path + "rcmSystemDefinition-VxRack.json", path + "complianceDataDevicePOWEREDGE.json", systemUUID)
@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataDevice13():
    getComplianceData("VXRACK", "FLEX", "VCENTER", "VCENTER", "VCENTER", path + "complianceDataDeviceVCENTER.json", systemUUID, 3, 18)
@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataDevice14():
    getComplianceDataDeviceSubComps("ESXI", "lab.vce.com", path + "rcmSystemDefinition-VxRack.json", path + "complianceDataDeviceVCENTER.json", systemUUID)   
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataDevice15():
    getComplianceData_INVALID(compUUID[:8])
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataDevice16():
    getComplianceData_INVALID("----")
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataDevice17():
    getComplianceData_INVALID("0-0-0-0")
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataDevice18():
    getComplianceData_INVALID("<>")
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataDevice19():
    getComplianceData_INVALID("  ")
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataDevice20():
    getComplianceData_NULL()
