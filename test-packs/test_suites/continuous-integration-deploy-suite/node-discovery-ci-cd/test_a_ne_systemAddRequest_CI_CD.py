#!/usr/bin/python
# Author: cullia
# Revision: 2.0
# Code Reviewed by:
# Description: Configure a system with vcenter & rackhd

import af_support_tools
import json
import os
import pytest
import time


@pytest.fixture(scope="module", autouse=True)
def load_test_data():
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

    global rmq_username
    rmq_username = 'guest'
    global rmq_password
    rmq_password = 'guest'
    global port
    port = 5672


#######################################################################################################################


# @pytest.mark.dne_paqx_parent_mvp
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
    af_support_tools.rmq_publish_message(host=ipaddress, rmq_username=rmq_username, rmq_password=rmq_password,
                                         exchange='exchange.dell.cpsd.syds.system.definition.request',
                                         routing_key='dell.cpsd.syds.converged.system.addition.requested',
                                         headers={
                                             '__TypeId__': 'com.dell.cpsd.syds.converged.system.addition.requested'},
                                         payload=the_payload)

    # #****************************************************
    # #TODO I think This is where we can monitor the vcenter registering with consul. Connented out until code committed. Need to validate manually via trace log first.
    #
    # #Make sure the queue is clean
    # af_support_tools.rmq_purge_queue(host=ipaddress, port=port, rmq_username=rmq_username, rmq_password=rmq_password,
    #                                  queue='test.endpoint.registration.event')
    #
    # waitForMsg('test.controlplane.vcenter.response')
    # return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
    #                                                       rmq_password=rmq_password,
    #                                                       queue='test.controlplane.vcenter.response',
    #                                                       remove_message=True)
    #
    # checkForErrors(return_message)
    # return_json = json.loads(return_message, encoding='utf-8')
    # assert return_json['responseInfo']['message'] == 'SUCCESS', 'ERROR: Vcenter validation failure'
    #
    #
    # waitForMsg('test.endpoint.registration.event')
    # return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
    #                                                       rmq_password=rmq_password,
    #                                                       queue='test.endpoint.registration.event',
    #                                                       remove_message=True)
    #
    # checkForErrors(return_message)
    # return_json = json.loads(return_message, encoding='utf-8')
    # # assert return_json['endpoint']['type'] == 'vcenter', 'vcenter not registered with endpoint'
    # # TODO above is commented out as its consumming the wrong message
    #
    #
    # #****************************************************


    # Call the function to verify the system exists. This will return the system UUID.

    the_payload = '{"messageProperties":{"timestamp":"2010-01-01T12:00:00Z","correlationId":"sys-def-req-abcd-abcdabcdabcd","replyTo":"sds.localhost"},"systemsFilter":{"systemUuid":"","systemIdentifier":"","serialNumber":""}}'

    af_support_tools.rmq_publish_message(host=ipaddress,
                                         port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                         exchange='exchange.dell.cpsd.syds.system.definition.request',
                                         routing_key='dell.cpsd.syds.converged.system.list.requested',
                                         headers={'__TypeId__': 'com.dell.cpsd.syds.converged.system.list.requested'},
                                         payload=the_payload,
                                         payload_type='json')

    # We need to wait until the queue gets the response message
    waitForMsg('test.system.list.found')
    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port,
                                                          rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.system.list.found')

    return_json = json.loads(return_message, encoding='utf-8')
    my_systemUuid = return_json['convergedSystems'][0]['uuid']
    print('\nTEST: System Exists - System UUID: ', my_systemUuid, ': PASSED\n')

    cleanup()
    return my_systemUuid


#######################################################################################################################


def cleanup():
    # Delete the test queues
    print('Cleaning up...')

    af_support_tools.rmq_delete_queue(host=ipaddress, port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                      queue='test.system.list.found')

    af_support_tools.rmq_delete_queue(host=ipaddress, port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                      queue='test.controlplane.vcenter.response')

    af_support_tools.rmq_delete_queue(host=ipaddress, port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                      queue='test.endpoint.registration.event')


def bindQueus():
    print('\nCreating Queues')

    af_support_tools.rmq_bind_queue(host=ipaddress,
                                    port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                    queue='test.system.list.found',
                                    exchange='exchange.dell.cpsd.syds.system.definition.response',
                                    routing_key='#')

    af_support_tools.rmq_bind_queue(host=ipaddress,
                                    port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                    queue='test.controlplane.vcenter.response',
                                    exchange='exchange.cpsd.controlplane.vcenter.response',
                                    routing_key='#')

    af_support_tools.rmq_bind_queue(host=ipaddress,
                                    port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                    queue='test.endpoint.registration.event',
                                    exchange='exchange.dell.cpsd.endpoint.registration.event',
                                    routing_key='#')


def waitForMsg(queue):
    q_len = 0
    timeout = 0

    while q_len < 1:
        time.sleep(1)
        timeout += 1

        q_len = af_support_tools.rmq_message_count(host=ipaddress,
                                                   port=port,
                                                   rmq_username=rmq_username,
                                                   rmq_password=rmq_password,
                                                   queue=queue)

        if timeout > 50:
            print('ERROR: Message took to long to return. Something is wrong')


            #######################################################################################################################


def checkForErrors(return_message):
    checklist = 'errors'
    if checklist in return_message:
        print('\nBUG: Error in Response Message\n')
        assert False  # This assert is to fail the test
