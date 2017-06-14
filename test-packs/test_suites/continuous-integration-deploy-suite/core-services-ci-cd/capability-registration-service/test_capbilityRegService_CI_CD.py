#!/usr/bin/python
# Author: cullia
# Revision: 2.1
# Code Reviewed by:
# Description: Verify the service is running, logfiles exist and all RMQ bindings are present.
#
# Copyright (c) 2017 Dell Inc. or its subsidiaries.  All Rights Reserved.
# Dell EMC Confidential/Proprietary Information
#
import af_support_tools
import json
import pytest
import requests


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
def test_capabilityRegistry_servicerunning():
    """
    Title           :       Verify the Capability Registry service is running
    Description     :       This method tests docker service for a container
                            It will fail if :
                                Docker service is not running for the container
    Parameters      :       none
    Returns         :       None
    """

    print('\n* * * Testing the Capability Registry on system:', ipaddress, '* * *\n')

    service_name = 'symphony-capability-registry-service'

    # 1. Test the service is running
    sendCommand = "docker ps --filter name=" + service_name + "  --format '{{.Status}}' | awk '{print $1}'"
    my_return_status = af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                                         command=sendCommand, return_output=True)
    my_return_status = my_return_status.strip()
    print('\nDocker Container is:', my_return_status, '\n')
    assert my_return_status == 'Up', (service_name + " not running")


@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_capabilityRegistry_log_files_exist():
    """
    Title           :       Verify Capability Registry log files exist
    Description     :       This method tests that the Capability Registry log files exist.
                            It will fail:
                                If the the error and/or info log files do not exists
                                If the error log file contains AuthenticationFailureException, RuntimeException or NullPointerException.
    Parameters      :       None
    Returns         :       None
    """

    filePath = '/opt/dell/cpsd/capability-registry-service/logs/'
    errorLogFile = 'capability-registry-error.log'
    infoLogFile = 'capability-registry-info.log'

    # Verify the log files exist
    sendCommand = 'ls ' + filePath
    my_return_status = af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                                         command=sendCommand, return_output=True)
    assert errorLogFile in my_return_status, 'Error: ' + errorLogFile + ' does not exist'
    assert infoLogFile in my_return_status, 'Error: ' + infoLogFile + ' does not exist'
    print('Valid log files exist')


@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_capabilityRegistry_log_files_free_of_exceptions():
    """
    Title           :       Verify there are no exceptions in the log files
    Description     :       This method tests that the Capability Registry log files contain no Exceptions.
                            It will fail:
                                If the the error and/or info log files do not exists
                                If the error log file contains AuthenticationFailureException, RuntimeException or NullPointerException.
    Parameters      :       None
    Returns         :       None
    """

    filePath = '/opt/dell/cpsd/capability-registry-service/logs/'
    errorLogFile = 'capability-registry-error.log'
    excep1 = 'AuthenticationFailureException'
    excep2 = 'RuntimeException'
    excep3 = 'NullPointerException'

    error_list = []

    # Verify there are no Authentication errors
    sendCommand = 'cat ' + filePath + errorLogFile + ' | grep \'' + excep1 + '\''
    my_return_status = af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                                         command=sendCommand, return_output=True)
    if (excep1 in my_return_status):
        error_list.append(excep1)

    # Verify there are no RuntimeException errors
    sendCommand = 'cat ' + filePath + errorLogFile + ' | grep \'' + excep2 + '\''
    my_return_status = af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                                         command=sendCommand, return_output=True)
    if (excep2 in my_return_status):
        error_list.append(excep2)

    # Verify there are no NullPointerException errors
    sendCommand = 'cat ' + filePath + errorLogFile + ' | grep \'' + excep3 + '\''
    my_return_status = af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                                         command=sendCommand, return_output=True)
    if (excep3 in my_return_status):
        error_list.append(excep3)

    assert not error_list, 'Exceptions in log files, Review the ' + errorLogFile + ' file'

    print('No Authentication, RuntimeException or NullPointerException in log files\n')


# ****************************************************************
# Verify the "exchange.dell.cpsd.hdp.capability.registry.binding" Exchange are bound to the correct queues

@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_capabilityRegistry_Exchanges_capability_registry_binding_to_capability_registry_binding(
        suppliedExchange='exchange.dell.cpsd.hdp.capability.registry.binding',
        suppliedQueue='exchange.dell.cpsd.hdp.capability.registry.binding'):
    """
    Title           :       Verify the exchange.dell.cpsd.hdp.capability.registry.binding to exchange.dell.cpsd.hdp.capability.registry.binding RMQ binding
    Description     :       This method tests that a binding exists between a RMQ Exchange & a RMQ Queue.
                            It uses the RMQ API to check.
                            It will fail if :
                                The RMQ binding does not exist
    Parameters      :       1. RMQ Exchange. 2. RQM Queue
    Returns         :       None
    """
    queues = rest_queue_list(user=rmq_username, password=rmq_password, host=ipaddress, port=15672, virtual_host='%2f',
                             exchange=suppliedExchange)
    queues = json.dumps(queues)

    assert suppliedQueue in queues, 'The queue "' + suppliedQueue + '" is not bound to the exchange "' + suppliedExchange + '"'
    print(suppliedExchange, '\nis bound to\n', suppliedQueue, '\n')


# ****************************************************************
# Verify the "exchange.dell.cpsd.hdp.capability.registry.control" Exchanges are bound to the correct queues

@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_capabilityRegistry_Exchanges_capability_registry_control_to_cisco_network_data_provider(
        suppliedExchange='exchange.dell.cpsd.hdp.capability.registry.control',
        suppliedQueue='queue.dell.cpsd.hdp.capability.registry.control.cisco-network-data-provider'):
    """
    Title           :       Verify the exchange.dell.cpsd.hdp.capability.registry.control to queue.dell.cpsd.hdp.capability.registry.control.cisco-network-data-provider RMQ binding
    Description     :       This method tests that a binding exists between a RMQ Exchange & a RMQ Queue.
                            It uses the RMQ API to check.
                            It will fail if :
                                The RMQ binding does not exist
    Parameters      :       1. RMQ Exchange. 2. RQM Queue
    Returns         :       None
    """

    queues = rest_queue_list(user=rmq_username, password=rmq_password, host=ipaddress, port=15672, virtual_host='%2f',
                             exchange=suppliedExchange)
    queues = json.dumps(queues)

    assert suppliedQueue in queues, 'The queue "' + suppliedQueue + '" is not bound to the exchange "' + suppliedExchange + '"'
    print(suppliedExchange, '\nis bound to\n', suppliedQueue, '\n')


@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_capabilityRegistry_Exchanges_capability_registry_control_to_endpoint_registry(
        suppliedExchange='exchange.dell.cpsd.hdp.capability.registry.control',
        suppliedQueue='queue.dell.cpsd.hdp.capability.registry.control.endpoint-registry'):
    """
    Title           :       Verify the exchange.dell.cpsd.hdp.capability.registry.control to queue.dell.cpsd.hdp.capability.registry.control.endpoint-registry RMQ binding
    Description     :       This method tests that a binding exists between a RMQ Exchange & a RMQ Queue.
                            It uses the RMQ API to check.
                            It will fail if :
                                The RMQ binding does not exist
    Parameters      :       1. RMQ Exchange. 2. RQM Queue
    Returns         :       None
    """
    queues = rest_queue_list(user=rmq_username, password=rmq_password, host=ipaddress, port=15672, virtual_host='%2f',
                             exchange=suppliedExchange)
    queues = json.dumps(queues)

    assert suppliedQueue in queues, 'The queue "' + suppliedQueue + '" is not bound to the exchange "' + suppliedExchange + '"'
    print(suppliedExchange, '\nis bound to\n', suppliedQueue, '\n')


@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_capabilityRegistry_Exchanges_capability_registry_control_to_node_discovery_paqx(
        suppliedExchange='exchange.dell.cpsd.hdp.capability.registry.control',
        suppliedQueue='queue.dell.cpsd.hdp.capability.registry.control.node-discovery-paqx'):
    """
    Title           :       Verify the exchange.dell.cpsd.hdp.capability.registry.control to queue.dell.cpsd.hdp.capability.registry.control.node-discovery-paqx RMQ binding
    Description     :       This method tests that a binding exists between a RMQ Exchange & a RMQ Queue.
                            It uses the RMQ API to check.
                            It will fail if :
                                The RMQ binding does not exist
    Parameters      :       1. RMQ Exchange. 2. RQM Queue
    Returns         :       None
    """
    queues = rest_queue_list(user=rmq_username, password=rmq_password, host=ipaddress, port=15672, virtual_host='%2f',
                             exchange=suppliedExchange)
    queues = json.dumps(queues)

    assert suppliedQueue in queues, 'The queue "' + suppliedQueue + '" is not bound to the exchange "' + suppliedExchange + '"'
    print(suppliedExchange, '\nis bound to\n', suppliedQueue, '\n')


@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_capabilityRegistry_Exchanges_capability_registry_control_to_poweredge_compute_data_provider(
        suppliedExchange='exchange.dell.cpsd.hdp.capability.registry.control',
        suppliedQueue='queue.dell.cpsd.hdp.capability.registry.control.poweredge-compute-data-provider'):
    """
    Title           :       Verify the exchange.dell.cpsd.hdp.capability.registry.control to queue.dell.cpsd.hdp.capability.registry.control.poweredge-compute-data-provider RMQ binding
    Description     :       This method tests that a binding exists between a RMQ Exchange & a RMQ Queue.
                            It uses the RMQ API to check.
                            It will fail if :
                                The RMQ binding does not exist
    Parameters      :       1. RMQ Exchange. 2. RQM Queue
    Returns         :       None
    """
    queues = rest_queue_list(user=rmq_username, password=rmq_password, host=ipaddress, port=15672, virtual_host='%2f',
                             exchange=suppliedExchange)
    queues = json.dumps(queues)

    assert suppliedQueue in queues, 'The queue "' + suppliedQueue + '" is not bound to the exchange "' + suppliedExchange + '"'
    print(suppliedExchange, '\nis bound to\n', suppliedQueue, '\n')


@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_capabilityRegistry_Exchanges_capability_registry_control_to_rackhd_adapter(
        suppliedExchange='exchange.dell.cpsd.hdp.capability.registry.control',
        suppliedQueue='queue.dell.cpsd.hdp.capability.registry.control.rackhd-adapter'):
    """
    Title           :       Verify the exchange.dell.cpsd.hdp.capability.registry.control to queue.dell.cpsd.hdp.capability.registry.control.rackhd-adapter RMQ binding
    Description     :       This method tests that a binding exists between a RMQ Exchange & a RMQ Queue.
                            It uses the RMQ API to check.
                            It will fail if :
                                The RMQ binding does not exist
    Parameters      :       1. RMQ Exchange. 2. RQM Queue
    Returns         :       None
    """
    queues = rest_queue_list(user=rmq_username, password=rmq_password, host=ipaddress, port=15672, virtual_host='%2f',
                             exchange=suppliedExchange)
    queues = json.dumps(queues)

    assert suppliedQueue in queues, 'The queue "' + suppliedQueue + '" is not bound to the exchange "' + suppliedExchange + '"'
    print(suppliedExchange, '\nis bound to\n', suppliedQueue, '\n')


@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_capabilityRegistry_Exchanges_capability_registry_control_to_vcenter_adapter(
        suppliedExchange='exchange.dell.cpsd.hdp.capability.registry.control',
        suppliedQueue='queue.dell.cpsd.hdp.capability.registry.control.vcenter-adapter'):
    """
    Title           :       Verify the exchange.dell.cpsd.hdp.capability.registry.control to queue.dell.cpsd.hdp.capability.registry.control.vcenter-adapter RMQ binding
    Description     :       This method tests that a binding exists between a RMQ Exchange & a RMQ Queue.
                            It uses the RMQ API to check.
                            It will fail if :
                                The RMQ binding does not exist
    Parameters      :       1. RMQ Exchange. 2. RQM Queue
    Returns         :       None
    """
    queues = rest_queue_list(user=rmq_username, password=rmq_password, host=ipaddress, port=15672, virtual_host='%2f',
                             exchange=suppliedExchange)
    queues = json.dumps(queues)

    assert suppliedQueue in queues, 'The queue "' + suppliedQueue + '" is not bound to the exchange "' + suppliedExchange + '"'
    print(suppliedExchange, '\nis bound to\n', suppliedQueue, '\n')


@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_capabilityRegistry_Exchanges_capability_registry_control_to_vcenter_compute_data_provider(
        suppliedExchange='exchange.dell.cpsd.hdp.capability.registry.control',
        suppliedQueue='queue.dell.cpsd.hdp.capability.registry.control.vcenter-compute-data-provider'):
    """
    Title           :       Verify the exchange.dell.cpsd.hdp.capability.registry.control to queue.dell.cpsd.hdp.capability.registry.control.vcenter-compute-data-provider RMQ binding
    Description     :       This method tests that a binding exists between a RMQ Exchange & a RMQ Queue.
                            It uses the RMQ API to check.
                            It will fail if :
                                The RMQ binding does not exist
    Parameters      :       1. RMQ Exchange. 2. RQM Queue
    Returns         :       None
    """
    queues = rest_queue_list(user=rmq_username, password=rmq_password, host=ipaddress, port=15672, virtual_host='%2f',
                             exchange=suppliedExchange)
    queues = json.dumps(queues)

    assert suppliedQueue in queues, 'The queue "' + suppliedQueue + '" is not bound to the exchange "' + suppliedExchange + '"'
    print(suppliedExchange, '\nis bound to\n', suppliedQueue, '\n')


# ****************************************************************
# Verify the "exchange.dell.cpsd.hdp.capability.registry.event" Exchanges are bound to the correct queues

@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_capabilityRegistry_Exchanges_capability_registry_event_to_event_node_discovery_paqx(
        suppliedExchange='exchange.dell.cpsd.hdp.capability.registry.event',
        suppliedQueue='queue.dell.cpsd.hdp.capability.registry.event.node-discovery-paqx'):
    """
    Title           :       Verify the exchange.dell.cpsd.hdp.capability.registry.event to queue.dell.cpsd.hdp.capability.registry.event.node-discovery-paqx RMQ binding
    Description     :       This method tests that a binding exists between a RMQ Exchange & a RMQ Queue.
                            It uses the RMQ API to check.
                            It will fail if :
                                The RMQ binding does not exist
    Parameters      :       1. RMQ Exchange. 2. RQM Queue
    Returns         :       None
    """
    queues = rest_queue_list(user=rmq_username, password=rmq_password, host=ipaddress, port=15672, virtual_host='%2f',
                             exchange=suppliedExchange)
    queues = json.dumps(queues)

    assert suppliedQueue in queues, 'The queue "' + suppliedQueue + '" is not bound to the exchange "' + suppliedExchange + '"'
    print(suppliedExchange, '\nis bound to\n', suppliedQueue, '\n')


@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_capabilityRegistry_Exchanges_capability_registry_event_to_event_dne_paqx(
        suppliedExchange='exchange.dell.cpsd.hdp.capability.registry.event',
        suppliedQueue='queue.dell.cpsd.hdp.capability.registry.event.dne-paqx'):
    """
    Title           :       Verify the exchange.dell.cpsd.hdp.capability.registry.event to queue.dell.cpsd.hdp.capability.registry.event.dne-paqx RMQ binding
    Description     :       This method tests that a binding exists between a RMQ Exchange & a RMQ Queue.
                            It uses the RMQ API to check.
                            It will fail if :
                                The RMQ binding does not exist
    Parameters      :       1. RMQ Exchange. 2. RQM Queue
    Returns         :       None
    """
    queues = rest_queue_list(user=rmq_username, password=rmq_password, host=ipaddress, port=15672, virtual_host='%2f',
                             exchange=suppliedExchange)
    queues = json.dumps(queues)

    assert suppliedQueue in queues, 'The queue "' + suppliedQueue + '" is not bound to the exchange "' + suppliedExchange + '"'
    print(suppliedExchange, '\nis bound to\n', suppliedQueue, '\n')


@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_capabilityRegistry_Exchanges_capability_registry_event_to_event_rackhd_adapter(
        suppliedExchange='exchange.dell.cpsd.hdp.capability.registry.event',
        suppliedQueue='queue.dell.cpsd.hdp.capability.registry.event.rackhd-adapter'):
    """
    Title           :       Verify the exchange.dell.cpsd.hdp.capability.registry.event to queue.dell.cpsd.hdp.capability.registry.event.rackhd-adapter RMQ binding
    Description     :       This method tests that a binding exists between a RMQ Exchange & a RMQ Queue.
                            It uses the RMQ API to check.
                            It will fail if :
                                The RMQ binding does not exist
    Parameters      :       1. RMQ Exchange. 2. RQM Queue
    Returns         :       None
    """
    queues = rest_queue_list(user=rmq_username, password=rmq_password, host=ipaddress, port=15672, virtual_host='%2f',
                             exchange=suppliedExchange)
    queues = json.dumps(queues)

    assert suppliedQueue in queues, 'The queue "' + suppliedQueue + '" is not bound to the exchange "' + suppliedExchange + '"'
    print(suppliedExchange, '\nis bound to\n', suppliedQueue, '\n')


@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_capabilityRegistry_Exchanges_capability_registry_event_to_event_vcenter_adapter(
        suppliedExchange='exchange.dell.cpsd.hdp.capability.registry.event',
        suppliedQueue='queue.dell.cpsd.hdp.capability.registry.event.vcenter-adapter'):
    """
    Title           :       Verify the exchange.dell.cpsd.hdp.capability.registry.event to queue.dell.cpsd.hdp.capability.registry.event.vcenter-adapter RMQ binding
    Description     :       This method tests that a binding exists between a RMQ Exchange & a RMQ Queue.
                            It uses the RMQ API to check.
                            It will fail if :
                                The RMQ binding does not exist
    Parameters      :       1. RMQ Exchange. 2. RQM Queue
    Returns         :       None
    """
    queues = rest_queue_list(user=rmq_username, password=rmq_password, host=ipaddress, port=15672, virtual_host='%2f',
                             exchange=suppliedExchange)
    queues = json.dumps(queues)

    assert suppliedQueue in queues, 'The queue "' + suppliedQueue + '" is not bound to the exchange "' + suppliedExchange + '"'
    print(suppliedExchange, '\nis bound to\n', suppliedQueue, '\n')


# ****************************************************************
# Verify the "exchange.dell.cpsd.hdp.capability.registry.request" Exchanges are bound to the correct queues

@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_capabilityRegistry_Exchanges_capability_registry_request_to_capability_registry_request(
        suppliedExchange='exchange.dell.cpsd.hdp.capability.registry.request',
        suppliedQueue='queue.dell.cpsd.hdp.capability.registry.request'):
    """
    Title           :       Verify the exchange.dell.cpsd.hdp.capability.registry.request to queue.dell.cpsd.hdp.capability.registry.request RMQ binding
    Description     :       This method tests that a binding exists between a RMQ Exchange & a RMQ Queue.
                            It uses the RMQ API to check.
                            It will fail if :
                                The RMQ binding does not exist
    Parameters      :       1. RMQ Exchange. 2. RQM Queue
    Returns         :       None
    """
    queues = rest_queue_list(user=rmq_username, password=rmq_password, host=ipaddress, port=15672, virtual_host='%2f',
                             exchange=suppliedExchange)
    queues = json.dumps(queues)

    assert suppliedQueue in queues, 'The queue "' + suppliedQueue + '" is not bound to the exchange "' + suppliedExchange + '"'
    print(suppliedExchange, '\nis bound to\n', suppliedQueue, '\n')


# ****************************************************************
# Verify the capability.registry Exchanges are bound to the correct queues

@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_capabilityRegistry_Exchanges_capability_registry_response_to_response_coprhd_adapter(
        suppliedExchange='exchange.dell.cpsd.hdp.capability.registry.response',
        suppliedQueue='queue.dell.cpsd.hdp.capability.registry.response.coprhd-adapter'):
    """
    Title           :       Verify the exchange.dell.cpsd.hdp.capability.registry.response to queue.dell.cpsd.hdp.capability.registry.response.coprhd-adapter RMQ binding
    Description     :       This method tests that a binding exists between a RMQ Exchange & a RMQ Queue.
                            It uses the RMQ API to check.
                            It will fail if :
                                The RMQ binding does not exist
    Parameters      :       1. RMQ Exchange. 2. RQM Queue
    Returns         :       None
    """
    queues = rest_queue_list(user=rmq_username, password=rmq_password, host=ipaddress, port=15672, virtual_host='%2f',
                             exchange=suppliedExchange)
    queues = json.dumps(queues)

    assert suppliedQueue in queues, 'The queue "' + suppliedQueue + '" is not bound to the exchange "' + suppliedExchange + '"'
    print(suppliedExchange, '\nis bound to\n', suppliedQueue, '\n')


@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_capabilityRegistry_Exchanges_capability_registry_response_to_response_dne_paqx(
        suppliedExchange='exchange.dell.cpsd.hdp.capability.registry.response',
        suppliedQueue='queue.dell.cpsd.hdp.capability.registry.response.dne-paqx'):
    """
    Title           :       Verify the exchange.dell.cpsd.hdp.capability.registry.response to queue.dell.cpsd.hdp.capability.registry.response.dne-paqx RMQ binding
    Description     :       This method tests that a binding exists between a RMQ Exchange & a RMQ Queue.
                            It uses the RMQ API to check.
                            It will fail if :
                                The RMQ binding does not exist
    Parameters      :       1. RMQ Exchange. 2. RQM Queue
    Returns         :       None
    """
    queues = rest_queue_list(user=rmq_username, password=rmq_password, host=ipaddress, port=15672, virtual_host='%2f',
                             exchange=suppliedExchange)
    queues = json.dumps(queues)

    assert suppliedQueue in queues, 'The queue "' + suppliedQueue + '" is not bound to the exchange "' + suppliedExchange + '"'
    print(suppliedExchange, '\nis bound to\n', suppliedQueue, '\n')


@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_capabilityRegistry_Exchanges_capability_registry_response_to_response_node_discovery_paqx(
        suppliedExchange='exchange.dell.cpsd.hdp.capability.registry.response',
        suppliedQueue='queue.dell.cpsd.hdp.capability.registry.response.node-discovery-paqx'):
    """
    Title           :       Verify the exchange.dell.cpsd.hdp.capability.registry.response to queue.dell.cpsd.hdp.capability.registry.response.node-discovery-paqx RMQ binding
    Description     :       This method tests that a binding exists between a RMQ Exchange & a RMQ Queue.
                            It uses the RMQ API to check.
                            It will fail if :
                                The RMQ binding does not exist
    Parameters      :       1. RMQ Exchange. 2. RQM Queue
    Returns         :       None
    """
    queues = rest_queue_list(user=rmq_username, password=rmq_password, host=ipaddress, port=15672, virtual_host='%2f',
                             exchange=suppliedExchange)
    queues = json.dumps(queues)

    assert suppliedQueue in queues, 'The queue "' + suppliedQueue + '" is not bound to the exchange "' + suppliedExchange + '"'
    print(suppliedExchange, '\nis bound to\n', suppliedQueue, '\n')


@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_capabilityRegistry_Exchanges_capability_registry_response_to_response_rackhd_adapter(
        suppliedExchange='exchange.dell.cpsd.hdp.capability.registry.response',
        suppliedQueue='queue.dell.cpsd.hdp.capability.registry.response.rackhd-adapter'):
    """
    Title           :       Verify the exchange.dell.cpsd.hdp.capability.registry.response to queue.dell.cpsd.hdp.capability.registry.response.rackhd-adapter RMQ binding
    Description     :       This method tests that a binding exists between a RMQ Exchange & a RMQ Queue.
                            It uses the RMQ API to check.
                            It will fail if :
                                The RMQ binding does not exist
    Parameters      :       1. RMQ Exchange. 2. RQM Queue
    Returns         :       None
    """
    queues = rest_queue_list(user=rmq_username, password=rmq_password, host=ipaddress, port=15672, virtual_host='%2f',
                             exchange=suppliedExchange)
    queues = json.dumps(queues)

    assert suppliedQueue in queues, 'The queue "' + suppliedQueue + '" is not bound to the exchange "' + suppliedExchange + '"'
    print(suppliedExchange, '\nis bound to\n', suppliedQueue, '\n')


@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_capabilityRegistry_Exchanges_capability_registry_response_to_response_vcenter_adapter(
        suppliedExchange='exchange.dell.cpsd.hdp.capability.registry.response',
        suppliedQueue='queue.dell.cpsd.hdp.capability.registry.response.vcenter-adapter'):
    """
    Title           :       Verify the exchange.dell.cpsd.hdp.capability.registry.response to queue.dell.cpsd.hdp.capability.registry.response.vcenter-adapter RMQ binding
    Description     :       This method tests that a binding exists between a RMQ Exchange & a RMQ Queue.
                            It uses the RMQ API to check.
                            It will fail if :
                                The RMQ binding does not exist
    Parameters      :       1. RMQ Exchange. 2. RQM Queue
    Returns         :       None
    """
    queues = rest_queue_list(user=rmq_username, password=rmq_password, host=ipaddress, port=15672, virtual_host='%2f',
                             exchange=suppliedExchange)
    queues = json.dumps(queues)

    assert suppliedQueue in queues, 'The queue "' + suppliedQueue + '" is not bound to the exchange "' + suppliedExchange + '"'
    print(suppliedExchange, '\nis bound to\n', suppliedQueue, '\n')


#######################################################################################################################
# These are common functions that are used throughout the main test.

def rest_queue_list(user=None, password=None, host=None, port=None, virtual_host=None, exchange=None):
    url = 'http://%s:%s/api/exchanges/%s/%s/bindings/source' % (host, port, virtual_host, exchange)
    response = requests.get(url, auth=(user, password))
    queues = [q['destination'] for q in response.json()]
    return queues

#######################################################################################################################
