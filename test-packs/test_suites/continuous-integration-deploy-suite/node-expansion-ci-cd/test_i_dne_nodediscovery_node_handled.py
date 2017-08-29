#!/usr/bin/python
# Author:
# Revision: 2.0
# Code Reviewed by:
# Description:
#
# Copyright (c) 2017 Dell Inc. or its subsidiaries.  All Rights Reserved.
# Dell EMC Confidential/Proprietary Information
#

import json
import pytest
import af_support_tools
import time
import requests
import sys
import os


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
@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_dne_discovered_node_handled():
    """
    Title           :       Verify that dne/nodes API has disocvered Dell nodes
    Description     :       A dummy node discovered message is published to trigger the node discovery process
                            It will fail if :
                                A node is already present
                                The NodeID in the API doesn't match what RackHD sent
                                The UUID in the api doesnt match the EIDS generated value
    Parameters      :       none
    Returns         :       None
    """

    print('\nRunning Test on system: ', ipaddress)

    cleanup('test.rackhd.node.discovered.event')
    cleanup('test.eids.identity.request')
    cleanup('test.eids.identity.response')
    bindQueues('exchange.dell.cpsd.adapter.rackhd.node.discovered.event', 'test.rackhd.node.discovered.event')
    bindQueues('exchange.dell.cpsd.eids.identity.request', 'test.eids.identity.request')
    bindQueues('exchange.dell.cpsd.eids.identity.response', 'test.eids.identity.response')

    time.sleep(2)

    # Step 1: Verify the api list is empty
    currentNodes = listDellNodesAPI()
    assert currentNodes == '[]', 'ERROR: New nodes are already discovered and waiting to be handled'

    # Step 2: Publish a message to dummy a node discovery. Values used here are all dummy values.
    the_payload = '{"data":{"ipMacAddresses":[{"ipAddress":"172.31.128.12","macAddress":"fb-43-62-54-d4-3a"},{"macAddress":"b9-ce-c4-73-10-35"},{"macAddress":"4d-63-c5-48-9f-5c"},{"macAddress":"1d-97-c3-a0-42-1a"},{"macAddress":"ce-1d-b5-a6-65-ad"},{"macAddress":"30-e5-72-6f-78-79"}],"nodeId":"123456789012345678909777","nodeType":"compute"},"messageProperties":{"timestamp":"2017-06-27T08:58:32.437+0000"},"action":"discovered","createdAt":"2017-06-27T08:58:31.871Z","nodeId":"123456789012345678909777","severity":"information","type":"node","typeId":"123456789012345678909777","version":"1.0"}'

    af_support_tools.rmq_publish_message(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                         rmq_username=cpsd.props.rmq_username, rmq_password=cpsd.props.rmq_password,
                                         exchange='exchange.dell.cpsd.adapter.rackhd.node.discovered.event',
                                         routing_key='',
                                         headers={
                                             '__TypeId__': 'com.dell.converged.capabilities.compute.discovered.nodes.api.NodeEventDiscovered'},
                                         payload=the_payload, ssl_enabled=cpsd.props.rmq_ssl_enabled)

    # Step 3: Verify the node was discovered and returned a nodeID
    nodeID = rmqNodeDiscover()

    # Step 4: Verify the EIDS Messages sequence and get the UUID for the new node
    uuid = verifyEidsMessage()

    # Step 5: Verify the API now lists the discovered nodeID & UUID
    currentNodes = listDellNodesAPI()

    error_list = []

    if (nodeID in currentNodes):
        error_list.append(nodeID)

    if (uuid not in currentNodes):
        error_list.append(uuid)

    assert not error_list, 'ERROR: Node not in returned api data'

    cleanup('test.rackhd.node.discovered.event')
    cleanup('test.eids.identity.request')
    cleanup('test.eids.identity.response')


#####################################################################
# These are the main functions called in the test.

def listDellNodesAPI():
    # Function to sent a GET to an API. Returns the body of the message.

    print('\nListing Dell Nodes on API')

    url_body = ':8071/dne/nodes'
    my_url = 'http://' + ipaddress + url_body

    print('GET:', my_url)

    try:
        url_response = requests.get(my_url)
        url_response.raise_for_status()

        # 200
        print(url_response)

        the_response = url_response.text

        print('API Return Data:', the_response)

        return the_response

    # Error check the response
    except Exception as err:
        # Return code error (e.g. 404, 501, ...)
        print(err)
        print('\n')
        raise Exception(err)


def rmqNodeDiscover():
    # Verify the Node Discovered Event message
    # Return the newly discovered nodeID value

    assert waitForMsg('test.rackhd.node.discovered.event'), 'Error: No Node Discovered Msg Recieved'
    return_message = af_support_tools.rmq_consume_message(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                                          rmq_username=cpsd.props.rmq_username,
                                                          rmq_password=cpsd.props.rmq_password,
                                                          ssl_enabled=cpsd.props.rmq_ssl_enabled,
                                                          queue='test.rackhd.node.discovered.event')

    return_json = json.loads(return_message, encoding='utf-8')

    nodeID = return_json['data']['nodeId']

    return nodeID


def verifyEidsMessage():
    # We need to verify that the triggered eids.identity.request is valid.
    # Check the EIDS request messages
    # Return the EIDS UUID generated value

    assert waitForMsg('test.eids.identity.request'), 'Error: No request sent to EIDS'
    return_message = af_support_tools.rmq_consume_message(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                                          rmq_username=cpsd.props.rmq_username,
                                                          rmq_password=cpsd.props.rmq_password,
                                                          ssl_enabled=cpsd.props.rmq_ssl_enabled,
                                                          queue='test.eids.identity.request')

    # Check the EIDS response message
    assert waitForMsg('test.eids.identity.response'), 'Error: Mor response for EIDS'
    return_message = af_support_tools.rmq_consume_message(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                                          rmq_username=cpsd.props.rmq_username,
                                                          rmq_password=cpsd.props.rmq_password,
                                                          ssl_enabled=cpsd.props.rmq_ssl_enabled,
                                                          queue='test.eids.identity.response')

    return_json = json.loads(return_message, encoding='utf-8')

    uuid = return_json['elementIdentifications'][0]['elementUuid']

    return uuid


#####################################################################
# These are small functions called throughout the test.

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
    # This function keeps looping untill a message is in the specified queue. We do need it to timeout and throw an error
    # if a message never arrives. Once a message appears in the queue the function is complete and main continues.

    # The length of the queue, it will start at 0 but as soon as we get a response it will increase
    q_len = 0

    # Represents the number of seconds that have gone by since the method started
    timeout = 0

    # Max number of seconds to wait
    max_timeout = 500

    # Amount of time in seconds that the loop is going to wait on each iteration
    sleeptime = 1

    while q_len < 1:
        time.sleep(sleeptime)
        timeout += sleeptime

        q_len = af_support_tools.rmq_message_count(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                                   rmq_username=cpsd.props.rmq_username,
                                                   rmq_password=cpsd.props.rmq_password,
                                                   ssl_enabled=cpsd.props.rmq_ssl_enabled,
                                                   queue=queue)

        if timeout > max_timeout:
            print('ERROR: Message took too long to return. Something is wrong')
            return False

    return True

#######################################################################################################################
