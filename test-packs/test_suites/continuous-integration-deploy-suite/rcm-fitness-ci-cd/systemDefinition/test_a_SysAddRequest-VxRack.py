import af_support_tools
import pytest
import json
import os
import time
import paramiko


@pytest.fixture(scope="module", autouse=True)
def load_test_data():
    # Update config ini files at runtime
    my_data_file = os.environ.get(
        'AF_RESOURCES_PATH') + '/continuous-integration-deploy-suite/symphony-sds-VxRack.properties'
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

    # Set Vars
    global payload_file
    payload_file = 'continuous-integration-deploy-suite/symphony-sds-VxRack.ini'
    global payload_header
    payload_header = 'payload'
    global payload_property_sys
    payload_property_sys = 'sys_payload'
    global payload_property_req
    payload_property_req = 'sys_request_payload'
    global payload_property_hal
    payload_property_hal = 'ccv_payload'


#######################################################################################################################

# *** THIS IS THE MAIN TEST *** Add a system
@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_SystemAdditionRequested():
    cleanup()

    bindSDSQueus()

    # Get the payload data from the config symphony-sds.ini file.
    the_payload = af_support_tools.get_config_file_property(config_file=payload_file,
                                                            heading=payload_header,
                                                            property=payload_property_sys)

    # Publish the message
    af_support_tools.rmq_publish_message(host=ipaddress, rmq_username=rmq_username, rmq_password=rmq_password,
                                         exchange='exchange.dell.cpsd.syds.system.definition.request',
                                         routing_key='dell.cpsd.syds.converged.system.addition.requested',
                                         headers={
                                             '__TypeId__': 'com.dell.cpsd.syds.converged.system.addition.requested'},
                                         payload=the_payload)

    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.system.list.request')

    published_json = json.loads(the_payload, encoding='utf-8')
    return_json = json.loads(return_message, encoding='utf-8')

    # Checking the "Message received" matches the "Message published"
    assert published_json == return_json
    print('\nTEST: Published Message Received: PASSED')

    # Call the function to verify the generated credentials.addition.requested message is correct.
    verifyCSmessage()

    # Call the function to verify the system exists. This is not a necessary step but it will return the system UUID.
    verify_SystemExists()

    cleanup()


# *** Kick of the collectComponentVersion Msg
@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
def test_HAL_CollectComponentVersion():
    bindHALQueus()

    # Get the collectComponentVersions payload data from the config symphony-sds.ini file.
    the_payload = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                            property=payload_property_hal)

    # Publish the HAL message to collectcomponentversions
    af_support_tools.rmq_publish_message(host=ipaddress, rmq_username=rmq_username, rmq_password=rmq_password,
                                         exchange='exchange.dell.cpsd.hal.orchestrator.request',
                                         routing_key='dell.cpsd.hal.orchestrator.collect.component.versions',
                                         headers={
                                             '__TypeId__': 'com.dell.cpsd.hal.orchestrator.service.collect.component.versions'},
                                         payload=the_payload)

    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.hal.orchestrator.request', remove_message=False)

    published_json = json.loads(the_payload, encoding='utf-8')
    return_json = json.loads(return_message, encoding='utf-8')

    # Checking the "Message received" matches the "Message published"
    assert published_json == return_json
    print('\nTEST: Published Message Received: PASSED')

    # We need to wait until the queue gets the response message and timeout if it never arrives
    q_len = 0
    timeout = 0

    while q_len < 1:
        time.sleep(1)
        timeout += 1

        q_len = af_support_tools.rmq_message_count(host=ipaddress,
                                                   port=port,
                                                   rmq_username=rmq_username,
                                                   rmq_password=rmq_password,
                                                   queue='test.hal.orchestrator.response')

        # If the test queue doesn't get a message them something is wrong. Time out needs to be high as msg can take 3+ minutes
        if timeout > 500:
            print('ERROR: HAL Responce Message took to long to return. Something is wrong')
            cleanup()
            break

    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.hal.orchestrator.response', remove_message=False)

    return_json = json.loads(return_message, encoding='utf-8')

    # Only if the message sequence successfully ran will the returned json message have the following attributes.
    assert return_json['messageProperties']['correlationId']
    assert return_json['messageProperties']['replyTo']
    assert return_json['systems']
    assert return_json['groups']
    assert return_json['devices']
    assert return_json['subComponents']

    # This is commented out as there is a defect here
    # DEFECT: assert return_json ['groups'][0]['parentSystemUuids']

    print('\nTEST: CollectComponentVersions run: PASSED')

    # cleanup()


#######################################################################################################################

def cleanup():
    # Delete the test queues
    print('Cleaning up...')

    af_support_tools.rmq_delete_queue(host=ipaddress, port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                      queue='test.system.list.request')

    af_support_tools.rmq_delete_queue(host=ipaddress, port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                      queue='test.system.list.found')

    af_support_tools.rmq_delete_queue(host=ipaddress, port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                      queue='test.hal.orchestrator.request')

    # af_support_tools.rmq_delete_queue(host=ipaddress, port=port, rmq_username=rmq_username, rmq_password=rmq_password,
    #                                   queue='test.hal.orchestrator.response')

    af_support_tools.rmq_delete_queue(host=ipaddress, port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                      queue='test.component.credential.request')

    af_support_tools.rmq_delete_queue(host=ipaddress, port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                      queue='test.system.definition.event')


def bindSDSQueus():
    af_support_tools.rmq_bind_queue(host=ipaddress,
                                    port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                    queue='test.system.list.request',
                                    exchange='exchange.dell.cpsd.syds.system.definition.request',
                                    routing_key='#')

    af_support_tools.rmq_bind_queue(host=ipaddress,
                                    port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                    queue='test.system.list.found',
                                    exchange='exchange.dell.cpsd.syds.system.definition.response',
                                    routing_key='#')

    af_support_tools.rmq_bind_queue(host=ipaddress, port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                    queue='test.system.definition.event',
                                    exchange='exchange.dell.cpsd.syds.system.definition.event',
                                    routing_key='#')

    af_support_tools.rmq_bind_queue(host=ipaddress, port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                    queue='test.component.credential.request',
                                    exchange='exchange.dell.cpsd.cms.credentials.request',
                                    routing_key='#')


def bindHALQueus():
    af_support_tools.rmq_bind_queue(host=ipaddress,
                                    port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                    queue='test.hal.orchestrator.request',
                                    exchange='exchange.dell.cpsd.hal.orchestrator.request',
                                    routing_key='#')

    # Create a test queue that will bind to system.definition.response
    af_support_tools.rmq_bind_queue(host=ipaddress,
                                    port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                    queue='test.hal.orchestrator.response',
                                    exchange='exchange.dell.cpsd.hal.orchestrator.response',
                                    routing_key='#')


def verifyCSmessage():
    # We need to verify that the triggered component.credentials.addition.requested is valid.

    q_len = 0
    timeout = 0

    while q_len < 1:
        time.sleep(1)
        timeout += 1

        q_len = af_support_tools.rmq_message_count(host=ipaddress, port=port, rmq_username=rmq_username,
                                                   rmq_password=rmq_password,
                                                   queue='test.component.credential.request')

        # If the test queue doesn't get a message then something is wrong
        if timeout > 10:
            print('ERROR: CS Request Message took to long to return. Something is wrong')
            cleanup()
            break

    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.component.credential.request')

    return_json = json.loads(return_message, encoding='utf-8')

    if 'credentialUuid' not in return_message:
        print('\nTEST FAIL: Invalid "credentials.addition.requested" message structure. credentialUuid missing')
    if 'endpointUuid' not in return_message:
        print('\nTEST FAIL: Invalid "credentials.addition.requested" message structure. endpointUuid missing')
    if 'componentUuid' not in return_message:
        print('\nTEST FAIL: Invalid "credentials.addition.requested" message structure. componentUuid missing')

    assert return_json['messageProperties']['correlationId']
    assert return_json['messageProperties']['replyTo']
    assert return_json['messageProperties']['timestamp']
    assert return_json['endpoints'][0]['credentials'][0]['credentialUuid']
    print('credentials.addition.requested is valid')


def verify_SystemExists():
    # Check that the system exists
    print('Verifying system does exist...')
    time.sleep(2)
    # Get the payload data from the config symphony-sds.ini file.
    the_payload = af_support_tools.get_config_file_property(config_file=payload_file, heading=payload_header,
                                                            property=payload_property_req)

    af_support_tools.rmq_publish_message(host=ipaddress,
                                         port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                         exchange='exchange.dell.cpsd.syds.system.definition.request',
                                         routing_key='dell.cpsd.syds.converged.system.list.requested',
                                         headers={'__TypeId__': 'com.dell.cpsd.syds.converged.system.list.requested'},
                                         payload=the_payload,
                                         payload_type='json')

    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.system.list.request')

    published_json = json.loads(the_payload, encoding='utf-8')
    return_json = json.loads(return_message, encoding='utf-8')

    # Checking the "Message received" matches the "Message published"
    assert published_json == return_json
    print('\nTEST: Published Message Received: PASSED')

    q_len = 0
    timeout = 0

    # We need to wait until the queue gets the response message
    while q_len < 1:
        time.sleep(1)
        timeout += 1

        q_len = af_support_tools.rmq_message_count(host=ipaddress,
                                                   port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                                   queue='test.system.list.found')

        # If the test queue doesn't get a message then something is wrong
        if timeout > 10:
            print('ERROR: Sys Found Response Message took to long to return. Something is wrong')
            cleanup()
            break

    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port,
                                                          rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.system.list.found')

    return_json = json.loads(return_message, encoding='utf-8')

    # Here we verify that a system is returned. Cannot be overly specific checking parameters as values will vary.
    assert return_json['messageProperties']['correlationId']
    assert return_json['messageProperties']['replyTo']
    assert return_json['messageProperties']['timestamp']
    assert return_json['convergedSystems']
    assert return_json['convergedSystems'][0]['uuid']
    assert not return_json['convergedSystems'][0]['groups']
    assert not return_json['convergedSystems'][0]['endpoints']
    assert not return_json['convergedSystems'][0]['subSystems']
    assert not return_json['convergedSystems'][0]['components']

    config = json.loads(return_message, encoding='utf-8')
    my_systemUuid = config['convergedSystems'][0]['uuid']
    print('\nTEST: System Exists - System UUID: ', my_systemUuid)

#######################################################################################################################



# test_SystemAdditionRequested()
# test_HAL_CollectComponentVersion()
