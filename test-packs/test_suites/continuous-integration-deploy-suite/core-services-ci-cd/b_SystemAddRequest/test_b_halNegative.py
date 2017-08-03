#!/usr/bin/python
# Author: Linjong
# Revision: 2.0
# Code Reviewed by:
# Description: Hal orchestrator negative tests:- invalid json and invalid message properties

import af_support_tools
import pytest
import json
import time
import paramiko

@pytest.fixture(scope="module", autouse=True)
def load_test_data():
    global payload_file
    payload_file = 'continuous-integration-deploy-suite/symphony-sds.ini'
    global payload_header
    payload_header = 'payload'
    global payload_property_hal_neg_invalid_json
    payload_property_hal_neg_invalid_json = 'invalid_json_hal'
    global payload_property_hal_neg_invalid_msg_properties
    payload_property_hal_neg_invalid_msg_properties = 'invalid_msg_properties_hal'
    global env_file
    env_file = 'env.ini'
    global ipaddress
    ipaddress = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='hostname')
    global cli_username
    cli_username = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='username')
    global cli_password
    cli_password = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='password')
    global rmq_username
    rmq_username = 'guest'
    global rmq_password
    rmq_password = 'guest'
    global port
    port = 5672

#######################################################################################################################

# *** collectComponentVersion Negative Test ***
@pytest.mark.core_services_mvp_extended
#Negative 1 Test - Invalid JSON Format
def test_Hal_collectComponentVersions_invalid_json():

    print("Running HAL negative test No.1 - Invalid JSON...")

    bindHALQueus()

    the_payload = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                            property=payload_property_hal_neg_invalid_json)

    #print(the_payload)

    #publish hal message
    time.sleep(1)
    af_support_tools.rmq_publish_message(host=ipaddress, rmq_username=rmq_username, rmq_password=rmq_password,
                                         exchange='exchange.dell.cpsd.hal.orchestrator.request',
                                         routing_key='dell.cpsd.hal.orchestrator.collect.component.versions',
                                         headers={
                                             '__TypeId__': 'com.dell.cpsd.hal.orchestrator.service.collect.component.versions'},
                                         payload=the_payload)

    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.hal.orchestrator.request')

    #Check json file
    try:
        return_json = json.loads(return_message, encoding='utf-8')
        print("return message: " + return_json)
        i_am_json = True
    except Exception:
        i_am_json = False

    assert i_am_json == False
    if i_am_json == False:
        print('Verified JSON is invalid')

    time.sleep(1)

    sendCommand = 'docker ps | grep hal-orchestrator | awk \'{system("docker exec -i "$1" cat /opt/dell/cpsd/hal-orchestrator/logs/hal-orchestrator-error.log")}\''

    error1 = "(attempt 1)"
    error2 = "Unexpected character"
    error3 = "VAMQP1009E"
    error4 = "VAMQP1008E AMQP error (attempt 1)"

    my_return_text = af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password, command=sendCommand, return_output=True)
    #print("PRINT MY RETURNED TEXT: " + my_return_text)

    assert error1 in my_return_text
    assert error2 in my_return_text
    assert error3 in my_return_text
    assert error4 in my_return_text
    print('Test Pass: Expected errors are in file')

    print('Test 1 of 2: Invalid JSON: TEST PASSED\n')
    print('****************************************')

    time.sleep(1)


########################################################################################################################

#Negative Test 2 - Invalid Message Properties
@pytest.mark.core_services_mvp_extended
def test_Hal_collectComponentVersions_invalid_msg_properties():

    print("Running HAL negative test No.2 - Invalid message properties...")

    bindHALQueus()

    #invalid message properties payload
    the_payload = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                            property=payload_property_hal_neg_invalid_msg_properties)


    #print(the_payload)

    #publishMessage(the_payload)
    time.sleep(1)
    af_support_tools.rmq_publish_message(host=ipaddress,rmq_username=rmq_username,rmq_password=rmq_password,
                                         exchange='exchange.dell.cpsd.hal.orchestrator.request',
                                         routing_key='dell.cpsd.hal.orchestrator.collect.component.versions',
                                         headers={
                                             '__TypeId__': 'com.dell.cpsd.hal.orchestrator.service.collect.component.versions'},
                                         payload=the_payload)

    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.hal.orchestrator.request')

    published_json = json.loads(the_payload, encoding='utf-8')
    return_json = json.loads(return_message, encoding='utf-8')

    assert published_json == return_json
    print('\nTEST: Published Message Received: PASSED\n')

    sendCommand = 'docker ps | grep hal-orchestrator | awk \'{system("docker exec -i "$1" cat /opt/dell/cpsd/hal-orchestrator/logs/hal-orchestrator-error.log") }\''
    error1 = "VAMQP1008E AMQP error"
    error2 = "(attempt 1)"
    error3 = "VAMQP1009E"
    error4 = "Message has failed with no recovery details."

    my_return_text = af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password, command=sendCommand, return_output=True)
    #print("PRINT MY RETURNED TEXT: " + my_return_text)

    assert error1 in my_return_text
    assert error2 in my_return_text
    assert error3 in my_return_text
    assert error4 in my_return_text
    print('Test Pass: Expected errors are in file')

    print('Test 2 of 2: Invalid Message Properties: TEST PASSED\n')
    print('******************************************************')

    time.sleep(1)
########################################################################################################################

def bindHALQueus():
    print('\nCreating HAL Queue')
    af_support_tools.rmq_bind_queue(host=ipaddress,
                                    port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                    queue='test.hal.orchestrator.request',
                                    exchange='exchange.dell.cpsd.hal.orchestrator.request',
                                    routing_key='#')

    time.sleep(2)

def validJson(return_message):
    try:
        return_json = json.loads(return_message, encoding='utf-8')
        i_am_json = True
    except Exception:
        i_am_json = False

    assert i_am_json == True

########################################################################################################################
#test_Hal_collectComponentVersions_invalid_msg_properties()
#test_Hal_collectComponentVersions_invalid_json()
