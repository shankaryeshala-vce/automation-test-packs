#!/usr/bin/python
# Author: cullia
# Revision: 2.1
# Code Reviewed by:
# Description: Verify the Capability Registery Ping-Pong Message sequence.
#
# Copyright (c) 2017 Dell Inc. or its subsidiaries.  All Rights Reserved.
# Dell EMC Confidential/Proprietary Information
#
import af_support_tools
import json
import pytest
import time


@pytest.fixture(scope="module", autouse=True)
def load_test_data():
    import cpsd
    global cpsd

    af_support_tools.rmq_get_server_side_certs(host_hostname=cpsd.props.base_hostname,
                                               host_username=cpsd.props.base_username,
                                               host_password=cpsd.props.base_password, host_port=22,
                                               rmq_certs_path=cpsd.props.rmq_cert_path)

    # Set config ini file name
    global env_file
    env_file = 'env.ini'

    # Test VM Details
    global ipaddress
    ipaddress = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='hostname')

    global cli_username
    cli_username = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS',
                                                             property='username')

    global cli_password
    cli_password = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS',
                                                             property='password')

    # RMQ Details
    global rmq_username
    rmq_username = af_support_tools.get_config_file_property(config_file=env_file, heading='RabbitMQ',
                                                             property='username')
    global rmq_password
    rmq_password = af_support_tools.get_config_file_property(config_file=env_file, heading='RabbitMQ',
                                                             property='password')
    global port
    port = af_support_tools.get_config_file_property(config_file=env_file, heading='RabbitMQ',
                                                     property='ssl_port')


#####################################################################
# These are the main tests.
#####################################################################

@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_capabilityRegistry_Control_and_Binding_Ping_Message():
    """
    Title           :       Verify the Capability Registry Control Ping Message
    Description     :       Every 7 seconds the Capability Registery sends out a message asking "who's out there?".
                            This is a "ping" message. Each service that is alive will respond with a "pong" message.
                            The correlationID value will be the same on all messages so this is used to track that we
                            are getting the correct message and not just "any" message.
                            It will fail if :
                               No capability.registry.control message is published.
                               The containerID does not match the body of the message.
    Parameters      :       none
    Returns         :       None
    """

    print('\nRunning Test on system: ', ipaddress)

    cleanup()
    bindQueues()

    print('\n*******************************************************\n')

    global correlationID  # Set as a Global parameter as it will be used in the next test.

    # Ensure the Control & Binding Queues are empty to start
    af_support_tools.rmq_purge_queue(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                     rmq_username=cpsd.props.rmq_username,
                                     rmq_password=cpsd.props.rmq_password,
                                     queue='test.capability.registry.control', ssl_enabled=cpsd.props.rmq_ssl_enabled)

    af_support_tools.rmq_purge_queue(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                     rmq_username=cpsd.props.rmq_username,
                                     rmq_password=cpsd.props.rmq_password,
                                     queue='test.capability.registry.binding', ssl_enabled=cpsd.props.rmq_ssl_enabled)

    print('\nTest: The Capability Registry Control. Verify the Ping message')

    # Wait for & consume a "Ping" Message. The message is left in the queue to be consumed again. The correlationID is
    # in the header and the return_basic_properties flag is set to True in order to get the header value. When
    # basic_properties are returned the message cannot be converted to json which is the reason its "consumed" twice.
    waitForMsg('test.capability.registry.control')
    return_message = af_support_tools.rmq_consume_message(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                                          rmq_username=cpsd.props.rmq_username,
                                                          rmq_password=cpsd.props.rmq_password,
                                                          queue='test.capability.registry.control',
                                                          ssl_enabled=cpsd.props.rmq_ssl_enabled,
                                                          remove_message=False, return_basic_properties=True)

    # Save the correlationID to be used in next part of the test
    correlationID = return_message[0].correlation_id
    correlationID = json.dumps(correlationID)

    print('The CorrelationID for this Control Msg:', correlationID)

    # The message is consumed again, checked for errors and converted to JSON. The body of the message contains the
    # containerID under the "hostname" value. This value will be compared to the actual containerID value
    return_message = af_support_tools.rmq_consume_message(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                                          rmq_username=cpsd.props.rmq_username,
                                                          rmq_password=cpsd.props.rmq_password,
                                                          queue='test.capability.registry.control',
                                                          ssl_enabled=cpsd.props.rmq_ssl_enabled)

    checkForErrors(return_message)
    return_json = json.loads(return_message, encoding='utf-8')
    retunedValue = return_json['hostname']

    # Get the actual Container ID value and compare it to the RMQ message body
    containerID = getdockerID('capability-registry-service')  # getdockerID() logs into vm and returns the dockerID

    # The value in the msg body should match the container ID. If they do not match indicates multiple containers
    assert containerID == retunedValue

    print('The Capability Registry Control Ping message is sent and has the correct containerID:', containerID)
    print('\n*******************************************************\n')


@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_capabilityRegistry_Control_and_Binding_Pong_Message():
    """
    Title           :       Verify the Capability Registry Binding Pong Message
    Description     :       Every 7 seconds the Capability Registery sends out a message asking "who's out there?".
                            This is a "ping" message. Each service that is alive will respond with a "pong" message.
                            The correlationID value will be the same on all messages so this is used to track that we
                            are getting the correct message and not just "any" message.
                            It will fail if :
                               Not all expected services respond with their Pong message.
                               If a service responds twice (indicates multiple containers are running for the same service)
    Parameters      :       none
    Returns         :       None
    """
    print("Test: The Capability Registry Binding. Verify the Pong message from each provider / adapter")

    # This is the list of current/providers
    capabilityProvider_Cisco_Network_Data_Provider = 'cisco-network-data-provider'
    capabilityProvider_Poweredge_Compute_Data_Provider = 'poweredge-compute-data-provider'
    capabilityProvider_Vcenter_Compute_Data_Provider = 'vcenter-compute-data-provider'
    capabilityProvider_Rackhd_Adapter = 'rackhd-adapter'
    capabilityProvider_Vcenter_Adapter = 'vcenter-adapter'
    capabilityProvider_Coprhd_Adapter = 'coprhd-adapter'
    capabilityProvider_Endpoint_Registry = 'endpoint-registry'
    capabilityProvider_Node_Discovery_Paqx = 'node-discovery-paqx'

    # Each provider/adapter is given a flag that will be set to True once its responded. This method is used as the order
    # in which the responses come in is random. When all are tested the allTested flag is set and the test completes.
    cisco_Network_Data_Provider_Tested = False
    poweredge_Compute_Data_Provider_Tested = False
    vcenter_Compute_Data_Provider_Tested = False
    rackhd_Adapter_Tested = False
    vcenter_Adapter_Tested = False
    coprhd_Adapter_Tested = False
    endpoint_Registry_Tested = False
    node_Discovery_Paqx_Tested = False

    allTested = False

    # To prevent the test waiting indefinitely we need to provide a timeout.  When new adapters/providers are added to
    # the test the expectedNumberOfBindings value will increase.
    errorTimeout = 0
    expectedNumberOfBindings = 8

    # Keep consuming messages until this condition is no longer true
    while allTested == False and errorTimeout <= expectedNumberOfBindings:

        # Only a message that comes in with the same correlationID as the Ping message is tested
        waitForMsg('test.capability.registry.binding')
        return_message = af_support_tools.rmq_consume_message(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                                              rmq_username=cpsd.props.rmq_username,
                                                              rmq_password=cpsd.props.rmq_password,
                                                              queue='test.capability.registry.binding',
                                                              ssl_enabled=cpsd.props.rmq_ssl_enabled,
                                                              remove_message=False, return_basic_properties=True)

        testcorrelationID = return_message[0].correlation_id
        testcorrelationID = json.dumps(testcorrelationID)

        if testcorrelationID == correlationID:  # Only check messages that have the same CorrelationID as the ping message

            error_list = []
            return_message = af_support_tools.rmq_consume_message(host=cpsd.props.base_hostname,
                                                                  port=cpsd.props.rmq_port,
                                                                  rmq_username=cpsd.props.rmq_username,
                                                                  rmq_password=cpsd.props.rmq_password,
                                                                  queue='test.capability.registry.binding',
                                                                  ssl_enabled=cpsd.props.rmq_ssl_enabled)
            checkForErrors(return_message)

            if capabilityProvider_Cisco_Network_Data_Provider in return_message:
                if (cisco_Network_Data_Provider_Tested == True):
                    error_list.append(capabilityProvider_Cisco_Network_Data_Provider)
                else:
                    print('Test:', capabilityProvider_Cisco_Network_Data_Provider, 'Binding Message returned\n')
                    cisco_Network_Data_Provider_Tested = True

            if capabilityProvider_Poweredge_Compute_Data_Provider in return_message:
                if (poweredge_Compute_Data_Provider_Tested == True):
                    error_list.append(capabilityProvider_Poweredge_Compute_Data_Provider)
                else:
                    print('Test:', capabilityProvider_Poweredge_Compute_Data_Provider, 'Binding Message returned\n')
                    poweredge_Compute_Data_Provider_Tested = True

            if capabilityProvider_Vcenter_Compute_Data_Provider in return_message:
                if (vcenter_Compute_Data_Provider_Tested == True):
                    error_list.append(capabilityProvider_Vcenter_Compute_Data_Provider)
                else:
                    print('Test:', capabilityProvider_Vcenter_Compute_Data_Provider, 'Binding Message returned\n')
                    vcenter_Compute_Data_Provider_Tested = True

            if capabilityProvider_Rackhd_Adapter in return_message:
                if (rackhd_Adapter_Tested == True):
                    error_list.append(capabilityProvider_Rackhd_Adapter)
                else:
                    print('Test:', capabilityProvider_Rackhd_Adapter, 'Binding Message returned\n')
                    rackhd_Adapter_Tested = True

            if capabilityProvider_Vcenter_Adapter in return_message:
                if (vcenter_Adapter_Tested == True):
                    error_list.append(capabilityProvider_Vcenter_Adapter)
                else:
                    print('Test:', capabilityProvider_Vcenter_Adapter, 'Binding Message returned\n')
                    vcenter_Adapter_Tested = True

            if capabilityProvider_Coprhd_Adapter in return_message:
                if (coprhd_Adapter_Tested == True):
                    error_list.append(capabilityProvider_Coprhd_Adapter)
                else:
                    print('Test:', capabilityProvider_Coprhd_Adapter, 'Binding Message returned\n')
                    coprhd_Adapter_Tested = True

            if capabilityProvider_Endpoint_Registry in return_message:
                if (endpoint_Registry_Tested == True):
                    error_list.append(capabilityProvider_Endpoint_Registry)
                else:
                    print('Test:', capabilityProvider_Endpoint_Registry, 'Binding Message returned\n')
                    endpoint_Registry_Tested = True

            if capabilityProvider_Node_Discovery_Paqx in return_message:
                if (node_Discovery_Paqx_Tested == True):
                    error_list.append(capabilityProvider_Node_Discovery_Paqx)
                else:
                    print('Test:', capabilityProvider_Node_Discovery_Paqx, 'Binding Message returned\n')
                    node_Discovery_Paqx_Tested = True

            assert not error_list, 'Multiple Containers Running'

            if cisco_Network_Data_Provider_Tested == True \
                    and poweredge_Compute_Data_Provider_Tested == True \
                    and vcenter_Compute_Data_Provider_Tested == True \
                    and rackhd_Adapter_Tested == True \
                    and vcenter_Adapter_Tested == True \
                    and coprhd_Adapter_Tested == True \
                    and endpoint_Registry_Tested == True \
                    and node_Discovery_Paqx_Tested == True:
                allTested = True

        # A timeout is included to prevent an infinite loop waiting for a response.
        # If a response hasn't been received the flag will still be false and this can be used to return an error.
        if errorTimeout == expectedNumberOfBindings:

            error_list = []

            if cisco_Network_Data_Provider_Tested == False:
                print('ERROR:', capabilityProvider_Cisco_Network_Data_Provider, 'Binding Message is not returned')
                error_list.append(capabilityProvider_Cisco_Network_Data_Provider)

            if poweredge_Compute_Data_Provider_Tested == False:
                print('ERROR:', capabilityProvider_Poweredge_Compute_Data_Provider, 'Binding Message is not returned')
                error_list.append(capabilityProvider_Poweredge_Compute_Data_Provider)

            if vcenter_Compute_Data_Provider_Tested == False:
                print('ERROR:', capabilityProvider_Vcenter_Compute_Data_Provider, 'Binding Message is not returned')
                error_list.append(capabilityProvider_Vcenter_Compute_Data_Provider)

            if rackhd_Adapter_Tested == False:
                print('ERROR:', capabilityProvider_Rackhd_Adapter, 'Binding Message is not returned')
                error_list.append(capabilityProvider_Rackhd_Adapter)

            if vcenter_Adapter_Tested == False:
                print('ERROR:', capabilityProvider_Vcenter_Adapter, 'Binding Message is not returned')
                error_list.append(capabilityProvider_Vcenter_Adapter)

            if coprhd_Adapter_Tested == False:
                print('ERROR:', capabilityProvider_Coprhd_Adapter, 'Binding Message is not returned')
                error_list.append(capabilityProvider_Coprhd_Adapter)

            if node_Discovery_Paqx_Tested == False:
                print('ERROR:', capabilityProvider_Node_Discovery_Paqx, 'Binding Message is not returned')
                error_list.append(capabilityProvider_Node_Discovery_Paqx)

            if endpoint_Registry_Tested == False:
                print('ERROR:', capabilityProvider_Endpoint_Registry, 'Binding Message is not returned')
                error_list.append(capabilityProvider_Endpoint_Registry)

            assert not error_list, 'Not all expected bindings are replying'

        errorTimeout += 1

    print('\n*******************************************************\n')

    cleanup()


#######################################################################################################################
# These are common functions that are used throughout the main test.
def bindQueues():
    af_support_tools.rmq_bind_queue(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                    rmq_username=cpsd.props.rmq_username, rmq_password=cpsd.props.rmq_password,
                                    queue='test.capability.registry.control',
                                    exchange='exchange.dell.cpsd.hdp.capability.registry.control',
                                    routing_key='#', ssl_enabled=cpsd.props.rmq_ssl_enabled)

    af_support_tools.rmq_bind_queue(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                    rmq_username=cpsd.props.rmq_username, rmq_password=cpsd.props.rmq_password,
                                    queue='test.capability.registry.binding',
                                    exchange='exchange.dell.cpsd.hdp.capability.registry.binding',
                                    routing_key='#', ssl_enabled=cpsd.props.rmq_ssl_enabled)


def cleanup():
    af_support_tools.rmq_delete_queue(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                      rmq_username=cpsd.props.rmq_username, rmq_password=cpsd.props.rmq_password,
                                      queue='test.capability.registry.control', ssl_enabled=cpsd.props.rmq_ssl_enabled)

    af_support_tools.rmq_delete_queue(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                      rmq_username=cpsd.props.rmq_username, rmq_password=cpsd.props.rmq_password,
                                      queue='test.capability.registry.binding', ssl_enabled=cpsd.props.rmq_ssl_enabled)


def waitForMsg(queue):
    # This function keeps looping until a message is in the specified queue. We do need it to timeout and throw an error
    # if a message never arrives. Once a message appears in the queue the function is complete and main continues.

    # The length of the queue, it will start at 0 but as soon as we get a response it will increase
    q_len = 0

    # Represents the number of seconds that have gone by since the method started
    timeout = 0

    # Max number of seconds to wait
    max_timeout = 100

    # Amount of time in seconds that the loop is going to wait on each iteration
    sleeptime = 1

    while q_len < 1:
        time.sleep(sleeptime)
        timeout += sleeptime

        q_len = af_support_tools.rmq_message_count(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                                   rmq_username=cpsd.props.rmq_username,
                                                   rmq_password=cpsd.props.rmq_password,
                                                   queue=queue, ssl_enabled=cpsd.props.rmq_ssl_enabled)

        if timeout > max_timeout:
            print('ERROR: Message took too long to return. Something is wrong')
            cleanup()
            break


def checkForErrors(return_message):
    checklist = 'errors'
    if checklist in return_message:
        print('\nBUG: Error in Response Message\n')
        assert False  # This assert is to fail the test


def getdockerID(imageName):
    image = imageName

    sendCommand = 'docker ps | grep ' + image + ' | awk \'{print $1}\''
    containerID = af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                                    command=sendCommand, return_output=True)

    containerID = containerID.strip()
    return (containerID)

#######################################################################################################################
