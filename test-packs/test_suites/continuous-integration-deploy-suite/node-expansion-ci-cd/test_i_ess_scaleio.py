#!/usr/bin/python
# Author:
# Revision: 1.2
# Code Reviewed by:
# Description: Testing the ESS on VCluster.

#
# Copyright (c) 2017 Dell Inc. or its subsidiaries.  All Rights Reserved.
# Dell EMC Confidential/Proprietary Information
#

import af_support_tools
import pytest
import json
import time
import requests
import os
import uuid


##############################################################################################

@pytest.fixture(scope="module", autouse=True)
def load_test_data():
    import cpsd
    global cpsd

    # Set config ini file name
    global env_file
    env_file = 'env.ini'

    # Test VM Details
    global ipaddress
    ipaddress = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS',
                                                           property='hostname')

    af_support_tools.rmq_get_server_side_certs(host_hostname=cpsd.props.base_hostname,
                                               host_username=cpsd.props.base_username,
                                               host_password=cpsd.props.base_password, host_port=22,
                                               rmq_certs_path=cpsd.props.rmq_cert_path)

    global rmq_username
    rmq_username = cpsd.props.rmq_username

    global rmq_password
    rmq_password = cpsd.props.rmq_password

    global port
    port = cpsd.props.rmq_port

    global rmq_cert_path
    rmq_cert_path = cpsd.props.rmq_cert_path

    global rmq_ssl_enabled
    rmq_ssl_enabled = cpsd.props.rmq_ssl_enabled

#####################################################################
# These are the main tests.
#####################################################################

@pytest.mark.daily_status
@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_handle_validateScaleIO_ESS_message():
    print("\n======================= Handle validateScaleio Request message =======================\n")

    cleanupQ('test.ess.service.response')
    bindQueue('exchange.dell.cpsd.service.ess.response', 'test.ess.service.response')

    print("Send validate ScaleIO request message ...\n")
    simulate_validateScaleIORequest_message();

    print("Consume validate scaleIO response message ...\n")
    listingsMsg = consumeResponse('test.ess.service.response')
    cleanupQ('test.ess.service.response')

    assert len(listingsMsg['validStorage']) == 3, "Error - should have 2 valid storagePools"
    assert len(listingsMsg['invalidStorage']) == 2, "Error - should have 3 failed storagePools"

#######################################################################################################################

def simulate_validateScaleIORequest_message():

    print(" Publishing a scaleio request message .. ")
    my_routing_key = 'ess.service.request.' + str(uuid.uuid4())

    filePath = os.environ['AF_TEST_SUITE_PATH'] + '/continuous-integration-deploy-suite/node-expansion-ci-cd/fixtures/ess_scaleioInfo.json'

    with open(filePath) as fixture:

        my_payload = fixture.read()
        print(my_payload)
        af_support_tools.rmq_publish_message(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                             rmq_username=cpsd.props.rmq_username, rmq_password=cpsd.props.rmq_password,
                                             exchange='exchange.dell.cpsd.service.ess.request',
                                             routing_key=my_routing_key,
                                             headers={
                                                 '__TypeId__': 'com.dell.cpsd.service.engineering.standards.EssValidateStoragePoolRequestMessage'},
                                             payload=my_payload,
                                             payload_type='json',ssl_enabled=cpsd.props.rmq_ssl_enabled)

####################################################################################################
def consumeResponse(testqueue):
    """ Consume the next message received on the testqueue and return the message in json format"""

    waitForMsg('test.ess.service.response')

    return_message = af_support_tools.rmq_consume_message(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                                          rmq_username=cpsd.props.rmq_username,
                                                          rmq_password=cpsd.props.rmq_password,ssl_enabled=cpsd.props.rmq_ssl_enabled,
                                                          queue='test.ess.service.response')

    return_message = json.loads(return_message, encoding='utf-8')

    print ( json.dumps(return_message))
    return return_message

####################################################################################################


def cleanupQ(testqueue):
    """ Delete the passed-in queue."""

    af_support_tools.rmq_delete_queue(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                      rmq_username=cpsd.props.rmq_username,
                                      rmq_password=cpsd.props.rmq_password,
                                      queue=testqueue, ssl_enabled=cpsd.props.rmq_ssl_enabled)


def bindQueue(exchange, testqueue):
    """ Bind 'testqueue' to 'exchange'."""
    af_support_tools.rmq_bind_queue(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                    rmq_username=cpsd.props.rmq_username,
                                    rmq_password=cpsd.props.rmq_password,
                                    queue=testqueue,
                                    exchange=exchange,
                                    routing_key='#', ssl_enabled=cpsd.props.rmq_ssl_enabled)


def waitForMsg(queue):
    # This function keeps looping untill a message is in the specified queue. We do need it to timeout and throw an error
    # if a message never arrives. Once a message appears in the queue the function is complete and main continues.

    print ('Waiting for message')
    # The length of the queue, it will start at 0 but as soon as we get a response it will increase
    q_len = 0

    # Represents the number of seconds that have gone by since the method started
    timeout = 0

    # Max number of seconds to wait
    max_timeout = 15

    # Amount of time in seconds that the loop is going to wait on each iteration
    sleeptime = 10

    while q_len < 1:
        time.sleep(sleeptime)
        timeout += sleeptime

        q_len = af_support_tools.rmq_message_count(host=ipaddress,
                                                   port=port,
                                                   rmq_username=rmq_username,
                                                   rmq_password=rmq_password,
                                                   ssl_enabled=rmq_ssl_enabled,
                                                   queue=queue)

        if timeout > max_timeout:
            print('ERROR: Message took too long to return. Something is wrong')
            cleanupQ(queue)
            break
