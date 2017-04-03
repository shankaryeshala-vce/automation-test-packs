#!/usr/bin/python
# Author:cullia
# Updated by: olearj10
# Date: 3 April 2017
# Revision:2.1
# Code Reviewed by:
# Description: Standalone testing of the Identity Service. No other services are used. No system needs to be defined
# to run this test.

import af_support_tools
import pytest
import json
import identity_lib

try:
    env_file = 'env.ini'
    ipaddress = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='hostname')

except:
    print('Possible configuration error')

# Use this to by-pass the config.ini file
#ipaddress = '10.3.60.129'

payload_file = 'identity_service/payload.ini'
payload_header = 'identity_service'
payload_property_identifyelement = 'identifyelement'
payload_property_describeelement = 'describeelement'
payload_property_keyaccuracy = 'keyaccuracy'
payload_property_keyaccuracy_ab_ac_neg = ['keyaccuracyid_ab', 'keyaccuracyid_ac', 'keyaccuracyid_neg']
payload_property_negative_messages = ['ident_no_element_type', 'describe_no_element']


#payload_property_negative_messages = ['ident_no_element_type', 'ident_no_class', 'ident_no_context', 'describe_no_element']


# Always specify user names & password here at the start. Makes changing them later much easier,
rmq_username = 'test'
rmq_password = 'test'
cli_username = 'root'
cli_password = 'V1rtu@1c3!'
port = 5672

# Cleanup Any old Queues Before testing starts
identity_lib.cleanup(ipaddress)
print("Binding Test Queses & Creating Payload Messages")
identity_lib.bind_queues(ipaddress)
identity_lib.create_messages()


@pytest.mark.core_services_mvp
def test_ident_status():
    print('\nRunning Identity Status test on system: ', ipaddress)
    status_command = 'docker ps | grep identity-service'
    status = af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                               command=status_command, return_output=True)
    assert "Up" in status, "Identity Service not Running"
    print("Identity Service Running")


@pytest.mark.core_services_mvp
def test_identify_element():
    identity_lib.cleanup(ipaddress)
    identity_lib.bind_queues(ipaddress)
    identified_errors = []

    # Get the payload from the .ini file that will be used in the Published message
    the_payload = af_support_tools.get_config_file_property(config_file=payload_file,
                                                            heading=payload_header,
                                                            property=payload_property_identifyelement)

    print('Sending Identify Element Message\n')

    # Publish the message
    af_support_tools.rmq_publish_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                         rmq_password=rmq_password,
                                         exchange='exchange.dell.cpsd.eids.identity.request',
                                         routing_key='dell.cpsd.eids.identity.request',
                                         headers={'__TypeId__': 'dell.cpsd.core.identity.identify.element'},
                                         payload=the_payload,
                                         payload_type='json')

    identity_lib.waitForMsg('test.identity.request', ipaddress)
    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.identity.request')

    published_json = json.loads(the_payload, encoding='utf-8')
    return_json = json.loads(return_message, encoding='utf-8')

    # Compare the 2 files. If they match the message was successfully published & received to rabbitMQ test queue.
    print("Verifying Message sent to RabbitMQ...")
    assert published_json == return_json, "Message Not Published to RabbitMQ"
    print('Published Message Received.')

    print('\nConsuming Response Message...')
    # At this stage we have verified that a message was published & received.
    # Next we need to check that we got the expected Response to our request.
    identity_lib.waitForMsg('test.identity.response', ipaddress)
    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.identity.response')

    # Convert the returned message to json format and run asserts on the expected output.
    return_json = json.loads(return_message, encoding='utf-8')

    # Verify the response message has the expected format & parameters
    print("Checking Response Message attributes...")
    if not return_json['timestamp']:
        identified_errors.append("No timestamp in message")
    if return_json['correlationId'] not in the_payload:
        identified_errors.append("correlationId error")

    for _ in range(len(return_json['elementIdentifications'])):
        if return_json['elementIdentifications'][_]['correlationUuid'] not in the_payload:
            identified_errors.append("correlationUuid error")
        assert return_json['elementIdentifications'][_]['elementUuid']

    assert not identified_errors

    print('TEST: All requested CorrelationUuid have had elementUuid values returned: PASSED')
    print('\n*******************************************************')


@pytest.mark.core_services_mvp
@pytest.mark.parametrize("elementuuid", identity_lib.get_element_uuids(ipaddress))
def test_describe_element(elementuuid):
    identity_lib.cleanup(ipaddress)
    identity_lib.bind_queues(ipaddress)
    identity_lib.create_describe_message(elementuuid)
    describe_errors = []

    # Get identify elements payload from the .ini file that will be used to verify elements described
    ident_elements = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                               property=payload_property_identifyelement)

    # Get the payload from the .ini file that will be used in the Published message
    the_payload = af_support_tools.get_config_file_property(config_file=payload_file,
                                                            heading=payload_header,
                                                            property=payload_property_describeelement)

    print('Sending Describe Element...\n')

    # Publish the message
    af_support_tools.rmq_publish_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                         rmq_password=rmq_password,
                                         exchange='exchange.dell.cpsd.eids.identity.request',
                                         routing_key='dell.cpsd.eids.identity.request',
                                         headers={'__TypeId__': 'dell.cpsd.core.identity.describe.element'},
                                         payload=the_payload,
                                         payload_type='json')

    identity_lib.waitForMsg('test.identity.request', ipaddress)
    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.identity.request')

    published_json = json.loads(the_payload, encoding='utf-8')
    return_json = json.loads(return_message, encoding='utf-8')

    # Compare the 2 files. If they match the message was successfully published & received.
    print("Verifying Message sent to RabbitMQ...")
    assert published_json == return_json
    print('Published Message Received.')

    print('\nConsuming Response Message...')
    # At this stage we have verified that a message was published & received.
    # Next we need to check that we got the expected Response to our request.
    identity_lib.waitForMsg('test.identity.response', ipaddress)
    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.identity.response')

    # Convert the returned message to json format and run asserts on the expected output.
    return_json = json.loads(return_message, encoding='utf-8')

    # Verify the response message has the expected format & parameters
    print("Checking Response Message attributes...")
    if not return_json['timestamp']:
        describe_errors.append("No timestamp in message")
    if return_json['correlationId'] not in the_payload:
        describe_errors.append("correlationId error")

    classification = return_json['elementDescriptions'][0]['classification']
    elementType = return_json['elementDescriptions'][0]['elementType']

    # Check values from elementdescribed response against IdentifyElements message, except for 'ELEMENT_UUID'
    for _ in range(len(return_json['elementDescriptions'][0]['businessKeys'])):
        if return_json['elementDescriptions'][0]['businessKeys'][_]['key'] != 'ELEMENT_UUID':
            value = return_json['elementDescriptions'][0]['businessKeys'][_]['value']
            if classification and elementType and value not in ident_elements:
                describe_errors.append('Element Described Message Error')

    assert not describe_errors
    print('TEST: All requested CorrelationUuid have had element description values returned: PASSED')
    print('\n*******************************************************')


@pytest.mark.core_services_mvp
def test_key_accuracy_abc():
    identity_lib.cleanup(ipaddress)
    identity_lib.bind_queues(ipaddress)
    accuracy_errors = []
    global assigned_uuid
    # An element that is identifiable by 3 business keys and the key accuracy was set at 2
    # User should be later able to identify that same element by any combinations of two business keys

    # Get the payload from the .ini file that will be used in the Published message
    the_payload = af_support_tools.get_config_file_property(config_file=payload_file,
                                                            heading=payload_header,
                                                            property=payload_property_keyaccuracy)

    print('Sending Identify Element Key Accuracy Message ABC\n')
    # Publish the message
    af_support_tools.rmq_publish_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                         rmq_password=rmq_password,
                                         exchange='exchange.dell.cpsd.eids.identity.request',
                                         routing_key='dell.cpsd.eids.identity.request',
                                         headers={'__TypeId__': 'com.dell.cpsd.identity.service.api.IdentifyElements'},
                                         payload=the_payload,
                                         payload_type='json')

    identity_lib.waitForMsg('test.identity.request', ipaddress)
    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.identity.request')

    published_json = json.loads(the_payload, encoding='utf-8')
    return_json = json.loads(return_message, encoding='utf-8')

    # Compare the 2 files. If they match the message was successfully published & received.
    print("Verifying Message sent to RabbitMQ...")
    assert published_json == return_json
    print('Published Message Received.')

    print('\nConsuming Response Message...')
    identity_lib.waitForMsg('test.identity.response', ipaddress)
    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.identity.response')

    # Convert the returned message to json format and run asserts on the expected output.
    return_json = json.loads(return_message, encoding='utf-8')

    # Verify the response message has the expected format & parameters
    print("Checking Response Message attributes...")
    if not return_json['timestamp']:
        accuracy_errors.append("No timestamp in message")
    if return_json['correlationId'] not in the_payload:
        accuracy_errors.append("correlationId error")

    for _ in range(len(return_json['elementIdentifications'])):
        if return_json['elementIdentifications'][_]['correlationUuid'] not in the_payload:
            accuracy_errors.append("correlationUuid error")
        assert return_json['elementIdentifications'][_]['elementUuid']
        assigned_uuid = return_json['elementIdentifications'][_]['elementUuid']

    assert not accuracy_errors
    print('Response UUID Generated: ', assigned_uuid)
    print('TEST: KeyAccuracy ABC, CorrelationUuid have had elementuuid values returned: PASSED')
    print('\n*******************************************************')

@pytest.mark.core_services_mvp
@pytest.mark.parametrize("payload_property", payload_property_keyaccuracy_ab_ac_neg)
def test_key_accuracy_ab_ac_neg(payload_property):
    identity_lib.cleanup(ipaddress)
    identity_lib.bind_queues(ipaddress)
    accuracy_errors = []

    # ******************************************************************************************************************
    # Get the payload from the .ini file that will be used in the Published message
    the_payload = af_support_tools.get_config_file_property(config_file=payload_file,
                                                            heading=payload_header,
                                                            property=payload_property)

    print('Sending Identify Element Key Accuracy Messages\n')
    # Publish the message
    af_support_tools.rmq_publish_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                         rmq_password=rmq_password,
                                         exchange='exchange.dell.cpsd.eids.identity.request',
                                         routing_key='dell.cpsd.eids.identity.request',
                                         headers={'__TypeId__': 'dell.cpsd.core.identity.identify.element'},
                                         payload=the_payload,
                                         payload_type='json')

    identity_lib.waitForMsg('test.identity.request', ipaddress)
    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.identity.request')

    published_json = json.loads(the_payload, encoding='utf-8')
    return_json = json.loads(return_message, encoding='utf-8')

    # Compare the 2 files. If they match the message was successfully published & received.
    print("Verifying Message sent to RabbitMQ...")
    assert published_json == return_json
    print('Published Message Received.')

    print('\nConsuming Response Message...')

    # At this stage we have verified that a message was published & received.
    # Next we need to check that we got the expected Response to our request.
    identity_lib.waitForMsg('test.identity.response', ipaddress)
    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.identity.response')

    # Convert the returned message to json format and run asserts on the expected output.
    return_json = json.loads(return_message, encoding='utf-8')

    # Verify the response message has the expected format & parameters
    print("Checking Response Message attributes...")
    if not return_json['timestamp']:
        accuracy_errors.append("No timestamp in message")
    if return_json['correlationId'] not in the_payload:
        accuracy_errors.append("correlationId error")

    for _ in range(len(return_json['elementIdentifications'])):
        if return_json['elementIdentifications'][_]['correlationUuid'] not in the_payload:
            accuracy_errors.append("correlationUuid error")
        assert return_json['elementIdentifications'][_]['elementUuid']
        identified_uuid = return_json['elementIdentifications'][_]['elementUuid']
        print('Identified UUID: ', identified_uuid)

        if payload_property == 'keyaccuracyid_neg':
            if identified_uuid == assigned_uuid:
                accuracy_errors.append("Error: ElementUuid match for Key Accuracy negative")
        else:
            if identified_uuid != assigned_uuid:
                accuracy_errors.append("ElementUuid Mismatch for Key Accuracy")

    assert not accuracy_errors
    print('TEST: KeyAccuracy, CorrelationUuid have had elementuuid values returned: PASSED')
    print('\n*******************************************************')

@pytest.mark.core_services_mvp
@pytest.mark.parametrize("payload_property", payload_property_negative_messages)
def test_negative_messages(payload_property):
    identity_lib.cleanup(ipaddress)
    identity_lib.bind_queues(ipaddress)
    negative_errors = []

    if payload_property == 'describe_no_element':
        header = 'dell.cpsd.core.identity.describe.element'
    else:
        header = 'dell.cpsd.core.identity.identify.element'

    # ***************************************************************************************************************
    # Get the payload from the .ini file that will be used in the Published message
    the_payload = af_support_tools.get_config_file_property(config_file=payload_file,
                                                            heading=payload_header,
                                                            property=payload_property)

    # Publish the message
    print('Sending Negative test Messages\n')
    af_support_tools.rmq_publish_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                         rmq_password=rmq_password,
                                         exchange='exchange.dell.cpsd.eids.identity.request',
                                         routing_key='dell.cpsd.eids.identity.request',
                                         headers={'__TypeId__': header},
                                         payload=the_payload,
                                         payload_type='json')

    identity_lib.waitForMsg('test.identity.request', ipaddress)
    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.identity.request')

    published_json = json.loads(the_payload, encoding='utf-8')
    return_json = json.loads(return_message, encoding='utf-8')

    # Compare the 2 files. If they match the message was successfully published & received.
    print("Verifying Message sent to RabbitMQ...")
    assert published_json == return_json
    print('Published Message Received.')
    print('\nConsuming Response Message...')
    # At this stage we have verified that a message was published & received.
    # Next we need to check that we got the expected Response to our request.
    identity_lib.waitForMsg('test.identity.response', ipaddress)
    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.identity.response')

    # Convert the returned message to json format and run asserts on the expected output.
    print("Checking Response Message attributes...")
    return_json = json.loads(return_message, encoding='utf-8')

    # Verify the response message has the expected format & parameters
    if not return_json['timestamp']:
        negative_errors.append("No timestamp in message")
    if return_json['correlationId'] not in the_payload:
        negative_errors.append("correlationId error")

    if payload_property == "ident_no_element_type":
        if return_json['errorMessage'] != 'EIDS1004E Invalid request message':
            negative_errors.append("Error message incorrect")
            print("Incorrect error message responce" + return_json)
    if payload_property == "describe_no_element":
        if return_json['errorMessage'] != 'EIDS1006E Failed to describe element':
            negative_errors.append("Error message incorrect")
            print("Incorrect error message responce" + return_json)

    assert not negative_errors
    print("Negative Message Test Passed")

#######################################################################################################################
