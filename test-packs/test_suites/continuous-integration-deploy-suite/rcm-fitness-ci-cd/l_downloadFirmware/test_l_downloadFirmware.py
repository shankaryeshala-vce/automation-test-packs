#!/usr/bin/python
import pika
import json
import time
import af_support_tools
import pytest
import os
import re


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
    global payload_messageInvalid
    payload_messageInvalid = 'invalid_download'

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

    global message
    message = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header, property=payload_message)
    global messageSec
    messageSec = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                           property=payload_messageSec)
    global messageThird
    messageThird = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                             property=payload_messageThird)
    global messageInvalid
    messageInvalid = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                               property=payload_messageInvalid)


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


def resetTestQueues(testRequest, testResponse, testCredRequest, testCredResponse):
    # messageReqHeader = {'__TypeId__': 'com.dell.cpsd.esrs.service.download.credentials.requested'}
    # messageResHeaderComplete = {'__TypeId__': 'com.dell.cpsd.prepositioning.downloader.file.download.completed'}
    # messageResHeaderProgress = {'__TypeId__': 'com.dell.cpsd.prepositioning.downloader.file.download.progress'}

    credentials = pika.PlainCredentials(rmq_username, rmq_password)
    parameters = pika.ConnectionParameters(host, port, '/', credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    af_support_tools.rmq_purge_queue(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username, queue=testRequest,
                                     ssl_enabled=False)
    af_support_tools.rmq_purge_queue(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                     queue=testResponse, ssl_enabled=False)
    af_support_tools.rmq_purge_queue(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                     queue=testCredRequest, ssl_enabled=False)
    af_support_tools.rmq_purge_queue(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                     queue=testCredResponse, ssl_enabled=False)

    time.sleep(2)
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


def downloadFWFileRequest(payLoad, requestFile, requestCredentials, responseFileComplete):
    messageReqHeader = {'__TypeId__': 'com.dell.cpsd.prepositioning.downloader.file.download.request'}
    messageResHeaderComplete = {'__TypeId__': 'com.dell.cpsd.prepositioning.downloader.file.download.completed'}
    messageResHeaderProgress = {'__TypeId__': 'com.dell.cpsd.prepositioning.downloader.file.download.progress'}

    credentials = pika.PlainCredentials(rmq_username, rmq_password)
    parameters = pika.ConnectionParameters(host, port, '/', credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    resetTestQueues('testDownloadFWRequest', 'testDownloadFWResponse', 'testCredentialsRequest', 'testCredentialsResponse')
    print("Queues reset.")

    time.sleep(2)
    #deletePreviousDownloadFiles("VMW-ESX-6.0.0-lsi_mr3-6.903.85.00_MR-3818071.zip",
    #                           "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader/repository/downloads/")
    print("Previous downloads deleted.")
    time.sleep(2)

    # af_support_tools.rmq_publish_message(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
    #                                      exchange="exchange.dell.cpsd.esrs.request",
    #                                      routing_key="dell.cpsd.esrs.download.request",
    #                                      headers=messageReqHeader, payload=payLoad, payload_type='json',
    #                                      ssl_enabled=False)

    af_support_tools.rmq_publish_message(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
                                         exchange="exchange.dell.cpsd.prepositioning.downloader.request",
                                         routing_key="dell.cpsd.prepositioning.downloader.request",
                                         headers=messageReqHeader, payload=payLoad, payload_type='json',
                                         ssl_enabled=False)

    print("Download request published.")
    time.sleep(10)

    my_request_body = af_support_tools.rmq_consume_message(host=host, port=port,
                                                           rmq_username=rmq_username, rmq_password=rmq_username,
                                                           queue='testDownloadFWRequest',
                                                           ssl_enabled=False)
    af_support_tools.rmq_payload_to_file(my_request_body, path + requestFile)
    time.sleep(10)
    my_response_credentials_body = af_support_tools.rmq_consume_message(host=host, port=port,
                                                                        rmq_username=rmq_username,
                                                                        rmq_password=rmq_username,
                                                                        queue='testCredentialsResponse',
                                                                        ssl_enabled=False)
    af_support_tools.rmq_payload_to_file(my_response_credentials_body, path + requestCredentials)

    print("Download request and credential response consumed.")
    time.sleep(60)

    my_response_download_body = af_support_tools.rmq_consume_all_messages(host=host, port=port,
                                                                          rmq_username=rmq_username,
                                                                          rmq_password=rmq_username,
                                                                          queue='testDownloadFWResponse',
                                                                          ssl_enabled=False)
    af_support_tools.rmq_payload_to_file(my_response_download_body, path + responseFileComplete)

    print("Download response consumed.")

    time.sleep(1)


# def downloadFWFileMulti(payLoad, secPayLoad, thirdPayLoad, requestFile, requestCredentials, responseFileComplete):
#     resetTestQueues('testDownloadFWRequest', 'testDownloadFWResponse', 'testDownloadFWCredentials')
#     time.sleep(2)
#     print("Queues reset.")
#
#     deletePreviousDownloadFiles("VMW-ESX-6.0.0-lsi_mr3-6.903.85.00_MR-3818071.zip",
#                                 "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader/repository/downloads/")
#
#     print("Previous downloads deleted.")
#     time.sleep(2)
#
#     af_support_tools.rmq_publish_message(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
#                                          exchange="exchange.dell.cpsd.esrs.request",
#                                          routing_key="dell.cpsd.esrs.download.request",
#                                          headers=messageReqHeader, payload=payLoad, payload_type='json',
#                                          ssl_enabled=False)
#     time.sleep(2)
#
#     af_support_tools.rmq_publish_message(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
#                                          exchange="exchange.dell.cpsd.esrs.request",
#                                          routing_key="dell.cpsd.esrs.download.request",
#                                          headers=messageReqHeader, payload=secPayLoad, payload_type='json',
#                                          ssl_enabled=False)
#     time.sleep(2)
#
#     af_support_tools.rmq_publish_message(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
#                                          exchange="exchange.dell.cpsd.esrs.request",
#                                          routing_key="dell.cpsd.esrs.download.request",
#                                          headers=messageReqHeader, payload=thirdPayLoad, payload_type='json',
#                                          ssl_enabled=False)
#
#     print("Three file download requests published.")
#     time.sleep(10)
#
#     my_request_body = af_support_tools.rmq_consume_all_messages(host=host, port=port,
#                                                                 rmq_username=rmq_username, rmq_password=rmq_username,
#                                                                 queue='testDownloadFWRequest', ssl_enabled=False)
#     af_support_tools.rmq_payload_to_file(my_request_body, path + requestFile)
#
#     my_response_credentials_body = af_support_tools.rmq_consume_all_messages(host=host, port=port,
#                                                                              rmq_username=rmq_username,
#                                                                              rmq_password=rmq_username,
#                                                                              queue='testDownloadFWCredentials',
#                                                                              ssl_enabled=False)
#     af_support_tools.rmq_payload_to_file(my_response_credentials_body, path + requestCredentials)
#
#     print("Download request and credential response consumed.")
#     time.sleep(80)
#
#     my_response_download_body = af_support_tools.rmq_consume_all_messages(host=host, port=port,
#                                                                           rmq_username=rmq_username,
#                                                                           rmq_password=rmq_username,
#                                                                           queue='testDownloadFWResponse',
#                                                                           ssl_enabled=False)
#     af_support_tools.rmq_payload_to_file(my_response_download_body, path + responseFileComplete)
#
#     print("All download responses consumed.")
#     time.sleep(1)
#
#
# def downloadFWFileRequestInvalid(payLoad, requestFile, requestCredentials, responseFileComplete):
#     resetTestQueues('testDownloadFWRequest', 'testDownloadFWResponse', 'testDownloadFWCredentials')
#     time.sleep(2)
#     print("Queues reset.")
#
#     deletePreviousDownloadFiles("VMW-ESX-6.0.0-lsi_mr3-6.903.85.00_MR-3818071.zip",
#                                 "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader/repository/downloads/")
#     time.sleep(2)
#     print("Previous downloads deleted.")
#
#     # af_support_tools.rmq_publish_message(host=host, port=port, rmq_username=uname, rmq_password=password,
#     #                                      exchange="exchange.dell.cpsd.esrs.request",
#     #                                      routing_key="dell.cpsd.esrs.download.request",
#     #                                      headers=messageReqHeader, payload=payLoad, ssl_enabled=False)
#
#     af_support_tools.rmq_publish_message(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username,
#                                          exchange="exchange.dell.cpsd.esrs.request",
#                                          routing_key="dell.cpsd.esrs.download.request",
#                                          headers=messageReqHeader, payload=payLoad, payload_type='json',
#                                          ssl_enabled=False)
#     print("Download request for invalid filename published.")
#     time.sleep(10)
#
#     my_request_body = af_support_tools.rmq_consume_message(host=host, port=port,
#                                                            rmq_username=rmq_username, rmq_password=rmq_username,
#                                                            queue='testDownloadFWRequest', ssl_enabled=False)
#     af_support_tools.rmq_payload_to_file(my_request_body, path + requestFile)
#
#     my_response_credentials_body = af_support_tools.rmq_consume_message(host=host, port=port,
#                                                                         rmq_username=rmq_username,
#                                                                         rmq_password=rmq_username,
#                                                                         queue='testDownloadFWCredentials',
#                                                                         ssl_enabled=False)
#     af_support_tools.rmq_payload_to_file(my_response_credentials_body, path + requestCredentials)
#     print("Download request and credential response consumed.")
#
#     time.sleep(5)
#     my_response_download_body = af_support_tools.rmq_consume_message(host=host, port=port,
#                                                                      rmq_username=rmq_username,
#                                                                      rmq_password=rmq_username,
#                                                                      queue='testDownloadFWResponse', ssl_enabled=False)
#     af_support_tools.rmq_payload_to_file(my_response_download_body, path + responseFileComplete)
#     print("All download responses consumed.")
#     time.sleep(1)


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
        assert "swid" in dataInput.keys(), "Swid not included in published attributes."
        # assert "url" in dataInput.keys(), "URL not included in published attributes."
        assert "fileName" in dataInput.keys(), "fileName not included in published attributes."
        return

    assert False, ("Unable to verify published attributes.")


# def verifyMultiPublishedAttributes(filename):
#     count = 0
#     with open(filename, "rU") as dataFile:
#         dataInput = json.load(dataFile)
#
#     print(dataInput[count].keys())
#     print("\nName of file: %s" % dataFile.name)
#
#     assert len(dataInput) == 3, "Expected to find three published messages."
#     if len(dataInput) > 0:
#         while count < len(dataInput):
#             assert "timestamp" in dataInput[count][
#                 "messageProperties"], "Timestamp not included in published attributes."
#             assert "correlationId" in dataInput[count][
#                 "messageProperties"], "Correlation Id not included in published attributes."
#             assert "replyTo" in dataInput[count]["messageProperties"], "Reply To not included in published attributes."
#             assert "swid" in dataInput[count].keys(), "Swid not included in published attributes."
#             assert "url" in dataInput[count].keys(), "URL not included in published attributes."
#             assert "fileName" in dataInput[count].keys(), "fileName not included in published attributes."
#             assert dataInput[count]["swid"] == "VCEVISIONDEV01", "Unexpected SWID returned."
#             assert dataInput[count]["messageProperties"]["replyTo"] == "esrs.symphonyint238"
#             assert dataInput[count]["url"] is "", "URL is not empty."
#             count += 1
#             return
#    assert False, ("Unable to verify published attributes.")

def verifyConsumedAttributes(requestFile, credentialsFile, responseFile, hashType, family):
    numRCMs = 0
    count = 0
    filepath = "file:///opt/dell/cpsd/rcm-fitness/prepositioning-downloader/repository/downloads"
    requestData = open(requestFile, "rU")
    dataInput = json.load(requestData)

    credentialsData = open(credentialsFile, "rU")
    dataCredentials = json.load(credentialsData)

    dataFile = open(responseFile, "rU")
    data = json.load(dataFile)
    print(data)
    print("\nName of file: %s" % dataFile.name)

    sizeNIC = checkFileSize("BIOS_PFWCY_WN64_2.2.5.EXE",
                            "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader/repository/downloads/")
    sizeBIOS = checkFileSize("VMW-ESX-6.0.0-lsi_mr3-6.903.85.00_MR-3818071.zip.md5",
                             "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader/repository/downloads/")
    sizeRAID = checkFileSize("VMW-ESX-6.0.0-lsi_mr3-6.903.85.00_MR-3818071.zip",
                             "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader/repository/downloads/")

    maxCount = len(data)
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

        if ("url") in data[maxCount-1].keys():
            print("Count: %d" % count)
            assert "timestamp" in data[maxCount-1]["messageProperties"], "Timestamp not included in consumed attributes."
            assert "correlationId" in data[maxCount-1][
                "messageProperties"], "Correlation Id not included in consumed attributes."
            assert "replyTo" in data[maxCount-1]["messageProperties"], "Reply To not included in consumed attributes."
            assert "hashType" in data[maxCount-1].keys(), "Hash Type not included in consumed attributes."
            assert "hashVal" in data[maxCount-1].keys(), "Hash not included in consumed attributes."
            assert "swid" in data[maxCount-1].keys(), "Swid not included in consumed attributes."
            assert "size" in data[maxCount-1].keys(), "Size not included in consumed attributes."
            assert "fileUUID" in data[maxCount-1].keys(), "File UUID not included in consumed attributes."

            # assert data[count]["fileUUID"] == dataCredentials["fileUUID"], "FileUUIDs don't match in consumed messages."
            # assert data["fileName"] == dataInput["fileName"], "File names are not consistent."
            assert data[maxCount-1]["url"] != dataCredentials["url"], "URLs don't match in consumed messages."
            assert filepath in data[maxCount-1]["url"], "Download complete does not include expected URL."
            print(data[maxCount-1]["size"])
            print(dataCredentials["size"])
            assert data[maxCount-1]["size"] == dataCredentials["size"], "File sizes don't match in consumed messages."
            # assert data["swid"] == dataCredentials["swid"], "Swids don't match in consumed messages."
            assert data[maxCount-1]["size"] == sizeNIC or sizeBIOS or sizeRAID, "Size not consistent with expected value."
            assert dataInput["messageProperties"]["correlationId"] in data[maxCount-1]["messageProperties"][
                "correlationId"], "Corr Ids don't match in consumed messages."
            assert dataInput["messageProperties"]["replyTo"] == data[maxCount-1]["messageProperties"][
                "replyTo"], "Corr Ids don't match in consumed messages."
            assert data[maxCount-1]["hashType"] == hashType, "Incorrect hashType detailed."

            hashVal = data[maxCount-1]["hashVal"]
        else:
            print("Consumed download response message not a Complete.")

        count += 1

    if dataCredentials["fileFound"] == True:
        if ("url") in dataCredentials.keys():
            assert dataCredentials["fileName"] == dataInput["fileName"], "File names are not consistent."
            assert dataCredentials["swid"] in dataCredentials["url"], "Swid not included in Credential response URL."
            assert dataCredentials["size"] == fileSize, "Size not consistent with expected value."
            assert dataInput["messageProperties"]["correlationId"] in dataCredentials["messageProperties"][
                "correlationId"], "Corr Ids don't match in consumed messages."
            assert dataInput["messageProperties"]["replyTo"] == dataCredentials["messageProperties"][
                "replyTo"], "Corr Ids don't match in consumed messages."
            assert dataCredentials["hashType"] == hashType, "Incorrect hashType detailed."
            assert dataCredentials[
                       "size"] == sizeNIC or sizeBIOS or sizeRAID, "Size not consistent with expected value."

            assert dataCredentials["swid"] in dataCredentials["header"][
                "authorization"], "Swid not included in Credential response URL authorization details."
            assert family in dataCredentials["header"][
                "authorization"], "Swid not included in Credential response URL authorization details."
            assert dataCredentials["header"][
                       "productFamily"] == family, "Product Family not included in Credential response URL authorization details."
            assert dataCredentials["header"]["serialNumber"] == dataCredentials[
                "swid"], "Serial number not match Swid in Credential response URL authorization details."

            assert dataCredentials["hashVal"] == hashVal, "Hash values do not match."
            return

    else:
        print("Consumed credential response message not complete.")

    print("Response attributes match those defined in request.")
    print("Downloaded file size: %s" % fileSize)

#
# def verifyMultiConsumedAttributes(requestFile, credentialsFile, responseFile, hashType, family):
#     count = 0
#
#     path = "file:///opt/dell/cpsd/rcm-fitness/prepositioning-downloader/repository/downloads"
#     requestData = open(requestFile, "rU")
#     dataInput = json.load(requestData)
#
#     credentialsData = open(credentialsFile, "rU")
#     dataCredentials = json.load(credentialsData)
#
#     dataFile = open(responseFile, "rU")
#     data = json.load(dataFile)
#     print(data)
#     print("\nName of file: %s" % dataFile.name)
#
#     sizeNIC = checkFileSize("Network_Firmware_8028X_WN64_17.5.11_A00.EXE",
#                             "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader/repository/downloads/")
#     sizeBIOS = checkFileSize("BIOS_PFWCY_WN64_2.2.5.EXE",
#                              "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader/repository/downloads/")
#     sizeRAID = checkFileSize("SAS-RAID_Firmware_VH28K_WN64_25.4.0.0017_A06.EXE",
#                              "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader/repository/downloads/")
#
#     print("Total messages consumed: %d" % len(data))
#
#     try:
#         while count < len(data):
#             if ("url") in data[count].keys():
#                 assert "timestamp" in data[count]["messageProperties"], "Timestamp not included in consumed attributes."
#                 assert "correlationId" in data[count][
#                     "messageProperties"], "Correlation Id not included in consumed attributes."
#                 assert "replyTo" in data[count]["messageProperties"], "Reply To not included in consumed attributes."
#                 assert "hashType" in data[count].keys(), "Hash Type not included in consumed attributes."
#                 assert "hashVal" in data[count].keys(), "Hash not included in consumed attributes."
#                 assert "swid" in data[count].keys(), "Swid not included in consumed attributes."
#                 assert "size" in data[count].keys(), "Size not included in consumed attributes."
#                 assert "fileUUID" in data[count].keys(), "File UUID not included in consumed attributes."
#
#                 credCount = 0
#
#                 if data[count]["fileUUID"] == dataCredentials[credCount]["fileUUID"]:
#                     print("Count: %d" % count)
#                     print("credCount: %d" % credCount)
#                     print("Checking response messages.....A")
#                     # assert data["fileName"] == dataInput["fileName"], "File names are not consistent."
#                     assert data[count]["url"] != dataCredentials[credCount][
#                         "url"], "URLs don't match in consumed messages."
#                     assert path in data[count]["url"], "Download complete does not include expected URL."
#                     assert data[count]["size"] == dataCredentials[credCount][
#                         "size"], "File sizes don't match in consumed messages."
#                     # assert data["swid"] == dataCredentials["swid"], "Swids don't match in consumed messages."
#                     assert data[count][
#                                "size"] == sizeNIC or sizeBIOS or sizeRAID, "Size not consistent with expected value."
#                     # assert data[count]["messageProperties"]["correlationId"] in dataCredentials[credCount]["messageProperties"][
#                     #    "correlationId"], "Corr Ids don't match in consumed messages."
#                     assert data[count]["messageProperties"]["replyTo"] == "esrs.symphonyint238"
#                     assert data[count]["messageProperties"]["replyTo"] == \
#                            dataCredentials[credCount]["messageProperties"][
#                                "replyTo"], "Reply To don't match in consumed messages."
#                     assert data[count]["hashType"] == hashType, "Incorrect hashType detailed."
#                     # count += 1
#                     credCount += 1
#                 elif data[count]["fileUUID"] == dataCredentials[1]["fileUUID"]:
#                     credCount = 1
#                     # count = 0
#                     print("Count: %d" % count)
#                     print("credCount: %d" % credCount)
#                     print("Checking response messages.....B")
#                     assert data[count]["url"] != dataCredentials[credCount][
#                         "url"], "URLs don't match in consumed messages."
#                     assert data[count]["size"] == dataCredentials[credCount][
#                         "size"], "File sizes don't match in consumed messages."
#                     assert data[count][
#                                "size"] == sizeNIC or sizeBIOS or sizeRAID, "Size not consistent with expected value."
#                     # assert data[count]["messageProperties"]["correlationId"] in dataCredentials[credCount]["messageProperties"][
#                     #    "correlationId"], "Corr Ids don't match in consumed messages."
#                     assert data[count]["messageProperties"]["replyTo"] == "esrs.symphonyint238"
#                     assert data[count]["messageProperties"]["replyTo"] == \
#                            dataCredentials[credCount]["messageProperties"][
#                                "replyTo"], "Reply To don't match in consumed messages."
#                     assert data[count]["hashType"] == hashType, "Incorrect hashType detailed."
#                     # count += 1
#                     credCount += 1
#                 else:
#                     credCount = 2
#                     # count = 0
#                     print("Count: %d" % count)
#                     print("credCount: %d" % credCount)
#                     print("Checking response messages.....C")
#                     assert data[count]["url"] != dataCredentials[credCount][
#                         "url"], "URLs don't match in consumed messages."
#                     assert data[count]["size"] == dataCredentials[credCount][
#                         "size"], "File sizes don't match in consumed messages."
#                     assert data[count][
#                                "size"] == sizeNIC or sizeBIOS or sizeRAID, "Size not consistent with expected value."
#                     # assert data[count]["messageProperties"]["correlationId"] in dataCredentials[credCount]["messageProperties"][
#                     #    "correlationId"], "Corr Ids don't match in consumed messages."
#                     assert data[count]["messageProperties"]["replyTo"] == "esrs.symphonyint238"
#                     assert data[count]["messageProperties"]["replyTo"] == \
#                            dataCredentials[credCount]["messageProperties"][
#                                "replyTo"], "Reply To don't match in consumed messages."
#                     assert data[count]["hashType"] == hashType, "Incorrect hashType detailed."
#                     # count += 1
#                     credCount += 1
#             else:
#                 raise "No URL defined in response, incorrect message returned to download request."
#             count += 1
#
#             return (True)
#
#     print("Response attributes match those defined in request.")
#     print("Downloaded BIOS file size: %s" % sizeBIOS)
#     print("Downloaded NIC file size: %s" % sizeNIC)
#
#
# def verifyConsumedAttributesInvalid(requestFile, credentialsFile, responseFile, hashType, family):
#     numRCMs = 0
#     path = "file:///opt/dell/cpsd/rcm-fitness/prepositioning-downloader/repository/downloads"
#     requestData = open(requestFile, "rU")
#     dataInput = json.load(requestData)
#
#     credentialsData = open(credentialsFile, "rU")
#     dataCredentials = json.load(credentialsData)
#
#     dataFile = open(responseFile, "rU")
#     data = json.load(dataFile)
#     # print(data.keys())
#     print("\nName of file: %s" % dataFile.name)
#
#     # checkFileSize("BIOS_PFWCY_WN64_2.2.5.EXE", "/rootfs/opt/dell/cpsd/rcm-fitness/prepositioning-downloader/repository/downloads/")
#
#     if ("errorCode") in data.keys():
#         print(data["errorCode"])
#         print(data)
#         print(data.keys())
#         print(data["errorMessage"])
#         assert dataInput["fileName"] in data["errorMessage"], "No file name included in error message text."
#         assert dataInput["messageProperties"]["correlationId"] in data["messageProperties"][
#             "correlationId"], "Corr Ids don't match in consumed messages."
#
#         assert "errorMessage" in data.keys(), "Error Message not included in consumed attributes."
#         assert "timestamp" in data["messageProperties"], "Timestamp not included in consumed attributes."
#         assert "correlationId" in data["messageProperties"], "Correlation Id not included in consumed attributes."
#         assert "replyTo" in data["messageProperties"], "Reply To not included in consumed attributes."
#         assert "hashType" in data.keys(), "Hash Type not included in consumed attributes."
#         assert "size" in data.keys(), "Size not included in consumed attributes."
#         assert "fileUUID" in data.keys(), "File UUID not included in consumed attributes."
#
#         assert data["size"] == 0, "Size of ZERO not returned in error."
#         assert data["errorMessage"] == dataCredentials["errorMessage"], "Error messages are not consistent."
#         assert data["fileUUID"] == dataCredentials["fileUUID"], "FileUUIDs are not consistent."
#         assert data["size"] == dataCredentials["size"], "File sizes don't match in consumed messages."
#         assert dataInput["messageProperties"]["replyTo"] == data["messageProperties"][
#             "replyTo"], "Corr Ids don't match in consumed messages."
#         assert data["hashType"] == dataCredentials["hashType"], "Incorrect hashType detailed."
#         print("Invalid request triggered expected Download response.")
#
#     else:
#         print("Download response on Invalid filename didn't include an error code.")
#
#     if dataCredentials["fileFound"] == False:
#         assert "errorMessage" in dataCredentials.keys(), "No error message in credentials response."
#         assert "replyTo" in dataCredentials["messageProperties"], "No message detailed in credentials response."
#         assert dataInput["fileName"] in dataCredentials["errorMessage"], "No file name included in error message text."
#         # assert dataCredentials["fileName"] == dataInput["fileName"], "File names are not consistent."
#         assert dataCredentials["size"] == 0, "Size of ZERO not returned in error."
#         assert dataInput["messageProperties"]["correlationId"] in dataCredentials["messageProperties"][
#             "correlationId"], "Corr Ids don't match in consumed messages."
#         assert dataInput["messageProperties"]["replyTo"] == dataCredentials["messageProperties"][
#             "replyTo"], "ReplyTo values don't match in consumed messages."
#         assert dataCredentials["hashType"] == hashType, "Incorrect hashType detailed."
#         print("Invalid request triggered expected Credentials response.")
#     # assert dataCredentials["swid"] in dataCredentials["header"][
#     #                "authorization"], "Swid not included in Credential response URL authorization details."
#     #            assert family in dataCredentials["header"][
#     #                "authorization"], "Swid not included in Credential response URL authorization details."
#     #            assert dataCredentials["header"][
#     #                       "productFamily"] == family, "Product Family not included in Credential response URL authorization details."
#     #            assert dataCredentials["header"]["serialNumber"] == dataCredentials[
#     #                "swid"], "Serial number not match Swid in Credential response URL authorization details."
#
#     else:
#         assert dataCredentials["fileFound"] == True, "Unexpected fileFOund value returned."
#         print("Credentials response on Invalid filename returned a Found flag in error.")
#
#     print("Response attributes match those defined in request.")


def verifyProgressMessage(requestFile, credentialsFile, responseFile):
    numRCMs = 0
    count = 0
    path = "file:///opt/dell/cpsd/rcm-fitness/prepositioning-downloader/repository/downloads"
    requestData = open(requestFile, "rU")
    dataInput = json.load(requestData)

    credentialsData = open(credentialsFile, "rU")
    dataCredentials = json.load(credentialsData)
    dataFile = open(responseFile, "rU")
    data = json.load(dataFile)
    print(data)
    print("\nName of file: %s" % dataFile.name)

    sizeNIC = checkFileSize("Network_Firmware_8028X_WN64_17.5.11_A00.EXE",
                            "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader/repository/downloads/")
    sizeBIOS = checkFileSize("BIOS_PFWCY_WN64_2.2.5.EXE",
                             "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader/repository/downloads/")
    sizeRAID = checkFileSize("SAS-RAID_Firmware_VH28K_WN64_25.4.0.0017_A06.EXE",
                             "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader/repository/downloads/")

    maxCount = len(data)
    print("Total messages consumed: %d" % maxCount)
    while count < maxCount:
        if ("totalSize") in data[count].keys():
            print("Count: %d" % count)
            assert "timestamp" in data[count]["messageProperties"], "Timestamp not included in consumed attributes."
            assert "correlationId" in data[count][
                "messageProperties"], "Correlation Id not included in consumed attributes."
            assert "downloadedSize" in data[count].keys(), "Hash Type not included in consumed attributes."
            assert "downloadSpeed" in data[count].keys(), "Hash not included in consumed attributes."
            # assert "swid" in data[count].keys(), "Swid not included in consumed attributes."
            # assert "size" in data[count].keys(), "Size not included in consumed attributes."
            assert "fileUUID" in data[count].keys(), "File UUID not included in consumed attributes."

            assert data[count]["fileUUID"] == dataCredentials["fileUUID"], "FileUUIDs don't match in consumed messages."
            # assert data["fileName"] == dataInput["fileName"], "File names are not consistent."
            # assert data[count]["url"] != dataCredentials["url"], "URLs don't match in consumed messages."
            # assert data[count]["url"] == path + '/' + dataInput["fileName"], "Download complete does not include expected URL."
            assert data[count]["totalSize"] == dataCredentials["size"], "File sizes don't match in consumed messages."
            assert data[count]["totalSize"] != data[count][
                "downloadedSize"], "Progress message download size matches expected file size, unexpected."
            # assert data["swid"] == dataCredentials["swid"], "Swids don't match in consumed messages."
            assert data[count][
                       "totalSize"] == sizeNIC or sizeBIOS or sizeRAID, "Size not consistent with expected value."
            assert data[count]["downloadedSize"] > 0, "No bytes downloaded as per progress message."
            assert data[count]["downloadSpeed"] > 0, "No download speed returned as per progress message."
            assert dataInput["messageProperties"]["correlationId"] in data[count]["messageProperties"][
                "correlationId"], "Corr Ids don't match in consumed messages."
            return
        count += 1

    assert False, ("Progress message is not complete.")


def deletePreviousDownloadFiles(filename, filepath):
    sendCommand = "find / -name downloads"
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
    sendCommand = "find / -name " + filename
    fileStatus = af_support_tools.send_ssh_command(host=host, username=cli_username, password=cli_password,
                                                   command=sendCommand, return_output=True)
    if fileStatus is not "":
        fileStatus = fileStatus.rstrip()

    else:
        print("Specified file not found.")

    print("File status: %s" % fileStatus)

    if filepath in fileStatus:
        sendCommand = "ls -ltr " + fileStatus + " | awk \'FNR == 1 {print$5}\'"
        global fileSize
        fileSize = af_support_tools.send_ssh_command(host=host, username=cli_username, password=cli_password,
                                                     command=sendCommand, return_output=True)
        print("Size: %s" % fileSize)
        fileSize = int(fileSize.rstrip())
        # print("Size: %d" % fileSize)
        return fileSize

    assert False, ("Attempt to check File Size is unsuccessful.")


# #@pytest.mark.rcm_fitness_mvp_extended
# def test_downloadFWFileRequest3():
#     downloadFWFileRequestInvalid(messageInvalid, 'invalidDownloadFWRequest.json', 'invalidDownloadFWCredentials.json',
#                                  'invalidDownloadFWResponse.json')
#
#
# #@pytest.mark.rcm_fitness_mvp_extended
# def test_verifyConsumedAttributes3():
#     verifyConsumedAttributesInvalid(path + 'invalidDownloadFWRequest.json', path + 'invalidDownloadFWCredentials.json',
#                                     path + 'invalidDownloadFWResponse.json', "SHA-256", "VCEVision")


#@pytest.mark.rcm_fitness_mvp_extended
#@pytest.mark.rcm_fitness_mvp
def test_downloadFWFileRequest():
    downloadFWFileRequest(messageThird, 'downloadFWRequest.json', 'downloadFWCredentials.json',
                          'downloadFWResponse.json')


#@pytest.mark.rcm_fitness_mvp_extended
#@pytest.mark.rcm_fitness_mvp
def test_verifyPublishedAttributes():
    verifyPublishedAttributes(path + 'downloadFWRequest.json')


#@pytest.mark.rcm_fitness_mvp_extended
#@pytest.mark.rcm_fitness_mvp
def test_verifyConsumedAttributes():
    verifyConsumedAttributes(path + 'downloadFWRequest.json', path + 'downloadFWCredentials.json',
                             path + 'downloadFWResponse.json', "SHA-256", "VCEVision")


#@pytest.mark.rcm_fitness_mvp_extended
#@pytest.mark.rcm_fitness_mvp
def test_checkFileSize():
    checkFileSize("BIOS_PFWCY_WN64_2.2.5.EXE",
                  "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader/repository/downloads/")


# time.sleep(2)

#
# #@pytest.mark.rcm_fitness_mvp_extended
# def test_downloadFWFileRequest2():
#     downloadFWFileRequest(messageThird, 'repeatDownloadFWRequest.json', 'repeatDownloadFWCredentials.json',
#                           'repeatDownloadFWResponse.json')
#
#
# #@pytest.mark.rcm_fitness_mvp_extended
# def test_verifyConsumedAttributes2():
#     verifyConsumedAttributes(path + 'repeatDownloadFWRequest.json', path + 'repeatDownloadFWCredentials.json',
#                              path + 'repeatDownloadFWResponse.json', "SHA-256", "VCEVision")
#
#
# #@pytest.mark.rcm_fitness_mvp_extended
# def test_verifyProgressMessage():
#     verifyProgressMessage(path + 'repeatDownloadFWRequest.json', path + 'repeatDownloadFWCredentials.json',
#                           path + 'repeatDownloadFWResponse.json')
#
#
# #@pytest.mark.rcm_fitness_mvp_extended
# def test_checkFileSize2():
#     checkFileSize("BIOS_PFWCY_WN64_2.2.5.EXE",
#                   "/opt/dell/cpsd/rcm-fitness/prepositioning-downloader/repository/downloads/")
#
#
# # time.sleep(2)
#
#
# #@pytest.mark.rcm_fitness_mvp_extended
# def test_downloadFWFileMulti():
#     downloadFWFileMulti(message, messageSec, messageThird, 'multiDownloadFWRequest.json',
#                         'multiDownloadFWCredentials.json', 'multiDownloadFWResponse.json')
#
#
# #@pytest.mark.rcm_fitness_mvp_extended
# def test_verifyMultiPublishedAttributes():
#     verifyMultiPublishedAttributes(path + 'multiDownloadFWRequest.json')
#
#
# #@pytest.mark.rcm_fitness_mvp_extended
# def test_verifyMultiConsumedAttributes():
#     verifyMultiConsumedAttributes(path + 'multiDownloadFWRequest.json', path + 'multiDownloadFWCredentials.json',
#                                   path + 'multiDownloadFWResponse.json', "SHA-256", "VCEVision")
#
#
# # time.sleep(2)
#
#
# #@pytest.mark.rcm_fitness_mvp_extended
# def test_downloadFWFileMulti2():
#     downloadFWFileMulti(message, messageSec, messageThird, 'secMultiDownloadFWRequest.json',
#                         'secMultiDownloadFWCredentials.json', 'secMultiDownloadFWResponse.json')
#
#
# #@pytest.mark.rcm_fitness_mvp_extended
# def test_verifyMultiPublishedAttributes2():
#     verifyMultiPublishedAttributes(path + 'secMultiDownloadFWRequest.json')
#
#
# #@pytest.mark.rcm_fitness_mvp_extended
# def test_verifyMultiConsumedAttributes2():
#     verifyMultiConsumedAttributes(path + 'secMultiDownloadFWRequest.json', path + 'secMultiDownloadFWCredentials.json',
#                                   path + 'secMultiDownloadFWResponse.json', "SHA-256", "VCEVision")
