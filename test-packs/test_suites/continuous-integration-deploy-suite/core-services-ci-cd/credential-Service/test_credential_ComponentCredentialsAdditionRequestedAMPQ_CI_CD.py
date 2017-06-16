#!/usr/bin/python
# Author: cullia
# Revision: 2.0
# Code Reviewed by:
# Description: This will test the Credential Service. Feature & negative tests are include. This can be run on a system
# with or without a system configured. But it can only be run once on any system.

import af_support_tools
import pytest
import json
import time
import unittest


# Payloads from symphony-sds.ini:- location: continuous-integration-deploy-suite/symphony-sds.ini
try:
    payload_file = 'continuous-integration-deploy-suite/symphony-sds.ini'
    #payload_file = 'symphony-sds.ini'
    payload_heading = 'credential_tests'
    payload_property_add = 'cs_cred_addition'
    payload_property_req = 'cs_cred_request'
    payload_property_neg1 = 'cs_no_comp_addition'
    payload_property_neg2 = 'ca_dup_ep_addition'
    payload_property_neg3 = 'cs_invalid_json'
    payload_property_neg4 = 'cs_invalid_msg_prop'
    payload_property_neg5 = 'cs_req_invalid_uuid'

    env_file = 'env.ini'
    ipaddress = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='hostname')
    cli_username = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='username')
    cli_password = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='password')
except:
    print('Possible configuration error')

port = 5672
rmq_username = 'guest'
rmq_password = 'guest'

# Add & verify component credentials
#@pytest.mark.core_services_mvp
#@unittest.skip("skipping till this is modified to use new credentials service API")
def test_CS_ComponentCredentials_CI():
    print('\nRunning mvp test on system: ', ipaddress)
    cleanup()

    bindQueues()

    # Create the payload messages using valid values to be used in the individual tests.
    createCSPayload()

    print('************************************************')

    CS_CredAdd_CredReq()

######################################################################################################################

# Add & verify component credentials
#@pytest.mark.core_services_mvp_extended
#@unittest.skip("skipping till this is modified to use new credentials service API")
def test_CS_ComponentCredentials():
    print('\nRunning mvp extended test on system: ', ipaddress)
    cleanup()

    bindQueues()

    # Create the payload messages using valid values to be used in the individual tests.
    createCSPayload()

    print('************************************************')

    CS_CredAdd_CredReq()
    #CS_CredAdd_duplicateComponents()
    CS_CredAdd_duplicateEndpoints()
    CS_CredAdd_noCompUuid()
    CS_CredAdd_DBdown()
    CS_CredReq_DBdown()
    CS_CredReq_invalidJson()
    CS_CredReq_invalidMsgProp()
    CS_CredReq_invalidUuid()

    cleanup()


######################################################################################################################
# 1. Test that a single component credentials can be added and retrieved
def CS_CredAdd_CredReq():
    print("\nRunning test No. 1 - Add and retrieve component credentials...")

    # Calling and using the payload from symphony-sds.ini file
    the_payload = af_support_tools.get_config_file_property(config_file=payload_file,
                                                            heading=payload_heading,
                                                            property=payload_property_add)

    publishMessageCredAdd(the_payload)

    time.sleep(2)

    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.component.credential.request')

    validJson(return_message)
    published_json = json.loads(the_payload, encoding='utf-8')
    return_json = json.loads(return_message, encoding='utf-8')

    # Checking the "Message received" matches the "Message published"
    assert published_json == return_json
    print('TEST: Published Message Received: PASSED')

    time.sleep(2)

    # Check that the credentials added are now returned on request
    # Payload for listing the component credentials
    the_payload = af_support_tools.get_config_file_property(config_file=payload_file,
                                                            heading=payload_heading,
                                                            property=payload_property_req)

    publishMessageCredReq(the_payload)

    time.sleep(2)

    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.component.credential.request')

    validJson(return_message)
    published_json = json.loads(the_payload, encoding='utf-8')
    return_json = json.loads(return_message, encoding='utf-8')

    # Checking the "Message received" matches the "Message published"
    assert published_json == return_json
    print('TEST: Published Message Received: PASSED')
    print(published_json)
    time.sleep(2)

    # Consume the response message
    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.component.credential.response')
    print('Return Message from rmq_consume message:')
    print(return_message)
    return_json = json.loads(return_message, encoding='utf-8')

    if 'error' in return_message:
        print("something is wrong")
        return

    # checking values in request queue
    assert return_json['messageProperties']['correlationId']
    assert return_json['messageProperties']['replyTo']
    assert return_json['messageProperties']['timestamp']
    assert return_json['credentials'][0]['componentUuid']
    assert return_json['credentials'][0]['endpointUuid']
    assert return_json['credentials'][0]['name']
    assert return_json['credentials'][0]['credentialElement']
    assert return_json['credentials'][1]['componentUuid']
    assert return_json['credentials'][1]['endpointUuid']
    assert return_json['credentials'][1]['name']
    assert return_json['credentials'][1]['credentialElement']
    assert return_json['credentials'][2]['componentUuid']
    assert return_json['credentials'][2]['endpointUuid']
    assert return_json['credentials'][2]['name']
    assert return_json['credentials'][2]['credentialElement']

    print('Test 1 of 9: All expected credentials returned\n')
    print('************************************************')
    time.sleep(1)


# 2, Negative Test - Components with the same uuid should not be added to the DB
# 2. Feature Test - Component with the same uuid can be updated in the DB now
def CS_CredAdd_duplicateComponents():
    print("Running test No. 2 - Feature Test: Component with same UUID can be updated in DB...")

    clearLogFiles()

    # Calling and using the payload from symphony-sds.ini file
    the_payload = af_support_tools.get_config_file_property(config_file=payload_file,
                                                            heading=payload_heading,
                                                            property=payload_property_add)

    publishMessageCredAdd(the_payload)
    #print('Payload:\n')
    #print(the_payload)
    time.sleep(2)

    # Consume received msg
    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.component.credential.response')
    validJson(return_message)
    #print('Return message:')
    #print(return_message)
    published_json = json.loads(the_payload, encoding='utf-8')
    return_json = json.loads(return_message, encoding='utf-8')

    # Checking the "Message received" matches the "Message published"
    assert published_json == return_json
    print('Published Message Received: PASSED')

    # Check that that the returned message was received and has the valid error code
    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.component.credential.response')
    print('Return Message from rmq_consume message:')
    print(return_message)
    return_json = json.loads(return_message, encoding='utf-8')
    assert return_json['errors'][0]['code'] == "VAMQP1012E"

    sendCommand = 'docker ps | grep credentials-service | awk \'{system("docker exec -i "$1" cat /opt/dell/cpsd/credentials/logs/credentials-service-info.log") }\''
    error1 = "A different object with the same identifier value was already associated with the session"
    error2 = "(attempt 3)"
    error3 = "VAMQP1009E"

    # Return contents of the credentials-service-error.log
    my_return_text = af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                                       command=sendCommand, return_output=True)

    assert error1 in my_return_text
    assert error2 in my_return_text
    assert error3 in my_return_text

    print('Test 2 of 9: Valid error messages are returned\n')
    print('************************************************')
    time.sleep(1)


# 3. Negative Test - Endpoints with the same uuid should not be added to the DB
def CS_CredAdd_duplicateEndpoints():
    print("Running test No. 3 - Negative: Cannot add same endpoints...")

    clearLogFiles()

    # Calling and using the payload from symphony-sds.ini file
    the_payload = af_support_tools.get_config_file_property(config_file=payload_file,
                                                            heading=payload_heading,
                                                            property=payload_property_neg2)

    publishMessageCredAdd(the_payload)

    time.sleep(2)

    # Consume request queue and check
    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.component.credential.request')

    validJson(return_message)
    published_json = json.loads(the_payload, encoding='utf-8')
    return_json = json.loads(return_message, encoding='utf-8')

    # Checking the "Message received" matches the "Message published"
    assert published_json == return_json
    print('Published Message Received: PASSED')

    # Check that that the returned message was received and has the valid error code
    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.component.credential.response')
    print('Return Message from rmq_consume message:')
    print(return_message)
    return_json = json.loads(return_message, encoding='utf-8')
    assert return_json['errors'][0]['code'] == "VAMQP1012E"

    sendCommand = 'docker ps | grep credentials-service | awk \'{system("docker exec -i "$1" cat /opt/dell/cpsd/credentials/logs/credentials-service-error.log") }\''
    error1 = "A different object with the same identifier value was already associated with the session"
    error2 = "(attempt 3)"
    error3 = "VAMQP1009E"

    # Return contents of the credentials-service-error.log
    my_return_text = af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                                       command=sendCommand, return_output=True)

    assert error1 in my_return_text
    assert error2 in my_return_text
    assert error3 in my_return_text

    print('Test 3 of 9: Valid error messages are returned\n')
    print('************************************************')
    time.sleep(1)


# 4, Negative Test - A "ComponentCredentialsAdditionRequested" message is NOT processed with NO componentUuid value set
def CS_CredAdd_noCompUuid():
    print("Running test No. 4 - No componentUuid value set...")

    # Calling and using the payload from symphony-sds.ini file
    the_payload = af_support_tools.get_config_file_property(config_file=payload_file,
                                                            heading=payload_heading,
                                                            property=payload_property_neg1)

    publishMessageCredAdd(the_payload)

    time.sleep(2)

    # Consume received
    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.component.credential.request')

    validJson(return_message)
    published_json = json.loads(the_payload, encoding='utf-8')
    return_json = json.loads(return_message, encoding='utf-8')

    # Checking the "Message received" matches the "Message published"
    assert published_json == return_json
    print('Published Message Received: PASSED')

    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.component.credential.response')

    return_json = json.loads(return_message, encoding='utf-8')

    # TODO - Find out the expected behaviour. Currently there is a defect. DE11732

    print('Test 4 of 9: THIS TEST IS INCOMPLETE. THERE IS A DEFECT\n')
    print('************************************************')
    time.sleep(1)


# 5. Negative Test - Request addition of credentials when Postgres database is down
def CS_CredAdd_DBdown():
    # Expected behavior - 3 attempts in the credentials service log and an error message in the RabbitMQ UI console

    print("Running test No. 5 - Cannot add when DB is down...")
    clearLogFiles()

    # Commands to be used to stop & start the the database
    sendShutDBcommand = 'service postgresql-9.6.service stop'
    sendStartDBcommand = 'service postgresql-9.6.service start'

    print("Stopping PostgresDB...")
    af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                      command=sendShutDBcommand,
                                      return_output=False)

    # Get the payload data from the config symphony-sds.ini file.
    the_payload = af_support_tools.get_config_file_property(config_file=payload_file,
                                                            heading=payload_heading,
                                                            property=payload_property_add)

    # Publish the message to credentials.request
    publishMessageCredAdd(the_payload)

    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.component.credential.request')

    validJson(return_message)
    published_json = json.loads(the_payload, encoding='utf-8')
    return_json = json.loads(return_message, encoding='utf-8')

    # Checking the "Message received" matches the "Message published"
    assert published_json == return_json
    print('Published Message Received: PASSED')

    time.sleep(5)  # Need to wait as the response here takes longer (3 attempts)

    # Check that that the response message was received and has the valid error code
    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.component.credential.response')

    return_json = json.loads(return_message, encoding='utf-8')
    assert return_json['errors'][0]['code'] == "VAMQP1012E"

    sendCommand = 'docker ps | grep credentials-service | awk \'{system("docker exec -i "$1" cat /opt/dell/cpsd/credentials/logs/credentials-service-error.log") }\''
    error1 = "Unable to acquire JDBC Connection"
    error2 = "(attempt 3)"
    error3 = "VAMQP1009E"

    time.sleep(3)  # Need to wait as the response here takes longer (3 attempts)

    # Return contents of the credentials-service-error.log
    my_return_text = af_support_tools.send_ssh_command(host=ipaddress, username=cli_username,
                                                       password=cli_password,
                                                       command=sendCommand, return_output=True)

    # Starting the DB before the asserts in case they fail. This way the DB will be up.
    print("Starting PostgresDB...")
    af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                      command=sendStartDBcommand, return_output=False)

    assert error1 in my_return_text
    assert error2 in my_return_text
    assert error3 in my_return_text

    time.sleep(3)

    print('Test 5 of 9: Valid errors when DB down on cred add\n')
    print('************************************************')
    time.sleep(1)


# 6. Negative Test - Request return of credentials when Postgres database is down
def CS_CredReq_DBdown():
    # Expected behavior - 3 attempts in the credentials service log and an error message in the RabbitMQ UI console

    print("Running test No. 6 - Cannot request when DB is down...")
    clearLogFiles()

    # Commands to stop & start the the database
    sendShutDBcommand = 'service postgresql-9.6.service stop'
    sendStartDBcommand = 'service postgresql-9.6.service start'

    print("Stopping PostgresDB...")
    af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                      command=sendShutDBcommand,
                                      return_output=False)

    # Get the payload data from the config symphony-sds.ini file.
    the_payload = af_support_tools.get_config_file_property(config_file=payload_file,
                                                            heading=payload_heading,
                                                            property=payload_property_req)

    publishMessageCredReq(the_payload)

    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.component.credential.request')

    return_json = json.loads(return_message, encoding='utf-8')

    validJson(return_message)
    published_json = json.loads(the_payload, encoding='utf-8')
    return_json = json.loads(return_message, encoding='utf-8')

    # Checking the "Message received" matches the "Message published"
    assert published_json == return_json
    print('Published Message Received: PASSED')

    time.sleep(5)  # Need to wait as the response here takes longer (3 attempts)

    # Check that that the response message was received and has the valid error code
    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.component.credential.response')

    return_json = json.loads(return_message, encoding='utf-8')
    assert return_json['errors'][0]['code'] == "VAMQP1012E"

    # Send the command to credentials-service-error.log file
    sendCommand = 'docker ps | grep credentials-service | awk \'{system("docker exec -i "$1" cat /opt/dell/cpsd/credentials/logs/credentials-service-error.log") }\''
    error1 = "Unable to acquire JDBC Connection"
    error2 = "(attempt 3)"
    error3 = "VAMQP1009E"

    time.sleep(3)  # Need to wait as the response here takes longer (3 attempts)

    # Return contents of the credentials-service-error.log
    my_return_text = af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                                       command=sendCommand, return_output=True)

    # Starting the DB before the asserts in case they fail. This way the DB will be up.
    print("Starting PostgresDB...")
    af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                      command=sendStartDBcommand, return_output=False)

    assert error1 in my_return_text
    assert error2 in my_return_text
    assert error3 in my_return_text

    print('Test 6 of 9: Valid errors when DB down on cred req\n')
    print('************************************************')
    time.sleep(1)


# Negative Test 7. Invalid json file
def CS_CredReq_invalidJson():
    print("Running test No. 7 - Invalid json file...")

    clearLogFiles()

    print('check log file')
    time.sleep(30)

    the_payload = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_heading,
                                                            property=payload_property_neg3)

    publishMessageCredReq(the_payload)

    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.component.credential.request')

    try:
        return_json = json.loads(return_message, encoding='utf-8')
        i_am_json = True
    except Exception:
        i_am_json = False

    assert i_am_json == False
    if i_am_json == False:
        print('Verified json is invalid')

    sendCommand = 'docker ps | grep credentials-service | awk \'{system("docker exec -i "$1" cat /opt/dell/cpsd/credentials/logs/credentials-service-error.log") }\''
    error1 = "VAMQP1008E AMQP error (attempt 1)"
    error2 = "expected close marker for Object"
    error3 = "(attempt 3)"

    # Return contents of the credentials-service-error.log
    my_return_text = af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                                       command=sendCommand, return_output=True)

    time.sleep(3)

    assert error1 in my_return_text
    assert error2 in my_return_text
    assert error3 not in my_return_text

    print('Test 7 of 9: Invalid JSON: TEST PASSED\n')
    print('************************************************')
    time.sleep(1)


# Negative Test 8. Invalid Message Properties
def CS_CredReq_invalidMsgProp():
    print("Running test No. 8 - Request Credentials with Invalid message properties...")

    clearLogFiles()

    the_payload = af_support_tools.get_config_file_property(config_file=payload_file,
                                                            heading=payload_heading,
                                                            property=payload_property_neg4)

    publishMessageCredReq(the_payload)

    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.component.credential.request')

    validJson(return_message)
    published_json = json.loads(the_payload, encoding='utf-8')
    return_json = json.loads(return_message, encoding='utf-8')

    # Checking the "Message received" matches the "Message published"
    assert published_json == return_json
    print('Published Message Received: PASSED')

    # There will be no response message. We can verify the "test.component.credential.response" queue is empty.
    q_len = af_support_tools.rmq_message_count(host=ipaddress, port=port, rmq_username=rmq_username,
                                               rmq_password=rmq_password, queue='test.component.credential.response')
    assert q_len == 0

    sendCommand = 'docker ps | grep credentials-service | awk \'{system("docker exec -i "$1" cat /opt/dell/cpsd/credentials/logs/credentials-service-error.log") }\''
    error1 = "VAMQP2004E Message property [correlationId] is empty.]"
    error2 = "VAMQP1008E AMQP error"
    error3 = "(attempt 3)"

    my_return_text = af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                                       command=sendCommand, return_output=True)
    time.sleep(2)

    assert error1 in my_return_text
    assert error2 in my_return_text
    assert error3 not in my_return_text

    print('Test 8 of 9: Invalid Message Format: TEST PASSED\n')
    print('************************************************')
    time.sleep(1)


# Test 9. Invalid UUID in request - expect nothing
def CS_CredReq_invalidUuid():
    print("Running test No. 9 - Request creds with Invalid UUID in request...")

    clearLogFiles()

    the_payload = af_support_tools.get_config_file_property(config_file=payload_file,
                                                            heading=payload_heading,
                                                            property=payload_property_neg5)

    publishMessageCredReq(the_payload)

    time.sleep(1)

    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.component.credential.request')

    validJson(return_message)
    published_json = json.loads(the_payload, encoding='utf-8')
    return_json = json.loads(return_message, encoding='utf-8')

    # Checking the "Message received" matches the "Message published"
    assert published_json == return_json
    print('Published Message Received: PASSED')

    # Consume the response message
    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.component.credential.response')

    return_json = json.loads(return_message, encoding='utf-8')

    # checking values in request queue
    assert return_json['messageProperties']['correlationId']
    assert return_json['messageProperties']['replyTo']
    assert return_json['messageProperties']['timestamp']
    assert return_json['errors'][0]['code'] == "VAMQP1012E"

    # sendCommand = 'docker ps | credentials-service | awk \'{system("docker exec -i "$1" cat /opt/dell/rcm-fitness/services/credential/logs/credentials-service-error.log") }\''
    sendCommand = 'docker ps | grep credentials-service | awk \'{system("docker exec -i "$1" cat /opt/dell/cpsd/credentials/logs/credentials-service-error.log") }\''
    error1 = "VAMQP1008E AMQP error (attempt 1)"
    error2 = "No endpoints in database or something went wrong"
    error3 = "(attempt 3)"

    my_return_text = af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                                       command=sendCommand, return_output=True)

    time.sleep(2)

    assert error1 in my_return_text
    assert error2 in my_return_text
    assert error3 in my_return_text

    print('Test 9 of 9: As expected nothing returned\n')
    print('************************************************')
    time.sleep(1)


######################################################################################################################

def cleanup():
    print('Cleaning up...')

    af_support_tools.rmq_delete_queue(host=ipaddress, port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                      queue='test.component.credential.request')

    af_support_tools.rmq_delete_queue(host=ipaddress, port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                      queue='test.component.credential.response')


def bindQueues():
    af_support_tools.rmq_bind_queue(host=ipaddress, port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                    queue='test.component.credential.request',
                                    exchange='exchange.dell.cpsd.cms.credentials.request',
                                    routing_key='#')

    af_support_tools.rmq_bind_queue(host=ipaddress, port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                    queue='test.component.credential.response',
                                    exchange='exchange.dell.cpsd.cms.credentials.response',
                                    routing_key='#')


def clearLogFiles():
    sendCommand = 'docker ps | grep credentials-service | awk \'{system("docker exec -i "$1" sh -c \\"echo > /opt/dell/cpsd/credentials/logs/credentials-service-error.log\\"") }\''
    af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                      command=sendCommand, return_output=False)

    time.sleep(2)


def validJson(return_message):
    try:
        return_json = json.loads(return_message, encoding='utf-8')
        i_am_json = True
    except Exception:
        i_am_json = False

    assert i_am_json == True


def publishMessageCredAdd(the_payload):
    # Publish the message to system.addition.requested using the json file
    af_support_tools.rmq_publish_message(host=ipaddress, rmq_username=rmq_username, rmq_password=rmq_password,
                                         exchange='exchange.dell.cpsd.cms.credentials.request',
                                         routing_key='dell.cpsd.cms.component.credentials.addition.requested',
                                         headers={
                                             '__TypeId__': 'com.dell.cpsd.cms.component.credentials.addition.requested'},
                                         payload=the_payload)


def publishMessageCredReq(the_payload):
    af_support_tools.rmq_publish_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                         rmq_password=rmq_password,
                                         exchange='exchange.dell.cpsd.cms.credentials.request',
                                         routing_key='dell.cpsd.cms.credentials.requested',
                                         headers={'__TypeId__': 'com.dell.cpsd.cms.component.credentials.requested'},
                                         payload=the_payload,
                                         payload_type='json')


def createCSPayload():
    # This function creates the payloads to be used it the tests.
    print('Creating payload files')

    add_component_payload = '{"messageProperties":{"timestamp":"2010-01-01T12:00:00Z","correlationId":"test-add-cred-abcd-abcd-abcd-abcdabcdabcd","replyTo":"sds.localhost.localdomain"},"componentUuid":"8154b2cf-edf7-4c90-aca3-e9b2fc094d74","endpoints":[{"endpointUuid":"e0909b91-6700-4786-8912-162b1fad2e6c","credentials":[{"credentialUuid":"4300f6cc-9b79-4dce-94d7-44e7041fe982","name":"basic","credentialElement":{"username":"basic-user1","password":"basic-password1","community":""}},{"credentialUuid":"20ac5972-a8ff-4883-b3aa-a2e791286a89","name":"advanced","credentialElement":{"username":"advanced-user1","password":"advanced-password1","community":""}}]},{"endpointUuid":"cfcd61e9-8a6e-4b65-ad41-809974b6cec2","credentials":[{"credentialUuid":"22e2799d-9d1f-4b91-b5aa-9c2627c57fd6","name":"DEFAULT","credentialElement":{"username":"","password":"","community":"private"}}]}]}'

    af_support_tools.set_config_file_property(config_file=payload_file, heading=payload_heading,
                                              property=payload_property_add, value=add_component_payload)

    request_component_payload = '{"messageProperties":{"timestamp":"2010-01-01T12:00:00Z","correlationId":"test-request-cred-abcd-abcd-abcd-abcdabcdabcd","replyTo":"hal.localhost.localdomain"},"credentials":[{"componentUuid":"8154b2cf-edf7-4c90-aca3-e9b2fc094d74","endpointUuid":"e0909b91-6700-4786-8912-162b1fad2e6c","name":"basic"},{"componentUuid":"8154b2cf-edf7-4c90-aca3-e9b2fc094d74","endpointUuid":"cfcd61e9-8a6e-4b65-ad41-809974b6cec2","name":"DEFAULT"},{"componentUuid":"8154b2cf-edf7-4c90-aca3-e9b2fc094d74","endpointUuid":"e0909b91-6700-4786-8912-162b1fad2e6c","name":"advanced"}],"encryptionParameters":{"algorithm":"RSA","publicKeyString":"MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEApMfZc2NkfgA3luWpdJqRSR+DYsF0dxnNualryuVNWKGIdAnJ4O+4AjSJf7bsNrQx08CK0FLkQ+y5cp7CkjprBRvdEoSTA9WTLG9aJ2GAIXYuTruvDz7gACJb/EauXgkfgcmlpHyIZOs8i/9Ti87gmsHVh8rsOQXPm3tvOFj+cFTbXP754+bROfa2a+qz2X5fLaXARljEdMlt0m5BippTIhKArZOH9VqIyTaXDt4n7/UYlPQPtmGtnec/+8LUx05RbGznQcn3zeidWcrUl9fQ5UjdMJ6ve6L043FT1Y/ykRPau00F9npYTWTfPl9OJDpsK6aspxXkKmGyVCxc51uI2QIDAQAB"}}'
    af_support_tools.set_config_file_property(config_file=payload_file, heading=payload_heading,
                                              property=payload_property_req, value=request_component_payload)

    no_ep_component_payload = '{"messageProperties":{"timestamp":"2010-01-01T12:00:00Z","correlationId":"test-add-cred-no-compuuid-abcd-abcdabcdabcd","replyTo":"sds.localhost.localdomain"},"componentUuid":"","endpoints":[{"endpointUuid":"x0909b91-6700-4786-8912-162b1fad2e6c","credentials":[{"credentialUuid":"x300f6cc-9b79-4dce-94d7-44e7041fe982","name":"basic","credentialElement":{"username":"basic-user1","password":"basic-password1","community":""}},{"credentialUuid":"x0ac5972-a8ff-4883-b3aa-a2e791286a89","name":"advanced","credentialElement":{"username":"advanced-user1","password":"advanced-password1","community":""}}]},{"endpointUuid":"xfcd61e9-8a6e-4b65-ad41-809974b6cec2","credentials":[{"credentialUuid":"x2e2799d-9d1f-4b91-b5aa-9c2627c57fd6","name":"DEFAULT","credentialElement":{"username":"","password":"","community":"private"}}]}]}'
    af_support_tools.set_config_file_property(config_file=payload_file, heading=payload_heading,
                                              property=payload_property_neg1, value=no_ep_component_payload)

    dup_ep_component_payload = '{"messageProperties":{"timestamp":"2010-01-01T12:00:00Z","correlationId":"test-add-cred-dup-endpoint-abcdabcdabcd","replyTo":"sds.localhost.localdomain"},"componentUuid":"zdup0000-endp-test-aca3-e9b2fc094d74","endpoints":[{"endpointUuid":"zdup0000-endp-test-8912-162b1fad2e6c","credentials":[{"credentialUuid":"z300f6cc-9b79-4dce-94d7-44e7041fe982","name":"basic","credentialElement":{"username":"basic-user1","password":"basic-password1","community":""}}]},{"endpointUuid":"zdup0000-endp-test-8912-162b1fad2e6c","credentials":[{"credentialUuid":"z2e2799d-9d1f-4b91-b5aa-9c2627c57fd6","name":"DEFAULT","credentialElement":{"username":"","password":"","community":"private"}}]}]}'
    af_support_tools.set_config_file_property(config_file=payload_file, heading=payload_heading,
                                              property=payload_property_neg2, value=dup_ep_component_payload)

    invalid_json_payload = '{"messageProperties":{"timestamp":"2010-01-01T12:00:00Z","correlationId":"invalid-json-abcd-abcd-abcd-abcdabcdabcd","replyTo":"sds.localhost.localdomain","componentUuid":"8154b2cf-edf7-4c90-aca3-e9b2fc094d74","endpoints":[{"endpointUuid":"e0909b91-6700-4786-8912-162b1fad2e6c","credentials":[{"credentialUuid":"4300f6cc-9b79-4dce-94d7-44e7041fe982","name":"basic","credentialElement":{"username":"basic-user1","password":"basic-password1","community":""}},{"credentialUuid":"20ac5972-a8ff-4883-b3aa-a2e791286a89","name":"advanced","credentialElement":{"username":"advanced-user1","password":"advanced-password1","community":""}}]},{"endpointUuid":"cfcd61e9-8a6e-4b65-ad41-809974b6cec2","credentials":[{"credentialUuid":"22e2799d-9d1f-4b91-b5aa-9c2627c57fd6","name":"DEFAULT","credentialElement":{"username":"","password":"","community":"private"}}]}]}'
    af_support_tools.set_config_file_property(config_file=payload_file, heading=payload_heading,
                                              property=payload_property_neg3, value=invalid_json_payload)

    invalid_msg_properties_payload = '{"messageProperties":{"BLAH1":"2010-01-01T12:00:00Z","BLAH2":"invalidproperties-abcd-abcd-abcd-abcdabcdabcd","BLAH3":"sds.localhost.localdomain"},"componentUuid":"8154b2cf-edf7-4c90-aca3-e9b2fc094d74","endpoints":[{"endpointUuid":"e0909b91-6700-4786-8912-162b1fad2e6c","credentials":[{"credentialUuid":"4300f6cc-9b79-4dce-94d7-44e7041fe982","name":"basic","credentialElement":{"username":"basic-user1","password":"basic-password1","community":""}},{"credentialUuid":"20ac5972-a8ff-4883-b3aa-a2e791286a89","name":"advanced","credentialElement":{"username":"advanced-user1","password":"advanced-password1","community":""}}]},{"endpointUuid":"cfcd61e9-8a6e-4b65-ad41-809974b6cec2","credentials":[{"credentialUuid":"22e2799d-9d1f-4b91-b5aa-9c2627c57fd6","name":"DEFAULT","credentialElement":{"username":"","password":"","community":"private"}}]}]}'
    af_support_tools.set_config_file_property(config_file=payload_file, heading=payload_heading,
                                              property=payload_property_neg4, value=invalid_msg_properties_payload)

    request_component_invalid_uuid_payload = '{"messageProperties":{"timestamp":"2010-01-01T12:00:00Z","correlationId":"test-request-cred-invalid-comp-uuid-abcdabcdabcd","replyTo":"hal.localhost.localdomain"},"credentials":[{"componentUuid":"invalid0-edf7-4c90-aca3-e9b2fc094d74","endpointUuid":"invalid0-6700-4786-8912-162b1fad2e6c","name":"basic"},{"componentUuid":"invalid0-edf7-4c90-aca3-e9b2fc094d74","endpointUuid":"invalid0-8a6e-4b65-ad41-809974b6cec2","name":"DEFAULT"},{"componentUuid":"invalid0-edf7-4c90-aca3-e9b2fc094d74","endpointUuid":"invalid0-6700-4786-8912-162b1fad2e6c","name":"advanced"}],"encryptionParameters":{"algorithm":"RSA","publicKeyString":"MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEApMfZc2NkfgA3luWpdJqRSR+DYsF0dxnNualryuVNWKGIdAnJ4O+4AjSJf7bsNrQx08CK0FLkQ+y5cp7CkjprBRvdEoSTA9WTLG9aJ2GAIXYuTruvDz7gACJb/EauXgkfgcmlpHyIZOs8i/9Ti87gmsHVh8rsOQXPm3tvOFj+cFTbXP754+bROfa2a+qz2X5fLaXARljEdMlt0m5BippTIhKArZOH9VqIyTaXDt4n7/UYlPQPtmGtnec/+8LUx05RbGznQcn3zeidWcrUl9fQ5UjdMJ6ve6L043FT1Y/ykRPau00F9npYTWTfPl9OJDpsK6aspxXkKmGyVCxc51uI2QIDAQAB"}}'
    af_support_tools.set_config_file_property(config_file=payload_file, heading=payload_heading,
                                              property=payload_property_neg5,
                                              value=request_component_invalid_uuid_payload)

#test_CS_ComponentCredentials_CI()
#test_CS_ComponentCredentials()
