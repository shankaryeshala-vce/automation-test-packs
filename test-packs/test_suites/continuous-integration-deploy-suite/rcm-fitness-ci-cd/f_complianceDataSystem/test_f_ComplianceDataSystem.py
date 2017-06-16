#!/usr/bin/env python
import json
import requests
import pytest
import af_support_tools
import os
import re


@pytest.fixture(scope="module", autouse=True)
def load_test_data():
    global path
    path = '/home/autouser/PycharmProjects/auto-framework/test_suites/continuous-integration-deploy-suite/rcm-fitness-ci-cd/restLevelTests/complianceDataSystem/'
    ensurePathExists(path)
    purgeOldOutput(path, "complianceDataSystem")

    global ssl_options
    ssl_options = {"ca_certs": "/etc/rabbitmq/certs/testca/cacert.pem",
                   "certfile": "/etc/rabbitmq/certs/certs/client/cert.pem",
                   "keyfile": "/etc/rabbitmq/certs/certs/client/key.pem", "cert_reqs": "ssl.CERT_REQUIRED",
                   "ssl_version": "ssl.PROTOCOL_TLSv1_2"}

    # Set config ini file name
    global env_file
    env_file = 'env.ini'

    global host
    host = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='hostname')

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

            # print("\nExtracting UUID from response....\n")
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


# ("VXRACK", "FLEX", "VXRACKFLEX", "730", "R730XD", "SERVER", path + "complianceDataSystemPOWEREDGE.json", systemUUID)

def getComplianceDataSystem(product, family, identifier, deviceFamily, deviceModel, deviceType, compDataFilename,
                            sysUUID):
    subIndex = 0
    compIndex = 0
    groupIndex = 0
    deviceIndex = 0
    i = 0

    url = 'http://' + host + ':19080/rcm-fitness-api/api/system/definition/' + sysUUID
    resp = requests.get(url)
    data = json.loads(resp.text)
    assert resp.status_code == 200, "Request has not been acknowledged as expected."

    url = 'http://' + host + ':19080/rcm-fitness-api/api/system/definition/' + sysUUID + '/component/'
    resp = requests.get(url)
    deviceData = json.loads(resp.text)

    assert resp.status_code == 200, "Request has not been acknowledged as expected."
    print("Requesting system details from Compliance Data Service.\n")

    totalComponents = len(deviceData["components"])

    compURL = 'http://' + host + ':19080/rcm-fitness-api/api/compliance/data/system/' + sysUUID

    compResp = requests.get(compURL)
    compData = json.loads(compResp.text)

    assert compResp.status_code == 200, "Request has not been acknowledged as expected."

    with open(compDataFilename, 'a') as outfile:
        json.dump(compData, outfile, sort_keys=True, indent=4, ensure_ascii=False)

    if len(compData["devices"]) != "":

        assert not compData["message"], "Expected message field to be NULL."
        assert compData["convergedSystem"]["systemUuid"] == deviceData[
            "systemUuid"] == systemUUID, "Response shows incorrect System UUID."
        assert compData["convergedSystem"]["product"] == product, "Response not detail Model."
        assert compData["convergedSystem"]["modelFamily"] == family, "Response not detail Family."
        assert compData["convergedSystem"]["identifier"] == identifier, "Response not detail Identifier."
        assert "serialNumber" in compData["convergedSystem"], "Response not detail Serial Number."

        assert compData["convergedSystem"]["model"] == data["system"]["definition"][
            "model"], "Unexpected Model returned."
        assert compData["convergedSystem"]["modelFamily"] == data["system"]["definition"][
            "modelFamily"], "Unexpected Model returned."
        assert compData["convergedSystem"]["product"] == data["system"]["definition"][
            "product"], "Unexpected Product returned."
        assert compData["convergedSystem"]["identifier"] == data["system"]["identity"][
            "identifier"], "Unexpected Identifier returned."
        assert compData["convergedSystem"]["serialNumber"] == data["system"]["identity"][
            "serialNumber"], "Unexpected Serial No. returned."
        assert len(compData["convergedSystem"]["links"]) > 0, "No link returned for Converged System."

        print("Verifying Converged System....")
        totalGroups = len(compData["groups"])
        assert totalGroups > 0, "response not including a list of Groups."
        totalDevices = len(compData["devices"])
        assert totalDevices > 0, "response not including a list of Devices."
        totalSubComponents = len(compData["subComponents"])
        assert totalSubComponents > 0, "response not including a list of Devices."

        while groupIndex < totalGroups:
            if compData["groups"][groupIndex]["uuid"] == data["system"]["groups"][i]["uuid"]:
                assert compData["groups"][groupIndex]["parentSystemUuids"][
                           0] == systemUUID, "Response not detail parent System UUID."
                assert compData["groups"][groupIndex]["type"] == "STORAGE" or "NETWORK" or "COMPUTE"
                print("Done System type: %s" % compData["groups"][groupIndex]["type"])
                i += 1
            groupIndex += 1
        print("Verifying groups....")
        index = 0
        while deviceIndex < totalDevices:
            if compData["devices"][deviceIndex]["uuid"] == deviceData["components"][compIndex]["uuid"]:
                # assert compData["devices"][deviceIndex]["uuid"] == deviceData["components"][deviceIndex]["uuid"], "Response detailed an empty group UUID."
                assert compData["devices"][deviceIndex]["parentGroupUuids"][0] == \
                       deviceData["components"][compIndex]["parentGroupUuids"][
                           0], "Response not detail parent Group UUID."
                assert "productFamily" in compData["devices"][deviceIndex][
                    "elementData"], "Response not detail Product Family."
                assert "modelFamily" in compData["devices"][deviceIndex][
                    "elementData"], "Response not detail Model Family."
                assert "model" in compData["devices"][deviceIndex]["elementData"], "Response not detail Model."
                assert "identifier" in compData["devices"][deviceIndex][
                    "elementData"], "Response not detail Identifier."
                assert "elementType" in compData["devices"][deviceIndex][
                    "elementData"], "Response not detail ElementType."
                # assert "ipAddress" in compData["devices"][deviceIndex]["elementData"], "Response not detail IP Address."
                # assert "serialNumber" in compData["devices"][deviceIndex]["elementData"], "Response not detail Serial Number."
                assert compData["devices"][deviceIndex]["auditData"][
                           "collectedTime"] != "", "Response not detail Collection Time."
                assert compData["devices"][deviceIndex]["auditData"][
                           "collectionSentTime"] != "", "Response not detail Collection Sent Time."
                assert compData["devices"][deviceIndex]["auditData"][
                           "messageReceivedTime"] != "", "Response not detail Received Time."

                if compData["devices"][deviceIndex]["elementData"]["modelFamily"] == deviceFamily:
                    assert compData["devices"][deviceIndex]["uuid"] == deviceData["components"][compIndex][
                        "uuid"], "Response detailed an empty group UUID."
                    assert compData["devices"][deviceIndex]["parentGroupUuids"][0] == \
                           deviceData["components"][compIndex]["parentGroupUuids"][
                               0], "Response not detail parent Group UUID."
                    assert compData["devices"][deviceIndex]["elementData"][
                               "elementType"] == deviceType, "Response not detail Element Type."
                    assert compData["devices"][deviceIndex]["elementData"][
                               "model"] == deviceModel, "Response not detail Model."
                    assert compData["devices"][deviceIndex]["elementData"]["elementType"] == \
                           deviceData["components"][compIndex]["identity"][
                               "elementType"], "Response not detail Element Type."
                    assert compData["devices"][deviceIndex]["elementData"]["model"] == \
                           deviceData["components"][compIndex]["definition"]["model"], "Response not detail Model."
                    assert compData["devices"][deviceIndex]["elementData"]["modelFamily"] == \
                           deviceData["components"][compIndex]["definition"][
                               "modelFamily"], "Response not detail Identifier."
                    assert compData["devices"][deviceIndex]["elementData"]["productFamily"] == \
                           deviceData["components"][compIndex]["definition"][
                               "productFamily"], "Response not detail Product Family."
                    assert compData["devices"][deviceIndex]["elementData"]["identifier"] == \
                           deviceData["components"][compIndex]["identity"][
                               "identifier"], "Response not detail Identifier."
                    macAddress = compData["devices"][deviceIndex]["elementData"]["identifier"]
                    if ":" in macAddress:
                        countColon = macAddress.count(":")
                        assert countColon == 5, "Unexpected MAC address format returned."
                    # assert compData["devices"][deviceIndex]["elementData"]["serialNumber"] != "", "Response not detail Serial Number."
                    assert compData["devices"][deviceIndex]["auditData"][
                               "collectedTime"] != "", "Response not detail Collection Time."
                    assert compData["devices"][deviceIndex]["auditData"][
                               "collectionSentTime"] != "", "Response not detail Collection Sent Time."
                    assert compData["devices"][deviceIndex]["auditData"][
                               "messageReceivedTime"] != "", "Response not detail Received Time."
                    print(compData["devices"][deviceIndex]["elementData"]["modelFamily"])
                    print(compData["devices"][deviceIndex]["elementData"]["elementType"])
                    print("Done Device: %s\n" % compData["devices"][deviceIndex]["elementData"]["identifier"])

                compIndex += 1
            deviceIndex += 1
        deviceIndex = 0
        print("Verifying Devices completed....\n")


# ("ESXi", "lab.vce.com", path + "rcmSystemDefinition-VxRack.json", path + "complianceDataSystemVCENTER.json", systemUUID)

def getComplianceDataSystemSubComps(elementType, identifier, sysDefFilename, compDataFilename, sysUUID):
    subIndex = 0
    getSystemDefinition()

    url = 'http://' + host + ':19080/rcm-fitness-api/api/system/definition/' + sysUUID

    resp = requests.get(url)
    data = json.loads(resp.text)

    assert resp.status_code == 200, "Request has not been acknowledged as expected."
    print("Requesting system details from Compliance Data Service.\n")

    with open(sysDefFilename, 'w') as outfile:
        json.dump(data, outfile, sort_keys=True, indent=4, ensure_ascii=False)

    compURL = 'http://' + host + ':19080/rcm-fitness-api/api/compliance/data/system/' + sysUUID

    compResp = requests.get(compURL)
    compData = json.loads(compResp.text)

    assert compResp.status_code == 200, "Request has not been acknowledged as expected."

    with open(compDataFilename, 'w') as outfile:
        json.dump(compData, outfile, sort_keys=True, indent=4, ensure_ascii=False)

    index = 0

    if len(compData["devices"]) != "":
        totalSubComponents = len(compData["subComponents"])

        while subIndex < totalSubComponents:
            # print("Starting subComps: %d" % subIndex)
            if identifier in compData["subComponents"][subIndex]["elementData"]["identifier"]:
                if compData["subComponents"][subIndex]["parentDeviceUuid"] == compData["devices"][index]["uuid"]:
                    assert "uuid" in compData["subComponents"][subIndex], "Response detailed an empty group UUID."
                    assert "parentDeviceUuid" in compData["subComponents"][
                        subIndex], "Response not detail parent Group UUID."
                    assert "elementType" in compData["subComponents"][subIndex][
                        "elementData"], "Response not detail Element Type."
                    assert "identifier" in compData["subComponents"][subIndex][
                        "elementData"], "Response not detail Identifier."
                    assert "modelFamily" in compData["subComponents"][subIndex][
                        "elementData"], "Response not detail Family."
                    assert "model" in compData["subComponents"][subIndex]["elementData"], "Response not detail Model."
                    assert "messageReceivedTime" in compData["subComponents"][subIndex][
                        "auditData"], "Response not detail Received Time."
                    assert "type" in compData["subComponents"][subIndex]["versionDatas"][0], "Response not detail Type."
                    assert "version" in compData["subComponents"][subIndex]["versionDatas"][
                        0], "Response not detail Version."

                    assert compData["subComponents"][subIndex]["uuid"] != "", "Response not detail subcomponent UUID."
                    assert compData["subComponents"][subIndex]["elementData"][
                               "elementType"] == elementType, "Response returns incorrect Type."
                    assert identifier in compData["subComponents"][subIndex]["elementData"][
                        "identifier"], "Response returns incorrect Identifier."
                    assert compData["subComponents"][subIndex]["parentDeviceUuid"] == compData["devices"][index][
                        "uuid"], "Response not detail parent Group UUID."
                    assert compData["subComponents"][subIndex]["auditData"][
                               "messageReceivedTime"] != "", "No timestamp included."
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
                    index += 1

                print("Done SubComp: %s\n" % elementType)
            subIndex += 1


def getComplianceDataSystem_INVALID(sysUUID):
    subIndex = 0
    compIndex = 0
    versionIndex = 0
    getSystemDefinition()

    url = 'http://' + host + ':19080/rcm-fitness-api/api/compliance/data/system/' + sysUUID

    resp = requests.get(url)
    data = json.loads(resp.text)

    # assert resp.status_code == 200, "Request has not been acknowledged as expected."

    if not data["convergedSystem"]:
        if "message" in data.keys():
            if ('RFCA1003E') in data["code"]:
                assert resp.status_code == 500, "Request has not been acknowledged as expected."
                print("Message: %s" % data["message"])
                assert ('RCDS1006E Error retrieving system compliance data') in (
                data["message"]), "Returned Error Message text not as expected."
                # assert ('RFCA1005I') in (data["code"]), "Returned Error Message does not reflect expected Error Code."
                assert (sysUUID) in (data["message"]), "Returned Error Message does not include expected compUUID."

            if ('RFCA1005I') in (data["code"]):
                assert resp.status_code == 200, "Request has not been acknowledged as expected."
                print("Message: %s" % data["message"])
                assert ('RFCA1005I No compliance data was found') in (
                data["message"]), "Returned Error Message text not as expected."
                # assert ('RFCA1005I') in (data["code"]), "Returned Error Message does not reflect expected Error Code."
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
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataSystem1():
    getComplianceDataSystem("VXRACK", "FLEX", "VXRACKFLEX", "730", "R730XD", "SERVER",
                            path + "complianceDataSystemPOWEREDGE.json", systemUUID)


@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataSystem2():
    getComplianceDataSystemSubComps("NIC", "Ethernet 10G 2P", path + "rcmSystemDefinition-VxRack.json",
                                    path + "complianceDataSystemPOWEREDGE.json", systemUUID)


@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataSystem3():
    getComplianceDataSystemSubComps("NIC", "Ethernet 10G 4P", path + "rcmSystemDefinition-VxRack.json",
                                    path + "complianceDataSystemPOWEREDGE.json", systemUUID)


@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataSystem4():
    getComplianceDataSystemSubComps("BIOS", "BIOS", path + "rcmSystemDefinition-VxRack.json",
                                    path + "complianceDataSystemPOWEREDGE.json", systemUUID)


@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataSystem5():
    getComplianceDataSystemSubComps("iDRAC", "Remote Access", path + "rcmSystemDefinition-VxRack.json",
                                    path + "complianceDataSystemPOWEREDGE.json", systemUUID)


@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataSystem6():
    getComplianceDataSystemSubComps("RAID", "PERC H730", path + "rcmSystemDefinition-VxRack.json",
                                    path + "complianceDataSystemPOWEREDGE.json", systemUUID)


@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataSystem7():
    getComplianceDataSystem("VXRACK", "FLEX", "VXRACKFLEX", "630", "R630", "SERVER",
                            path + "complianceDataSystemPOWEREDGE.json", systemUUID)


@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataSystem8():
    getComplianceDataSystemSubComps("NIC", "Ethernet 10G 2P", path + "rcmSystemDefinition-VxRack.json",
                                    path + "complianceDataSystemPOWEREDGE.json", systemUUID)


@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataSystem9():
    getComplianceDataSystemSubComps("NIC", "Ethernet 10G 4P", path + "rcmSystemDefinition-VxRack.json",
                                    path + "complianceDataSystemPOWEREDGE.json", systemUUID)


@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataSystem10():
    getComplianceDataSystemSubComps("BIOS", "BIOS", path + "rcmSystemDefinition-VxRack.json",
                                    path + "complianceDataSystemPOWEREDGE.json", systemUUID)


@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataSystem11():
    getComplianceDataSystemSubComps("iDRAC", "Remote Access", path + "rcmSystemDefinition-VxRack.json",
                                    path + "complianceDataSystemPOWEREDGE.json", systemUUID)


@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataSystem12():
    getComplianceDataSystemSubComps("RAID", "PERC H730", path + "rcmSystemDefinition-VxRack.json",
                                    path + "complianceDataSystemPOWEREDGE.json", systemUUID)


@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataSystem13():
    getComplianceDataSystem("VXRACK", "FLEX", "VXRACKFLEX", "VCENTER", "VCENTER", "VCENTER",
                            path + "complianceDataSystemVCENTER.json", systemUUID)


@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataSystem14():
    getComplianceDataSystemSubComps("ESXi", "lab.vce.com", path + "rcmSystemDefinition-VxRack.json",
                                    path + "complianceDataSystemVCENTER.json", systemUUID)


@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataSystem15():
    getComplianceDataSystem_INVALID(systemUUID[:8])


@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataSystem16():
    getComplianceDataSystem_INVALID("----")


@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataSystem17():
    getComplianceDataSystem_INVALID(" ")


@pytest.mark.rcm_fitness_mvp_extended
def test_getComplianceDataSystem18():
    getComplianceDataSystem_NULL()
