#!/usr/bin/env python
import json
import pika
import sys
import logging
import requests
from collections import Counter
import pytest
import libs.rabbitmqTraceParse
import libs.rabbitmqConfigLib as rabbitconfig

rabbithost = '10.3.61.215'
rabbituser = 'root'
rabbitpassword = 'V1rtu@1c3!'
maxLatencyAllowed = 5

host = '10.3.61.215'
path = '/home/autouser/PycharmProjects/auto-framework/test_suites/restAPItests/'
open(path + "rcmSystemDefinition.json", 'w').close()
# open(path + "rcmComplianceData.json", 'w').close()
# open(path + "rcmAvailableRCMs.json", 'w').close()
# open(path + "rcmRCMDefinitionDetails.json", 'w').close()
# open(path + "rcmEvaluationDetails.json", 'w').close()
# open(path + "rcm*.json", 'w').close()

def getSystemDefinition():
    url = 'http://' + host + ':19080/rcm-fitness-api/api/system/definition/'
    resp = requests.get(url)
    data = json.loads(resp.text)

    print("Requesting UUID from System Definition....")
    assert resp.status_code == 200, "Request has not been acknowledged as expected."

    if data != "":
        if data["systems"][0]["systemUuid"] != "":
            with open(path + 'rcmSystemDefinition.json', 'w') as outfile:
                json.dump(data, outfile, sort_keys=True, indent=4, ensure_ascii=False)

            print("\nExtracting UUID from response....\n")
            global systemUUID
            systemUUID = data["systems"][0]["systemUuid"]
            print(systemUUID)
        else:
            print("\nNo System UUID returned in REST response")
            print(data["message"])

    print("Defined SystemUUID: %s" % systemUUID)
    return systemUUID

# def getSystemDefinitionByUUID(product, family, model, type):
#     url = 'http://' + host + ':19080/rcm-fitness-api/api/system/definition/' + systemUUID
#     resp = requests.get(url)
#     data = json.loads(resp.text)
#     groupIndex = 0
#     totalGroups = 0
#
#     print("Requesting a systems specific details ....")
#     assert resp.status_code == 200, "Request has not been acknowledged as expected."
#
#     if data != "":
#         if data["system"]["systemUuid"] != "":
#             with open(path + 'rcmSystemDefinitionByUUID.json', 'w') as outfile:
#                 json.dump(data, outfile, sort_keys=True, indent=4, ensure_ascii=False)
#
#             assert "systemUuid" in data["system"], "Response not detail System UUID."
#             assert "product" in data["system"], "Response not detail Product."
#             assert "family" in data["system"], "Response not detail Family."
#             assert "model" in data["system"], "Response not detail Model."
#             assert "componentTag" in data["system"], "Response not detail Component Tag."
#             assert "serialNumber" in data["system"], "Response not detail Serial No."
#             assert "groups" in data["system"], "Response not detail component Groups."
#
#             assert data["system"]["systemUuid"] == systemUUID, "Response details incorrent System UUID."
#             assert data["system"]["product"] == product, "Response details incorrect Product."
#             assert data["system"]["family"] == family, "Response details incorrect Family."
#             assert data["system"]["serialNumber"] != "", "Response details empty Serial Number."
#             assert model in data["system"]["model"], "Response details incorrect Model."
#
#             totalGroups = len(data["system"]["groups"])
#             assert totalGroups > 0, "Empty list of Groups returned."
#
#             print("\nTotal groups: %d" % totalGroups)
#             print("\nExtracting groupUUID from response....\n")
#             while groupIndex < totalGroups:
#                 if data["system"]["groups"][groupIndex]["type"] == type:
#                     global groupUUID
#                     groupUUID = data["system"]["groups"][groupIndex]["groupUuid"]
#
#                 groupIndex += 1
#
#             print(groupUUID)
#         else:
#             print("\nNo systemUUID returned in REST response")
#             print(data["message"])
#
# def getComponentBySystemUUID(family, series, type, tag):
#     url = 'http://' + host + ':19080/rcm-fitness-api/api/system/definition/' + systemUUID + '/component'
#     resp = requests.get(url)
#     data = json.loads(resp.text)
#     compIndex = 0
#     totalComponents = 0
#     totalEndpts = 0
#
#
#     print("Requesting a systems specific details ....")
#     assert resp.status_code == 200, "Request has not been acknowledged as expected."
#
#     if data != "":
#         if data["systemUuid"] != "":
#             with open(path + 'rcmComponentBySystemUUID.json', 'w') as outfile:
#                 json.dump(data, outfile, sort_keys=True, indent=4, ensure_ascii=False)
#
#             assert data["systemUuid"] == systemUUID, "Response did not detail the expected system UUID."
#
#             totalComponents = len(data["components"])
#             assert totalComponents > 0, "Empty list of Components returned."
#
#             print("\nTotal components: %d" % totalComponents)
#             #print("\nExtracting groupUUID from response....\n")
#             while compIndex < totalComponents:
#                 if data["components"][compIndex]["series"] == series:
#                     assert data["components"][compIndex]["group"] == groupUUID, "Response includes unexpected group ID."
#                     assert data["components"][compIndex]["family"] == family, "Response includes unexpected Family."
#                     assert tag in data["components"][compIndex]["componentTag"], "Response includes unexpected Component Tag."
#                     totalEndpts = len(data["components"][compIndex]["endpoints"])
#                     assert totalEndpts > 0, "Empty list of Endpoints returned for this component."
#
#                     #groupUUID = data["system"]["groups"][groupIndex]["groupUuid"]
#
#                 compIndex += 1
#             #print(groupUUID)
#         else:
#             print("\nNo system returned in REST response.")
#             print(data["message"])

def getComplianceData(model, type, filename):
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
            if data["components"][compIndex]["series"] == model:
                global compUUID
                compUUID = data["components"][compIndex]["componentUuid"]

                compURL = 'http://' + host + ':19080/rcm-fitness-api/api/compliance/data/device/' + compUUID

                compResp = requests.get(compURL)
                compData = json.loads(compResp.text)

                assert compResp.status_code == 200, "Request has not been acknowledged as expected."

                with open(filename, 'a') as outfile:
                    json.dump(compData, outfile, sort_keys=True, indent=4, ensure_ascii=False)

                while subIndex < len(compData["subComponents"]):
                    if "model" in compData["subComponents"][subIndex]["elementData"]:
                        if model in (compData["subComponents"][subIndex]["elementData"]["model"]) and (compData["subComponents"][subIndex]["elementData"]["elementType"] == type):
                            while versionIndex < len(compData["subComponents"][subIndex]["versionDatas"]):
                                if (compData["subComponents"][subIndex]["versionDatas"][versionIndex]["type"]) == "FIRMWARE":
                                    global nexusFWversion
                                    nexusFWversion = (compData["subComponents"][subIndex]["versionDatas"][versionIndex]["version"])
                                    print("\n\nComponent requested: %s" % compUUID)
                                    print("\nDiscovered firmware version: %s\n\n" % nexusFWversion)
                                versionIndex += 1
                    subIndex += 1
            compIndex += 1

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
            if data["components"][compIndex]["series"] == model:
                global compUUID
                compUUID = data["components"][compIndex]["componentUuid"]

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
                                    global nexusFWversion
                                    nexusFWversion = (compData["subComponents"][subIndex]["versionDatas"][versionIndex]["version"])
                                    print("\n\nComponent requested: %s" % compUUID)
                                    print("\nDiscovered firmware version: %s\n\n" % nexusFWversion)
                                versionIndex += 1
                    subIndex += 1
            compIndex += 1

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

@pytest.mark.TCComplianeScan_SetupTrace
def test_getRCMsetup():
    # enable rabbitmq tracing to support perf measurements
    rabbitconfig.enable_firehose(rabbithost, rabbituser, rabbitpassword, "json")
    rabbitconfig.create_firehose_queue(rabbithost)

#@pytest.mark.TC546466
@pytest.mark.TC546466_Vblock
def test_getSysDef1():
    getSystemDefinition()
@pytest.mark.TC546467
def test_getComplianceData1():
    getComplianceData("N3K-C3048TP-1GE", "FIXEDMODULE", path + "rcmComplianceData-N3k.json")
@pytest.mark.TC546469
def test_getAvailableRCM1():
    getAvailableRCMs("Vblock", "340", "6.0", "6.0.11", path + "rcmAvailableRCMs-N3k.json")
@pytest.mark.TC546468
def test_getRCMDefinition1():
    getRCMDefinition("Nexus 3048", path + "rcmRCMDefinitionDetails-N3k.json")
@pytest.mark.TC546470
def test_getRCMEval1():
    getRCMEvaluation("Nexus", "3048", path + "rcmEvaluationDetails-N3k.json")
@pytest.mark.TC546467
def test_getComplianceData2():
    getComplianceData("N5K", "FIXEDMODULE", path + "rcmComplianceData-N5k.json")
@pytest.mark.TC546469
def test_getAvailableRCM2():
    getAvailableRCMs("Vblock", "340", "6.0", "6.0.11", path + "rcmAvailableRCMs-N5k.json")
@pytest.mark.TC546468
def test_getRCMDefinition2():
    getRCMDefinition("Nexus 55xx", path + "rcmRCMDefinitionDetails-N5k.json")
@pytest.mark.TC546470
def test_getRCMEval2():
    getRCMEvaluation("Nexus", "55xx", path + "rcmEvaluationDetails-N5k.json")
@pytest.mark.TC546467
def test_getComplianceData3():
    getComplianceData("MDS9K", "FIXEDMODULE", path + "rcmComplianceData-MDS9k.json")
@pytest.mark.TC546469
def test_getAvailableRCM3():
    getAvailableRCMs("Vblock", "340", "6.0", "6.0.10", path + "rcmAvailableRCMs-MDS9k.json")
@pytest.mark.TC546468
def test_getRCMDefinition3():
    getRCMDefinition("MDS 9148", path + "rcmRCMDefinitionDetails-MDS9k.json")
@pytest.mark.TC546470
def test_getRCMEval3():
    getRCMEvaluation("MDS", "9148", path + "rcmEvaluationDetails-MDS9k.json")
@pytest.mark.TC546467
def test_getComplianceData4():
    getComplianceData("N3K", "FIXEDMODULE", path + "rcmComplianceData-N3k-Mismatch.json")
@pytest.mark.TC546469
def test_getAvailableRCM4():
    getAvailableRCMs("Vblock", "340", "5.0", "5.0.4", path + "rcmAvailableRCMs-N3k-Mismatch.json")
@pytest.mark.TC546468
def test_getRCMDefinition4():
    getRCMDefinition("Nexus 3048", path + "rcmRCMDefinitionDetails-N3k-Mismatch.json")
@pytest.mark.TC546470
def test_getRCMEval4():
    getRCMEvaluation("Nexus", "3048", path + "rcmEvaluationDetails-N3k-Mismatch.json")
@pytest.mark.TC546467
def test_getComplianceData5():
    getComplianceData("N5K", "FIXEDMODULE", path + "rcmComplianceData-N5k-Mismatch.json")
@pytest.mark.TC546469
def test_getAvailableRCM5():
    getAvailableRCMs("Vblock", "340", "5.0", "5.0.7", path + "rcmAvailableRCMs-N5k-Mismatch.json")
@pytest.mark.TC546468
def test_getRCMDefinition5():
    getRCMDefinition("Nexus 55xx", path + "rcmRCMDefinitionDetails-N5k-Mismatch.json")
@pytest.mark.TC546470
def test_getRCMEval5():
    getRCMEvaluation("Nexus", "55xx", path + "rcmEvaluationDetails-N5k-Mismatch.json")
@pytest.mark.TC546467
def test_getComplianceData6():
    getComplianceData("MDS9K", "FIXEDMODULE", path + "rcmComplianceData-MDS9k-Mismatch.json")
@pytest.mark.TC546469
def test_getAvailableRCM6():
    getAvailableRCMs("Vblock", "340", "6.0", "6.0.1", path + "rcmAvailableRCMs-MDS9k-Mismatch.json")
@pytest.mark.TC546468
def test_getRCMDefinition6():
    getRCMDefinition("MDS 9148", path + "rcmRCMDefinitionDetails-MDS9k-Mismatch.json")
@pytest.mark.TC546470
def test_getRCMEval6():
    getRCMEvaluation("MDS", "9148", path + "rcmEvaluationDetails-MDS9k-Mismatch.json")


@pytest.mark.TCComplianceScan_CleanupTrace
def test_getRCMcleanup():
    # turn-off rabbitmq tracing
    rabbitconfig.disable_firehose(rabbithost, rabbituser, rabbitpassword)
    rabbitconfig.delete_firehose_queue(rabbithost)


@pytest.mark.TCComplianceScan_Perf_Scenario_Latency
def test_getRCMPerf1():
    remotetracefile = '/var/log/rabbitmq/trace-files/my-new-trace.log'
    localtracefile = '/tmp/tracejson.log'
    # retrieve the rabbitmqtrace file for local parsing
    rabbitmqTraceParse.retrieve_tracelogfile(rabbithost, rabbituser, rabbitpassword, remotetracefile, localtracefile)
    firehosefile = open(localtracefile, 'rt')
    # Check the rabbitmq tracefile to ensure none of the correlation scenarios took longer then maxLatencyAllowed (seconds) to complete
    assert rabbitmqTraceParse.generateTimingsLog(firehosefile, maxLatencyAllowed) == False, \
        'One (or more) of the latency readings were too high, ie. greater then that set in the testscript (maxLatencyAllowed). \
         All timings are saved to /tmp/summarisedrabbitMQTrace_<timestamp>.log'
