#!/usr/bin/python
# Author: cullia
# Revision: 1.0
# Code Reviewed by:
# Description: Testing the vCenter-Adapter Container.
#
# Copyright (c) 2017 Dell Inc. or its subsidiaries.  All Rights Reserved.
# Dell EMC Confidential/Proprietary Information
#
import af_support_tools
import pytest
import json
import requests
import os
import time


##############################################################################################

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

    # vCenter VM IP & Creds details
    global capreg_config_file
    capreg_config_file = 'continuous-integration-deploy-suite/config_capreg.ini'

    global capreg_config_header
    capreg_config_header = 'config_details'

    global vcenter_IP
    vcenter_IP = af_support_tools.get_config_file_property(config_file=capreg_config_file,
                                                           heading=capreg_config_header, property='vcenter')
    global vcenter_username
    vcenter_username = af_support_tools.get_config_file_property(config_file=capreg_config_file,
                                                                 heading=capreg_config_header, property='vcenter_user')
    global vcenter_password
    vcenter_password = af_support_tools.get_config_file_property(config_file=capreg_config_file,
                                                                 heading=capreg_config_header,
                                                                 property='vcenter_password')
    global vcenter_port
    vcenter_port = '443'


#####################################################################
# These are the main tests.
#####################################################################

@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_vcenter_adapter_servicerunning():
    """
    Title           :       Verify the vCenter-Adapter service is running
    Description     :       This method tests docker service for a container
                            It will fail if :
                                Docker service is not running for the container
    Parameters      :       none
    Returns         :       None
    """

    print('\n* * * Testing the VCenter-Adapter Service on system:', ipaddress, '* * *\n')

    service_name = 'symphony-vcenter-adapter-service'

    # 1. Test the service is running
    sendCommand = "docker ps --filter name=" + service_name + "  --format '{{.Status}}' | awk '{print $1}'"
    my_return_status = af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                                         command=sendCommand, return_output=True)
    my_return_status = my_return_status.strip()
    print('\nDocker Container is:', my_return_status, '\n')
    assert my_return_status == 'Up', (service_name + " not running")


@pytest.mark.parametrize('exchange, queue', [
    ('exchange.cpsd.controlplane.vcenter.response', 'queue.dell.cpsd.dne-paqx.response.dne-paqx'),
    ('exchange.cpsd.controlplane.vcenter.request', 'queue.dell.cpsd.controlplane.vcenter.cluster.discover'),
    ('exchange.cpsd.controlplane.vcenter.request', 'queue.dell.cpsd.controlplane.vcenter.clusteroperation'),
    ('exchange.cpsd.controlplane.vcenter.request', 'queue.dell.cpsd.controlplane.vcenter.discover'),
    ('exchange.cpsd.controlplane.vcenter.request', 'queue.dell.cpsd.controlplane.vcenter.host.enter-maintenance'),
    ('exchange.cpsd.controlplane.vcenter.request', 'queue.dell.cpsd.controlplane.vcenter.host.powercommand'),
    ('exchange.cpsd.controlplane.vcenter.request', 'queue.dell.cpsd.controlplane.vcenter.register'),
    ('exchange.cpsd.controlplane.vcenter.request', 'queue.dell.cpsd.controlplane.vcenter.softwareVIB'),
    ('exchange.cpsd.controlplane.vcenter.request', 'queue.dell.cpsd.controlplane.vcenter.softwareVIBConfigure'),
    ('exchange.cpsd.controlplane.vcenter.request', 'queue.dell.cpsd.controlplane.vcenter.vm.destroy'),
    ('exchange.dell.cpsd.hdp.hal.data.provider.vcenter.compute.data.provider.request', 'queue.dell.cpsd.hdp.hal.data.provider.device.data.discovery.request.vcenter-compute-data-provider'),
    ('exchange.dell.cpsd.hdp.hal.data.provider.vcenter.compute.data.provider.request', 'queue.dell.cpsd.hdp.hal.data.provider.endpoint.validation.request.vcenter-compute-data-provider'),
    ('exchange.dell.cpsd.syds.system.definition.response', 'queue.dell.cpsd.adapter.vcenter.component.configuration.found'),
    ('exchange.dell.cpsd.cms.credentials.response', 'queue.dell.cpsd.adapter.vcenter.component.credentials.found'),
    ('exchange.dell.cpsd.endpoint.registration.event', 'queue.dell.cpsd.controlplane.vcenter.endpoint-events'),
    ('exchange.dell.cpsd.hdp.capability.registry.control','queue.dell.cpsd.hdp.capability.registry.control.vcenter-adapter'),
    ('exchange.dell.cpsd.hdp.capability.registry.event', 'queue.dell.cpsd.hdp.capability.registry.event.vcenter-adapter'),
    ('exchange.dell.cpsd.hdp.capability.registry.response', 'queue.dell.cpsd.hdp.capability.registry.response.vcenter-adapter')
])
@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_vcenter_adapter_RMQ_bindings(exchange, queue):
    """
    Title           :       Verify the RMQ bindings
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
def test_vcenter_adapter_full_ListCapabilities():
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

    # Necessary step to manually register a vcenter device in order to get a full list of capabilities.
    registerVcenter()
    time.sleep(10)  # allow time for it to be configured

    print("\nTest: Send in a list capabilities message and to verify all vCenter Adapter capabilities are present")

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

    time.sleep(5)
    checkForErrors(return_message)

    # Verify the vcenter Apapter Response
    identity = 'vcenter-adapter'
    capabilities1 = 'vcenter-consul-register'
    capabilities2 = 'vcenter-discover'
    capabilities3 = 'vcenter-enterMaintenance'
    capabilities4 = 'vcenter-destroy-virtualMachine'
    capabilities5 = 'vcenter-powercommand'
    capabilities6 = 'vcenter-discover-cluster'
    capabilities7 = 'vcenter-remove-host'
    capabilities8 = 'vcenter-addhostvcenter'
    capabilities9 = 'vcenter-install-software-vib'
    capabilities10 = 'vcenter-configure-software-vib'

    error_list = []

    if (identity not in return_message):
        error_list.append(identity)
    if (capabilities1 not in return_message):
        error_list.append(capabilities1)
    if (capabilities2 not in return_message):
        error_list.append(capabilities2)
    if (capabilities3 not in return_message):
        error_list.append(capabilities3)
    if (capabilities4 not in return_message):
        error_list.append(capabilities4)
    if (capabilities5 not in return_message):
        error_list.append(capabilities5)
    if (capabilities6 not in return_message):
        error_list.append(capabilities6)
    if (capabilities7 not in return_message):
        error_list.append(capabilities7)
    if (capabilities8 not in return_message):
        error_list.append(capabilities8)
    if (capabilities9 not in return_message):
        error_list.append(capabilities9)
    if (capabilities10 not in return_message):
        error_list.append(capabilities10)

    assert not error_list, ('Missing some vcenter-adapter capabilities')

    print('All expected vcenter-adapter Capabilities Returned\n')

    cleanup()


@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_vcenter_adapter_log_files_exist():
    """
    Title           :       Verify vcenter-adapter log files exist
    Description     :       This method tests that the vCenter Adapter log files exist.
                            It will fail:
                                If the the error and/or info log files do not exists
    Parameters      :       None
    Returns         :       None
    """

    service = 'vcenter-adapter-service'
    filePath = '/opt/dell/cpsd/vcenter-adapter-service/logs/'
    errorLogFile = 'vcenter-adapter-error.log'
    infoLogFile = 'vcenter-adapter-info.log'

    sendCommand = 'docker ps | grep '+service+' | awk \'{system("docker exec -i "$1" ls '+filePath+'") }\''

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
def test_vcenter_adapter_log_files_free_of_exceptions():
    """
    Title           :       Verify there are no exceptions in the log files
    Description     :       This method tests that the vcenter-adapter log files contain no Exceptions.
                            It will fail:
                                If the the error and/or info log files do not exists
                                If the error log file contains AuthenticationFailureException, RuntimeException, NullPointerException or BeanCreationException.
    Parameters      :       None
    Returns         :       None
    """

    service = 'vcenter-adapter-service'
    filePath = '/opt/dell/cpsd/vcenter-adapter-service/logs/'
    errorLogFile = 'vcenter-adapter-error.log'
    excep1 = 'AuthenticationFailureException'
    excep2 = 'RuntimeException'
    excep3 = 'NullPointerException'
    excep4 = 'BeanCreationException'

    # Verify the log files exist
    sendCommand = 'docker ps | grep '+service+' | awk \'{system("docker exec -i "$1" ls '+filePath+'") }\''

    my_return_status = af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                                         command=sendCommand, return_output=True)

    assert errorLogFile in my_return_status, 'Log file does not exist so unable to check for exceptions'

    error_list = []

    # Verify there are no Authentication errors
    sendCommand = 'docker ps | grep '+service+' | awk \'{system("docker exec -i "$1" cat /'+filePath+errorLogFile+' | grep '+excep1+'") }\''
    my_return_status = af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                                         command=sendCommand, return_output=True)
    print (my_return_status)
    if (excep1 in my_return_status):
        error_list.append(excep1)

    # Verify there are no RuntimeException errors
    sendCommand = 'docker ps | grep '+service+' | awk \'{system("docker exec -i "$1" cat /'+filePath+errorLogFile+' | grep '+excep2+'") }\''
    my_return_status = af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                                         command=sendCommand, return_output=True)
    if (excep2 in my_return_status):
        error_list.append(excep2)

    # Verify there are no NullPointerException errors
    sendCommand = 'docker ps | grep '+service+' | awk \'{system("docker exec -i "$1" cat /'+filePath+errorLogFile+' | grep '+excep3+'") }\''
    my_return_status = af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                                         command=sendCommand, return_output=True)
    if (excep3 in my_return_status):
        error_list.append(excep3)

    # Verify there are no BeanCreationException errors
    sendCommand = 'docker ps | grep '+service+' | awk \'{system("docker exec -i "$1" cat /'+filePath+errorLogFile+' | grep '+excep4+'") }\''
    my_return_status = af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                                         command=sendCommand, return_output=True)
    if (excep4 in my_return_status):
        error_list.append(excep4)

    assert not error_list, 'Exceptions in log files, Review the ' + errorLogFile + ' file'

    print('No '+ excep1, excep2, excep3, excep4 +' exceptions in log files\n')


##############################################################################################
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

    af_support_tools.rmq_bind_queue(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                    rmq_username=cpsd.props.rmq_username,
                                    rmq_password=cpsd.props.rmq_password,
                                    queue='test.capability.registry.response',
                                    exchange='exchange.dell.cpsd.hdp.capability.registry.response',
                                    routing_key='#', ssl_enabled=cpsd.props.rmq_ssl_enabled)


def cleanup():
    af_support_tools.rmq_delete_queue(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                      rmq_username=cpsd.props.rmq_username, rmq_password=cpsd.props.rmq_password,
                                      queue='test.capability.registry.control', ssl_enabled=cpsd.props.rmq_ssl_enabled)

    af_support_tools.rmq_delete_queue(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                      rmq_username=cpsd.props.rmq_username, rmq_password=cpsd.props.rmq_password,
                                      queue='test.capability.registry.binding', ssl_enabled=cpsd.props.rmq_ssl_enabled)

    af_support_tools.rmq_delete_queue(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                      rmq_username=cpsd.props.rmq_username,
                                      rmq_password=cpsd.props.rmq_password,
                                      queue='test.capability.registry.response', ssl_enabled=cpsd.props.rmq_ssl_enabled)


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


def rest_queue_list(user=None, password=None, host=None, port=None, virtual_host=None, exchange=None):
    """
    Description     :       This method returns all the RMQ Queues that are bound to a names RMQ Exchange.
    Parameters      :       RMQ User, RMQ password, host, port & exchange. Always virtual_host = '%2f'
    Returns         :       A list of the Queues bound to the named Exchange/
    """
    url = 'http://%s:%s/api/exchanges/%s/%s/bindings/source' % (host, port, virtual_host, exchange)
    response = requests.get(url, auth=(user, password))
    queues = [q['destination'] for q in response.json()]
    return queues

    #######################################################################################################################


def registerVcenter():
    # Until consul is  working properly & integrated with the vcenter adapter in the same environment we need to register
    # it manually by sending this message.


    the_payload = '{"messageProperties":{"timestamp":"2010-01-01T12:00:00Z","correlationId":"vcenter-registtration-corr-id","replyTo":"localhost"},"registrationInfo":{"address":"https://' + vcenter_IP + ':'+ vcenter_port+'","username":"' + vcenter_username + '","password":"' + vcenter_password + '"}}'

    af_support_tools.rmq_publish_message(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                         rmq_username=cpsd.props.rmq_username, rmq_password=cpsd.props.rmq_password,
                                         ssl_enabled=cpsd.props.rmq_ssl_enabled,
                                         exchange='exchange.cpsd.controlplane.vcenter.request',
                                         routing_key='controlplane.hypervisor.vcenter.endpoint.register',
                                         headers={
                                             '__TypeId__': 'com.dell.cpsd.vcenter.registration.info.request'},
                                         payload=the_payload)
