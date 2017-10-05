#!/usr/bin/python
import pika
import json
import time
import af_support_tools
import pytest
import os
import re
import datetime
import sys
import logging
import requests


@pytest.fixture(scope="module", autouse=True)
def load_test_data():
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


@pytest.fixture()
def sys():
    url = 'http://' + host + ':19080/rcm-fitness-api/api/install/firmware/status/b8d5f1a9-7c85-475c-9ba3-a1cdde9a4c57'
    response = requests.get(url)
    assert response.status_code == 200, "Request has not been acknowledged as expected."
    data = response.json()

    # assert data["systems"][0]["uuid"] != ""
    # print("\nExtracting systemUUID from response....\n")
    # uuidlist = []
    # for k, v in data.items():
    #     if isinstance(v, list):
    #         for system in v:
    #             uuidlist.append(system["uuid"])
    #             print(uuidlist)
    #
    # return uuidlist


def test_install_firmware(sys):
    url = 'http://' + host + ':19080/rcm-fitness-api/api/install/firmware'
    body = {'filePath': '/home/cpsd/firmware/SAS-RAID_Firmware_VH28K_WN64_25.4.0.0017_A06',
    'subComponentType': 'RAID',
    'deviceId': '2c9fedf6-3fcf-379e-9fc5-1dd15b71d3fd'}
    data_json = json.dumps(body)
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    response = requests.post(url, data_json, headers=headers)
    data = response.json()



#ToDo
#Invalid UUID
#Incorrect sub-component type


















#
#
#
#
#
#
#
# def verifyRESTdownloadSingleFileRequest(filename):
#     resetTestQueues()
#     print("Queues reset.")
#     deletePreviousDownloadFiles("100mbfiletest.zip",
#                               "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader-service/repository/downloads/")
#
#     #url = 'http://' + host + ':10000/rcm-fitness-paqx/rcm-fitness-api/api/download/firmware/'
#     url = 'http://' + host + ':19080/rcm-fitness-api/api/download/firmware/'
#     payload = {'fileName': filename}
#     headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
#     resp = requests.post(url, data=json.dumps(payload), headers=headers)
#
#     print("Returned status code: %d" % resp.status_code)
#     data = json.loads(resp.text)
#     assert resp.status_code == 200, "Request has not been acknowledged as expected."
#
#     print(data)
#     if data != "":
#         assert data["state"] == "ACKNOWLEDGED", "Unexpected initial state returned."
#         assert len(data["uuid"]) > 16, "No valid request UUID returned."
#         assert data["uuid"] in data["link"]["href"], "Request UUID not found in returned HREF link."
#         assert data["link"]["method"] == "GET", "Unexpected method returned in response."
#         print("URL: %s" % data["link"]["href"])
#         # assert "10000/rcm-fitness-paqx/rcm-fitness-api/api/download/firmware/status/" in data["link"]["href"], "No URL included in response to query subsequent progress."
#         assert "19080/rcm-fitness-api/api/download/firmware/status/" in data["link"][
#             "href"], "No URL included in response to query subsequent progress."
#         assert data["link"]["rel"] == "download-status"
#         print("Download request's initial response verified.")
#
#         statusURL = data["link"]["href"]
#         statusData = requests.get(statusURL)
#         statusResp = json.loads(statusData.text)
#
#         while statusResp["state"] != "COMPLETE":
#             time.sleep(0.5)
#             statusURL = data["link"]["href"]
#             statusData = requests.get(statusURL)
#             statusResp = json.loads(statusData.text)
#             if statusResp["state"] == "FAILED":
#                 assert False, "Download request unexpectedly failed."
#             print("Checking....")
#         return
#     assert False, ("Initial REST update request not complete.")
#
# def verifyRESTdownloadInvalidFileRequest(filename):
#     resetTestQueues()
#     print("Queues reset.")
#     deletePreviousDownloadFiles("100mbfiletest.zip",
#                               "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader-service/repository/downloads/")
#
#     #url = 'http://' + host + ':10000/rcm-fitness-paqx/rcm-fitness-api/api/download/firmware/'
#     url = 'http://' + host + ':19080/rcm-fitness-api/api/download/firmware/'
#     payload = {'fileName': filename}
#     headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
#     resp = requests.post(url, data=json.dumps(payload), headers=headers)
#
#     print("Returned status code: %d" % resp.status_code)
#     data = json.loads(resp.text)
#     assert resp.status_code == 200, "Request has not been acknowledged as expected."
#
#     print(data)
#     if data != "":
#         assert data["state"] == "ACKNOWLEDGED", "Unexpected initial state returned."
#         print("Download request's initial response verified.")
#
#         statusURL = data["link"]["href"]
#         statusData = requests.get(statusURL)
#         statusResp = json.loads(statusData.text)
#
#         while statusResp["state"] != "FAILED":
#             time.sleep(0.5)
#             statusURL = data["link"]["href"]
#             statusData = requests.get(statusURL)
#             statusResp = json.loads(statusData.text)
#             print("Checking for failed status....")
#
#         if statusResp["state"] == "FAILED":
#             assert statusResp["error"] is not None, "Expected error message not included in response."
#         return
#     assert False, ("Initial REST update request not complete.")
#
# def verifyRESTdownloadSingleFileRequestSTATUS(filename):
#     resetTestQueues()
#     print("Queues reset.")
#
#     deletePreviousDownloadFiles("100mbfiletest.zip",
#                               "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader-service/repository/downloads/")
#
#     url = 'http://' + host + ':19080/rcm-fitness-api/api/download/firmware/'
#     payload = {'fileName': filename}
#     headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
#     resp = requests.post(url, data=json.dumps(payload), headers=headers)
#
#     print("Returned status code: %d" % resp.status_code)
#     data = json.loads(resp.text)
#     assert resp.status_code == 200, "Request has not been acknowledged as expected."
#
#     if data["state"] == "ACKNOWLEDGED":
#         print("Request acknowleded, now query status using link provided.")
#         assert "19080/rcm-fitness-api/api/download/firmware/status/" in data["link"]["href"], "No URL included in response to query subsequent progress."
#         statusURL = data["link"]["href"]
#         print(data)
#         print("HREF URL: %s " % statusURL)
#         assert data["link"]["rel"] == "download-status", "Unexpected REL value returned."
#         assert data["link"]["method"] == "GET", "Unexpected method value returned."
#         assert data["url"] is None, "Unexpected URL returned in ack."
#         assert data["hashVal"] is None, "Unexpected hash returned in ack."
#         assert data["downloadedSize"] is None, "Unexpected downloadedSize returned in ack."
#         assert data["size"] is None, "Unexpected size returned in ack."
#         assert data["error"] is None, "Unexpected error returned in ack."
#         time.sleep(1)
#         statusData = requests.get(statusURL)
#         statusResp = json.loads(statusData.text)
#         print(2.1)
#         assert statusResp["state"] == "COMPLETE" or "IN_PROGRESS", "Unexpected initial state returned."
#         assert len(statusResp["uuid"]) > 16, "No valid request UUID returned."
#         assert statusResp["uuid"] in statusResp["link"]["href"], "Request UUID not found in returned HREF link."
#         assert statusResp["link"]["method"] == "GET", "Unexpected method returned in response."
#         print(2.2)
#         assert "19080/rcm-fitness-api/api/download/firmware/status/" in statusResp["link"]["href"], "No URL included in response to query subsequent progress."
#         assert statusResp["link"]["rel"] == "download-status", "Unexpected REL value returned."
#         #assert filename in statusResp["url"], "Expected filename not included in returned URL."
#         #assert len(statusResp["hashVal"]) > 32, "HashVal not the expected length."
#         assert statusResp["downloadedSize"] != 0, "Unexpected download size returned."
#         #assert statusResp["size"] != 0, "Unexpected file size returned."
#         #assert statusResp["downloadedSize"] <= statusResp["size"], "Download size is reported as larger than expected size."
#         assert statusResp["error"] is None, "Unexpected error returned."
#         print("Download request's status response verified.")
#
#     i = 0
#     while statusResp["state"] != "COMPLETE":
#         print(3)
#
#         assert statusResp["state"] == "IN_PROGRESS" or "ACKNOWLEDGED", "Unexpected initial state returned."
#         assert len(statusResp["uuid"]) > 16, "No valid request UUID returned."
#         assert statusResp["uuid"] in statusResp["link"]["href"], "Request UUID not found in returned HREF link."
#         assert statusResp["link"]["method"] == "GET", "Unexpected method returned in response."
#         # assert "10000/rcm-fitness-paqx/rcm-fitness-api/api/download/firmware/status/" in statusResp["link"]["href"], "No URL included in response to query subsequent progress."
#         assert "19080/rcm-fitness-api/api/download/firmware/status/" in statusResp["link"][
#             "href"], "No URL included in response to query subsequent progress."
#         assert statusResp["link"]["rel"] == "download-status"
#         #assert filename in statusResp["url"], "Expected filename not included in returned URL."
#         #assert len(statusResp["hashVal"]) > 32, "HashVal not the expected length."
#         assert statusResp["downloadedSize"] != 0, "Unexpected download size returned."
#         #assert statusResp["size"] != 0, "Unexpected file size returned."
#         #assert statusResp["downloadedSize"] == statusResp["size"], "Download size is reported as larger than expected size."
#         assert statusResp["error"] is None, "Unexpected error returned."
#
#         time.sleep(0.5)
#         statusURL = statusResp["link"]["href"]
#         #statusResp = requests.get(statusURL)
#         statusData = requests.get(statusURL)
#         statusResp = json.loads(statusData.text)
#         print("Download request's progress response verified.")
#
#         if statusResp["state"] == "IN_PROGRESS":
#             i += 1
#             print("In here... Loop: %d" % i)
#             time.sleep(0.5)
#             statusURL = statusResp["link"]["href"]
#             # statusResp = requests.get(statusURL)
#             statusData = requests.get(statusURL)
#             statusResp = json.loads(statusData.text)
#             print("Progressing...")
#             continue
#
#
#
#     if statusResp["state"] == "COMPLETE":
#         print(4)
#         assert statusResp["state"] == "COMPLETE", "Unexpected initial state returned."
#         assert len(statusResp["uuid"]) > 16, "No valid request UUID returned."
#         assert statusResp["uuid"] in statusResp["link"]["href"], "Request UUID not found in returned HREF link."
#         assert statusResp["link"]["method"] == "GET", "Unexpected method returned in response."
#         # assert "10000/rcm-fitness-paqx/rcm-fitness-api/api/download/firmware/status/" in statusResp["link"]["href"], "No URL included in response to query subsequent progress."
#         assert "19080/rcm-fitness-api/api/download/firmware/status/" in statusResp["link"][
#             "href"], "No URL included in response to query subsequent progress."
#         assert statusResp["link"]["rel"] == "download-status"
#         assert filename in statusResp["url"], "Expected filename not included in returned URL."
#         assert len(statusResp["hashVal"]) > 32, "HashVal not the expected length."
#         assert statusResp["downloadedSize"] != 0, "Unexpected download size returned."
#         assert statusResp["size"] != 0, "Unexpected file size returned."
#         assert statusResp["downloadedSize"] == statusResp["size"], "Download size is reported as larger than expected size."
#         assert statusResp["error"] is None, "Unexpected error returned."
#         print("Download request's complete response verified.")
#         return
#
#     if statusResp["state"] != "COMPLETE":
#         if statusResp["state"] != "IN_PROGRESS":
#             print(statusResp["state"])
#             assert False, "Invalid status reported."
#             #return
#     assert False, "Initial REST update request not complete."
#
# def verifyRESTdownloadMultiFileRequest(filename, secFilename, thirdFilename):
#     resetTestQueues()
#     print("Queues reset.")
#     deletePreviousDownloadFiles("100mbfiletest.zip",
#                               "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader-service/repository/downloads/")
#
#     #url = 'http://' + host + ':10000/rcm-fitness-paqx/rcm-fitness-api/api/download/firmware/'
#     url = 'http://' + host + ':19080/rcm-fitness-api/api/download/firmware/'
#     payload = {'fileName': filename}
#     headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
#     resp = requests.post(url, data=json.dumps(payload), headers=headers)
#
#     print("Returned status code: %d" % resp.status_code)
#     data = json.loads(resp.text)
#     assert resp.status_code == 200, "Request has not been acknowledged as expected."
#
#     #url = 'http://' + host + ':10000/rcm-fitness-paqx/rcm-fitness-api/api/download/firmware/'
#     url = 'http://' + host + ':19080/rcm-fitness-api/api/download/firmware/'
#     payload = {'fileName': secFilename}
#     headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
#     resp = requests.post(url, data=json.dumps(payload), headers=headers)
#     secdata = json.loads(resp.text)
#     assert resp.status_code == 200, "Request has not been acknowledged as expected."
#
#     #url = 'http://' + host + ':10000/rcm-fitness-paqx/rcm-fitness-api/api/download/firmware/'
#     url = 'http://' + host + ':19080/rcm-fitness-api/api/download/firmware/'
#     payload = {'fileName': thirdFilename}
#     headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
#     resp = requests.post(url, data=json.dumps(payload), headers=headers)
#     thirddata = json.loads(resp.text)
#     assert resp.status_code == 200, "Request has not been acknowledged as expected."
#
#     print(data)
#     if data != "":
#         if secdata != "":
#             if thirddata != "":
#                 assert data["state"] == "ACKNOWLEDGED", "Unexpected initial state returned."
#                 # assert "10000/rcm-fitness-paqx/rcm-fitness-api/api/download/firmware/status/" in data["link"]["href"], "No URL included in response to query subsequent progress."
#                 assert "19080/rcm-fitness-api/api/download/firmware/status/" in data["link"][
#                     "href"], "No URL included in response to query subsequent progress."
#                 assert secdata["state"] == "ACKNOWLEDGED", "Unexpected initial state returned."
#                 # assert "10000/rcm-fitness-paqx/rcm-fitness-api/api/download/firmware/status/" in data["link"]["href"], "No URL included in response to query subsequent progress."
#                 assert "19080/rcm-fitness-api/api/download/firmware/status/" in secdata["link"][
#                     "href"], "No URL included in response to query subsequent progress."
#                 assert thirddata["state"] == "ACKNOWLEDGED", "Unexpected initial state returned."
#                 # assert "10000/rcm-fitness-paqx/rcm-fitness-api/api/download/firmware/status/" in data["link"]["href"], "No URL included in response to query subsequent progress."
#                 assert "19080/rcm-fitness-api/api/download/firmware/status/" in thirddata["link"][
#                     "href"], "No URL included in response to query subsequent progress."
#                 print("Download request's initial response verified.")
#
#                 statusURL = data["link"]["href"]
#                 secstatusURL = secdata["link"]["href"]
#                 thirdstatusURL = thirddata["link"]["href"]
#                 statusData = requests.get(statusURL)
#                 secstatusData = requests.get(secstatusURL)
#                 thirdstatusData = requests.get(thirdstatusURL)
#                 statusResp = json.loads(statusData.text)
#                 secstatusResp = json.loads(secstatusData.text)
#                 thirdstatusResp = json.loads(thirdstatusData.text)
#
#                 print(statusResp["state"])
#                 print(secstatusResp["state"])
#                 print(thirdstatusResp["state"])
#
#                 while statusResp["state"] != "COMPLETE":
#                     print("Checking 1st file....")
#                     time.sleep(0.5)
#                     statusURL = data["link"]["href"]
#                     statusData = requests.get(statusURL)
#                     statusResp = json.loads(statusData.text)
#
#                 while secstatusResp["state"] != "COMPLETE":
#                     print("Checking 2nd file....")
#                     time.sleep(0.5)
#                     secstatusURL = secdata["link"]["href"]
#                     secstatusData = requests.get(secstatusURL)
#                     secstatusResp = json.loads(secstatusData.text)
#
#                 while thirdstatusResp["state"] != "COMPLETE":
#                     print("Checking 3rd file....")
#                     time.sleep(0.5)
#                     thirdstatusURL = thirddata["link"]["href"]
#                     thirdstatusData = requests.get(thirdstatusURL)
#                     thirdstatusResp = json.loads(thirdstatusData.text)
#
#                 return
#     assert False, ("Initial REST update request not complete.")
#
# def verifyRESTrepositoryStatus(filepath, filename):
#     url = 'http://' + host + ':8888/downloads/' + filepath
#     repoStatus = requests.get(url)
#     print(repoStatus.content)
#     assert repoStatus.status_code == 200, "Request has not been acknowledged as expected."
#
#     content = repoStatus.content.decode('utf-8')
#
#     if repoStatus.content != "":
#         assert filepath in content, "Response does not include file path."
#         assert filename in content, "Response does not include file name."
#         # print("Done")
#         return
#     assert False, "Failing....."
#
# @pytest.mark.rcm_fitness_mvp_extended
# @pytest.mark.rcm_fitness_mvp
# def test_verifyRESTdownloadSingleFileRequest1():
#     verifyRESTdownloadSingleFileRequest("RCM/3.2.1/VxRack_1000_FLEX/Component/Controller_Firmware/SAS-RAID_Firmware_VH28K_WN64_25.4.0.0017_A06.EXE")
#
# @pytest.mark.rcm_fitness_mvp_extended
# @pytest.mark.rcm_fitness_mvp
# def test_verifyRESTdownloadSingleFileRequestSTATUS1():
#     verifyRESTdownloadSingleFileRequestSTATUS("RCM/3.2.1/VxRack_1000_FLEX/Component/Controller_Firmware/SAS-RAID_Firmware_VH28K_WN64_25.4.0.0017_A06.EXE")
#
# @pytest.mark.rcm_fitness_mvp_extended
# def test_verifyRESTrepositoryStatus1():
#     verifyRESTrepositoryStatus("RCM/3.2.1/VxRack_1000_FLEX/Component/Controller_Firmware/", "SAS-RAID_Firmware_VH28K_WN64_25.4.0.0017_A06.EXE")
#
# @pytest.mark.rcm_fitness_mvp_extended
# def test_verifyRESTdownloadSingleFileRequest2():
#     verifyRESTdownloadSingleFileRequest("100mbfiletest.zip")
#
# @pytest.mark.rcm_fitness_mvp_extended
# def test_verifyRESTdownloadSingleFileRequestSTATUS2():
#     verifyRESTdownloadSingleFileRequestSTATUS("100mbfiletest.zip")
#
# @pytest.mark.rcm_fitness_mvp_extended
# def test_verifyRESTrepositoryStatus2():
#     verifyRESTrepositoryStatus("", "100mbfiletest.zip")
#
#
# # @pytest.mark.rcm_fitness_mvp
# # def test_verifyRESTdownloadInvalidFileRequest3():
# #     verifyRESTdownloadInvalidFileRequest("RCM/3.2.1/SAS-RAID_Firmware_VH28K_WN64_25.4.0.0017_A06.EXE")
#
#
# # @pytest.mark.rcm_fitness_mvp
# # def test_verifyRESTdownloadInvalidFileRequest4():
# #     verifyRESTdownloadInvalidFileRequest("////")
#
# # @pytest.mark.rcm_fitness_mvp
# # def test_verifyRESTdownloadInvalidFileRequest5():
# #     verifyRESTdownloadInvalidFileRequest("")
# #
#
# @pytest.mark.rcm_fitness_mvp_extended
# @pytest.mark.rcm_fitness_mvp
# def test_verifyRESTdownloadMultiFileRequest6():
#     verifyRESTdownloadMultiFileRequest("RCM/3.2.1/VxRack_1000_FLEX/Component/Controller_Firmware/SAS-RAID_Firmware_VH28K_WN64_25.4.0.0017_A06.EXE", "100mbfiletest.zip", "RCM/3.2.2/VxRack_1000_FLEX/Component/BIOS/2.2.5/BIOS_PFWCY_WN64_2.2.5.EXE")
#
# @pytest.mark.rcm_fitness_mvp_extended
# @pytest.mark.rcm_fitness_mvp
# def test_verifyRESTrepositoryStatus6():
#     verifyRESTrepositoryStatus("RCM/3.2.1/VxRack_1000_FLEX/Component/Controller_Firmware/", "SAS-RAID_Firmware_VH28K_WN64_25.4.0.0017_A06.EXE")
#
# @pytest.mark.rcm_fitness_mvp_extended
# @pytest.mark.rcm_fitness_mvp
# def test_verifyRESTrepositoryStatus6a():
#     verifyRESTrepositoryStatus("", "100mbfiletest.zip")
#
# @pytest.mark.rcm_fitness_mvp_extended
# @pytest.mark.rcm_fitness_mvp
# def test_verifyRESTrepositoryStatus6b():
#     verifyRESTrepositoryStatus("RCM/3.2.2/VxRack_1000_FLEX/Component/BIOS/2.2.5/", "BIOS_PFWCY_WN64_2.2.5.EXE")



# @pytest.mark.rcm_fitness_mvp_extended
# @pytest.mark.rcm_fitness_mvp
# def test_verifyRESTdownloadSingleFileRequest7():
#     verifyRESTdownloadSingleFileRequest("RCM/3.2.1/VxRack_1000_FLEX/Component/Controller_Firmware/SAS-RAID_Firmware_VH28K_WN64_25.4.0.0017_A06.EXE")
