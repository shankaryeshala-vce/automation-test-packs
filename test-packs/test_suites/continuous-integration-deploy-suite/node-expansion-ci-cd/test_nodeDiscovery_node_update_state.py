#!/usr/bin/python
# Author: russed5
# Revision: 1.0
# Code Reviewed by:
# Description: Testing the ability to change the state of nodes in the Node disocvery postgres DB
#
# Copyright (c) 2017 Dell Inc. or its subsidiaries.  All Rights Reserved.
# Dell EMC Confidential/Proprietary Information
#

import af_support_tools
import json
import os
import pytest
import requests
import requests.exceptions
import time


##############################################################################################

@pytest.fixture(scope="module", autouse=True)
def load_test_data():
    import cpsd
    global cpsd

    # Set config ini file name
    global env_file
    env_file = 'env.ini'

    # Test VM Details
    global ipaddress
    ipaddress = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS',
                                                          property='hostname')
    global cli_username
    cli_username = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS',
                                                              property='username')
    global cli_password
    cli_password = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS',
                                                              property='password')

    af_support_tools.rmq_get_server_side_certs(host_hostname=cpsd.props.base_hostname,
                                               host_username=cpsd.props.base_username,
                                               host_password=cpsd.props.base_password, host_port=22,
                                               rmq_certs_path=cpsd.props.rmq_cert_path)

    global rmq_username
    rmq_username = cpsd.props.rmq_username
    global rmq_password
    rmq_password = cpsd.props.rmq_password
    global rmq_port
    rmq_port = cpsd.props.rmq_port
    global rmq_cert_path
    rmq_cert_path = cpsd.props.rmq_cert_path
    global rmq_ssl_enabled
    rmq_ssl_enabled = cpsd.props.rmq_ssl_enabled


    # a node with the following properties will be added to the DB for testing purposes
    global testElementId
    testElementId = "44f0d5ac-44a6-48e0-bf98-93eaa7f452d3"
    global testNodeId
    testNodeId = "443819a2dc8f96b33e08569d"

##############################################################################################

@pytest.mark.dne_paqx_parent
@pytest.mark.dne_paqx_parent_mvp_extended
def test_changeNodeStateToFAILED():
    """ Verify that the state of a Node, persisted by the Node Discovery PAQX, can be set to 'FAILED'"""

    # ARRANGE
    # Add a testNode  to the node discovery 'compute_node' table in the DISCOVERED state
    insertNodeIntoDB(testElementId, testNodeId, 'DISCOVERED')
    symphonyNodeId = testElementId

    # ACT
    # now set the nodeStatus to FAILED
    sendNodeAllocationRequestMessage(symphonyNodeId, "FAILED")

    # ASSERT
    # verify the new state by querying the REST API, then cleanup
    nodeListing = listNodes()
    deleteEntryInNodeComputeTable(testElementId)

    # there may be multiple nodes in the listing
    for node in nodeListing:
        if node['symphonyUuid'] == symphonyNodeId :
            assert "FAILED" == node["nodeStatus"], "Error, Status change not persisted"


##############################################################################################

@pytest.mark.dne_paqx_parent
@pytest.mark.dne_paqx_parent_mvp_extended
def test_changeNodeStateToADDED():
    """ Verify that the state of a Node, persisted by the Node Discovery PAQX, can be set to 'ADDED'"""

    # ARRANGE
    # Add a testNode  to the node discovery 'compute_node' table in the DISCOVERED state
    insertNodeIntoDB(testElementId, testNodeId, 'DISCOVERED')
    symphonyNodeId = testElementId

    # ACT
    # now set the nodeStatus to ADDED and verify the new state by querying the REST API
    sendNodeAllocationRequestMessage(symphonyNodeId, "ADDED")

    # ASSERT
    # verify the new state by querying the REST API, then cleanup
    nodeListing = listNodes()
    deleteEntryInNodeComputeTable(testElementId)

    # there may be multiple nodes in the listing
    for node in nodeListing:
        if node['symphonyUuid'] == symphonyNodeId :
            assert "ADDED" == node["nodeStatus"], "Error, Status change not persisted"


##############################################################################################

@pytest.mark.dne_paqx_parent
@pytest.mark.dne_paqx_parent_mvp_extended
def test_changeNodeStateToDISCOVERED():
    """ Verify that the state of a Node, persisted by the Node Discovery PAQX, can be set to 'DISCOVERED'"""

    # ARRANGE
    # Add a testNode  to the node discovery 'compute_node' table in the FAILED state
    insertNodeIntoDB(testElementId, testNodeId, 'FAILED')
    symphonyNodeId = testElementId

    # ACT
    # now set the nodeStatus to DISCOVERED and verify the new state by querying the REST API
    sendNodeAllocationRequestMessage(symphonyNodeId, "DISCOVERED")

    # ASSERT
    # verify the new state by querying the REST API, then cleanup
    nodeListing = listNodes()
    deleteEntryInNodeComputeTable(testElementId)

    # there may be multiple nodes in the listing
    for node in nodeListing:
        if node['symphonyUuid'] == symphonyNodeId :
            assert "DISCOVERED" == node["nodeStatus"], "Error, Status change not persisted"


##############################################################################################

@pytest.mark.dne_paqx_parent
@pytest.mark.dne_paqx_parent_mvp_extended
def test_changeNodeStateToRESERVED():
    """ Verify that the state of a Node, persisted by the Node Discovery PAQX, can be set to 'RESERVED'"""

    # ARRANGE
    # Add a testNode  to the node discovery 'compute_node' table in the DISCOVERED state
    insertNodeIntoDB(testElementId, testNodeId, 'DISCOVERED')
    symphonyNodeId = testElementId


    # ACT
    # now set the nodeStatus to RESERVED and verify the new state by querying the REST API
    sendNodeAllocationRequestMessage(symphonyNodeId, "RESERVED")

    # ASSERT
    # verify the new state by querying the REST API, then cleanup
    nodeListing = listNodes()
    deleteEntryInNodeComputeTable(testElementId)

    # there may be multiple nodes in the listing
    for node in nodeListing:
        if node['symphonyUuid'] == symphonyNodeId :
            assert "RESERVED" == node["nodeStatus"], "Error, Status change not persisted"

##############################################################################################

@pytest.mark.dne_paqx_parent
@pytest.mark.dne_paqx_parent_mvp_extended
def test_lookupNodeState():
    """ Verify that the state(s) of a Node persisted by the Node Discovery PAQX can be looked-up"""

    # ARRANGE
    error_list = []

    # ARRANGE
    # Add a testNode  to the node discovery 'compute_node' table in the DISCOVERED state
    insertNodeIntoDB(testElementId, testNodeId, 'DISCOVERED')
    symphonyNodeId = testElementId

    # bind a test q to the node discovery exchange so that we can consume a response to our message
    # but first we delete it to ensure it doesn't already exist
    cleanupQ('test.dne.paqx.node.response')
    bindQueue('exchange.dell.cpsd.paqx.node.discovery.response', 'test.dne.paqx.node.response')

    # ACT
    # send a LookupNodeAllocationRequestMessage and read-in the response
    sendNodeAllocationRequestMessage(symphonyNodeId, "LOOKUP")


    # ASSERT
    # consume response for verification and cleanup
    lookupResponse = consumeResponse('test.dne.paqx.node.response')
    cleanupQ('test.dne.paqx.node.response')
    deleteEntryInNodeComputeTable(testElementId)

    if lookupResponse['status'] != "SUCCESS":
        error_list.append("Errror : The lookupResponse message did not have a status of SUCCESS")
    if lookupResponse['nodeAllocationInfo']['elementIdentifier'] != symphonyNodeId :
        error_list.append("Errror : The elementIdentifier filed in the lookupResponse message is incorrect")
    if lookupResponse['nodeAllocationInfo']['nodeIdentifier'] != testNodeId:
        error_list.append("Errror : The nodeIdentifier field in the lookupResponse message is incorrect")
    if lookupResponse['nodeAllocationInfo']['allocationStatus'] != "DISCOVERED" :
        error_list.append("Errror : The allocationStatus field in the lookupResponse message is incorrect")
    if lookupResponse['nodeAllocationErrors'] != [] :
        error_list.append("Errror : nodeAllocationErrors in the lookupResponse message : %r" % lookupResponse['nodeAllocationErrors'])

    assert not error_list

##############################################################################################

@pytest.mark.dne_paqx_parent_mvp_extended
def test_getListOfNodes():
    """ Verify that a listing of all Node states can be retrieved."""

    # ARRANGE
    # Add a testNode  to the node discovery 'compute_node' table in the DISCOVERED state
    insertNodeIntoDB(testElementId, testNodeId, 'DISCOVERED')
    symphonyNodeId = testElementId

    # bind a test q to the node discovery exchange so that we can consume a response to our message
    cleanupQ('test.dne.paqx.node.response')
    bindQueue('exchange.dell.cpsd.paqx.node.discovery.response', 'test.dne.paqx.node.response')

    # ACT
    sendNodeAllocationRequestMessage(symphonyNodeId, "LISTING")

    # ASSERT
    # consume response for verification and cleanup
    listingsMsg = consumeResponse('test.dne.paqx.node.response')
    cleanupQ('test.dne.paqx.node.response')
    deleteEntryInNodeComputeTable(testElementId)

    assert listingsMsg['discoveredNodes'], "Error - No discovered nodes were returned in Listing"
    for node in listingsMsg['discoveredNodes']:
        if node['nodeId'] == testNodeId :
            assert "DISCOVERED" == node["allocationStatus"], "Error, wrong Node Status returned in listing"
            assert symphonyNodeId == node['convergedUuid'], "Error, wrong converged UUID returned in listing"



##############################################################################################

def insertNodeIntoDB(elementId, nodeId, nodeStatus):
    """ Insert a new node entry, DISCOVERED state, into the compute_node table in the postgres database.

    :parameter: elementId - symphonyUUID (eg. '44f0d5ac-44a6-48e0-bf98-93eaa7f452d3')
    :parameter: nodeId - rackHD-node-ID (eg. '443819a2dc8f96b33e08569d')
    :parameter: nodeStatus - state (eg. RESERVED or DISCOVERED or ADDED ...)
    :return: The result of the psql command (success result is 'INSERT 0 1')
    """

    # write the INSERT command into a file on the remote host for ease of execution
    insertCmd = "insert into ndpx.compute_node(ELEMENT_ID, NODE_ID, NODE_STATUS, LOCKING_VERSION) values ('" + \
                elementId + "', '" + nodeId + "', '" + nodeStatus + "', 0);"

    writeToFileCmd = "echo \"" + insertCmd + "\" > /tmp/sqlInsert.txt"

    try:
        result = af_support_tools.send_ssh_command(
            host=ipaddress,
            username=cli_username,
            password=cli_password,
            command=writeToFileCmd,
            return_output=True)


        # execute the PSQL command from file
        execSQLCommand = "sudo  -u postgres -H sh -c \"psql \\\"dbname=symphony options=--search_path=ndpx\\\" \
                        -f /tmp/sqlInsert.txt\""

        result = af_support_tools.send_ssh_command(
            host=ipaddress,
            username=cli_username,
            password=cli_password,
            command=execSQLCommand,
            return_output=True)

        return result

    except Exception as err:
        # Return code error
        print(err, '\n')
        raise Exception(err)


################################################################################################

def deleteEntryInNodeComputeTable(elementId):
    """ A Function to clear all entries form the postgres table 'compute_node'.

    :parameter: elementId - symphonyUUID (eg. '44f0d5ac-44a6-48e0-bf98-93eaa7f452d3')
    :return: the result of the delete command (sample success result is 'DELETE #'
    where '#' is the number of entries deleted. """

    deleteFromCommand = "DELETE FROM compute_node where ELEMENT_ID=\'" + elementId + "\';"
    writeToFileCommand = "echo \"" + deleteFromCommand + "\" > /tmp/sqlDelete.txt"

    try:

        result = af_support_tools.send_ssh_command(
                host=ipaddress,
                username=cli_username,
                password=cli_password,
                command=writeToFileCommand,
                return_output=True)

        execSQLCommand = "sudo  -u postgres -H sh -c \"psql \\\"dbname=symphony options=--search_path=ndpx\\\" \
                            -f /tmp/sqlDelete.txt\""

        result = af_support_tools.send_ssh_command(
                host=ipaddress,
                username=cli_username,
                password=cli_password,
                command=execSQLCommand,
                return_output=True)

        return result

    except Exception as err:
        # Return code error
        print(err, '\n')
        raise Exception(err)

################################################################################################

def sendNodeAllocationRequestMessage(node, state):
    """ Use the AMQP bus to send a start/cancel/fail/complete/lookup message to the node-discovery paqx for a specific node.

    :parameter: node - the symphonyUUID of a Node (eg. dc38f716-8d9e-42d6-a61b-fddf0269f5ac)
    :parameter: state - a string equal to DISCOVERED/FAILED/ADDED/LOOKUP or RESERVED"""

    if state == "DISCOVERED" : messageType = "cancel"
    elif state == "FAILED"   : messageType = "fail"
    elif state == "ADDED"    : messageType = "complete"
    elif state == "RESERVED" : messageType = "start"
    elif state == "LOOKUP" : messageType = "lookup"
    elif state == "LISTING": messageType = "list"

    my_exchange = "exchange.dell.cpsd.paqx.node.discovery.request"
    my_routing_key = "dell.cpsd.paqx.node.discovery.request"

    if messageType == "list" :
        my_type_id = "dell.converged.discovered." + messageType + ".nodes"
        my_payload = {"messageProperties": { "timestamp":"2017-09-07T03:54:39.500Z", \
                                         "correlationId":"90035098-3cd2-3fb0-9696-3f7d28e17f72", \
                                         "replyTo": "reply.to.queue.binding"}}
    else :
        my_type_id = "dell.converged.discovered.nodes." + messageType + ".node.allocation.request"
        my_payload = {"messageProperties": { "timestamp":"2017-09-07T03:54:39.500Z", \
                                         "correlationId":"90035098-3cd2-3fb0-9696-3f7d28e17f72", \
                                         "replyTo": "reply.to.queue.binding"}, \
                                         "elementIdentifier": node}

    try:
        # publish the AMQP message to set the state of the node
        af_support_tools.rmq_publish_message(host=ipaddress, rmq_username=rmq_username, rmq_password=rmq_password,
                                         port=rmq_port, ssl_enabled=rmq_ssl_enabled,
                                         exchange=my_exchange,
                                         routing_key=my_routing_key,
                                         headers={
                                             '__TypeId__': my_type_id},
                                         payload=json.dumps(my_payload))
        return None

    except Exception as err:
        # Return code error
        print(err, '\n')
        raise Exception(err)

##############################################################################################

def listNodes():
    """ Query the DNE REST API for a list of Nodes. """

    url = 'http://' + ipaddress + ':8071/dne/nodes'

    try:
        response = requests.get(url)
        response.raise_for_status()
        listing = response.text
        allNodes = json.loads(listing, encoding='utf-8')
        return allNodes

    except Exception as err:
        # Return code error (e.g. 404, 501, ...)
        print(err,'\n')
        raise Exception(err)

##############################################################################################

def getFirstValidNodeID() :
    "Get a list of all discovered nodes from the DNE and return the nodeID of the first one."

    allNodes = listNodes()
    firstNodeId = allNodes[0]['symphonyUuid']
    return firstNodeId


##################################################################################################

def bindQueue(exchange, testqueue):
    """ Bind 'testqueue' to 'exchange'."""

    af_support_tools.rmq_bind_queue(host=ipaddress,rmq_username=rmq_username, rmq_password=rmq_password,
                                    port=rmq_port, ssl_enabled=rmq_ssl_enabled,
                                    queue=testqueue,
                                    exchange=exchange,
                                    routing_key='#')

####################################################################################################

def consumeResponse(testqueue):
    """ Consume the next message received on the testqueue and return the message in json format"""
    waitForMsg('test.dne.paqx.node.response')
    rxd_message = af_support_tools.rmq_consume_message(host=ipaddress, port=rmq_port, rmq_username=rmq_username,
                                                              rmq_password=rmq_password,
                                                              queue=testqueue,
                                                              ssl_enabled=rmq_ssl_enabled)

    rxd_json = json.loads(rxd_message, encoding='utf-8')
    return rxd_json

####################################################################################################

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
    sleeptime = 10

    while q_len < 1:
        time.sleep(sleeptime)
        timeout += sleeptime

        q_len = af_support_tools.rmq_message_count(host=ipaddress,
                                                   port=rmq_port,
                                                   rmq_username=rmq_username,
                                                   rmq_password=rmq_password,
                                                   ssl_enabled=rmq_ssl_enabled,
                                                   queue=queue)

        if timeout > max_timeout:
            print('ERROR: Message took too long to return. Something is wrong')
            cleanupQ(queue)
            break

####################################################################################################

def cleanupQ(testqueue):
    """ Delete the passed-in queue."""

    af_support_tools.rmq_delete_queue(host=ipaddress, port=rmq_port,
                                      rmq_username=rmq_username,
                                      rmq_password=rmq_password,
                                      ssl_enabled=rmq_ssl_enabled,
                                    queue=testqueue)

