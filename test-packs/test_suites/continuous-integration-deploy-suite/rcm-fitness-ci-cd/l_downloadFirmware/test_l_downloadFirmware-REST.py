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
    global path
    path = "/home/autouser/PycharmProjects/auto-framework/test_suites/continuous-integration-deploy-suite/rcm-fitness-ci-cd/l_downloadFirmware/"
    global ssl_options
    ssl_options = {"ca_certs": "/etc/rabbitmq/certs/testca/cacert.pem",
                   "certfile": "/etc/rabbitmq/certs/certs/client/cert.pem",
                   "keyfile": "/etc/rabbitmq/certs/certs/client/key.pem", "cert_reqs": "ssl.CERT_REQUIRED",
                   "ssl_version": "ssl.PROTOCOL_TLSv1_2"}

    # Update config ini files at runtime
    # my_data_file = 'listRCMs.properties'
    my_data_file = os.environ.get(
        'AF_RESOURCES_PATH') + '/continuous-integration-deploy-suite/downloadInputs.properties'
    af_support_tools.set_config_file_property_by_data_file(my_data_file)

    # Set config ini file name
    global env_file
    env_file = 'env.ini'

    global host
    host = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='hostname')
    global port
    port = af_support_tools.get_config_file_property(config_file=env_file, heading='RabbitMQ', property='port')
    port = int(port)
    global rmq_username
    rmq_username = af_support_tools.get_config_file_property(config_file=env_file, heading='RabbitMQ',
                                                             property='username')
    global rmq_password
    rmq_password = af_support_tools.get_config_file_property(config_file=env_file, heading='RabbitMQ',
                                                             property='password')

    global ipaddress
    ipaddress = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='hostname')
    global cli_username
    cli_username = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS',
                                                             property='username')
    global cli_password
    cli_password = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS',
                                                             property='password')


    ensurePathExists(path)
    purgeOldOutput(path, "rest")

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

def deletePreviousDownloadFiles(filename, filepath):
    sendCommand = "find /opt/dell/cpsd -name downloads"
    dirStatus = af_support_tools.send_ssh_command(host=host, username=cli_username, password=cli_password,
                                                  command=sendCommand, return_output=True)

    print("Directory status A: %s" % dirStatus)
    if dirStatus is not "":
        dirStatus = dirStatus.rstrip() + "/"
        # dirStatus = (dirStatus + "/").rstrip()
    else:
        print("Downloads directory is missing.")
    print("Directory status B: %s" % dirStatus)

    if filepath in dirStatus:
        sendCommand = "rm -rf " + dirStatus + "*"
        print(sendCommand)
        fileDelete = af_support_tools.send_ssh_command(host=host, username=cli_username, password=cli_password,
                                                       command=sendCommand, return_output=True)
        sendCommand = 'find / -name "' + filename + '"'
        fileStatus = af_support_tools.send_ssh_command(host=host, username=cli_username, password=cli_password,
                                                       command=sendCommand, return_output=True)
        print("Current Status: %s" % fileStatus)
        assert filepath not in fileStatus, "File was not removed successfully."
    else:
        print(filename + "not found in the repo directory.")

def resetTestQueues():
    # messageReqHeader = {'__TypeId__': 'com.dell.cpsd.esrs.service.download.credentials.requested'}
    # messageResHeaderComplete = {'__TypeId__': 'com.dell.cpsd.prepositioning.downloader.file.download.completed'}
    # messageResHeaderProgress = {'__TypeId__': 'com.dell.cpsd.prepositioning.downloader.file.download.progress'}

    credentials = pika.PlainCredentials(rmq_username, rmq_password)
    parameters = pika.ConnectionParameters(host, port, '/', credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    af_support_tools.rmq_purge_queue(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username, queue='testDownloadFWRequest',
                                     ssl_enabled=False)
    af_support_tools.rmq_purge_queue(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                     queue='testDownloadFWResponse', ssl_enabled=False)
    af_support_tools.rmq_purge_queue(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                     queue='testCredentialsRequest', ssl_enabled=False)
    af_support_tools.rmq_purge_queue(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                     queue='testCredentialsResponse', ssl_enabled=False)

    time.sleep(0.5)
    print("Old test queues successfully purged.")

    af_support_tools.rmq_bind_queue(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                    queue='testDownloadFWRequest', exchange='exchange.dell.cpsd.prepositioning.downloader.request',
                                    routing_key='#', ssl_enabled=False)
    af_support_tools.rmq_bind_queue(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                    queue='testDownloadFWResponse',
                                    exchange='exchange.dell.cpsd.prepositioning.assetmanager.response',
                                    routing_key='#', ssl_enabled=False)
    af_support_tools.rmq_bind_queue(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                    queue='testCredentialsRequest', exchange='exchange.dell.cpsd.esrs.request',
                                    routing_key='#', ssl_enabled=False)
    af_support_tools.rmq_bind_queue(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                    queue='testCredentialsResponse', exchange='exchange.dell.cpsd.esrs.response',
                                    routing_key='#', ssl_enabled=False)
    print("New test queues successfully initialized.")

# filename, expectedDiskSize

def verifyRESTdownloadSingleFileRequest(filename):
    resetTestQueues()
    print("Queues reset.")
    deletePreviousDownloadFiles("100mbfiletest.zip",
                              "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader-service/repository/downloads/")

    #url = 'http://' + host + ':10000/rcm-fitness-paqx/rcm-fitness-api/api/download/firmware/'
    url = 'http://' + host + ':19080/rcm-fitness-api/api/download/firmware/'
    payload = {'fileName': filename}
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    resp = requests.post(url, data=json.dumps(payload), headers=headers)

    print("Returned status code: %d" % resp.status_code)
    data = json.loads(resp.text)
    assert resp.status_code == 200, "Request has not been acknowledged as expected."

    print(data)
    if data != "":
        assert data["state"] == "ACKNOWLEDGED", "Unexpected initial state returned."
        assert len(data["uuid"]) > 16, "No valid request UUID returned."
        assert data["uuid"] in data["link"]["href"], "Request UUID not found in returned HREF link."
        assert data["link"]["method"] == "GET", "Unexpected method returned in response."
        print("URL: %s" % data["link"]["href"])
        # assert "10000/rcm-fitness-paqx/rcm-fitness-api/api/download/firmware/status/" in data["link"]["href"], "No URL included in response to query subsequent progress."
        assert "19080/rcm-fitness-api/api/download/firmware/status/" in data["link"][
            "href"], "No URL included in response to query subsequent progress."
        assert data["link"]["rel"] == "download-status"
        print("Download request's initial response verified.")

        statusURL = data["link"]["href"]
        statusData = requests.get(statusURL)
        statusResp = json.loads(statusData.text)

        while statusResp["state"] != "COMPLETE":
            time.sleep(0.5)
            statusURL = data["link"]["href"]
            statusData = requests.get(statusURL)
            statusResp = json.loads(statusData.text)
            if statusResp["state"] == "FAILED":
                assert False, "Download request unexpectedly failed."
            print("Checking....")
        return
    assert False, ("Initial REST update request not complete.")

def verifyRESTdownloadInvalidFileRequest(filename):
    resetTestQueues()
    print("Queues reset.")
    deletePreviousDownloadFiles("100mbfiletest.zip",
                              "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader-service/repository/downloads/")

    #url = 'http://' + host + ':10000/rcm-fitness-paqx/rcm-fitness-api/api/download/firmware/'
    url = 'http://' + host + ':19080/rcm-fitness-api/api/download/firmware/'
    payload = {'fileName': filename}
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    resp = requests.post(url, data=json.dumps(payload), headers=headers)

    print("Returned status code: %d" % resp.status_code)
    data = json.loads(resp.text)
    assert resp.status_code == 200, "Request has not been acknowledged as expected."

    print(data)
    if data != "":
        assert data["state"] == "ACKNOWLEDGED", "Unexpected initial state returned."
        print("Download request's initial response verified.")

        statusURL = data["link"]["href"]
        statusData = requests.get(statusURL)
        statusResp = json.loads(statusData.text)

        while statusResp["state"] != "FAILED":
            time.sleep(0.5)
            statusURL = data["link"]["href"]
            statusData = requests.get(statusURL)
            statusResp = json.loads(statusData.text)
            print("Checking for failed status....")

        if statusResp["state"] == "FAILED":
            assert statusResp["error"] is not None, "Expected error message not included in response."
        return
    assert False, ("Initial REST update request not complete.")

def verifyRESTdownloadSingleFileRequestSTATUS(filename):
    resetTestQueues()
    print("Queues reset.")

    deletePreviousDownloadFiles("100mbfiletest.zip",
                              "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader-service/repository/downloads/")

    url = 'http://' + host + ':19080/rcm-fitness-api/api/download/firmware/'
    payload = {'fileName': filename}
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    resp = requests.post(url, data=json.dumps(payload), headers=headers)

    print("Returned status code: %d" % resp.status_code)
    data = json.loads(resp.text)
    assert resp.status_code == 200, "Request has not been acknowledged as expected."

    if data["state"] == "ACKNOWLEDGED":
        print("Request acknowleded, now query status using link provided.")
        assert "19080/rcm-fitness-api/api/download/firmware/status/" in data["link"]["href"], "No URL included in response to query subsequent progress."
        statusURL = data["link"]["href"]
        print(data)
        print("HREF URL: %s " % statusURL)
        assert data["link"]["rel"] == "download-status", "Unexpected REL value returned."
        assert data["link"]["method"] == "GET", "Unexpected method value returned."
        assert data["url"] is None, "Unexpected URL returned in ack."
        assert data["hashVal"] is None, "Unexpected hash returned in ack."
        assert data["downloadedSize"] is None, "Unexpected downloadedSize returned in ack."
        assert data["size"] is None, "Unexpected size returned in ack."
        assert data["error"] is None, "Unexpected error returned in ack."
        time.sleep(1)
        statusData = requests.get(statusURL)
        statusResp = json.loads(statusData.text)
        print(2.1)
        assert statusResp["state"] == "COMPLETE" or "IN_PROGRESS", "Unexpected initial state returned."
        assert len(statusResp["uuid"]) > 16, "No valid request UUID returned."
        assert statusResp["uuid"] in statusResp["link"]["href"], "Request UUID not found in returned HREF link."
        assert statusResp["link"]["method"] == "GET", "Unexpected method returned in response."
        print(2.2)
        assert "19080/rcm-fitness-api/api/download/firmware/status/" in statusResp["link"]["href"], "No URL included in response to query subsequent progress."
        assert statusResp["link"]["rel"] == "download-status", "Unexpected REL value returned."
        #assert filename in statusResp["url"], "Expected filename not included in returned URL."
        #assert len(statusResp["hashVal"]) > 32, "HashVal not the expected length."
        assert statusResp["downloadedSize"] != 0, "Unexpected download size returned."
        #assert statusResp["size"] != 0, "Unexpected file size returned."
        #assert statusResp["downloadedSize"] <= statusResp["size"], "Download size is reported as larger than expected size."
        assert statusResp["error"] is None, "Unexpected error returned."
        print("Download request's status response verified.")

    i = 0
    while statusResp["state"] != "COMPLETE":
        print(3)

        assert statusResp["state"] == "IN_PROGRESS" or "ACKNOWLEDGED", "Unexpected initial state returned."
        assert len(statusResp["uuid"]) > 16, "No valid request UUID returned."
        assert statusResp["uuid"] in statusResp["link"]["href"], "Request UUID not found in returned HREF link."
        assert statusResp["link"]["method"] == "GET", "Unexpected method returned in response."
        # assert "10000/rcm-fitness-paqx/rcm-fitness-api/api/download/firmware/status/" in statusResp["link"]["href"], "No URL included in response to query subsequent progress."
        assert "19080/rcm-fitness-api/api/download/firmware/status/" in statusResp["link"][
            "href"], "No URL included in response to query subsequent progress."
        assert statusResp["link"]["rel"] == "download-status"
        #assert filename in statusResp["url"], "Expected filename not included in returned URL."
        #assert len(statusResp["hashVal"]) > 32, "HashVal not the expected length."
        assert statusResp["downloadedSize"] != 0, "Unexpected download size returned."
        #assert statusResp["size"] != 0, "Unexpected file size returned."
        #assert statusResp["downloadedSize"] == statusResp["size"], "Download size is reported as larger than expected size."
        assert statusResp["error"] is None, "Unexpected error returned."

        time.sleep(0.5)
        statusURL = statusResp["link"]["href"]
        #statusResp = requests.get(statusURL)
        statusData = requests.get(statusURL)
        statusResp = json.loads(statusData.text)
        print("Download request's progress response verified.")

        if statusResp["state"] == "IN_PROGRESS":
            i += 1
            print("In here... Loop: %d" % i)
            time.sleep(0.5)
            statusURL = statusResp["link"]["href"]
            # statusResp = requests.get(statusURL)
            statusData = requests.get(statusURL)
            statusResp = json.loads(statusData.text)
            print("Progressing...")
            continue



    if statusResp["state"] == "COMPLETE":
        print(4)
        assert statusResp["state"] == "COMPLETE", "Unexpected initial state returned."
        assert len(statusResp["uuid"]) > 16, "No valid request UUID returned."
        assert statusResp["uuid"] in statusResp["link"]["href"], "Request UUID not found in returned HREF link."
        assert statusResp["link"]["method"] == "GET", "Unexpected method returned in response."
        # assert "10000/rcm-fitness-paqx/rcm-fitness-api/api/download/firmware/status/" in statusResp["link"]["href"], "No URL included in response to query subsequent progress."
        assert "19080/rcm-fitness-api/api/download/firmware/status/" in statusResp["link"][
            "href"], "No URL included in response to query subsequent progress."
        assert statusResp["link"]["rel"] == "download-status"
        assert filename in statusResp["url"], "Expected filename not included in returned URL."
        assert len(statusResp["hashVal"]) > 32, "HashVal not the expected length."
        assert statusResp["downloadedSize"] != 0, "Unexpected download size returned."
        assert statusResp["size"] != 0, "Unexpected file size returned."
        assert statusResp["downloadedSize"] == statusResp["size"], "Download size is reported as larger than expected size."
        assert statusResp["error"] is None, "Unexpected error returned."
        print("Download request's complete response verified.")
        return

    if statusResp["state"] != "COMPLETE":
        if statusResp["state"] != "IN_PROGRESS":
            print(statusResp["state"])
            assert False, "Invalid status reported."
            #return
    assert False, "Initial REST update request not complete."

def verifyRESTdownloadMultiFileRequest(filename, secFilename, thirdFilename):
    resetTestQueues()
    print("Queues reset.")
    deletePreviousDownloadFiles("100mbfiletest.zip",
                              "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader-service/repository/downloads/")

    #url = 'http://' + host + ':10000/rcm-fitness-paqx/rcm-fitness-api/api/download/firmware/'
    url = 'http://' + host + ':19080/rcm-fitness-api/api/download/firmware/'
    payload = {'fileName': filename}
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    resp = requests.post(url, data=json.dumps(payload), headers=headers)

    print("Returned status code: %d" % resp.status_code)
    data = json.loads(resp.text)
    assert resp.status_code == 200, "Request has not been acknowledged as expected."

    #url = 'http://' + host + ':10000/rcm-fitness-paqx/rcm-fitness-api/api/download/firmware/'
    url = 'http://' + host + ':19080/rcm-fitness-api/api/download/firmware/'
    payload = {'fileName': secFilename}
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    resp = requests.post(url, data=json.dumps(payload), headers=headers)
    secdata = json.loads(resp.text)
    assert resp.status_code == 200, "Request has not been acknowledged as expected."

    #url = 'http://' + host + ':10000/rcm-fitness-paqx/rcm-fitness-api/api/download/firmware/'
    url = 'http://' + host + ':19080/rcm-fitness-api/api/download/firmware/'
    payload = {'fileName': thirdFilename}
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    resp = requests.post(url, data=json.dumps(payload), headers=headers)
    thirddata = json.loads(resp.text)
    assert resp.status_code == 200, "Request has not been acknowledged as expected."

    print(data)
    if data != "":
        if secdata != "":
            if thirddata != "":
                assert data["state"] == "ACKNOWLEDGED", "Unexpected initial state returned."
                # assert "10000/rcm-fitness-paqx/rcm-fitness-api/api/download/firmware/status/" in data["link"]["href"], "No URL included in response to query subsequent progress."
                assert "19080/rcm-fitness-api/api/download/firmware/status/" in data["link"][
                    "href"], "No URL included in response to query subsequent progress."
                assert secdata["state"] == "ACKNOWLEDGED", "Unexpected initial state returned."
                # assert "10000/rcm-fitness-paqx/rcm-fitness-api/api/download/firmware/status/" in data["link"]["href"], "No URL included in response to query subsequent progress."
                assert "19080/rcm-fitness-api/api/download/firmware/status/" in secdata["link"][
                    "href"], "No URL included in response to query subsequent progress."
                assert thirddata["state"] == "ACKNOWLEDGED", "Unexpected initial state returned."
                # assert "10000/rcm-fitness-paqx/rcm-fitness-api/api/download/firmware/status/" in data["link"]["href"], "No URL included in response to query subsequent progress."
                assert "19080/rcm-fitness-api/api/download/firmware/status/" in thirddata["link"][
                    "href"], "No URL included in response to query subsequent progress."
                print("Download request's initial response verified.")

                statusURL = data["link"]["href"]
                secstatusURL = secdata["link"]["href"]
                thirdstatusURL = thirddata["link"]["href"]
                statusData = requests.get(statusURL)
                secstatusData = requests.get(secstatusURL)
                thirdstatusData = requests.get(thirdstatusURL)
                statusResp = json.loads(statusData.text)
                secstatusResp = json.loads(secstatusData.text)
                thirdstatusResp = json.loads(thirdstatusData.text)

                print(statusResp["state"])
                print(secstatusResp["state"])
                print(thirdstatusResp["state"])

                while statusResp["state"] != "COMPLETE":
                    print("Checking 1st file....")
                    time.sleep(0.5)
                    statusURL = data["link"]["href"]
                    statusData = requests.get(statusURL)
                    statusResp = json.loads(statusData.text)

                while secstatusResp["state"] != "COMPLETE":
                    print("Checking 2nd file....")
                    time.sleep(0.5)
                    secstatusURL = secdata["link"]["href"]
                    secstatusData = requests.get(secstatusURL)
                    secstatusResp = json.loads(secstatusData.text)

                while thirdstatusResp["state"] != "COMPLETE":
                    print("Checking 3rd file....")
                    time.sleep(0.5)
                    thirdstatusURL = thirddata["link"]["href"]
                    thirdstatusData = requests.get(thirdstatusURL)
                    thirdstatusResp = json.loads(thirdstatusData.text)

                return
    assert False, ("Initial REST update request not complete.")

def verifyRESTrepositoryStatus(filepath, filename):
    url = 'http://' + host + ':8888/downloads/' + filepath
    repoStatus = requests.get(url)
    print(repoStatus.content)
    assert repoStatus.status_code == 200, "Request has not been acknowledged as expected."

    content = repoStatus.content.decode('utf-8')

    if repoStatus.content != "":
        assert filepath in content, "Response does not include file path."
        assert filename in content, "Response does not include file name."
        # print("Done")
        return
    assert False, "Failing....."

@pytest.mark.daily_status
@pytest.mark.rcm_fitness_mvp_extended
@pytest.mark.rcm_fitness_mvp
def test_verifyRESTdownloadSingleFileRequest1():
    verifyRESTdownloadSingleFileRequest("RCM/3.2.1/VxRack_1000_FLEX/Component/Controller_Firmware/SAS-RAID_Firmware_VH28K_WN64_25.4.0.0017_A06.EXE")

@pytest.mark.daily_status
@pytest.mark.rcm_fitness_mvp_extended
@pytest.mark.rcm_fitness_mvp
def test_verifyRESTdownloadSingleFileRequestSTATUS1():
    verifyRESTdownloadSingleFileRequestSTATUS("RCM/3.2.1/VxRack_1000_FLEX/Component/Controller_Firmware/SAS-RAID_Firmware_VH28K_WN64_25.4.0.0017_A06.EXE")

@pytest.mark.daily_status
@pytest.mark.rcm_fitness_mvp_extended
def test_verifyRESTrepositoryStatus1():
    verifyRESTrepositoryStatus("RCM/3.2.1/VxRack_1000_FLEX/Component/Controller_Firmware/", "SAS-RAID_Firmware_VH28K_WN64_25.4.0.0017_A06.EXE")


@pytest.mark.rcm_fitness_mvp_extended
def test_verifyRESTdownloadSingleFileRequest2():
    verifyRESTdownloadSingleFileRequest("100mbfiletest.zip")

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyRESTdownloadSingleFileRequestSTATUS2():
    verifyRESTdownloadSingleFileRequestSTATUS("100mbfiletest.zip")

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyRESTrepositoryStatus2():
    verifyRESTrepositoryStatus("", "100mbfiletest.zip")


# @pytest.mark.rcm_fitness_mvp
# def test_verifyRESTdownloadInvalidFileRequest3():
#     verifyRESTdownloadInvalidFileRequest("RCM/3.2.1/SAS-RAID_Firmware_VH28K_WN64_25.4.0.0017_A06.EXE")


# @pytest.mark.rcm_fitness_mvp
# def test_verifyRESTdownloadInvalidFileRequest4():
#     verifyRESTdownloadInvalidFileRequest("////")

# @pytest.mark.rcm_fitness_mvp
# def test_verifyRESTdownloadInvalidFileRequest5():
#     verifyRESTdownloadInvalidFileRequest("")
#

@pytest.mark.rcm_fitness_mvp_extended
@pytest.mark.rcm_fitness_mvp
def test_verifyRESTdownloadMultiFileRequest6():
    verifyRESTdownloadMultiFileRequest("RCM/3.2.1/VxRack_1000_FLEX/Component/Controller_Firmware/SAS-RAID_Firmware_VH28K_WN64_25.4.0.0017_A06.EXE", "100mbfiletest.zip", "RCM/3.2.2/VxRack_1000_FLEX/Component/BIOS/2.2.5/BIOS_PFWCY_WN64_2.2.5.EXE")

@pytest.mark.rcm_fitness_mvp_extended
@pytest.mark.rcm_fitness_mvp
def test_verifyRESTrepositoryStatus6():
    verifyRESTrepositoryStatus("RCM/3.2.1/VxRack_1000_FLEX/Component/Controller_Firmware/", "SAS-RAID_Firmware_VH28K_WN64_25.4.0.0017_A06.EXE")

@pytest.mark.rcm_fitness_mvp_extended
@pytest.mark.rcm_fitness_mvp
def test_verifyRESTrepositoryStatus6a():
    verifyRESTrepositoryStatus("", "100mbfiletest.zip")

@pytest.mark.rcm_fitness_mvp_extended
@pytest.mark.rcm_fitness_mvp
def test_verifyRESTrepositoryStatus6b():
    verifyRESTrepositoryStatus("RCM/3.2.2/VxRack_1000_FLEX/Component/BIOS/2.2.5/", "BIOS_PFWCY_WN64_2.2.5.EXE")

# @pytest.mark.rcm_fitness_mvp_extended
# @pytest.mark.rcm_fitness_mvp
# def test_verifyRESTdownloadSingleFileRequest7():
#     verifyRESTdownloadSingleFileRequest("RCM/3.2.1/VxRack_1000_FLEX/Component/Controller_Firmware/SAS-RAID_Firmware_VH28K_WN64_25.4.0.0017_A06.EXE")
