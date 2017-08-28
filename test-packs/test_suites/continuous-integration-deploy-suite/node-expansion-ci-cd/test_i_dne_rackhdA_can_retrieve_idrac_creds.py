#!/usr/bin/python
# Author:
# Revision:
# Code Reviewed by:
# Description:
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


def test_dne_rackhdadapter_can_retrieve_idrac_credentials():
    """
        Title           :       RackHD can retrieve iDrac creds from Vault
        Description     :       Verify that when the rackhd-adapter requests iDrac credentials the system can retrieve
                                and decrypt them.
                                It will fail if :
                                   A SUCCESS message is not returned via RMQ.
                                   The expected text strings are not int he log file
        Parameters      :       none
        Returns         :       None
    """

    print('Running test on: ' + ipaddress)
    cleanup('test.controlplane.rackhd.response')
    bindQueues('exchange.dell.cpsd.controlplane.rackhd.response', 'test.controlplane.rackhd.response')

    print("\nTest: Send in a idrac.configure.request to request credentials")

    # Send in
    the_payload = '{"messageProperties":{"timestamp":"2017-06-07T13:54:39.500Z","correlationId":"req-idrac-creds-from-rackhd","replyTo":"reply.to.queue.binding"}}'

    af_support_tools.rmq_publish_message(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                         rmq_username=cpsd.props.rmq_username, rmq_password=cpsd.props.rmq_password,
                                         exchange='exchange.dell.cpsd.controlplane.rackhd.request',
                                         routing_key='dell.cpsd.controlplane.hardware.idrac.configure.request',
                                         headers={
                                             '__TypeId__': 'dell.converged.discovered.nodes.idrac.configure.boot.device.request'},
                                         payload=the_payload,
                                         payload_type='json',
                                         ssl_enabled=cpsd.props.rmq_ssl_enabled)

    # Wait for and consume the Capability Response Message
    assert waitForMsg('test.controlplane.rackhd.response'), 'Error:'
    return_message = af_support_tools.rmq_consume_message(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                                          rmq_username=cpsd.props.rmq_username,
                                                          rmq_password=cpsd.props.rmq_password,
                                                          queue='test.controlplane.rackhd.response',
                                                          ssl_enabled=cpsd.props.rmq_ssl_enabled)

    return_json = json.loads(return_message, encoding='utf-8')

    print (return_message)

    assert return_json['status'] == 'SUCCESS', 'Error: Did not get a Success Msg back.'

    print ('SUCCESS message returned to user')

    # We verify the expected values are in the log file by calling the verify_log_file() function
    error_list = verify_log_file()
    assert not error_list, ' Review the rackhd-adapter log file'


##############################################################################################
def verify_log_file():
    """
    Description     :       This method checks the rackhd-adapter-info.log for expected text strings.
                            It will fail:
                                Never
    Parameters      :       None
    Returns         :       An error list of missing strings if they exists. If not then an empty list.
    """

    filePath = '/opt/dell/cpsd/rackhd-adapter/logs/'
    infoLogFile = 'rackhd-adapter-info.log'

    check1 = 'ConfigureBootDeviceIdracRequestMessage'
    check2a = 'ComponentCredentialsAggregate - isComplete: \[true]'
    check2b = 'ComponentCredentialsAggregate - isComplete: [true]'
    check3 = 'ConfigureBootDeviceIdracService - Successfully decrypted the password'

    error_list = []

    # Verify
    sendCommand = 'cat ' + filePath + infoLogFile + ' | grep \'' + check1 + '\''
    my_return_status = af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                                         command=sendCommand, return_output=True)
    if (check1 not in my_return_status):
        error_list.append(check1)

    # Verify
    sendCommand = 'cat ' + filePath + infoLogFile + ' | grep \'' + check2a + '\''
    my_return_status = af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                                         command=sendCommand, return_output=True)
    if (check2b not in my_return_status):
        error_list.append(check2b)

    # Verify
    sendCommand = 'cat ' + filePath + infoLogFile + ' | grep \'' + check3 + '\''
    my_return_status = af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                                         command=sendCommand, return_output=True)
    if (check3 not in my_return_status):
        error_list.append(check3)

    return (error_list)


def bindQueues(exchange, queue):
    af_support_tools.rmq_bind_queue(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                    rmq_username=cpsd.props.rmq_username,
                                    rmq_password=cpsd.props.rmq_password,
                                    queue=queue,
                                    exchange=exchange,
                                    routing_key='#', ssl_enabled=cpsd.props.rmq_ssl_enabled)


def cleanup(queue):
    af_support_tools.rmq_delete_queue(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                      rmq_username=cpsd.props.rmq_username,
                                      rmq_password=cpsd.props.rmq_password,
                                      queue=queue, ssl_enabled=cpsd.props.rmq_ssl_enabled)


def waitForMsg(queue):
    # This function keeps looping until a message is in the specified queue. We do need it to timeout and throw an error
    # if a message never arrives. Once a message appears in the queue the function is complete and main continues.

    # The length of the queue, it will start at 0 but as soon as we get a response it will increase
    q_len = 0

    # Represents the number of seconds that have gone by since the method started
    timeout = 0

    # Max number of seconds to wait
    max_timeout = 10

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
            return False

    return True
