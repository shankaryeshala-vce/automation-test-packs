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
    global rmq_port
    rmq_port = af_support_tools.get_config_file_property(config_file=env_file, heading='RabbitMQ',
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


@pytest.mark.parametrize('exchange, queue', [
    ('exchange.dell.cpsd.hdp.capability.registry.binding', 'queue.dell.cpsd.hdp.capability.registry.binding'),
    ('exchange.dell.cpsd.hdp.capability.registry.control', 'queue.dell.cpsd.hdp.capability.registry.control.cisco-network-data-provider'),
    ('exchange.dell.cpsd.hdp.capability.registry.control', 'queue.dell.cpsd.hdp.capability.registry.control.coprhd-adapter'),
    ('exchange.dell.cpsd.hdp.capability.registry.control', 'queue.dell.cpsd.hdp.capability.registry.control.endpoint-registry'),
    ('exchange.dell.cpsd.hdp.capability.registry.control', 'queue.dell.cpsd.hdp.capability.registry.control.poweredge-compute-data-provider'),
    ('exchange.dell.cpsd.hdp.capability.registry.control', 'queue.dell.cpsd.hdp.capability.registry.control.rackhd-adapter'),
    ('exchange.dell.cpsd.hdp.capability.registry.control', 'queue.dell.cpsd.hdp.capability.registry.control.vcenter-adapter'),
    ('exchange.dell.cpsd.hdp.capability.registry.control', 'queue.dell.cpsd.hdp.capability.registry.control.vcenter-compute-data-provider'),
    ('exchange.dell.cpsd.hdp.capability.registry.event','queue.dell.cpsd.hdp.capability.registry.event.rackhd-adapter'),
    ('exchange.dell.cpsd.hdp.capability.registry.event','queue.dell.cpsd.hdp.capability.registry.event.vcenter-adapter'),
    ('exchange.dell.cpsd.hdp.capability.registry.event','queue.dell.cpsd.hdp.capability.registry.event.coprhd-adapter'),
    ('exchange.dell.cpsd.hdp.capability.registry.request','queue.dell.cpsd.hdp.capability.registry.request'),
    ('exchange.dell.cpsd.hdp.capability.registry.response','queue.dell.cpsd.hdp.capability.registry.response.coprhd-adapter'),
    ('exchange.dell.cpsd.hdp.capability.registry.response','queue.dell.cpsd.hdp.capability.registry.response.rackhd-adapter'),
    ('exchange.dell.cpsd.hdp.capability.registry.response','queue.dell.cpsd.hdp.capability.registry.response.vcenter-adapter'),
    ('exchange.dell.cpsd.hdp.capability.registry.response','queue.dell.cpsd.hdp.capability.registry.response.hal-orchestrator-service')
])
@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_capability_registry_RMQ_bindings_core(exchange, queue):
    """
    Title           :       Verify the Capability Registry expected RMQ bindings.
    Description     :       This method tests that a binding exists between a RMQ Exchange & a RMQ Queue.
                            It uses the RMQ API to check.
                            It will fail if :
                                The RMQ binding does not exist
    Parameters      :       1. RMQ Exchange. 2. RQM Queue
    Returns         :       None
    """

    queues = rest_queue_list(user=rmq_username, password=rmq_password, host=ipaddress, port=15672, virtual_host='%2f',
                             exchange=exchange)
    queues = json.dumps(queues)

    assert queue in queues, 'The queue "' + queue + '" is not bound to the exchange "' + exchange + '"'
    print(exchange, '\nis bound to\n', queue, '\n')


@pytest.mark.parametrize('exchange, queue', [
    ('exchange.dell.cpsd.hdp.capability.registry.control', 'queue.dell.cpsd.hdp.capability.registry.control.node-discovery-paqx'),
    ('exchange.dell.cpsd.hdp.capability.registry.event', 'queue.dell.cpsd.hdp.capability.registry.event.node-discovery-paqx'),
    ('exchange.dell.cpsd.hdp.capability.registry.event', 'queue.dell.cpsd.hdp.capability.registry.event.dne-paqx'),
    ('exchange.dell.cpsd.hdp.capability.registry.response','queue.dell.cpsd.hdp.capability.registry.response.dne-paqx'),
    ('exchange.dell.cpsd.hdp.capability.registry.response','queue.dell.cpsd.hdp.capability.registry.response.node-discovery-paqx')
])
@pytest.mark.dne_paqx_parent
@pytest.mark.dne_paqx_parent_mvp_extended
def test_capability_registry_RMQ_bindings_dne(exchange, queue):
    """
    Title           :       Verify the Capability Registry expected RMQ bindings.
    Description     :       This method tests that a binding exists between a RMQ Exchange & a RMQ Queue.
                            It uses the RMQ API to check.
                            It will fail if :
                                The RMQ binding does not exist
    Parameters      :       1. RMQ Exchange. 2. RQM Queue
    Returns         :       None
    """

    queues = rest_queue_list(user=rmq_username, password=rmq_password, host=ipaddress, port=15672, virtual_host='%2f',
                             exchange=exchange)
    queues = json.dumps(queues)

    assert queue in queues, 'The queue "' + queue + '" is not bound to the exchange "' + exchange + '"'
    print(exchange, '\nis bound to\n', queue, '\n')


@pytest.mark.parametrize('exchange, queue', [
    ('exchange.dell.cpsd.hdp.capability.registry.event','queue.dell.cpsd.hdp.capability.registry.event.fru-paqx'),
    ('exchange.dell.cpsd.hdp.capability.registry.response','queue.dell.cpsd.hdp.capability.registry.response.fru-paqx'),
])
@pytest.mark.fru_paqx_parent
@pytest.mark.fru_mvp
def test_capability_registry_RMQ_bindings_fru(exchange, queue):
    """
    Title           :       Verify the Capability Registry expected RMQ bindings.
    Description     :       This method tests that a binding exists between a RMQ Exchange & a RMQ Queue.
                            It uses the RMQ API to check.
                            It will fail if :
                                The RMQ binding does not exist
    Parameters      :       1. RMQ Exchange. 2. RQM Queue
    Returns         :       None
    """

    queues = rest_queue_list(user=rmq_username, password=rmq_password, host=ipaddress, port=15672, virtual_host='%2f',
                             exchange=exchange)
    queues = json.dumps(queues)

    assert queue in queues, 'The queue "' + queue + '" is not bound to the exchange "' + exchange + '"'
    print(exchange, '\nis bound to\n', queue, '\n')


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

    error_list = []

    if (errorLogFile not in my_return_status):
        error_list.append(errorLogFile)

    if (infoLogFile not in my_return_status):
        error_list.append(infoLogFile)

    assert not error_list, 'Log file missing'

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


#######################################################################################################################
# These are common functions that are used throughout the main test.

def rest_queue_list(user=None, password=None, host=None, port=None, virtual_host=None, exchange=None):
    url = 'http://%s:%s/api/exchanges/%s/%s/bindings/source' % (host, port, virtual_host, exchange)
    response = requests.get(url, auth=(user, password))
    queues = [q['destination'] for q in response.json()]
    return queues

#######################################################################################################################
