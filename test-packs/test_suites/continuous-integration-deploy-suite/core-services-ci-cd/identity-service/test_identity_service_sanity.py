#!/usr/bin/python
# Author:cullia
# Updated by: olearj10
# Date: 6 April 2017
# Revision:2.6
# Code Reviewed by:
# Description: Standalone testing of the Identity Service. No other services are used. No system needs to be defined
# to run this test.

import af_support_tools
import pytest
import json
import random
import time

@pytest.fixture(scope="module", autouse=True)
def load_test_data():
   # Set config ini file name
    global env_file
    env_file = 'env.ini'

    # Set Vars
	global ipaddress
    ipaddress = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='hostname')
	global user
    user = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='username')
	global password
    password = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='password')

    global identifyelement
    identifyelement = '{"timestamp":"2017-01-27T14:18:00.510Z","correlationId":"c92b8be9-a892-4a76-a8d3-933c85ead7bb","reply-to":"dell.cpsd.eids.identity.request.sds.gouldc-mint","elementIdentities":[{"correlationUuid":"fb4e839d-aba1-409e-82d7-7e4632d6b647","identity":{"elementType":"group","classification":"GROUP","parents":[{"elementType":"VCESYSTEM","classification":"SYSTEM","businessKeys":[{"businessKeyType":"CONTEXTUAL","key":"IDENTIFIER","value":"VXB-340"},{"businessKeyType":"ABSOLUTE","key":"SERIAL_NUMBER","value":"RTP-VXB340-DQAV34YX"}]}],"businessKeys":[{"businessKeyType":"CONTEXTUAL","key":"IDENTIFIER","value":"SystemNetwork"}]}},{"correlationUuid":"d4964090-76b8-4d4a-8068-4cd8ff258462","identity":{"elementType":"SWITCH","classification":"DEVICE","parents":[{"elementType":"group","classification":"GROUP","parents":[{"elementType":"VCESYSTEM","classification":"SYSTEM","businessKeys":[{"businessKeyType":"CONTEXTUAL","key":"IDENTIFIER","value":"VXB-340"},{"businessKeyType":"ABSOLUTE","key":"SERIAL_NUMBER","value":"RTP-VXB340-DQAV34YX"}]}],"businessKeys":[{"businessKeyType":"CONTEXTUAL","key":"IDENTIFIER","value":"SystemNetwork"}]}],"businessKeys":[{"businessKeyType":"CONTEXTUAL","key":"COMPONENT_TAG","value":"MGMT-N3A"}]}},{"correlationUuid":"93eb24fd-b8b0-49fa-8911-17f1cba72034","identity":{"elementType":"SWITCH","classification":"DEVICE","parents":[{"elementType":"group","classification":"GROUP","parents":[{"elementType":"VCESYSTEM","classification":"SYSTEM","businessKeys":[{"businessKeyType":"CONTEXTUAL","key":"IDENTIFIER","value":"VXB-340"},{"businessKeyType":"ABSOLUTE","key":"SERIAL_NUMBER","value":"RTP-VXB340-DQAV34YX"}]}],"businessKeys":[{"businessKeyType":"CONTEXTUAL","key":"IDENTIFIER","value":"SystemNetwork"}]}],"businessKeys":[{"businessKeyType":"CONTEXTUAL","key":"COMPONENT_TAG","value":"MGMT-N3B"}]}},{"correlationUuid":"0c180853-bff6-4813-9099-3f80816ce450","identity":{"elementType":"VCESYSTEM","classification":"SYSTEM","businessKeys":[{"businessKeyType":"CONTEXTUAL","key":"IDENTIFIER","value":"VXB-340"},{"businessKeyType":"ABSOLUTE","key":"SERIAL_NUMBER","value":"RTP-VXB340-DQAV34YX"}]}}]}'
    global keyaccuracyid_abc
    keyaccuracyid_abc = '{"timestamp":"2017-03-15T09:40:00.170Z","correlationId":"key-accuracy-0000-0000-0000","reply-to":"dell.cpsd.eids.identity.request.sds.test","elementIdentities":[{"correlationUuid":"12345-abcdef-54321-fedcba","identity":{"elementType":"TESTELEMENT","classification":"DEVICE","parents":[],"businessKeys":[{"businessKeyType":"CONTEXTUAL","key":"NAME","value":"THE_NAME"},{"businessKeyType":"CONTEXTUAL","key":"DESCRIPTION","value":"THE_DESCRIPTION"},{"businessKeyType":"CONTEXTUAL","key":"IPADDRESS","value":"THE_IPADDRESS"}],"contextualKeyAccuracy":2}}]}'
    global keyaccuracyid_ab
    keyaccuracyid_ab  = '{"timestamp":"2017-01-27T14:18:00.510Z","correlationId":"key-accuracy-identify-0000-0000","reply-to":"dell.cpsd.eids.identity.request.sds.test","elementIdentities":[{"correlationUuid":"12345-abcdef-54321-fedcba","identity":{"elementType":"TESTELEMENT","classification":"DEVICE","parents":[],"businessKeys":[{"businessKeyType":"CONTEXTUAL","key":"NAME","value":"THE_NAME"},{"businessKeyType":"CONTEXTUAL","key":"DESCRIPTION","value":"THE_DESCRIPTION"}]}}]}'
    global keyaccuracyid_ac
    keyaccuracyid_ac = '{"timestamp":"2017-01-27T14:18:00.510Z","correlationId":"key-accuracy-identify-0000-0000","reply-to":"dell.cpsd.eids.identity.request.sds.test","elementIdentities":[{"correlationUuid":"12345-abcdef-54321-fedcba","identity":{"elementType":"TESTELEMENT","classification":"DEVICE","parents":[],"businessKeys":[{"businessKeyType":"CONTEXTUAL","key":"NAME","value":"THE_NAME"},{"businessKeyType":"CONTEXTUAL","key":"IPADDRESS","value":"THE_IPADDRESS"}]}}]}'
    global keyaccuracyid_neg
    keyaccuracyid_neg = '{"timestamp":"2017-01-27T14:18:00.510Z","correlationId":"key-accuracy-identify-0000-0000","reply-to":"dell.cpsd.eids.identity.request.sds.test","elementIdentities":[{"correlationUuid":"12345-abcdef-54321-fedcba","identity":{"elementType":"TESTELEMENT","classification":"DEVICE","parents":[],"businessKeys":[{"businessKeyType":"CONTEXTUAL","key":"NAME","value":"THE_NAME"}]}}]}'
    global ident_no_element_type
    ident_no_element_type = '{"timestamp":"2017-01-27T14:18:00.510Z","correlationId":"c92b8be9-a892-4a76-a8d3-933c85ead7bb","reply-to":"dell.cpsd.eids.identity.request.sds.gouldc-mint","elementIdentities":[{"correlationUuid":"0c180853-bff6-4813-9099-3f80816ce450","identity":{"elementType":"","classification":"SYSTEM","businessKeys":[{"businessKeyType":"CONTEXTUAL","key":"IDENTIFIER","value":"VXB-340"},{"businessKeyType":"ABSOLUTE","key":"SERIAL_NUMBER","value":"RTP-VXB340-DQAV34YX"}]}}]}'
    global describe_no_element
    describe_no_element = '{"timestamp":"2017-01-27T14:51:00.570Z","correlationId":"5d7f6d34-4271-4593-9bad-1b95589e5189","reply-to":"dell.cpsd.eids.identity.request.hal.gouldc-mint","elementUuids":[]}'

    global elementUuid
    elementUuid = ''

    global rmq_username
    rmq_username = 'test'
    global rmq_password
    rmq_password = 'test'

#try:
#    env_file = 'env.ini'
#    ipaddress = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='hostname')
#    user = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='username')
#    password = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='password')
#except:
#    print('Possible configuration error.')

# Create the payload messages.
# Hint: the correllationId field can be used as a description which makes it easier to locate in the Trace log.
#identifyelement = '{"timestamp":"2017-01-27T14:18:00.510Z","correlationId":"c92b8be9-a892-4a76-a8d3-933c85ead7bb","reply-to":"dell.cpsd.eids.identity.request.sds.gouldc-mint","elementIdentities":[{"correlationUuid":"fb4e839d-aba1-409e-82d7-7e4632d6b647","identity":{"elementType":"group","classification":"GROUP","parents":[{"elementType":"VCESYSTEM","classification":"SYSTEM","businessKeys":[{"businessKeyType":"CONTEXTUAL","key":"IDENTIFIER","value":"VXB-340"},{"businessKeyType":"ABSOLUTE","key":"SERIAL_NUMBER","value":"RTP-VXB340-DQAV34YX"}]}],"businessKeys":[{"businessKeyType":"CONTEXTUAL","key":"IDENTIFIER","value":"SystemNetwork"}]}},{"correlationUuid":"d4964090-76b8-4d4a-8068-4cd8ff258462","identity":{"elementType":"SWITCH","classification":"DEVICE","parents":[{"elementType":"group","classification":"GROUP","parents":[{"elementType":"VCESYSTEM","classification":"SYSTEM","businessKeys":[{"businessKeyType":"CONTEXTUAL","key":"IDENTIFIER","value":"VXB-340"},{"businessKeyType":"ABSOLUTE","key":"SERIAL_NUMBER","value":"RTP-VXB340-DQAV34YX"}]}],"businessKeys":[{"businessKeyType":"CONTEXTUAL","key":"IDENTIFIER","value":"SystemNetwork"}]}],"businessKeys":[{"businessKeyType":"CONTEXTUAL","key":"COMPONENT_TAG","value":"MGMT-N3A"}]}},{"correlationUuid":"93eb24fd-b8b0-49fa-8911-17f1cba72034","identity":{"elementType":"SWITCH","classification":"DEVICE","parents":[{"elementType":"group","classification":"GROUP","parents":[{"elementType":"VCESYSTEM","classification":"SYSTEM","businessKeys":[{"businessKeyType":"CONTEXTUAL","key":"IDENTIFIER","value":"VXB-340"},{"businessKeyType":"ABSOLUTE","key":"SERIAL_NUMBER","value":"RTP-VXB340-DQAV34YX"}]}],"businessKeys":[{"businessKeyType":"CONTEXTUAL","key":"IDENTIFIER","value":"SystemNetwork"}]}],"businessKeys":[{"businessKeyType":"CONTEXTUAL","key":"COMPONENT_TAG","value":"MGMT-N3B"}]}},{"correlationUuid":"0c180853-bff6-4813-9099-3f80816ce450","identity":{"elementType":"VCESYSTEM","classification":"SYSTEM","businessKeys":[{"businessKeyType":"CONTEXTUAL","key":"IDENTIFIER","value":"VXB-340"},{"businessKeyType":"ABSOLUTE","key":"SERIAL_NUMBER","value":"RTP-VXB340-DQAV34YX"}]}}]}'
#keyaccuracyid_abc = '{"timestamp":"2017-03-15T09:40:00.170Z","correlationId":"key-accuracy-0000-0000-0000","reply-to":"dell.cpsd.eids.identity.request.sds.test","elementIdentities":[{"correlationUuid":"12345-abcdef-54321-fedcba","identity":{"elementType":"TESTELEMENT","classification":"DEVICE","parents":[],"businessKeys":[{"businessKeyType":"CONTEXTUAL","key":"NAME","value":"THE_NAME"},{"businessKeyType":"CONTEXTUAL","key":"DESCRIPTION","value":"THE_DESCRIPTION"},{"businessKeyType":"CONTEXTUAL","key":"IPADDRESS","value":"THE_IPADDRESS"}],"contextualKeyAccuracy":2}}]}'
#keyaccuracyid_ab  = '{"timestamp":"2017-01-27T14:18:00.510Z","correlationId":"key-accuracy-identify-0000-0000","reply-to":"dell.cpsd.eids.identity.request.sds.test","elementIdentities":[{"correlationUuid":"12345-abcdef-54321-fedcba","identity":{"elementType":"TESTELEMENT","classification":"DEVICE","parents":[],"businessKeys":[{"businessKeyType":"CONTEXTUAL","key":"NAME","value":"THE_NAME"},{"businessKeyType":"CONTEXTUAL","key":"DESCRIPTION","value":"THE_DESCRIPTION"}]}}]}'
#keyaccuracyid_ac = '{"timestamp":"2017-01-27T14:18:00.510Z","correlationId":"key-accuracy-identify-0000-0000","reply-to":"dell.cpsd.eids.identity.request.sds.test","elementIdentities":[{"correlationUuid":"12345-abcdef-54321-fedcba","identity":{"elementType":"TESTELEMENT","classification":"DEVICE","parents":[],"businessKeys":[{"businessKeyType":"CONTEXTUAL","key":"NAME","value":"THE_NAME"},{"businessKeyType":"CONTEXTUAL","key":"IPADDRESS","value":"THE_IPADDRESS"}]}}]}'
#keyaccuracyid_neg = '{"timestamp":"2017-01-27T14:18:00.510Z","correlationId":"key-accuracy-identify-0000-0000","reply-to":"dell.cpsd.eids.identity.request.sds.test","elementIdentities":[{"correlationUuid":"12345-abcdef-54321-fedcba","identity":{"elementType":"TESTELEMENT","classification":"DEVICE","parents":[],"businessKeys":[{"businessKeyType":"CONTEXTUAL","key":"NAME","value":"THE_NAME"}]}}]}'
#ident_no_element_type = '{"timestamp":"2017-01-27T14:18:00.510Z","correlationId":"c92b8be9-a892-4a76-a8d3-933c85ead7bb","reply-to":"dell.cpsd.eids.identity.request.sds.gouldc-mint","elementIdentities":[{"correlationUuid":"0c180853-bff6-4813-9099-3f80816ce450","identity":{"elementType":"","classification":"SYSTEM","businessKeys":[{"businessKeyType":"CONTEXTUAL","key":"IDENTIFIER","value":"VXB-340"},{"businessKeyType":"ABSOLUTE","key":"SERIAL_NUMBER","value":"RTP-VXB340-DQAV34YX"}]}}]}'
#describe_no_element = '{"timestamp":"2017-01-27T14:51:00.570Z","correlationId":"5d7f6d34-4271-4593-9bad-1b95589e5189","reply-to":"dell.cpsd.eids.identity.request.hal.gouldc-mint","elementUuids":[]}'

# ident_no_class = '{"timestamp":"2017-01-27T14:18:51Z","correlationId":"c92b8be9-a892-4a76-a8d3-933c85ead7bb","reply-to":"dell.cpsd.eids.identity.request.sds.gouldc-mint","elementIdentities":[{"correlationUuid":"0c180853-bff6-4813-9099-3f80816ce450","identity":{"elementType":"VCESYSTEM","classification":,"businessKeys":[{"businessKeyType":"CONTEXTUAL","key":"IDENTIFIER","value":"VXB-340"},{"businessKeyType":"ABSOLUTE","key":"SERIAL_NUMBER","value":"RTP-VXB340-DQAV34YX"}]}}]}'
# ident_no_context = '{"timestamp":"2017-01-27T14:18:51Z","correlationId":"c92b8be9-a892-4a76-a8d3-933c85ead7bb","reply-to":"dell.cpsd.eids.identity.request.sds.gouldc-mint","elementIdentities":[{"correlationUuid":"0c180853-bff6-4813-9099-3f80816ce450","identity":{"elementType":"VCESYSTEM","classification":"SYSTEM","businessKeys":[{"businessKeyType":,"key":"IDENTIFIER","value":"VXB-340"},{"businessKeyType":"ABSOLUTE","key":"SERIAL_NUMBER","value":"RTP-VXB340-DQAV34YX"}]}}]}'

# Arrays for Parameterization
#payload_keyaccuracy = [keyaccuracyid_abc, keyaccuracyid_ab, keyaccuracyid_ac, keyaccuracyid_neg]
#payload_negative_messages = [ident_no_element_type, describe_no_element]

# Globally defined string to hold described element uuid
#elementUuid = ''

# Always specify user names & password here at the start. Makes changing them later much easier,
#rmq_username = 'test'
#rmq_password = 'test'

##############################################################################################


@pytest.mark.core_services_mvp
def test_ident_status():
    print('\nRunning Identity Status test on system: ', ipaddress)
    status_command = 'docker ps | grep identity-service'
    status = af_support_tools.send_ssh_command(host=ipaddress, username=user, password=password,
                                               command=status_command, return_output=True)
    assert "Up" in status, "Identity Service not Running"
    print("Identity Service Running")
    # Cleanup Any old Queues Before main testing starts
    cleanup()


@pytest.mark.core_services_mvp
def test_identify_element():
    cleanup()
    bind_queues()
    identified_errors = []
    #global elementUuid

    print('Sending Identify Element Message\n')
    # Publish the message
    af_support_tools.rmq_publish_message(host=ipaddress, rmq_username=rmq_username,
                                         rmq_password=rmq_password,
                                         exchange='exchange.dell.cpsd.eids.identity.request',
                                         routing_key='dell.cpsd.eids.identity.request',
                                         headers={'__TypeId__': 'dell.cpsd.core.identity.identify.element'},
                                         payload=identifyelement,
                                         payload_type='json')

    assert waitForMsg('test.identity.request'), "Message took too long to return"
    return_message = af_support_tools.rmq_consume_message(host=ipaddress, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.identity.request')

    published_json = json.loads(identifyelement, encoding='utf-8')
    return_json = json.loads(return_message, encoding='utf-8')

    # Compare the 2 files. If they match the message was successfully published & received to rabbitMQ test queue.
    print("Verifying Message sent to RabbitMQ...")
    assert published_json == return_json, "Message Not Published to RabbitMQ"
    print('Published Message Received.')

    print('\nConsuming Response Message...')
    # At this stage we have verified that a message was published & received.
    # Next we need to check that we got the expected Response to our request.
    assert waitForMsg('test.identity.response'), "Message took too long to return"
    return_message = af_support_tools.rmq_consume_message(host=ipaddress, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.identity.response')

    # Convert the returned message to json format and run asserts on the expected output.
    return_json = json.loads(return_message, encoding='utf-8')

    # Verify the response message has the expected format & parameters
    print("Checking Response Message attributes...")
    if not return_json['timestamp']:
        identified_errors.append("No timestamp in message")
    if return_json['correlationId'] not in identifyelement:
        identified_errors.append("correlationId error")

    # Get number of element identifications in response
    total_ele_idents = len(return_json['elementIdentifications'])
    for _ in range(total_ele_idents):
        if return_json['elementIdentifications'][_]['correlationUuid'] not in identifyelement:
            identified_errors.append("correlationUuid error")
        assert return_json['elementIdentifications'][_]['elementUuid']

    # Collect random element uuid for describe, from the total number of identified elements
    # We Subtract one from total_ele_idents to give use a random number from 0 to n
    total_ele_idents -= 1
    elementUuid = return_json['elementIdentifications'][random.randint(0, total_ele_idents)]['elementUuid']

    assert not identified_errors

    print('TEST: All requested CorrelationUuid have had elementUuid values returned: PASSED')
    print('\n*******************************************************')


@pytest.mark.core_services_mvp
def test_describe_element():
    cleanup()
    bind_queues()
    describe_errors = []

    # Define Describe message using elementUuid from previous test
    describeelement = '{"timestamp":"2017-01-27T14:51:00.570Z","correlationId":"5d7f6d34-4271-4593-9bad-1b95589e5189","reply-to":"dell.cpsd.eids.identity.request.hal.gouldc-mint","elementUuids":["' + elementUuid + '"]}'
    print("Sending Describe Element for elementUUID: {}...".format(elementUuid))

    # Publish the message
    af_support_tools.rmq_publish_message(host=ipaddress, rmq_username=rmq_username,
                                         rmq_password=rmq_password,
                                         exchange='exchange.dell.cpsd.eids.identity.request',
                                         routing_key='dell.cpsd.eids.identity.request',
                                         headers={'__TypeId__': 'dell.cpsd.core.identity.describe.element'},
                                         payload=describeelement,
                                         payload_type='json')

    assert waitForMsg('test.identity.request'), "Message took too long to return"
    return_message = af_support_tools.rmq_consume_message(host=ipaddress, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.identity.request')

    published_json = json.loads(describeelement, encoding='utf-8')
    return_json = json.loads(return_message, encoding='utf-8')

    # Compare the 2 files. If they match the message was successfully published & received.
    print("Verifying Message sent to RabbitMQ...")
    assert published_json == return_json
    print('Published Message Received.')

    print('\nConsuming Response Message...')
    # At this stage we have verified that a message was published & received.
    # Next we need to check that we got the expected Response to our request.
    assert waitForMsg('test.identity.response'), "Message took too long to return"
    return_message = af_support_tools.rmq_consume_message(host=ipaddress, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.identity.response')

    # Convert the returned message to json format and run asserts on the expected output.
    return_json = json.loads(return_message, encoding='utf-8')

    # Verify the response message has the expected format & parameters
    print("Checking Response Message attributes...")
    if not return_json['timestamp']:
        describe_errors.append("No timestamp in message")
    if return_json['correlationId'] not in describeelement:
        describe_errors.append("correlationId error")

    classification = return_json['elementDescriptions'][0]['classification']
    elementType = return_json['elementDescriptions'][0]['elementType']

    # Check values from elementdescribed response against IdentifyElements message, except for 'ELEMENT_UUID'
    for _ in range(len(return_json['elementDescriptions'][0]['businessKeys'])):
        if return_json['elementDescriptions'][0]['businessKeys'][_]['key'] != 'ELEMENT_UUID':
            value = return_json['elementDescriptions'][0]['businessKeys'][_]['value']
            if classification and elementType and value not in identifyelement:
                describe_errors.append('Element Described Message Error')

    assert not describe_errors
    print('TEST: All requested CorrelationUuid have had element description values returned: PASSED')
    print('\n*******************************************************')


#@pytest.mark.core_services_mvp
@pytest.mark.parametrize("payload_message", payload_keyaccuracy)
def test_key_accuracy(payload_message):
    cleanup()
    bind_queues()
    accuracy_errors = []
    global assigned_uuid

    print('Sending Identify Element Key Accuracy Messages\n')
    # Publish the message
    af_support_tools.rmq_publish_message(host=ipaddress, rmq_username=rmq_username,
                                         rmq_password=rmq_password,
                                         exchange='exchange.dell.cpsd.eids.identity.request',
                                         routing_key='dell.cpsd.eids.identity.request',
                                         headers={'__TypeId__': 'dell.cpsd.core.identity.identify.element'},
                                         payload=payload_message,
                                         payload_type='json')

    assert waitForMsg('test.identity.request'), "Message took too long to return"
    return_message = af_support_tools.rmq_consume_message(host=ipaddress, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.identity.request')

    published_json = json.loads(payload_message, encoding='utf-8')
    return_json = json.loads(return_message, encoding='utf-8')

    # Compare the 2 files. If they match the message was successfully published & received.
    print("Verifying Message sent to RabbitMQ...")
    assert published_json == return_json
    print('Published Message Received.')

    print('\nConsuming Response Message...')

    # At this stage we have verified that a message was published & received.
    # Next we need to check that we got the expected Response to our request.
    assert waitForMsg('test.identity.response'), "Message took too long to return"
    return_message = af_support_tools.rmq_consume_message(host=ipaddress, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.identity.response')

    # Convert the returned message to json format and run asserts on the expected output.
    return_json = json.loads(return_message, encoding='utf-8')

    # Verify the response message has the expected format & parameters
    print("Checking Response Message attributes...")
    if not return_json['timestamp']:
        accuracy_errors.append("No timestamp in message")
    if return_json['correlationId'] not in payload_message:
        accuracy_errors.append("correlationId error")

    for _ in range(len(return_json['elementIdentifications'])):
        if return_json['elementIdentifications'][_]['correlationUuid'] not in payload_message:
            accuracy_errors.append("correlationUuid error")
        assert return_json['elementIdentifications'][_]['elementUuid']

        if payload_message == keyaccuracyid_abc:
            assigned_uuid = return_json['elementIdentifications'][_]['elementUuid']
            print('Response UUID Generated: ', assigned_uuid)
        else:
            identified_uuid = return_json['elementIdentifications'][_]['elementUuid']
            print('Identified UUID: ', identified_uuid)

        if payload_message == keyaccuracyid_neg:
            if identified_uuid == assigned_uuid:
                accuracy_errors.append("Error: ElementUuid match for Key Accuracy negative")
        elif payload_message != keyaccuracyid_abc:
            if identified_uuid != assigned_uuid:
                accuracy_errors.append("ElementUuid Mismatch for Key Accuracy")

    assert not accuracy_errors
    print('TEST: KeyAccuracy test pass.')
    print('\n*******************************************************')

#@pytest.mark.core_services_mvp
@pytest.mark.parametrize("payload_message", payload_negative_messages)
def test_negative_messages(payload_message):
    cleanup()
    bind_queues()
    negative_errors = []

    if payload_message == describe_no_element:
        header = 'dell.cpsd.core.identity.describe.element'
    else:
        header = 'dell.cpsd.core.identity.identify.element'

    # Publish the message
    print('Sending Negative test Messages\n')
    af_support_tools.rmq_publish_message(host=ipaddress, rmq_username=rmq_username,
                                         rmq_password=rmq_password,
                                         exchange='exchange.dell.cpsd.eids.identity.request',
                                         routing_key='dell.cpsd.eids.identity.request',
                                         headers={'__TypeId__': header},
                                         payload=payload_message,
                                         payload_type='json')

    assert waitForMsg('test.identity.request'), "Message took too long to return"
    return_message = af_support_tools.rmq_consume_message(host=ipaddress, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.identity.request')

    published_json = json.loads(payload_message, encoding='utf-8')
    return_json = json.loads(return_message, encoding='utf-8')

    # Compare the 2 files. If they match the message was successfully published & received.
    print("Verifying Message sent to RabbitMQ...")
    assert published_json == return_json
    print('Published Message Received.')
    print('\nConsuming Response Message...')
    # At this stage we have verified that a message was published & received.
    # Next we need to check that we got the expected Response to our request.
    assert waitForMsg('test.identity.response'), "Message took too long to return"
    return_message = af_support_tools.rmq_consume_message(host=ipaddress, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.identity.response')

    # Convert the returned message to json format and run asserts on the expected output.
    print("Checking Response Message attributes...")
    return_json = json.loads(return_message, encoding='utf-8')

    # Verify the response message has the expected format & parameters
    if not return_json['timestamp']:
        negative_errors.append("No timestamp in message")
    if return_json['correlationId'] not in payload_message:
        negative_errors.append("correlationId error")

    if payload_message == ident_no_element_type:
        if return_json['errorMessage'] != 'EIDS1004E Invalid request message':
            negative_errors.append("Error message incorrect")
            print("Incorrect error message responce" + return_json)
    if payload_message == describe_no_element:
        if return_json['errorMessage'] != 'EIDS1006E Failed to describe element':
            negative_errors.append("Error message incorrect")
            print("Incorrect error message responce" + return_json)

    assert not negative_errors
    print("Negative Message Test Passed")

#######################################################################################################################

# Delete the test queue
def cleanup():
    print('Cleaning up...')

    af_support_tools.rmq_delete_queue(host=ipaddress, rmq_username=rmq_username, rmq_password=rmq_password,
                                      queue='test.identity.request')

    af_support_tools.rmq_delete_queue(host=ipaddress, rmq_username=rmq_username, rmq_password=rmq_password,
                                      queue='test.identity.response')


# Create & bind the test queues
def bind_queues():
    print('Creating the test EIDS Queues')
    af_support_tools.rmq_bind_queue(host=ipaddress,
                                    rmq_username=rmq_username, rmq_password=rmq_password,
                                    queue='test.identity.request',
                                    exchange='exchange.dell.cpsd.eids.identity.request',
                                    routing_key='#')

    af_support_tools.rmq_bind_queue(host=ipaddress,
                                    rmq_username=rmq_username, rmq_password=rmq_password,
                                    queue='test.identity.response',
                                    exchange='exchange.dell.cpsd.eids.identity.response',
                                    routing_key='#')


def waitForMsg(queue):
    print("Waiting for message on queue:" + queue)
    # This function keeps looping until a message is in the specified queue. We do need it to timeout and throw an error
    # if a message never arrives. Once a message appears in the queue the function is complete and main continues.
    # The length of the queue, it will start at 0 but as soon as we get a response it will increase
    q_len = 0
    # Represents the number of seconds that have gone by since the method started
    timeout = 0
    # Max number of seconds to wait
    max_timeout = 10
    # Amount of time in seconds that the loop is going to wait on each iteration
    sleeptime = 1

    while q_len < 1:
        time.sleep(sleeptime)
        timeout += sleeptime

        q_len = af_support_tools.rmq_message_count(host=ipaddress,
                                                   port=5672,
                                                   rmq_username=rmq_username,
                                                   rmq_password=rmq_password,
                                                   queue=queue)

        if timeout > max_timeout:
            print('ERROR: Message took too long to return. Something is wrong')
            cleanup()
            return False
    return True
