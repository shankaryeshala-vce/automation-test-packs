#!/usr/bin/python
# Author: cullia
# Revision: 1.0
# Code Reviewed by:
# Description: Configure a system with vcenter

import af_support_tools
import json
import os
import pytest
import time
import requests


@pytest.fixture(scope="module", autouse=True)
def load_test_data():
    import cpsd
    global cpsd

    af_support_tools.rmq_get_server_side_certs(host_hostname=cpsd.props.base_hostname,
                                               host_username=cpsd.props.base_username,
                                               host_password=cpsd.props.base_password, host_port=22,
                                               rmq_certs_path=cpsd.props.rmq_cert_path)

    # Update config ini files at runtime
    my_data_file = os.environ.get('AF_RESOURCES_PATH') + '/continuous-integration-deploy-suite/symphony-sds.properties'
    af_support_tools.set_config_file_property_by_data_file(my_data_file)

    # Set config ini file name
    global env_file
    env_file = 'env.ini'

    # Set Vars
    global payload_file
    payload_file = 'continuous-integration-deploy-suite/symphony-sds.ini'
    global payload_header
    payload_header = 'payload'
    global payload_property_sys
    payload_property_sys = 'sys_payload_node_exp'

    global ipaddress
    ipaddress = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='hostname')

    global cli_username
    cli_username = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS',
                                                             property='username')
    global cli_password
    cli_password = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS',
                                                             property='password')


#######################################################################################################################


@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_DNE_SystemAdditionRequested():
    print('Defining System on system: ', ipaddress)

    cleanup()

    bindQueus()

    print('\n*******************************************************')
    print('Step 1. Sending RMQ System-Definition Message to configure system...')

    # Get the payload data from the config symphony-sds.ini file.
    the_payload = af_support_tools.get_config_file_property(config_file=payload_file,
                                                            heading=payload_header,
                                                            property=payload_property_sys)

    time.sleep(1)

    # Publish the message to define the system
    af_support_tools.rmq_publish_message(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                         rmq_username=cpsd.props.rmq_username, rmq_password=cpsd.props.rmq_password,
                                         exchange='exchange.dell.cpsd.syds.system.definition.request',
                                         routing_key='dell.cpsd.syds.converged.system.addition.requested',
                                         headers={
                                             '__TypeId__': 'com.dell.cpsd.syds.converged.system.addition.requested'},
                                         payload=the_payload, ssl_enabled=cpsd.props.rmq_ssl_enabled)

    # ****************************************************

    # Call the function to verify the system exists. This will validate the system has a UUID.

    the_payload = '{"messageProperties":{"timestamp":"2010-01-01T12:00:00Z","correlationId":"sys-def-req-abcd-abcdabcdabcd","replyTo":"sds.localhost"},"systemsFilter":{"systemUuid":"","systemIdentifier":"","serialNumber":""}}'

    af_support_tools.rmq_publish_message(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                         rmq_username=cpsd.props.rmq_username, rmq_password=cpsd.props.rmq_password,
                                         exchange='exchange.dell.cpsd.syds.system.definition.request',
                                         routing_key='dell.cpsd.syds.converged.system.list.requested',
                                         headers={'__TypeId__': 'com.dell.cpsd.syds.converged.system.list.requested'},
                                         payload=the_payload,
                                         payload_type='json', ssl_enabled=cpsd.props.rmq_ssl_enabled)

    # We need to wait until the queue gets the response message
    waitForMsg('test.system.list.found')
    return_message = af_support_tools.rmq_consume_message(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                                          rmq_username=cpsd.props.rmq_username,
                                                          rmq_password=cpsd.props.rmq_password,
                                                          queue='test.system.list.found',
                                                          ssl_enabled=cpsd.props.rmq_ssl_enabled)

    return_json = json.loads(return_message, encoding='utf-8')

    assert return_json['convergedSystems'], 'Error: No System with UUID has been returned.'

    my_systemUuid = return_json['convergedSystems'][0]['uuid']
    assert my_systemUuid, 'Error: No System with UUID has been returned.'
    print('\nTEST: System Exists - System UUID: ', my_systemUuid, ': PASSED\n')

    cleanup()


#######################################################################################################################


def cleanup():
    af_support_tools.rmq_delete_queue(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                      rmq_username=cpsd.props.rmq_username, rmq_password=cpsd.props.rmq_password,
                                      queue='test.system.list.found', ssl_enabled=cpsd.props.rmq_ssl_enabled)


def bindQueus():
    af_support_tools.rmq_bind_queue(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                    rmq_username=cpsd.props.rmq_username, rmq_password=cpsd.props.rmq_password,
                                    queue='test.system.list.found',
                                    exchange='exchange.dell.cpsd.syds.system.definition.response',
                                    routing_key='#', ssl_enabled=cpsd.props.rmq_ssl_enabled)


def waitForMsg(queue):
    q_len = 0
    timeout = 0

    while q_len < 1:
        time.sleep(1)
        timeout += 1

        q_len = af_support_tools.rmq_message_count(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                                   rmq_username=cpsd.props.rmq_username,
                                                   rmq_password=cpsd.props.rmq_password,
                                                   queue=queue, ssl_enabled=cpsd.props.rmq_ssl_enabled)

        if timeout > 50:
            print('ERROR: Message took to long to return. Something is wrong')


            #######################################################################################################################


def checkForErrors(return_message):
    checklist = 'errors'
    if checklist in return_message:
        assert False, '\nBUG: Error in Response Message\n'

#######################################################################################################################
