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
path = '/home/autouser/PycharmProjects/auto-framework/test_suites/continuousIntegration/c_systemDefinition/'
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

def getSystemDefinition(product, family, model, type):
    url = 'http://' + host + ':19080/rcm-fitness-api/api/system/definition/'
    resp = requests.get(url)
    data = json.loads(resp.text)

    groupIndex = linkIndex = totalGroups = 0
    totalEndpoints = totalSubSystems = totalComponents = totalLinks = 0

    print("GroupIndex: %d" % groupIndex)
    print("TotalSubSystems: %d" % totalSubSystems)

    print("Requesting UUID from System Definition....")
    assert resp.status_code == 200, "Request has not been acknowledged as expected."

    if data != "":
        if data["systems"][0]["uuid"] != "":
            with open(path + 'rcmSystemDefinition.json', 'w') as outfile:
                json.dump(data, outfile, sort_keys=True, indent=4, ensure_ascii=False)

            print("\nExtracting UUID from response....")
            global systemUUID
            systemUUID = data["systems"][0]["uuid"]
            print("Defined SystemUUID: %s" % systemUUID)
            assert "uuid" in data["systems"][0], "Response not detail System UUID."
            assert "identity" in data["systems"][0], "Response not detail Identity."
            assert "definition" in data["systems"][0], "Response not detail Definition."
            assert "groups" in data["systems"][0], "Response not detail Groups."
            assert "endpoints" in data["systems"][0], "Response not detail Endpoints."
            assert "subSystems" in data["systems"][0], "Response not detail Subsystems."
            assert "components" in data["systems"][0], "Response not detail Components."
            assert "links" in data["systems"][0], "Response not detail Links."

            assert data["systems"][0]["definition"]["product"] == product, "Response details incorrect Product."
            assert data["systems"][0]["definition"]["modelFamily"] == family, "Response details incorrect Family."
            assert data["systems"][0]["identity"]["serialNumber"] != "", "Response details empty Serial Number."
            assert model in data["systems"][0]["definition"]["model"], "Response details incorrect Model."

            # totalGroups = len(data["systems"][0]["groups"])
            # totalEndpoints = len(data["systems"][0]["endpoints"])
            # totalSubSystems = len(data["systems"][0]["subSystems"])
            # totalComponents = len(data["systems"][0]["components"])
            # totalLinks = len(data["systems"][0]["links"])
            #
            # assert totalGroups > 0, "Empty list of Groups returned."
            # assert totalEndpoints > 0, "Empty list of Endpoints returned."
            # assert totalSubSystems > 0, "Empty list of SubSystems returned."
            # assert totalComponents > 0, "Empty list of Components returned."
            # assert totalLinks > 0, "Empty list of Links returned."
            #
            # print("\nTotal groups: %d" % totalGroups)
            # print("\nExtracting groupUUID from response....\n")
            # while groupIndex < totalGroups:
            #     if data["systems"][0]["groups"][groupIndex]["type"] == type:
            #         global groupUUID
            #         groupUUID = data["systems"][0]["groups"][groupIndex]["groupUuid"]
            #         print("Defined groupUUID: %s" % groupUUID)
            #     groupIndex += 1
            #
            # while listIndex < totalLinks:
            #     print("Defined groupUUID: %s" % data["systems"][0]["links"][listIndex]["href"])
            #     assert data["systems"][0]["links"][listIndex]["href"] != "", "Empty links returned in HREF field."
            #     listIndex += 1
        else:
            print("\nNo System UUID returned in REST response")
            print(data["message"])


    return systemUUID

def getSystemDefinitionByUUID(product, family, model, type):
    url = 'http://' + host + ':19080/rcm-fitness-api/api/system/definition/' + systemUUID
    resp = requests.get(url)
    data = json.loads(resp.text)

    groupIndex = linkIndex = 0
    totalGroups = totalEndpoints = totalSubSystems = totalComponents = totalLinks = 0

    print("Requesting a systems specific details ....")
    assert resp.status_code == 200, "Request has not been acknowledged as expected."

    if data != "":
        if data["system"]["uuid"] != "":
            with open(path + 'rcmSystemDefinitionByUUID.json', 'w') as outfile:
                json.dump(data, outfile, sort_keys=True, indent=4, ensure_ascii=False)

            print("Defined SystemUUID: %s" % systemUUID)
            assert "uuid" in data["system"], "Response not detail System UUID."
            assert "identity" in data["system"], "Response not detail Identity."
            assert "definition" in data["system"], "Response not detail Definition."
            assert "groups" in data["system"], "Response not detail Groups."
            assert "endpoints" in data["system"], "Response not detail Endpoints."
            assert "subSystems" in data["system"], "Response not detail Subsystems."
            assert "components" in data["system"], "Response not detail Components."
            assert "links" in data["system"], "Response not detail Links."

            assert data["system"]["definition"]["product"] == product, "Response details incorrect Product."
            assert data["system"]["definition"]["modelFamily"] == family, "Response details incorrect Family."
            assert data["system"]["identity"]["serialNumber"] != "", "Response details empty Serial Number."
            assert model in data["system"]["definition"]["model"], "Response details incorrect Model."

            # totalGroups = len(data["system"][0]["groups"])
            # totalEndpoints = len(data["system"][0]["endpoints"])
            # totalSubSystems = len(data["system"][0]["subSystems"])
            # totalComponents = len(data["system"][0]["components"])
            # totalLinks = len(data["system"][0]["links"])
            #
            # assert totalGroups > 0, "Empty list of Groups returned."
            # assert totalEndpoints > 0, "Empty list of Endpoints returned."
            # assert totalSubSystems > 0, "Empty list of SubSystems returned."
            # assert totalComponents > 0, "Empty list of Components returned."
            # assert totalLinks > 0, "Empty list of Links returned."
            #
            # print("\nTotal groups: %d" % totalGroups)
            # print("\nExtracting groupUUID from response....\n")
            # while groupIndex < totalGroups:
            #     if data["system"][0]["groups"][groupIndex]["type"] == type:
            #         global groupUUID
            #         groupUUID = data["system"][0]["groups"][groupIndex]["groupUuid"]
            #         print("Defined groupUUID: %s" % groupUUID)
            #     groupIndex += 1
            #
            # while listIndex < totalLinks:
            #     print("Defined groupUUID: %s" % data["system"][0]["links"][listIndex]["href"])
            #     assert data["system"][0]["links"][listIndex]["href"] != "", "Empty links returned in HREF field."
            #     listIndex += 1
        else:
            print("\nNo System UUID returned in REST response")
            print(data["message"])

def getComponentBySystemUUID(family, series, type, tag, endpoints):
    url = 'http://' + host + ':19080/rcm-fitness-api/api/system/definition/' + systemUUID + '/component'
    resp = requests.get(url)
    data = json.loads(resp.text)

    compIndex = totalComponents = 0
    totalEndpts = endPts = 0


    print("Requesting a systems specific details ....")
    assert resp.status_code == 200, "Request has not been acknowledged as expected."

    if data != "":
        if data["systemUuid"] != "":
            with open(path + 'rcmComponentBySystemUUID.json', 'w') as outfile:
                json.dump(data, outfile, sort_keys=True, indent=4, ensure_ascii=False)

            assert data["systemUuid"] == systemUUID, "Response did not detail the expected system UUID."

            totalComponents = len(data["components"])
            assert totalComponents > 0, "Empty list of Components returned."

            print("\nTotal components: %d" % totalComponents)
            #print("\nExtracting groupUUID from response....\n")
            while compIndex < totalComponents:
                if data["components"][compIndex]["definition"]["modelFamily"] == series:
                    #assert data["components"][compIndex]["parentGroupUuids"][0] == groupUUID, "Response includes unexpected group ID."
                    assert data["components"][compIndex]["definition"]["productFamily"] == family, "Response includes unexpected Family."
                    assert tag in data["components"][compIndex]["identity"]["identifier"], "Response includes unexpected Component Tag."
                    totalEndpts = len(data["components"][compIndex]["endpoints"])
                    assert totalEndpts == endpoints, "Empty list of Endpoints returned for this component."
                    print("\nComponent: %s" % data["components"][compIndex]["definition"]["modelFamily"])
                    print("Tag: %s" % data["components"][compIndex]["identity"]["identifier"])
                    print("UUID: %s" % data["components"][compIndex]["uuid"])
                    print("Total Endpts: %d" % totalEndpts)
                    #groupUUID = data["system"]["groups"][groupIndex]["groupUuid"]
                compIndex += 1
                endPts = 0

        else:
            print("\nNo system returned in REST response.")
            print(data["message"])

def getSystemDefinitionInvalidUUID(invalidSystemUUID):
    #invalidSystemUUID = systemUUID[:8]
    print(invalidSystemUUID)
    url = 'http://' + host + ':19080/rcm-fitness-api/api/system/definition/' + invalidSystemUUID + '/'
    resp = requests.get(url)
    data = json.loads(resp.text)

    print(data["system"])
    print(data["message"])

    if not data["system"]:
        if ("message") in data.keys():
            print(data["message"])
            assert ('RFCA1017I') in (data["message"]), "Returned Error Message does not reflect expected Error Code."
            assert (invalidSystemUUID) in (data["message"]), "Returned Error Message does not reflect specified System UUID."

def getComponentByInvalidSystemUUID(invalidSystemUUID):
    #invalidSystemUUID = systemUUID[:8]
    print(invalidSystemUUID)
    url = 'http://' + host + ':19080/rcm-fitness-api/api/system/definition/' + invalidSystemUUID + '/component/'
    resp = requests.get(url)
    data = json.loads(resp.text)

    print(data["system"])
    print(data["message"])

    if not data["system"]:
        if ("message") in data.keys():
            print(data["message"])
            assert ('RFCA1017I') in (data["message"]), "Returned Error Message does not reflect expected Error Code."
            assert (invalidSystemUUID) in (data["message"]), "Returned Error Message does not reflect specified System UUID."

def getSystemDefinitionNullUUID():
    url = 'http://' + host + ':19080/rcm-fitness-api/api/system/definition//'
    resp = requests.get(url)
    #data = json.loads(resp.text)

    print("Requesting a NULL systems specific details ....")
    print(resp.status_code)
    assert resp.status_code == 404, "Request has not been acknowledged as expected."


#@pytest.mark.TC546466
# @pytest.mark.rcm_fitness_mvp
# def test_getSysDef1():
#     getSystemDefinition("VXRACK", "FLEX", "1000", "NETWORK")
# @pytest.mark.rcm_fitness_mvp
# def test_getSysDef2():
#     getSystemDefinitionByUUID("VXRACK", "FLEX", "1000", "NETWORK")
# @pytest.mark.rcm_fitness_mvp
# def test_getSysDef3():
#     getComponentBySystemUUID("NEXUS", "N3K", "SWITCH", "MGMT-", 2)
# @pytest.mark.rcm_fitness_mvp
# def test_getSysDef4():
#     getComponentBySystemUUID("NEXUS", "N5K", "SWITCH", "N5", 2)
# @pytest.mark.rcm_fitness_mvp
# def test_getSysDef4a():
#     getComponentBySystemUUID("NEXUS", "N9K", "SWITCH", "N9", 2)
# @pytest.mark.rcm_fitness_mvp
# def test_getSysDef5():
#     getComponentBySystemUUID("MDS", "MDS9000", "SWITCH", "M9", 2)
# # @pytest.mark.TC546466_Vblock
# # def test_getSysDef6():
# #     getComponentBySystemUUID("NSX", "NSX", "SWITCH", "NSX", 1)
# # @pytest.mark.TC546466_Vblock
# # def test_getSysDef7():
# #     getSystemDefinitionByUUID("VXBLOCK", "340", "VxB340", "STORAGE")
# # @pytest.mark.TC546466_Vblock
# # def test_getSysDef8():
# #     getComponentBySystemUUID("VNX", "VNX5400", "STORAGE_ARRAY", "ARRAY", 4)
# # @pytest.mark.TC546466_Vblock
# # def test_getSysDef9():
# #     getSystemDefinitionByUUID("VXBLOCK", "340", "VxB340", "MANAGEMENT_STORAGE")
# # @pytest.mark.TC546466_Vblock
# # def test_getSysDef10():
# #     getComponentBySystemUUID("VNXe", "VNXe3200", "STORAGE_ARRAY", "Array", 1)
# # @pytest.mark.TC546466_Vblock
# # def test_getSysDef11():
# #     getSystemDefinitionByUUID("VXBLOCK", "340", "VxB340", "COMPUTE")
# # @pytest.mark.TC546466_Vblock
# # def test_getSysDef12():
# #     getComponentBySystemUUID("UCS", "UCS1", "SERVER", "VMABO", 2)
# # @pytest.mark.TC546466_Vblock
# # def test_getSysDefInvalid():
# #     getSystemDefinitionInvalidUUID(systemUUID[:8])
# # @pytest.mark.TC546466_Vblock
# # def test_getSysDefInvalid2():
# #     getSystemDefinitionInvalidUUID("1111")
# # @pytest.mark.TC546466_Vblock
# # def test_getCompSysDefInvalid():
# #     getComponentByInvalidSystemUUID(systemUUID[:8])
# # @pytest.mark.TC546466_Vblock
# # def test_getCompSysDefInvalid2():
# #     getComponentByInvalidSystemUUID("1111")
# @pytest.mark.rcm_fitness_mvp
# def test_getSysDefNull():
#     getSystemDefinitionNullUUID()

