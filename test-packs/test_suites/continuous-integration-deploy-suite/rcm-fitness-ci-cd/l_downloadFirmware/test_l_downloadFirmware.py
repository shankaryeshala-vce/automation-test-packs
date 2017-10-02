#!/usr/bin/python
# Copyright © 2017 Dell Inc. or its subsidiaries.  All Rights Reserved
import pika
import json
import time
import af_support_tools
import pytest
import os
import re
import datetime
import string


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

    # Set Vars
    global payload_file
    payload_file = 'continuous-integration-deploy-suite/downloadInputs.ini'
    global payload_header
    payload_header = 'payload'
    global payload_message
    payload_message = 'first_download'
    global payload_messageSec
    payload_messageSec = 'second_download'
    global payload_messageThird
    payload_messageThird = 'third_download'
    global payload_bios1
    payload_bios1 = 'bios_download1'
    global payload_bios2
    payload_bios2 = 'bios_download2'
    global payload_sas1
    payload_sas1 = 'sas_download1'
    global payload_sas2
    payload_sas2 = 'sas_download2'
    global payload_esxi1
    payload_esxi1 = 'esxi_download1'
    global payload_esxi2
    payload_esxi2 = 'esxi_download2'
    global payload_messageInvalidFile
    payload_messageInvalidFile = 'invalid_file'
    global payload_messageInvalidReplyTo
    payload_messageInvalidReplyTo = 'invalid_replyto'
    global payload_messageInvalidSwid
    payload_messageInvalidSwid = 'invalid_swid'
    global payload_messageInvalidAll
    payload_messageInvalidAll = 'invalid_all'
    global payload_messageNoFile
    payload_messageNoFile = 'no_file'
    global payload_messageNoReplyTo
    payload_messageNoReplyTo = 'no_replyto'
    global payload_messageNoSwid
    payload_messageNoSwid = 'no_swid'
    global payload_messageNoAll
    payload_messageNoAll = 'no_all'

    global ipaddress
    ipaddress = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='hostname')
    global cli_username
    cli_username = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS',
                                                             property='username')
    global cli_password
    cli_password = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS',
                                                             property='password')

    ensurePathExists(path)
    purgeOldOutput(path, "loadFW")
    purgeOldOutput(path, "downloadAll")
    purgeOldOutput(path, "invalid")
    purgeOldOutput(path, "no")

    global message
    message = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header, property=payload_message)
    global messageSec
    messageSec = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                           property=payload_messageSec)
    global messageThird
    messageThird = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                             property=payload_messageThird)
    global messageBios1
    messageBios1 = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                             property=payload_bios1)
    global messageSas1
    messageSas1 = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                             property=payload_sas1)
    global messageEsxi1
    messageEsxi1 = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                             property=payload_esxi1)
    global messageBios2
    messageBios2 = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                             property=payload_bios2)
    global messageSas2
    messageSas2 = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                             property=payload_sas2)
    global messageEsxi2
    messageEsxi2 = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                             property=payload_esxi2)
    global messageInvalidFile
    messageInvalidFile = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                               property=payload_messageInvalidFile)
    global messageInvalidReplyTo
    messageInvalidReplyTo = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                               property=payload_messageInvalidReplyTo)
    global messageInvalidSwid
    messageInvalidSwid = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                               property=payload_messageInvalidSwid)
    global messageInvalidAll
    messageInvalidAll = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                               property=payload_messageInvalidAll)
    global messageNoFile
    messageNoFile = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                               property=payload_messageNoFile)
    global messageNoReplyTo
    messageNoReplyTo = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                               property=payload_messageNoReplyTo)
    global messageNoSwid
    messageNoSwid = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                               property=payload_messageNoSwid)
    global messageNoAll
    messageNoAll = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                               property=payload_messageNoAll)


def ensurePathExists(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)


def purgeOldOutput(dir, pattern):
    for f in os.listdir(dir):
        if re.search(pattern, f) and f.endswith(".json"):
            os.remove(os.path.join(dir, f))
            print("Old output files successfully deleted.")
        elif f.endswith(".txt"):
            os.remove(os.path.join(dir, f))
        else:
            print('Unable to locate output files to remove.')


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
def downloadFWFileRequest(payLoad, requestFile, requestCredentials, responseFileComplete, filename, expectedDiskSize):
    messageReqHeader = {'__TypeId__': 'com.dell.cpsd.prepositioning.downloader.file.download.request'}
    messageResHeaderComplete = {'__TypeId__': 'com.dell.cpsd.prepositioning.downloader.file.download.completed'}
    messageResHeaderProgress = {'__TypeId__': 'com.dell.cpsd.prepositioning.downloader.file.download.progress'}

    credentials = pika.PlainCredentials(rmq_username, rmq_password)
    parameters = pika.ConnectionParameters(host, port, '/', credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    resetTestQueues()
    print("Queues reset.")

    time.sleep(2)
    deletePreviousDownloadFiles("BIOS_PFWCY_WN64_2.2.5.EXE",
                              "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader-service/repository/downloads/")
    print("Previous downloads deleted.")
    time.sleep(2)

    af_support_tools.rmq_publish_message(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                         exchange="exchange.dell.cpsd.prepositioning.downloader.request",
                                         routing_key="dell.cpsd.prepositioning.downloader.request",
                                         headers=messageReqHeader, payload=payLoad, payload_type='json',
                                         ssl_enabled=False)

    print("Download request published.")

    time.sleep(2)
    q_len = 0
    timeout = 0

    while q_len < 1:
        time.sleep(1)
        timeout += 1

        q_len = af_support_tools.rmq_message_count(host=host, port=port,
                                                           rmq_username=rmq_username, rmq_password=rmq_username,
                                                           queue='testCredentialsResponse', ssl_enabled=False)

        # If the test queue doesn't get a message them something is wrong. Time out needs to be high as msg can take 3+ minutes
        if timeout > 60:
            print("ERROR: ESRS Credential response took too long to return.")
            break

    my_request_body = af_support_tools.rmq_consume_message(host=host, port=port,
                                                           rmq_username=rmq_username, rmq_password=rmq_username,
                                                           queue='testDownloadFWRequest',
                                                           ssl_enabled=False)
    af_support_tools.rmq_payload_to_file(my_request_body, path + requestFile)
    time.sleep(2)
    my_response_credentials_body = af_support_tools.rmq_consume_all_messages(host=host, port=port, rmq_username=rmq_username,
                                                                        rmq_password=rmq_username,
                                                                        queue='testCredentialsResponse',
                                                                        ssl_enabled=False)
    af_support_tools.rmq_payload_to_file(my_response_credentials_body, path + requestCredentials)

    print("Download request and credential response(s) consumed.")
    # time.sleep(delay)
    checkDisk = checkWritesComplete(filename, "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader-service/repository/downloads/")
    print(checkDisk)
    # assert False
    while checkDisk < expectedDiskSize:
        timeout += 1
        time.sleep(1)
        checkDisk = checkWritesComplete(filename, "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader-service/repository/downloads/")
        print(checkDisk)
        if timeout > 1000:
            assert False, "Download failed to complete in a timely manner"


    my_response_download_body = af_support_tools.rmq_consume_all_messages(host=host, port=port,
                                                                          rmq_username=rmq_username,
                                                                          rmq_password=rmq_username,
                                                                          queue='testDownloadFWResponse',
                                                                          ssl_enabled=False)
    af_support_tools.rmq_payload_to_file(my_response_download_body, path + responseFileComplete)

    print("Download response consumed.")

    # time.sleep(1)
    # assert False

def downloadFWFileMulti(payLoad, secPayLoad, thirdPayLoad, requestFile, requestCredentials, responseFileComplete, filename, expectedDiskSize, filename2, expectedDiskSize2):
    q_len = 0
    timeout = 0
    resetTestQueues()
    messageReqHeader = {'__TypeId__': 'com.dell.cpsd.prepositioning.downloader.file.download.request'}
    print("Queues reset.")

    deletePreviousDownloadFiles("BIOS_PFWCY_WN64_2.2.5.EXE",
                                "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader-service/repository/downloads/")

    print("Previous downloads deleted.")

    af_support_tools.rmq_publish_message(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                         exchange="exchange.dell.cpsd.prepositioning.downloader.request",
                                         routing_key="dell.cpsd.prepositioning.downloader.request",
                                         headers=messageReqHeader, payload=payLoad, payload_type='json',
                                         ssl_enabled=False)
    af_support_tools.rmq_publish_message(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                         exchange="exchange.dell.cpsd.prepositioning.downloader.request",
                                         routing_key="dell.cpsd.prepositioning.downloader.request",
                                         headers=messageReqHeader, payload=secPayLoad, payload_type='json',
                                         ssl_enabled=False)
    af_support_tools.rmq_publish_message(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                         exchange="exchange.dell.cpsd.prepositioning.downloader.request",
                                         routing_key="dell.cpsd.prepositioning.downloader.request",
                                         headers=messageReqHeader, payload=thirdPayLoad, payload_type='json',
                                         ssl_enabled=False)

    print("Three file download requests published.")

    checkDisk = checkWritesComplete(filename, "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader-service/repository/downloads/")
    print(checkDisk)
    while checkDisk < expectedDiskSize:
        timeout += 1
        time.sleep(1)
        print("File 1")
        checkDisk = checkWritesComplete(filename, "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader-service/repository/downloads/")
        print(checkDisk)
        if timeout > 1000:
            assert False, "ERROR: Download attempt doesn't appear to have completed in a timely manner."

    checkDisk2 = checkWritesComplete(filename2, "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader-service/repository/downloads/")
    print(checkDisk2)
    while checkDisk2 < expectedDiskSize2:
        timeout += 1
        time.sleep(5)
        print("File 2")
        checkDisk2 = checkWritesComplete(filename2, "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader-service/repository/downloads/")
        print(checkDisk2)
        if timeout > 1000:
            assert False, "ERROR: Download attempt doesn't appear to have completed in a timely manner."

    while q_len < 3:
        time.sleep(1)
        timeout += 1

        q_len = af_support_tools.rmq_message_count(host=host, port=port,
                                                           rmq_username=rmq_username, rmq_password=rmq_username,
                                                           queue='testCredentialsResponse', ssl_enabled=False)

        # If the test queue doesn't get a message them something is wrong. Time out needs to be high as msg can take 3+ minutes
        if timeout > 60:
            print("ERROR: ESRS Credential response took too long to return.")
            break

    my_request_body = af_support_tools.rmq_consume_all_messages(host=host, port=port,
                                                           rmq_username=rmq_username, rmq_password=rmq_username,
                                                           queue='testDownloadFWRequest',
                                                           ssl_enabled=False)
    af_support_tools.rmq_payload_to_file(my_request_body, path + requestFile)
    my_response_credentials_body = af_support_tools.rmq_consume_all_messages(host=host, port=port, rmq_username=rmq_username,
                                                                        rmq_password=rmq_username,
                                                                        queue='testCredentialsResponse',
                                                                        ssl_enabled=False)
    af_support_tools.rmq_payload_to_file(my_response_credentials_body, path + requestCredentials)

    print("Download request and credential response(s) consumed.")
    my_response_download_body = af_support_tools.rmq_consume_all_messages(host=host, port=port,
                                                                          rmq_username=rmq_username,
                                                                          rmq_password=rmq_username,
                                                                          queue='testDownloadFWResponse',
                                                                          ssl_enabled=False)
    af_support_tools.rmq_payload_to_file(my_response_download_body, path + responseFileComplete)

    print("Download response consumed.")

def downloadFWFileRequestInvalid(payLoad, requestFile, requestCredentials, responseFileComplete):
    messageReqHeader = {'__TypeId__': 'com.dell.cpsd.prepositioning.downloader.file.download.request'}
    resetTestQueues()
    print("Queues reset.")
    time.sleep(2)
    deletePreviousDownloadFiles("BIOS_PFWCY_WN64_2.2.5.EXE",
                                "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader-service/repository/downloads/")

    print("Previous downloads deleted.")

    # af_support_tools.rmq_publish_message(host=host, port=port, rmq_username=uname, rmq_password=password,
    #                                      exchange="exchange.dell.cpsd.esrs.request",
    #                                      routing_key="dell.cpsd.esrs.download.request",
    #                                      headers=messageReqHeader, payload=payLoad, ssl_enabled=False)

    af_support_tools.rmq_publish_message(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                         exchange="exchange.dell.cpsd.prepositioning.downloader.request",
                                         routing_key="dell.cpsd.prepositioning.downloader.request",
                                         headers=messageReqHeader, payload=payLoad, payload_type='json',
                                         ssl_enabled=False)
    print("Download request with invalid properties published.")
    time.sleep(2)
    q_len = 0
    timeout = 0

    while q_len < 1:
        time.sleep(1)
        timeout += 1

        q_len = af_support_tools.rmq_message_count(host=host, port=port,
                                                           rmq_username=rmq_username, rmq_password=rmq_username,
                                                           queue='testCredentialsResponse', ssl_enabled=False)

        # If the test queue doesn't get a message them something is wrong. Time out needs to be high as msg can take 3+ minutes
        if timeout > 60:
            print("ERROR: ESRS Credential response took too long to return.")
            break

    my_request_body = af_support_tools.rmq_consume_message(host=host, port=port,
                                                           rmq_username=rmq_username, rmq_password=rmq_username,
                                                           queue='testDownloadFWRequest', ssl_enabled=False)
    af_support_tools.rmq_payload_to_file(my_request_body, path + requestFile)


    my_response_credentials_body = af_support_tools.rmq_consume_message(host=host, port=port,
                                                                        rmq_username=rmq_username,
                                                                        rmq_password=rmq_username,
                                                                        queue='testCredentialsResponse',
                                                                        ssl_enabled=False)
    af_support_tools.rmq_payload_to_file(my_response_credentials_body, path + requestCredentials)
    print("Download request and credential response consumed.")

    time.sleep(2)
    my_response_download_body = af_support_tools.rmq_consume_all_messages(host=host, port=port,
                                                                     rmq_username=rmq_username,
                                                                     rmq_password=rmq_username,
                                                                     queue='testDownloadFWResponse', ssl_enabled=False)
    af_support_tools.rmq_payload_to_file(my_response_download_body, path + responseFileComplete)
    print("All download responses consumed.")
    time.sleep(1)

def verifyPublishedAttributes(filename):
    countInstances = 0
    with open(filename, "rU") as dataFile:
        dataInput = json.load(dataFile)

    print(dataInput.keys())
    print("\nName of file: %s" % dataFile.name)

    if len(dataInput["messageProperties"]) > 0:
        assert "timestamp" in dataInput["messageProperties"], "Timestamp not included in published attributes."
        assert "correlationId" in dataInput["messageProperties"], "Correlation Id not included in published attributes."
        assert "replyTo" in dataInput["messageProperties"], "Reply To not included in published attributes."
        # assert "swid" in dataInput.keys(), "Swid not included in published attributes."
        # assert "url" in dataInput.keys(), "URL not included in published attributes."
        assert "fileName" in dataInput.keys(), "fileName not included in published attributes."
        return

    assert False, ("Unable to verify published attributes.")

def verifyMultiPublishedAttributes(filename):
    count = 0
    with open(filename, "rU") as dataFile:
        dataInput = json.load(dataFile)

    print(dataInput[count].keys())
    print("\nName of file: %s" % dataFile.name)

    assert len(dataInput) == 3, "Expected to find three published messages."
    if len(dataInput) > 0:
        while count < len(dataInput):
            assert "timestamp" in dataInput[count][
                "messageProperties"], "Timestamp not included in published attributes."
            assert "correlationId" in dataInput[count][
                "messageProperties"], "Correlation Id not included in published attributes."
            assert "replyTo" in dataInput[count]["messageProperties"], "Reply To not included in published attributes."
            assert "fileName" in dataInput[count].keys(), "fileName not included in published attributes."
            assert dataInput[count]["messageProperties"]["replyTo"] == "dell.cpsd.prepositioning.downloader.completed"
            count += 1
            return

    assert False, "Unable to verify published attributes."

def verifyConsumedAttributes(filename, requestFile, credentialsFile, responseFile, hashType, family, esrsURL):
    numRCMs = 0
    maxInput = 0
    count = 0
    credCount = 0
    hashVal = []
    listDataInput = []
    filepath = "file:///opt/dell/cpsd/rcm-fitness/prepositioning-downloader-service/repository/downloads"
    requestData = open(requestFile, "rU")
    dataInput = json.load(requestData)
    listDataInput.append(dataInput)
    maxInput = len(listDataInput)
    print("Count: %d" % maxInput)
    print(listDataInput)

    credentialsData = open(credentialsFile, "rU")
    dataCredentials = json.load(credentialsData)

    dataFile = open(responseFile, "rU")
    data = json.load(dataFile)
    # print(data)
    print("\nName of file: %s" % dataFile.name)

    size = checkFileSize(filename, "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader-service/repository/downloads/")
    hash = checkFileHash(filename, "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader-service/repository/downloads/")
    # sizeMD5 = checkFileSize("VMW-ESX-6.0.0-lsi_mr3-6.903.85.00_MR-3818071.zip.md5",
    #                          "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader-service/repository/downloads/")
    # sizeRAID = checkFileSize("VMW-ESX-6.0.0-lsi_mr3-6.903.85.00_MR-3818071.zip",
    #                          "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader-service/repository/downloads/")

    maxCount = len(data)
    maxCreds = len(dataCredentials)
    print("Total messages consumed: %d" % maxCount)
    while count < maxCount:

        if ("errorCode") in data[count].keys():
            print(data[count]["errorCode"])
            if ("errorMessage") in data[count].keys():
                print(data[count]["errorMessage"])
                assert (data[count]["errorCode"][:-2]) in (
                    data[count]["errorMessage"]), "Returned Error Code not included in Error Message."
                assert ('orrelation') or ('uid') in (
                    data[count]["errorMessage"]), "Returned Error Message does not reflect missing correlation ID."

        for i in range(maxCount):
            if ("url") in data[i].keys() and data[i]["fileName"].endswith(filename):
                x = 0
                print("Count: %d" % i)
                print("HERE NOW")
                assert "timestamp" in data[i]["messageProperties"], "Timestamp not included in consumed attributes."
                assert "correlationId" in data[i][
                    "messageProperties"], "Correlation Id not included in consumed attributes."
                assert "replyTo" in data[i]["messageProperties"], "Reply To not included in consumed attributes."
                assert "hashType" in data[i].keys(), "Hash Type not included in consumed attributes."
                assert "hashVal" in data[i].keys(), "Hash not included in consumed attributes."
                assert "fileName" in data[i].keys(), "Swid not included in consumed attributes."
                assert "size" in data[i].keys(), "Size not included in consumed attributes."
                assert "fileUUID" in data[i].keys(), "File UUID not included in consumed attributes."
                #assert filepath in data[i]["url"], "Download complete does not include expected URL."

                # assert data["swid"] == dataCredentials["swid"], "Swids don't match in consumed messages."
                # assert data[maxCount-1]["size"] == sizeNIC or sizeBIOS or sizeRAID, "Size not consistent with expected value."
                assert data[i]["size"] == size, "Size not consistent with expected value."
                print("Message count: %d" % maxInput)
                print(listDataInput)
                while x < maxInput:
                    if maxInput > 1:
                        print(dataInput[x]["messageProperties"]["correlationId"])
                        print(data[i]["messageProperties"]["correlationId"])
                        if dataInput[x]["messageProperties"]["correlationId"] in data[i]["messageProperties"]["correlationId"]:
                            assert dataInput[x]["messageProperties"]["correlationId"] in data[i]["messageProperties"][
                                "correlationId"], "Corr Ids don't match in consumed messages."
                            assert dataInput[x]["messageProperties"]["replyTo"] == data[i]["messageProperties"][
                                "replyTo"], "Reply To values don't match in consumed messages."
                            print("Multiple Input verified.")
                        x += 1
                    else:
                        print(dataInput["messageProperties"]["correlationId"])
                        print(data[i]["messageProperties"]["correlationId"])
                        if dataInput["messageProperties"]["correlationId"] in data[i]["messageProperties"]["correlationId"]:
                            assert dataInput["messageProperties"]["correlationId"] in data[i]["messageProperties"][
                                "correlationId"], "Corr Ids don't match in consumed messages."
                            assert dataInput["messageProperties"]["replyTo"] == data[i]["messageProperties"][
                                "replyTo"], "Reply To values don't match in consumed messages."
                            print("Single Input verified.")
                        x += 1

                assert data[i]["hashType"] == hashType, "Incorrect hashType detailed."

                hashVal.append(data[i]["hashVal"])
                while credCount < maxCreds:
                    if data[i]["size"] == dataCredentials[credCount]["size"]:
                        if data[i]["fileUUID"] == dataCredentials[credCount]["fileUUID"]:
                            print(data[i]["size"])
                            print(dataCredentials[credCount]["size"])
                            # assert filepath in data[i]["url"], "Unexpected URL returned."
                            assert data[i]["fileName"] in data[i]["url"], "Unexpected URL returned."
                            assert data[i]["hashVal"] == hash, "Unexpected HASH found."
                            assert data[i]["fileUUID"] == dataCredentials[credCount]["fileUUID"], "FileUUIDs don't match in consumed messages."
                            print("Looking good...")
                    credCount += 1

            else:
                print("Consumed download response message not a Complete.")

        for cred in range(maxCreds):
            print("Cred count: %d" % cred)
            print("Total creds: %d" % maxCreds)
            if dataCredentials[cred]["fileFound"] == True:
                print("You are in....")
                if ("url") in dataCredentials[cred].keys() and dataCredentials[cred]["fileName"].endswith(filename):
                    x = 0
                    print("Even deeper now.....")

                    assert dataCredentials[cred]["swid"] in dataCredentials[cred]["url"], "Swid not included in Credential response URL."
                    assert dataCredentials[cred]["size"] == size, "Size not consistent with expected value."
                    while x < maxInput:
                        if maxInput > 1:
                            if dataInput[x]["messageProperties"]["correlationId"] in dataCredentials[cred]["messageProperties"]["correlationId"]:
                                if dataInput[x]["fileName"] in dataCredentials[cred]["fileName"]:
                                    assert dataInput[x]["messageProperties"]["replyTo"] == dataCredentials[cred]["messageProperties"][
                                        "origin"], "Reply To values don't match in consumed messages."
                                    assert dataCredentials[cred]["messageProperties"]["replyTo"] == "no-reply", "Unexpected replyTo returned in credential response"
                            x += 1
                        else:
                            if dataInput["messageProperties"]["correlationId"] in dataCredentials[cred]["messageProperties"]["correlationId"]:
                                if dataInput["fileName"] in dataCredentials[cred]["fileName"]:
                                    assert dataInput["messageProperties"]["replyTo"] == dataCredentials[cred]["messageProperties"][
                                        "origin"], "Reply To values don't match in consumed messages."
                                    assert dataCredentials[cred]["messageProperties"][
                                               "replyTo"] == "no-reply", "Unexpected replyTo returned in credential response"
                            x += 1

                    assert dataCredentials[cred]["hashType"] == hashType, "Incorrect hashType detailed."
                    assert dataCredentials[cred]["size"] == size, "Size not consistent with expected value."
                    assert esrsURL in dataCredentials[cred]["url"], "Host and port details incorrect in returned URL"
                    assert dataCredentials[cred]["swid"] in dataCredentials[cred]["header"][
                        "authorization"], "Swid not included in Credential response URL authorization details."
                    assert family in dataCredentials[cred]["header"][
                        "authorization"], "Swid not included in Credential response URL authorization details."
                    # assert dataCredentials["header"][
                    #            "productFamily"] == family, "Product Family not included in Credential response URL authorization details."
                    assert dataCredentials[cred]["header"]["serialNumber"] == dataCredentials[cred][
                        "swid"], "Serial number not match Swid in Credential response URL authorization details."

                    assert dataCredentials[cred]["hashVal"] == hash, "Hash values do not match."
                    print("Excellent")
                    return

        count += 1


    assert False, "Consumed response messages not complete."

def verifyMultiConsumedAttributes(requestFile, credentialsFile, responseFile, hashType, family, esrsURL):
    count = 0

    filepath = "file:///opt/dell/cpsd/rcm-fitness/prepositioning-downloader-service/repository/downloads"
    requestData = open(requestFile, "rU")
    dataInput = json.load(requestData)

    credentialsData = open(credentialsFile, "rU")
    dataCredentials = json.load(credentialsData)

    dataFile = open(responseFile, "rU")
    data = json.load(dataFile)
    print(data)
    print("\nName of file: %s" % dataFile.name)
    print("Request count: %d" % len(dataInput))
    print("Credential count: %d" % len(dataCredentials))
    print("Response count: %d" % len(data))

    sizeBIOS = checkFileSize("RCM/3.2.2/VxRack_1000_FLEX/Component/BIOS/2.2.5/BIOS_PFWCY_WN64_2.2.5.EXE",
                             "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader-service/repository/downloads/")
    sizeDAS = checkFileSize("DAS_Cache_Linux_1.zip",
                            "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader-service/repository/downloads/")
    sizeESX = checkFileSize("VMW-ESX-6.0.0-lsi_mr3-6.903.85.00_MR-3818071.zip",
                             "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader-service/repository/downloads/")


    print("Total messages consumed: %d" % len(data))

    while count < len(data):
        if "errorCode" in data[count].keys():
            print(data[count]["errorCode"])
            if ("errorMessage") in data[count].keys():
                print(data[count]["errorMessage"])
                assert (data[count]["errorCode"][:-2]) in (
                    data[count]["errorMessage"]), "Returned Error Code not included in Error Message."
                assert ('orrelation') or ('uid') in (
                    data[count]["errorMessage"]), "Returned Error Message does not reflect missing correlation ID."
                print("0.1")
        print("Count: %d" % count)
        print(data[count].keys())
        if "url" in data[count].keys():
            print("HERE NOW")
            assert "timestamp" in data[count]["messageProperties"], "Timestamp not included in consumed attributes."
            assert "correlationId" in data[count][
                "messageProperties"], "Correlation Id not included in consumed attributes."
            assert "replyTo" in data[count]["messageProperties"], "Reply To not included in consumed attributes."
            assert "hashType" in data[count].keys(), "Hash Type not included in consumed attributes."
            assert "hashVal" in data[count].keys(), "Hash not included in consumed attributes."
            #assert "swid" in data[count].keys(), "Swid not included in consumed attributes."
            assert "size" in data[count].keys(), "Size not included in consumed attributes."
            assert "fileUUID" in data[count].keys(), "File UUID not included in consumed attributes."
            assert filepath in data[count]["url"], "Download complete does not include expected URL."
            print("Expected Keys are included.")
            print("1.%d" % count)

            credCount = 0
            # assert data["fileName"] == dataInput["fileName"], "File names are not consistent."

            for respCount in range(len(data)):
                print("resp count: %d" % respCount)
                print("Total resps: %d" % len(data))
                print(data[respCount])
                if "url" not in data[respCount]:
                    continue
                if filepath in data[respCount]["url"]:
                    assert data[respCount]["hashType"] == hashType, "Incorrect hashtype detailed in complete message."
                    print("Hash value len: %d" % len(data[respCount]["hashVal"]))
                    print(data[respCount])
                    print(data[respCount]["messageProperties"]["replyTo"])
                    assert len(data[respCount]["hashVal"]) > 30, "Hash value in complete message not of the expected length"
                    assert "completed" in data[respCount]["messageProperties"]["replyTo"], "Incorrect replyTo value included in complete message."
                    print("2.1")

                    for credCount in range(len(dataCredentials)):
                        if data[respCount]["hashVal"] == dataCredentials[credCount]["hashVal"]:
                            if data[respCount]["messageProperties"]["correlationId"] == dataCredentials[credCount]["messageProperties"]["correlationId"]:
                                if data[respCount]["fileUUID"] == dataCredentials[credCount]["fileUUID"]:
                                    assert data[respCount]["fileName"] == dataCredentials[credCount]["fileName"], "File name values are not consistent."
                                    assert data[respCount]["fileName"] in dataCredentials[credCount]["errorMessage"], "Error text does not include expected file name."
                                    assert data[respCount]["fileName"] in data[respCount]["url"], "URL does not include  expected file name."
                                    assert data[respCount]["hashVal"] == dataCredentials[credCount]["hashVal"], "Hash values for file not consistent."
                                    print("Final Corr ID: %s" % data[respCount]["messageProperties"]["correlationId"])
                                    print("Cred Resp Corr ID: %s" % dataCredentials[credCount]["messageProperties"]["correlationId"])
                                    #assert data[respCount]["swid"] == family, "Unexpected swid returned in consumed messages."
                                    print(data[respCount]["messageProperties"]["correlationId"])
                                    print(dataCredentials[credCount]["messageProperties"]["correlationId"])
                                    assert data[respCount]["messageProperties"]["correlationId"] == dataCredentials[credCount]["messageProperties"]["correlationId"], "Corr Ids don't match in consumed messages."
                                    assert data[respCount]["messageProperties"]["replyTo"] == dataCredentials[credCount]["messageProperties"]["origin"], "Reply To values don't match in consumed messages."
                                    assert data[respCount]["size"] == dataCredentials[credCount]["size"], "Size values don't match in comsumed messages."
                                    assert data[respCount]["fileUUID"] == dataCredentials[credCount]["fileUUID"], "fileUUIDs don't match in consumed messages."
                                    print("2.2")

            for credCount in range(len(dataCredentials)):
                print("Cred count: %d" % credCount)
                print("Total creds: %d" % len(dataCredentials))
                print(dataCredentials[credCount]["fileFound"])
                if dataCredentials[credCount]["fileFound"] == True:
                    assert dataCredentials[credCount]["swid"] == family, "Unexpected swid returned in credential response."
                    assert dataCredentials[credCount]["swid"] in dataCredentials[credCount]["url"], "Swids don't match in consumed messages."
                    assert dataCredentials[credCount]["hashType"] == hashType, "Incorrect hashType detailed."
                    print("URL: %s" % dataCredentials[credCount]["url"])
                    assert esrsURL in dataCredentials[credCount]["url"], "Download complete does not include expected URL."
                    assert dataCredentials[credCount]["swid"] == dataCredentials[credCount]["header"]["serialNumber"], "Swids don't match in consumed messages."
                    assert dataCredentials[credCount]["header"]["productFamily"] in dataCredentials[credCount]["header"]["authorization"], "Unexpected header values returned."
                    print("3.1")

                    for inCount in range(len(dataInput)):
                        if "fileName" not in dataCredentials[credCount]:
                            continue
                        if dataCredentials[credCount]["fileName"] == dataInput[inCount]["fileName"]:
                            if dataCredentials[credCount]["messageProperties"]["correlationId"] == dataInput[inCount]["messageProperties"]["correlationId"]:
                                print("Checking response messages.....A")
                                assert dataCredentials[credCount]["fileName"] == dataInput[inCount]["fileName"], "File names are not consistent."
                                print("Orig Corr ID: %s" % dataInput[inCount]["messageProperties"]["correlationId"])
                                print("Cred Resp Corr ID: %s" % dataCredentials[credCount]["messageProperties"]["correlationId"])
                                assert dataCredentials[credCount]["messageProperties"]["correlationId"] == dataInput[inCount]["messageProperties"]["correlationId"], "Corr Ids don't match in consumed messages."
                                assert dataCredentials[credCount]["messageProperties"]["origin"] == dataInput[inCount]["messageProperties"]["replyTo"], "Reply To don't match in consumed messages."
                                assert dataCredentials[credCount]["messageProperties"]["replyTo"] == "no-reply", "Unexpected Reply TO on Creds response."
                                print("3.2")
                        # inCount += 1
                    print(len(data))
                    for respC in range(len(data)):
                        print(dataCredentials[credCount]["fileName"])
                        print(data[respC])
                        print(respC)
                        if "url" not in data[respC]:
                            continue
                        if dataCredentials[credCount]["fileName"] in data[respC]["url"]:
                            if dataCredentials[credCount]["messageProperties"]["correlationId"] == data[respC]["messageProperties"]["correlationId"]:
                                # assert dataCredentials[credCount]["fileName"] == data[respC]["fileName"], "File names are not consistent."
                                assert dataCredentials[credCount]["url"] != data[respC]["url"], "URLs don't match in consumed messages."
                                assert dataCredentials[credCount]["size"] == data[respC]["size"] or sizeMD5, "File sizes don't match in consumed messages."
                                assert dataCredentials[credCount]["messageProperties"]["correlationId"] == data[respC]["messageProperties"]["correlationId"], "Corr Ids don't match in consumed messages."
                                assert dataCredentials[credCount]["messageProperties"]["origin"] == data[respC]["messageProperties"]["replyTo"], "Reply To don't match in consumed messages."
                                assert dataCredentials[credCount]["hashType"] == hashType, "Incorrect hashType detailed."
                                print("3.3")
                                print("Response attributes match those defined in request.")
                                print("Downloaded BIOS file size: %s" % sizeBIOS)
                                print("Downloaded ZIP file size: %s" % sizeDAS)
                                print("Downloaded ESX file size: %s" % sizeESX)
                                return
                        # respC += 1
                    credCount += 1

        count += 1

        #return

    assert False, "Consumed response messages not complete."

def verifyConsumedAttributesInvalid(requestFile, credentialsFile, responseFile, hashType, family):
    numRCMs = 0
    path = "file:///opt/dell/cpsd/rcm-fitness/prepositioning-downloader-service/repository/downloads"
    requestData = open(requestFile, "rU")
    dataInput = json.load(requestData)

    # credentialsData = open(credentialsFile, "rU")
    # dataCredentials = json.load(credentialsData)

    dataFile = open(responseFile, "rU")
    data = json.load(dataFile)
    # print(data.keys())
    print("\nName of file: %s" % dataFile.name)

    # checkFileSize("BIOS_PFWCY_WN64_2.2.5.EXE", "/rootfs/opt/dell/cpsd/rcm-fitness/prepositioning-downloader-service/repository/downloads/")
    maxCount = len(data)

    for count in range(maxCount):
        if ("errorCode") not in data[count].keys():
            continue
        if ("errorCode") in data[count].keys():
            print(data[count]["errorCode"])
            print(data[count])
            print(data[count].keys())
            print(data[count]["errorMessage"])
            if os.path.exists(credentialsFile):
                credentialsData = open(credentialsFile, "rU")
                dataCredentials = json.load(credentialsData)
                print("Credentials response returned.")
                assert dataInput["fileName"] in dataCredentials[
                    "errorMessage"], "Expected file name included in error message text."
                assert data[count]["fileUUID"] == dataCredentials["fileUUID"], "FileUUIDs are not consistent."
                assert data[count]["size"] == dataCredentials["size"], "File sizes don't match in consumed messages."
                assert data[count]["hashType"] == dataCredentials["hashType"], "Incorrect hashType detailed."
                if dataCredentials["fileFound"] == False:
                    assert "errorMessage" in dataCredentials.keys(), "No error message in credentials response."
                    assert "replyTo" in dataCredentials[
                        "messageProperties"], "No message detailed in credentials response."
                    assert dataInput["fileName"] in dataCredentials[
                        "errorMessage"], "No file name included in error message text."
                    # assert dataCredentials["fileName"] == dataInput["fileName"], "File names are not consistent."
                    assert dataCredentials["size"] == 0, "Size of ZERO not returned in error."
                    assert dataInput["messageProperties"]["correlationId"] in dataCredentials["messageProperties"][
                        "correlationId"], "Corr Ids don't match in consumed messages."
                    assert dataInput["messageProperties"]["replyTo"] == dataCredentials["messageProperties"][
                        "origin"], "ReplyTo values don't match in consumed messages."
                    assert dataCredentials["hashType"] == hashType, "Incorrect hashType detailed."
                    print("Header key count: %d" % len(dataCredentials["header"].keys()))
                    assert len(dataCredentials[
                                   "header"].keys()) == 0, "Header should not included authorization keys or similar."
                    assert not dataCredentials["header"].keys(), "Header be an empty list."
                    assert "authorization" not in dataCredentials[
                        "header"], "Header should not included authorization keys."
                    print("Invalid request triggered expected Credentials response.")
                    print("Credentials response verified on failed request.")
            # else:
            #     continue

            assert dataInput["fileName"] in data[count]["errorMessage"], "Expected file name included in error message text."
            assert dataInput["messageProperties"]["correlationId"] in data[count]["messageProperties"][
                "correlationId"], "Corr Ids don't match in consumed messages."
            assert "errorMessage" in data[count].keys(), "Error Message not included in consumed attributes."
            assert "timestamp" in data[count]["messageProperties"], "Timestamp not included in consumed attributes."
            assert "correlationId" in data[count]["messageProperties"], "Correlation Id not included in consumed attributes."
            assert "replyTo" in data[count]["messageProperties"], "Reply To not included in consumed attributes."
            assert "hashType" in data[count].keys(), "Hash Type not included in consumed attributes."
            assert "size" in data[count].keys(), "Size not included in consumed attributes."
            assert "fileUUID" in data[count].keys(), "File UUID not included in consumed attributes."
            assert data[count]["size"] == 0, "Size of ZERO not returned in error."
            assert dataInput["messageProperties"]["replyTo"] == data[count]["messageProperties"][
                "replyTo"], "Reply To don't match in consumed messages."

            print("Download response verified on failed request.")

            #
            # if dataCredentials["fileFound"] == False:
            #     assert "errorMessage" in dataCredentials.keys(), "No error message in credentials response."
            #     assert "replyTo" in dataCredentials["messageProperties"], "No message detailed in credentials response."
            #     assert dataInput["fileName"] in dataCredentials["errorMessage"], "No file name included in error message text."
            #     # assert dataCredentials["fileName"] == dataInput["fileName"], "File names are not consistent."
            #     assert dataCredentials["size"] == 0, "Size of ZERO not returned in error."
            #     assert dataInput["messageProperties"]["correlationId"] in dataCredentials["messageProperties"][
            #         "correlationId"], "Corr Ids don't match in consumed messages."
            #     assert dataInput["messageProperties"]["replyTo"] == dataCredentials["messageProperties"][
            #         "replyTo"], "ReplyTo values don't match in consumed messages."
            #     assert dataCredentials["hashType"] == hashType, "Incorrect hashType detailed."
            #     print("Header key count: %d" % len(dataCredentials["header"].keys()))
            #     assert len(dataCredentials["header"].keys()) == 0, "Header should not included authorization keys or similar."
            #     assert not dataCredentials["header"].keys(), "Header be an empty list."
            #     assert "authorization" not in dataCredentials["header"], "Header should not included authorization keys."
            #     print("Invalid request triggered expected Credentials response.")
            #     print("Credentials response verified on failed request.")

            return

    assert False, "Response attributes do not match those defined in request."

def verifyProgressMessage(requestFile, credentialsFile, responseFile):
    numRCMs = 0
    count = 0

    filepath = "file:///opt/dell/cpsd/rcm-fitness/prepositioning-downloader-service/repository/downloads"
    requestData = open(requestFile, "rU")
    dataInput = json.load(requestData)

    credentialsData = open(credentialsFile, "rU")
    dataCredentials = json.load(credentialsData)

    dataFile = open(responseFile, "rU")
    data = json.load(dataFile)
    print(data)
    print("\nName of file: %s" % dataFile.name)
    print("Request count: %d" % len(dataInput))
    print("Credential count: %d" % len(dataCredentials))
    print("Response count: %d" % len(data))

    # sizeBIOS = checkFileSize("BIOS_PFWCY_WN64_2.2.5.EXE",
    #                          "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader-service/repository/downloads/")
    # sizePNG = checkFileSize("shai.png",
    #                         "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader-service/repository/downloads/")
    # sizeESX = checkFileSize("VMW-ESX-6.0.0-lsi_mr3-6.903.85.00_MR-3818071.zip",
    #                          "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader-service/repository/downloads/")
    # sizeMD5 = checkFileSize("VMW-ESX-6.0.0-lsi_mr3-6.903.85.00_MR-3818071.zip.md5",
    #                          "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader-service/repository/downloads/")
    sizeDAS = checkFileSize("DAS_Cache_Linux_1.zip",
                             "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader-service/repository/downloads/")

    #print(sizeDAS)

    credCount = len(dataCredentials)
    maxCount = len(data)
    print("Total messages consumed: %d" % maxCount)
    while count < maxCount:
        if ("totalSize") in data[count].keys():
            print("Count: %d" % count)
            assert "timestamp" in data[count]["messageProperties"], "Timestamp not included in consumed attributes."
            assert "correlationId" in data[count]["messageProperties"], "Correlation Id not included in consumed attributes."
            assert "downloadedSize" in data[count].keys(), "Hash Type not included in consumed attributes."
            assert "downloadSpeed" in data[count].keys(), "Hash not included in consumed attributes."
            # assert "swid" in data[count].keys(), "Swid not included in consumed attributes."
            # assert "size" in data[count].keys(), "Size not included in consumed attributes."
            assert "fileUUID" in data[count].keys(), "File UUID not included in consumed attributes."
            assert data[count]["totalSize"] > 0, "Unexpected file size returned."

            for cred in range(credCount):
                assert data[count]["fileUUID"] == dataCredentials[cred]["fileUUID"], "FileUUIDs don't match in consumed messages."
                assert data[count]["totalSize"] == dataCredentials[cred]["size"], "File sizes don't match in consumed messages."
                assert data[count]["totalSize"] != data[count]["downloadedSize"], "Progress message download size matches expected file size, unexpected."
                assert data[count]["totalSize"] == dataCredentials[cred]["size"], "Size not consistent in consumed messages."
                assert data[count]["totalSize"] == sizeDAS, "Size not consistent with expected value."
                # #assert data[count]["totalSize"] == sizeNIC or sizePNG or sizeESX or sizeMD5 or sizeDAS, "Size not consistent with expected value."
                # #assert data[count]["hashVal"] == hashDAS, "Hash not consistent with expected value."
                assert data[count]["downloadedSize"] >= 0, "No bytes downloaded as per progress message."
                assert data[count]["downloadSpeed"] >= 0, "No download speed returned as per progress message."
                assert dataInput["messageProperties"]["correlationId"] in data[count]["messageProperties"][
                    "correlationId"], "Corr Ids don't match in consumed messages."
                if data[count]["downloadSpeed"] > 0:
                    print("In here....")
                    assert data[count]["downloadedSize"] > 1, "Progress message downloaded size not as expected."
                    assert data[count]["downloadedSize"] < data[count]["totalSize"], "Progress message download size equal or greater than expected size."
                print("Here at last")
                count += 1
                return
        else:
            count += 1
            continue
        count += 1

    assert False, ("Progress message is not complete.")

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

def checkFileSize(filename, filepath):
    sendCommand = "find / -print0 | grep -FzZ " + filename
    print(sendCommand)
    fileStatus = af_support_tools.send_ssh_command(host=host, username=cli_username, password=cli_password,
                                                   command=sendCommand, return_output=True)
    if fileStatus is not "":
        fileStatus = fileStatus.rstrip()
        if filepath in fileStatus:
            sendCommand = "du -b " + fileStatus + " | cut -f 1-1"
            print(sendCommand)
            global fileSize
            fileSize = af_support_tools.send_ssh_command(host=host, username=cli_username, password=cli_password,
                                                         command=sendCommand, return_output=True)
            fileSize = "".join(fileSize.split())
            fileSize = int(fileSize.split("/", 1)[0])
            print("Size: %s" % fileSize)
            return fileSize
    else:
        pass
    #assert False, ("Attempt to check File Size is unsuccessful.")

def checkWritesComplete(filename, filepath):
    sendCommand = "find / -print0 | grep -FzZ " + filename
    fileStatus = af_support_tools.send_ssh_command(host=host, username=cli_username, password=cli_password,
                                                   command=sendCommand, return_output=True)
    if fileStatus is not "":
        fileStatus = fileStatus.rstrip()
        if filepath in fileStatus:
            sendCommand = "du -b " + fileStatus + " | cut -f 1-1"
            global totalRepoSize
            totalRepoSize = af_support_tools.send_ssh_command(host=host, username=cli_username, password=cli_password,
                                                         command=sendCommand, return_output=True)
            #print("Size: %s" % totalRepoSize)
            totalRepoSize = "".join(totalRepoSize.split())
            totalRepoSize = int(totalRepoSize.split("/", 1)[0])
            #print("Size: %d" % totalRepoSize)
            print("File status: %s" % fileStatus)
            return totalRepoSize
    else:
        pass
    #assert False, ("Attempt to check Repo Disk Usage is unsuccessful.")

def checkFileHash(filename, filepath):
    sendCommand = "find / -print0 | grep -FzZ " + filename
    fileStatus = af_support_tools.send_ssh_command(host=host, username=cli_username, password=cli_password,
                                                   command=sendCommand, return_output=True)

    if fileStatus is not "":
        fileStatus = fileStatus.rstrip()
        if filepath in fileStatus:
            # sendCommand = "ls -ltr " + fileStatus + " | awk \'FNR == 1 {print$5}\'"
            sendCommand = "sha256sum " + fileStatus + " | awk \'FNR == 1 {print$1}\'"
            global fileHash
            fileHash = af_support_tools.send_ssh_command(host=host, username=cli_username, password=cli_password,
                                                         command=sendCommand, return_output=True)
            print("Hash: %s" % fileHash)
            fileHash = "".join(fileHash.split())
            fileHash = (fileHash.split("/", 1)[0])
            print("Hash: %s" % fileHash)
            print("File status: %s" % fileStatus)
            return fileHash

    else:
        pass
    # assert False, "Attempt to check File Hash is unsuccessful."

def profileESRSResponseTimes(payLoad):
    messageReqHeader = {'__TypeId__': 'com.dell.cpsd.prepositioning.downloader.file.download.request'}
    resetTestQueues()
    print("Queues reset.")
    time.sleep(0.1)
    deletePreviousDownloadFiles("BIOS_PFWCY_WN64_2.2.5.EXE",
                                "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader-service/repository/downloads/")

    print("Previous downloads deleted.")
    count = 0
    t1 = 0
    t2 = 0
    timeDelta = 0
    averageDelta = 0
    sortedDelta = []
    listDelta = []

    while count < 200:
        af_support_tools.rmq_publish_message(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                             exchange="exchange.dell.cpsd.prepositioning.downloader.request",
                                             routing_key="dell.cpsd.prepositioning.downloader.request",
                                             headers=messageReqHeader, payload=payLoad, payload_type='json',
                                             ssl_enabled=False)
        print("\nCount: %d" % count)
        print("Download request published.")
        print(datetime.datetime.utcnow())
        t1 = datetime.datetime.utcnow()
        # time.sleep(0.1)
        q_len = 0
        timeout = 0

        while q_len < 1:

            q_len = af_support_tools.rmq_message_count(host=host, port=port,
                                                       rmq_username=rmq_username, rmq_password=rmq_username,
                                                       queue='testCredentialsResponse', ssl_enabled=False)
            timeout += 1
            time.sleep(0.1)
            if timeout > 500:
                print("ERROR: ESRS Credential response took too long to return.")
                break

        print (datetime.datetime.utcnow())
        t2 = datetime.datetime.utcnow()

        timeDelta = (t2 - t1).total_seconds()
        print(timeDelta)
        write_to_file = []
        write_to_file = [count, timeDelta]
        file = open('esrsProfile.txt', 'a')
        file.write("Loop: {} \tDelta: {}\n".format(*write_to_file))
        file.close
        assert timeDelta < 5, "Significant delay in response from ESRS."
        listDelta.append(timeDelta)
        averageDelta = sum(listDelta[0:(len(listDelta)-1)])/(len(listDelta))
        count += 1

        if len(listDelta) > 5 and timeDelta > 5:
            print(listDelta)
            sortedDelta = sorted(listDelta)
            sortedDelta = sortedDelta[-5:]
            print("Five longest response times: ")
            print(sortedDelta)

            print("Average delta: %0.3f" % averageDelta)
        else:
            continue

    time.sleep(1)
    resetTestQueues()
    assert count == 200, "Failed to complete 200 requests to profile."



@pytest.mark.rcm_fitness_mvp_extended
def test_downloadFWFileRequestInvalid():
    downloadFWFileRequestInvalid(messageInvalidFile, 'invalidFileFWRequest.json', 'invalidFileFWCredentials.json',
                                 'invalidFileFWResponse.json')

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyConsumedInvalidAttributes1():
    verifyConsumedAttributesInvalid(path + 'invalidFileFWRequest.json', path + 'invalidFileFWCredentials.json',
                                    path + 'invalidFileFWResponse.json', "SHA-256", "VCEVision")

@pytest.mark.rcm_fitness_mvp_extended
def test_downloadFWFileRequestInvalid4():
    downloadFWFileRequestInvalid(messageInvalidAll, 'invalidAllFWRequest.json', 'invalidAllFWCredentials.json',
                                 'invalidAllFWResponse.json')

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyConsumedInvalidAttributes4():
    verifyConsumedAttributesInvalid(path + 'invalidAllFWRequest.json', path + 'invalidAllFWCredentials.json',
                                    path + 'invalidAllFWResponse.json', "SHA-256", "VCEVision")

@pytest.mark.rcm_fitness_mvp_extended
def test_downloadFWFileRequestInvalid5():
    downloadFWFileRequestInvalid(messageNoFile, 'noFileFWRequest.json', 'noFileFWCredentials.json',
                                 'noFileFWResponse.json')

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyConsumedInvalidAttributes5():
    verifyConsumedAttributesInvalid(path + 'noFileFWRequest.json', path + 'noFileFWCredentials.json',
                                    path + 'noFileFWResponse.json', "SHA-256", "VCEVision")


@pytest.mark.rcm_fitness_mvp_extended
def test_downloadFWFileRequestInvalid8():
    downloadFWFileRequestInvalid(messageNoAll, 'noAllFWRequest.json', 'noAllFWCredentials.json',
                                 'noAllFWResponse.json')

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyConsumedInvalidAttributes8():
    verifyConsumedAttributesInvalid(path + 'noAllFWRequest.json', path + 'noAllFWCredentials.json',
                                    path + 'noAllFWResponse.json', "SHA-256", "VCEVision")

@pytest.mark.rcm_fitness_mvp_extended
@pytest.mark.rcm_fitness_mvp
def test_downloadFWFileRequest9():
    downloadFWFileRequest(message, 'downloadFWRequest.json', 'downloadFWCredentials.json',
                          'downloadFWResponse.json', "RCM/3.2.2/VxRack_1000_FLEX/Component/BIOS/2.2.5/BIOS_PFWCY_WN64_2.2.5.EXE", 24992920)

@pytest.mark.rcm_fitness_mvp_extended
@pytest.mark.rcm_fitness_mvp
def test_verifyPublishedAttributes9():
    verifyPublishedAttributes(path + 'downloadFWRequest.json')

@pytest.mark.rcm_fitness_mvp_extended
@pytest.mark.rcm_fitness_mvp
def test_verifyConsumedAttributes9():
    verifyConsumedAttributes("RCM/3.2.2/VxRack_1000_FLEX/Component/BIOS/2.2.5/BIOS_PFWCY_WN64_2.2.5.EXE", path + 'downloadFWRequest.json', path + 'downloadFWCredentials.json',
                             path + 'downloadFWResponse.json', "SHA-256", "BETA2ENG218", "https://10.234.100.5:9443/")

@pytest.mark.rcm_fitness_mvp_extended
def test_downloadFWFileRequest10():
    downloadFWFileRequest(messageSec, 'repeatDownloadFWRequest.json', 'repeatDownloadFWCredentials.json',
                          'repeatDownloadFWResponse.json', "DAS_Cache_Linux_1.zip", 111812532)


@pytest.mark.rcm_fitness_mvp_extended
def test_verifyConsumedAttributes10():
    verifyConsumedAttributes("DAS_Cache_Linux_1.zip", path + 'repeatDownloadFWRequest.json', path + 'repeatDownloadFWCredentials.json',
                             path + 'repeatDownloadFWResponse.json', "SHA-256", "BETA2ENG218", "https://10.234.100.5:9443/")


@pytest.mark.rcm_fitness_mvp_extended
def test_verifyProgressMessage10():
    verifyProgressMessage(path + 'repeatDownloadFWRequest.json', path + 'repeatDownloadFWCredentials.json',
                          path + 'repeatDownloadFWResponse.json')

@pytest.mark.rcm_fitness_mvp_extended
@pytest.mark.rcm_fitness_mvp
def test_downloadFWFileRequest11():
    downloadFWFileRequest(messageSas2, 'sasDownloadFWRequest.json', 'sasDownloadFWCredentials.json',
                          'sasDownloadFWResponse.json', "RCM/3.2.1/VxRack_1000_FLEX/Component/Controller_Firmware/SAS-RAID_Firmware_VH28K_WN64_25.4.0.0017_A06.EXE", 16505448)


@pytest.mark.rcm_fitness_mvp_extended
@pytest.mark.rcm_fitness_mvp
def test_verifyConsumedAttributes11():
    verifyConsumedAttributes("RCM/3.2.1/VxRack_1000_FLEX/Component/Controller_Firmware/SAS-RAID_Firmware_VH28K_WN64_25.4.0.0017_A06.EXE", path + 'sasDownloadFWRequest.json', path + 'sasDownloadFWCredentials.json',
                             path + 'sasDownloadFWResponse.json', "SHA-256", "BETA2ENG218", "https://10.234.100.5:9443/")

# # # # #
# # # # # RCM/3.2.3/VxRack_1000_FLEX/Component/Controller_Firmware/SAS-RAID_Firmware_2H45F_WN64_25.5.0.0018_A08.EXE
# # # # #
@pytest.mark.rcm_fitness_mvp_extended
def test_downloadFWFileMulti12():
    downloadFWFileMulti(message, messageSec, messageSas2, 'multiDownloadFWRequest.json',
                        'multiDownloadFWCredentials.json', 'multiDownloadFWResponse.json', "BIOS_PFWCY_WN64_2.2.5.EXE", 24992920, "DAS_Cache_Linux_1.zip", 109300)

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyMultiPublishedAttributes12():
    verifyMultiPublishedAttributes(path + 'multiDownloadFWRequest.json')

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyMultiConsumedAttributes12():
    verifyMultiConsumedAttributes(path + 'multiDownloadFWRequest.json', path + 'multiDownloadFWCredentials.json',
                                  path + 'multiDownloadFWResponse.json', "SHA-256", "BETA2ENG218", "https://10.234.100.5:9443/")

@pytest.mark.rcm_fitness_mvp_extended
def test_downloadFWFileMulti13():
    downloadFWFileMulti(message, messageSec, messageThird, 'secMultiDownloadFWRequest.json',
                        'secMultiDownloadFWCredentials.json', 'secMultiDownloadFWResponse.json', "BIOS_PFWCY_WN64_2.2.5.EXE", 24992920, "DAS_Cache_Linux_1.zip", 109300)

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyMultiPublishedAttributes13():
    verifyMultiPublishedAttributes(path + 'secMultiDownloadFWRequest.json')

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyMultiConsumedAttributes13():
    verifyMultiConsumedAttributes(path + 'secMultiDownloadFWRequest.json', path + 'secMultiDownloadFWCredentials.json',
                                  path + 'secMultiDownloadFWResponse.json', "SHA-256", "BETA2ENG218", "https://10.234.100.5:9443/")
# # # #

@pytest.mark.rcm_fitness_mvp_extended
def test_downloadFWFileRequest14():
    downloadFWFileMulti(message, messageBios1, messageBios2, 'downloadAllBiosFWRequest.json', 'downloadAllBiosFWCredentials.json',
                          'downloadAllBiosFWResponse.json', "BIOS_PFWCY_WN64_2.2.5.EXE", 24992920, "BIOS_6YDCM_WN64_2.4.3.EXE", 22808880)

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyMultiConsumedAttributes14():
    verifyMultiConsumedAttributes(path + 'downloadAllBiosFWRequest.json', path + 'downloadAllBiosFWCredentials.json',
                                  path + 'downloadAllBiosFWResponse.json', "SHA-256", "BETA2ENG218", "https://10.234.100.5:9443/")

# # #
@pytest.mark.rcm_fitness_mvp_extended
def test_downloadFWFileRequest15():
    downloadFWFileMulti(messageSas1, messageSas1, messageSas2, 'downloadAllSasFWRequest.json', 'downloadAllSasFWCredentials.json',
                          'downloadAllSasFWResponse.json', "SAS-RAID_Firmware_VH28K_WN64_25.4.0.0017_A06.EXE", 16505448, "SAS-RAID_Firmware_2H45F_WN64_25.5.0.0018_A08.EXE", 16729560)

@pytest.mark.rcm_fitness_mvp_extended
def test_verifyMultiConsumedAttributes15():
    verifyMultiConsumedAttributes(path + 'downloadAllSasFWRequest.json', path + 'downloadAllSasFWCredentials.json',
                             path + 'downloadAllSasFWResponse.json', "SHA-256", "BETA2ENG218", "https://10.234.100.5:9443/")


@pytest.mark.rcm_fitness_mvp_extended
def test_downloadFWFileRequest16():
    downloadFWFileMulti(messageEsxi1, messageEsxi1, messageEsxi2, 'downloadAllEsxiFWRequest.json', 'downloadAllEsxiFWCredentials.json',
                          'downloadAllEsxiFWResponse.json', "ESXi600-201610001-Build-4510822.zip", 366458004, "ESXi600-201703001-Build-5224934.zip", 367863254)


@pytest.mark.rcm_fitness_mvp_extended
def test_verifyMultiConsumedAttributes16():
    verifyMultiConsumedAttributes(path + 'downloadAllEsxiFWRequest.json', path + 'downloadAllEsxiFWCredentials.json',
                             path + 'downloadAllEsxiFWResponse.json', "SHA-256", "BETA2ENG218", "https://10.234.100.5:9443/")

@pytest.mark.rcm_fitness_mvp_extended
def test_profileESRSResponseTimes17():
    profileESRSResponseTimes(message)