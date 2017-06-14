#!/usr/bin/python
# Author: cullia
# Revision: 2.1
# Code Reviewed by:
# Description: Verify all expected capabilities are returned for all providers and adapters when the user submits a
#               registry.list.capability Message
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
def test_capabilityRegistry_ListCapabilities_cisco_network_data_provider():
    """
    Title           :       Verify the registry.list.capability Message returns all cisco-network-data-provider capabilities
    Description     :       A registry.list.capability message is sent.  It is expected that a response is returned that
                            includes a list of all the cisco-network-data-provider capabilities.
                            It will fail if :
                               No capability.registry.response is received.
                               The cisco-network-data-provider is not in the response.
                               The cisco-network-data-provider capabilities are not in the response.
    Parameters      :       none
    Returns         :       None
    """
    cleanup()
    bindQueues()

    print(
        "\nTest: Send in a list capabilities message and to verify all cisco-network-data-provider capabilities are present")

    # Send in a "list capabilities message"
    originalcorrelationID = 'capability-registry-list-test-cisco-corID'
    the_payload = '{}'

    af_support_tools.rmq_publish_message(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                         rmq_username=cpsd.props.rmq_username, rmq_password=cpsd.props.rmq_password,
                                         exchange='exchange.dell.cpsd.hdp.capability.registry.request',
                                         routing_key='dell.cpsd.hdp.capability.registry.request',
                                         headers={
                                             '__TypeId__': 'com.dell.cpsd.hdp.capability.registry.list.capability.providers'},
                                         payload=the_payload,
                                         payload_type='json',
                                         correlation_id={originalcorrelationID}, ssl_enabled=cpsd.props.rmq_ssl_enabled)

    # Wait for and consume the Capability Response Message
    waitForMsg('test.capability.registry.response')
    return_message = af_support_tools.rmq_consume_message(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                                          rmq_username=cpsd.props.rmq_username,
                                                          rmq_password=cpsd.props.rmq_password,
                                                          queue='test.capability.registry.response',
                                                          ssl_enabled=cpsd.props.rmq_ssl_enabled)

    checkForErrors(return_message)
    checkForFailures(return_message)

    # Verify the Cisco Network Adapter Response.
    ciscoName = 'cisco-network-data-provider'
    ciscoCapabilities1 = 'device-data-discovery'
    ciscoCapabilities2 = 'device-endpoint-validation'
    assert ciscoName in return_message, (ciscoName, 'not returned')
    assert ciscoCapabilities1 in return_message, (ciscoCapabilities1, 'capability is not available')
    assert ciscoCapabilities2 in return_message, (ciscoCapabilities2, 'capability is not available')
    print('\nAll expected cisco-network-data-provider Capabilities Returned\n')

    cleanup()


@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_capabilityRegistry_ListCapabilities_poweredge_compute_data_provider():
    """
    Title           :       Verify the registry.list.capability Message returns all poweredge-compute-data-provider capabilities
    Description     :       A registry.list.capability message is sent.  It is expected that a response is returned that
                            includes a list of all the poweredge-compute-data-provider capabilities.
                            It will fail if :
                               No capability.registry.response is received.
                               The poweredge-compute-data-provider is not in the response.
                               The poweredge-compute-data-provider capabilities are not in the response.
    Parameters      :       none
    Returns         :       None
    """
    cleanup()
    bindQueues()

    print("\nTest: Send in a list capabilities message and to verify all PowerEdge capabilities are present")

    # Send in a "list capabilities message"
    originalcorrelationID = 'capability-registry-list-PowerEdge-corID'
    the_payload = '{}'

    af_support_tools.rmq_publish_message(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                         rmq_username=cpsd.props.rmq_username, rmq_password=cpsd.props.rmq_password,
                                         exchange='exchange.dell.cpsd.hdp.capability.registry.request',
                                         routing_key='dell.cpsd.hdp.capability.registry.request',
                                         headers={
                                             '__TypeId__': 'com.dell.cpsd.hdp.capability.registry.list.capability.providers'},
                                         payload=the_payload,
                                         payload_type='json',
                                         correlation_id={originalcorrelationID}, ssl_enabled=cpsd.props.rmq_ssl_enabled)

    # Wait for and consume the Capability Response Message
    waitForMsg('test.capability.registry.response')
    return_message = af_support_tools.rmq_consume_message(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                                          rmq_username=cpsd.props.rmq_username,
                                                          rmq_password=cpsd.props.rmq_password,
                                                          queue='test.capability.registry.response',
                                                          ssl_enabled=cpsd.props.rmq_ssl_enabled)

    checkForErrors(return_message)
    checkForFailures(return_message)

    # Verify the PowerEdge Response
    powerEdgeName = 'poweredge-compute-data-provider'
    powerEdgeCapabilities1 = 'device-data-discovery'
    powerEdgeCapabilities2 = 'device-endpoint-validation'
    assert powerEdgeName in return_message, (powerEdgeName, 'not returned')
    assert powerEdgeCapabilities1 in return_message, (powerEdgeCapabilities1, 'capability is not available')
    assert powerEdgeCapabilities2 in return_message, (powerEdgeCapabilities2, 'capability is not available')
    print('All expected poweredge-compute-data-provider Capabilities Returned\n')

    cleanup()


@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_capabilityRegistry_ListCapabilities_vcenter_compute_data_provider():
    """
    Title           :       Verify the registry.list.capability Message returns all vcenter-compute-data-provider capabilities
    Description     :       A registry.list.capability message is sent.  It is expected that a response is returned that
                            includes a list of all the vcenter-compute-data-provider capabilities.
                            It will fail if :
                               No capability.registry.response is received.
                               The vcenter-compute-data-provider is not in the response.
                               The vcenter-compute-data-provider capabilities are not in the response.
    Parameters      :       none
    Returns         :       None
    """
    cleanup()
    bindQueues()

    print(
        "\nTest: Send in a list capabilities message and to verify all vCenter Compute Data Provider capabilities are present")

    # Send in a "list capabilities message"
    originalcorrelationID = 'capability-registry-list-vcenterdp-corID'
    the_payload = '{}'

    af_support_tools.rmq_publish_message(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                         rmq_username=cpsd.props.rmq_username, rmq_password=cpsd.props.rmq_password,
                                         exchange='exchange.dell.cpsd.hdp.capability.registry.request',
                                         routing_key='dell.cpsd.hdp.capability.registry.request',
                                         headers={
                                             '__TypeId__': 'com.dell.cpsd.hdp.capability.registry.list.capability.providers'},
                                         payload=the_payload,
                                         payload_type='json',
                                         correlation_id={originalcorrelationID}, ssl_enabled=cpsd.props.rmq_ssl_enabled)

    # Wait for and consume the Capability Response Message
    waitForMsg('test.capability.registry.response')
    return_message = af_support_tools.rmq_consume_message(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                                          rmq_username=cpsd.props.rmq_username,
                                                          rmq_password=cpsd.props.rmq_password,
                                                          queue='test.capability.registry.response',
                                                          ssl_enabled=cpsd.props.rmq_ssl_enabled)

    checkForErrors(return_message)
    checkForFailures(return_message)

    # Verify the vCenter Compute Data Provider Response
    vcenterDPName = 'vcenter-compute-data-provider'
    vcenterDPCapabilities1 = 'device-data-discovery'
    vcenterDPCapabilities2 = 'device-endpoint-validation'
    assert vcenterDPName in return_message, (vcenterDPName, 'not returned')
    assert vcenterDPCapabilities1 in return_message, (vcenterDPCapabilities1, 'capability is not available')
    assert vcenterDPCapabilities2 in return_message, (vcenterDPCapabilities1, 'capability is not available')

    print('All expected vcenter-compute-data-provider Capabilities Returned\n')

    cleanup()


@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_capabilityRegistry_ListCapabilities_rackhd_adapter():
    """
    Title           :       Verify the registry.list.capability Message returns all rackhd-adapter capabilities
    Description     :       A registry.list.capability message is sent.  It is expected that a response is returned that
                            includes a list of all the rackhd-adapter capabilities.
                            It will fail if :
                               No capability.registry.response is received.
                               The rackhd-adapter is not in the response.
                               The rackhd-adapter capabilites are not in the response.
    Parameters      :       none
    Returns         :       None
    """
    cleanup()
    bindQueues()

    print("\nTest: Send in a list capabilities message and to verify all RackHD Adapter capabilities are present")

    # Send in a "list capabilities message"
    originalcorrelationID = 'capability-registry-list-rackhd-adapter-corID'
    the_payload = '{}'

    af_support_tools.rmq_publish_message(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                         rmq_username=cpsd.props.rmq_username, rmq_password=cpsd.props.rmq_password,
                                         exchange='exchange.dell.cpsd.hdp.capability.registry.request',
                                         routing_key='dell.cpsd.hdp.capability.registry.request',
                                         headers={
                                             '__TypeId__': 'com.dell.cpsd.hdp.capability.registry.list.capability.providers'},
                                         payload=the_payload,
                                         payload_type='json',
                                         correlation_id={originalcorrelationID}, ssl_enabled=cpsd.props.rmq_ssl_enabled)

    # Wait for and consume the Capability Response Message
    waitForMsg('test.capability.registry.response')
    return_message = af_support_tools.rmq_consume_message(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                                          rmq_username=cpsd.props.rmq_username,
                                                          rmq_password=cpsd.props.rmq_password,
                                                          queue='test.capability.registry.response',
                                                          ssl_enabled=cpsd.props.rmq_ssl_enabled)

    checkForErrors(return_message)
    checkForFailures(return_message)

    # Verify the RackHD Apapter Response
    nodeDisName = 'rackhd-adapter'
    nodeDisCapabilities1 = 'rackhd-consul-register'
    assert nodeDisName in return_message, (nodeDisName, 'not returned')
    assert nodeDisCapabilities1 in return_message, (nodeDisCapabilities1, 'capability is not available')

    print('All expected rackhd-adapter Capabilities Returned\n')

    cleanup()


@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_capabilityRegistry_ListCapabilities_vcenter_adapter():
    """
    Title           :       Verify the registry.list.capability Message returns all vcenter-adapter capabilities
    Description     :       A registry.list.capability message is sent.  It is expected that a response is returned that
                            includes a list of all the vcenter-adapter capabilities.
                            It will fail if :
                               No capability.registry.response is received.
                               The vcenter-adapter is not in the response.
                               The vcenter-adapter capabilites are not in the response.
    Parameters      :       none
    Returns         :       None
    """
    cleanup()
    bindQueues()

    print("\nTest: Send in a list capabilities message and to verify all VCenter Adapter capabilities are present")

    # Send in a "list capabilities message"
    originalcorrelationID = 'capability-registry-list-vcenter-adapter-corID'
    the_payload = '{}'

    af_support_tools.rmq_publish_message(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                         rmq_username=cpsd.props.rmq_username, rmq_password=cpsd.props.rmq_password,
                                         exchange='exchange.dell.cpsd.hdp.capability.registry.request',
                                         routing_key='dell.cpsd.hdp.capability.registry.request',
                                         headers={
                                             '__TypeId__': 'com.dell.cpsd.hdp.capability.registry.list.capability.providers'},
                                         payload=the_payload,
                                         payload_type='json',
                                         correlation_id={originalcorrelationID}, ssl_enabled=cpsd.props.rmq_ssl_enabled)

    # Wait for and consume the Capability Response Message
    waitForMsg('test.capability.registry.response')
    return_message = af_support_tools.rmq_consume_message(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                                          rmq_username=cpsd.props.rmq_username,
                                                          rmq_password=cpsd.props.rmq_password,
                                                          queue='test.capability.registry.response',
                                                          ssl_enabled=cpsd.props.rmq_ssl_enabled)

    checkForErrors(return_message)
    checkForFailures(return_message)

    # Verify the VCenter Response
    vcenterName = 'vcenter-adapter'
    vcenterCapabilities1 = 'vcenter-consul-register'
    assert vcenterName in return_message, (vcenterName, 'not returned')
    assert vcenterCapabilities1 in return_message, (vcenterCapabilities1, 'capability is not available')

    print('All expected vcenter-adapter Capabilities Returned\n')

    cleanup()


@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_capabilityRegistry_ListCapabilities_coprhd_adapter():
    """
    Title           :       Verify the registry.list.capability Message returns all coprhd-adapter capabilities
    Description     :       A registry.list.capability message is sent.  It is expected that a response is returned that
                            includes a list of all the coprhd-adapter capabilities.
                            It will fail if :
                               No capability.registry.response is received.
                               The coprhd-adapter is not in the response.
                               The coprhd-adapter capabilities are not in the response.
    Parameters      :       none
    Returns         :       None
    """
    cleanup()
    bindQueues()

    print("\nTest: Send in a list capabilities message and to verify all CoprHD Adapter capabilities are present")

    # Send in a "list capabilities message"
    originalcorrelationID = 'capability-registry-list-coprhd-adapter-corID'
    the_payload = '{}'

    af_support_tools.rmq_publish_message(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                         rmq_username=cpsd.props.rmq_username, rmq_password=cpsd.props.rmq_password,
                                         exchange='exchange.dell.cpsd.hdp.capability.registry.request',
                                         routing_key='dell.cpsd.hdp.capability.registry.request',
                                         headers={
                                             '__TypeId__': 'com.dell.cpsd.hdp.capability.registry.list.capability.providers'},
                                         payload=the_payload,
                                         payload_type='json',
                                         correlation_id={originalcorrelationID}, ssl_enabled=cpsd.props.rmq_ssl_enabled)

    # Wait for and consume the Capability Response Message
    waitForMsg('test.capability.registry.response')
    return_message = af_support_tools.rmq_consume_message(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                                          rmq_username=cpsd.props.rmq_username,
                                                          rmq_password=cpsd.props.rmq_password,
                                                          queue='test.capability.registry.response',
                                                          ssl_enabled=cpsd.props.rmq_ssl_enabled)

    checkForErrors(return_message)
    checkForFailures(return_message)

    # Verify the CoprHD Response
    coprHDName = 'coprhd-adapter'
    coprHDCapabilities1 = 'coprhd-consul-register'
    assert coprHDName in return_message, (coprHDName, 'not returned')
    assert coprHDCapabilities1 in return_message, (coprHDCapabilities1, 'capability is not available')

    print('All expected coprhd-adapter Capabilities Returned\n')

    cleanup()


@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_capabilityRegistry_ListCapabilities_endpoint_registry():
    """
    Title           :       Verify the registry.list.capability Message returns all endpoint-registry capabilities
    Description     :       A registry.list.capability message is sent.  It is expected that a response is returned that
                            includes a list of all the endpoint-registry capabilities.
                            It will fail if :
                               No capability.registry.response is received.
                               The endpoint-registry is not in the response.
                               The endpoint-registry capabilities are not in the response.
    Parameters      :       none
    Returns         :       None
    """
    cleanup()
    bindQueues()

    print("\nTest: Send in a list capabilities message and to verify all endpoint-registry capabilities are present")

    # Send in a "list capabilities message"
    originalcorrelationID = 'capability-registry-listendpoint-registry-corID'
    the_payload = '{}'

    af_support_tools.rmq_publish_message(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                         rmq_username=cpsd.props.rmq_username, rmq_password=cpsd.props.rmq_password,
                                         exchange='exchange.dell.cpsd.hdp.capability.registry.request',
                                         routing_key='dell.cpsd.hdp.capability.registry.request',
                                         headers={
                                             '__TypeId__': 'com.dell.cpsd.hdp.capability.registry.list.capability.providers'},
                                         payload=the_payload,
                                         payload_type='json',
                                         correlation_id={originalcorrelationID}, ssl_enabled=cpsd.props.rmq_ssl_enabled)

    # Wait for and consume the Capability Response Message
    waitForMsg('test.capability.registry.response')
    return_message = af_support_tools.rmq_consume_message(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                                          rmq_username=cpsd.props.rmq_username,
                                                          rmq_password=cpsd.props.rmq_password,
                                                          queue='test.capability.registry.response',
                                                          ssl_enabled=cpsd.props.rmq_ssl_enabled)

    checkForErrors(return_message)
    checkForFailures(return_message)

    # Verify the Endpoint Registery Response
    endPointRegName = 'endpoint-registry'
    endPointRegCapabilities1 = 'endpoint-registry-lookup'
    assert endPointRegName in return_message, (endPointRegName, 'not returned')
    assert endPointRegCapabilities1 in return_message, (endPointRegCapabilities1, 'capability is not available')
    print('All expected endpoint-registry Capabilities Returned\n')

    cleanup()


@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_capabilityRegistry_ListCapabilities_node_discovery_paqx():
    """
    Title           :       Verify the registry.list.capability Message returns all node-discovery-paqx capabilities
    Description     :       A registry.list.capability message is sent.  It is expected that a response is returned that
                            includes a list of all the node-discovery-paqx capabilities.
                            It will fail if :
                               No capability.registry.response is received.
                               The node-discovery-paqx is not in the response.
                               The node-discovery-paqx capabilities are not in the response.
    Parameters      :       none
    Returns         :       None
    """
    cleanup()
    bindQueues()

    print("\nTest: Send in a list capabilities message and to verify all node-discovery-paqx capabilities are present")

    # Send in a "list capabilities message"
    originalcorrelationID = 'capability-registry-list-node-discover-corID'
    the_payload = '{}'

    af_support_tools.rmq_publish_message(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                         rmq_username=cpsd.props.rmq_username, rmq_password=cpsd.props.rmq_password,
                                         exchange='exchange.dell.cpsd.hdp.capability.registry.request',
                                         routing_key='dell.cpsd.hdp.capability.registry.request',
                                         headers={
                                             '__TypeId__': 'com.dell.cpsd.hdp.capability.registry.list.capability.providers'},
                                         payload=the_payload,
                                         payload_type='json',
                                         correlation_id={originalcorrelationID}, ssl_enabled=cpsd.props.rmq_ssl_enabled)

    # Wait for and consume the Capability Response Message
    waitForMsg('test.capability.registry.response')
    return_message = af_support_tools.rmq_consume_message(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                                          rmq_username=cpsd.props.rmq_username,
                                                          rmq_password=cpsd.props.rmq_password,
                                                          queue='test.capability.registry.response',
                                                          ssl_enabled=cpsd.props.rmq_ssl_enabled)

    checkForErrors(return_message)
    checkForFailures(return_message)

    # Verify the Node Discovery Response
    nodeDisName = 'node-discovery-paqx'
    nodeDisCapabilities1 = 'list-discovered-nodes'
    assert nodeDisName in return_message, (nodeDisName, 'not returned')
    assert nodeDisCapabilities1 in return_message, (nodeDisCapabilities1, 'capability is not available')

    print('All expected node-discovery-paqx Capabilities Returned\n')

    cleanup()


#######################################################################################################################
# These are common functions that are used throughout the main test.

def bindQueues():
    af_support_tools.rmq_bind_queue(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                    rmq_username=cpsd.props.rmq_username,
                                    rmq_password=cpsd.props.rmq_password,
                                    queue='test.capability.registry.response',
                                    exchange='exchange.dell.cpsd.hdp.capability.registry.response',
                                    routing_key='#', ssl_enabled=cpsd.props.rmq_ssl_enabled)


def cleanup():
    af_support_tools.rmq_delete_queue(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                      rmq_username=cpsd.props.rmq_username,
                                      rmq_password=cpsd.props.rmq_password,
                                      queue='test.capability.registry.response', ssl_enabled=cpsd.props.rmq_ssl_enabled)


def waitForMsg(queue):
    # This function keeps looping untill a message is in the specified queue. We do need it to timeout and throw an error
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


def checkForFailures(return_message):
    checklist = 'failureReasons'
    if checklist in return_message:
        return_json = json.loads(return_message, encoding='utf-8')
        errorMsg = return_json['failureReasons'][0]['message']
        print('The following error has been returned :', errorMsg)
        print('Possible component validation issue')
        assert False  # This assert is to fail the test

#######################################################################################################################
