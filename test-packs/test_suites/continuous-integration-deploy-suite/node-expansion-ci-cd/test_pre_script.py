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


    # Update setup_config.ini file at runtime
    my_data_file = os.environ.get('AF_RESOURCES_PATH') + '/continuous-integration-deploy-suite/setup_config.properties'
    af_support_tools.set_config_file_property_by_data_file(my_data_file)

    # RackHD VM IP & Creds details
    global setup_config_file
    setup_config_file = 'continuous-integration-deploy-suite/setup_config.ini'

    global setup_config_header
    setup_config_header = 'config_details'

    global rackHD_IP
    rackHD_IP = '10.234.122.100'
    #rackHD_IP = af_support_tools.get_config_file_property(config_file=setup_config_file, heading=setup_config_header,
    #                                                    property='rackhd_integration_ipaddress')

    global rackHD_username
    rackHD_username = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                heading=setup_config_header,
                                                                property='rackhd_username')

    global rackHD_password
    rackHD_password = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                heading=setup_config_header,
                                                                property='rackhd_password')

    global testNodeMAC
    testNodeMAC = '24:6e:96:55:e4:58'
    #testNodeMAC = af_support_tools.get_config_file_property(config_file=setup_config_file,
    #                                                       heading=setup_config_header,
    #                                                        property='dne_test_node_mac')

#####################################################################
# These is the main script.
#####################################################################

def test_delete_node_from_rackHD():

    token = retrieveRHDToken()          # Get the RackHD Authentication Token

    testNodeIdentifier = getNodeIdentifier(token, testNodeMAC) #Get the "id" value for the Node

    ###################
    # This is where we need to send a workflow to reboot the node in PXE boot. See email for details of steps taken
    # so far.
    # Call method to reboot node. This is not written yet.
    # A delay might be needed here. Not sure how long this takes to trigger.
    ###################

    # While the node is rebooting we need to remove it from RackHD
    print ('Attempting to delete node: '+ testNodeIdentifier)
    delete_node_response = deleteNodes(token, testNodeIdentifier)   # Call method to delete the node

    # A successfully deleted node returns no response body
    if delete_node_response == '':
        print ('Node deleted')

    #If an active RackHD workflow is running on the node we need to cancel it
    if 'active workflow is running' in delete_node_response:
        print ('Active Workflow need to be stopped...')
        cancelWorkflow(token, testNodeIdentifier)   # Call the method to cancel any workflows.

        print ('2nd attempt to delete node: '+ testNodeIdentifier)
        delete_node_response = deleteNodes(token, testNodeIdentifier)   # Try again to delete the node

        if delete_node_response == '':
            print ('Node deleted')

    print('Node '+ testNodeMAC + 'has been successfully deleted')

    ###################
    # Now that the node has been deleted and rebooted we need to verify it has been rediscovered by RackHD
    # This is commented out as we need to get the part that reboots the node working first. Or it can be tested by
    # manually rebooting node.
    # print('\nWaiting for rediscovery...')
    #
    # timeout = 0
    # while timeout < 120:
    #     response = getListNodes(token, testNodeMAC)
    #
    #     if testNodeMAC in response:
    #         print('Node has been rediscoverd')
    #
    #     else:
    #         timeout =+1
    #         time.sleep(1)
    #         if timeout > 119:
    #             assert False, 'Error: Node not rediscovered'

    ###################

    # Next we need to check that the node is in GET /dne/nodes or Symphoyony.

####################################################################################################
#grab a token
def retrieveRHDToken():
    url = "http://" + rackHD_IP + ":9090/login"
    header = {'Content-Type': 'application/json'}
    body = '{"username": "' + rackHD_username + '", "password": "' + rackHD_password + '"}'
    resp = requests.post(url, headers=header, data=body)
    tokenJson = json.loads(resp.text, encoding='utf-8')
    token = tokenJson["token"]
    return token


def getNodeIdentifier(token, testNodeMAC):

    apipath = '/api/2.0/nodes/'
    url = 'http://' + rackHD_IP + ':9090' + apipath
    headerstring = {"Content-Type": "application/json", "Authorization": "JWT " + token}
    response = requests.get(url,headers=headerstring)
    data_text = response.text
    data_json = json.loads(response.text, encoding='utf-8')

    print ('Looking for ',testNodeMAC)

    assert testNodeMAC in data_text, 'Error: Node not in Rackhd'

    for nodes in data_json:
        if testNodeMAC in nodes['identifiers']:
            testNodeIdentifier = nodes['id']
            return testNodeIdentifier


def deleteNodes(token, testNodeIdentifier):

    apipath = '/api/2.0/nodes/'
    url = 'http://' + rackHD_IP + ':9090' + apipath + testNodeIdentifier
    headerstring = {"Content-Type": "application/json", "Authorization": "JWT " + token}
    response = requests.delete(url,headers=headerstring)
    data = response.text
    return data


def cancelWorkflow(token, testNodeIdentifier):

    print ('Attempting to cancel workflow')
    attempt = 1

    while attempt<5:

        apipath = '/api/2.0/nodes/'
        url = 'http://' + rackHD_IP + ':9090' + apipath + testNodeIdentifier + '/workflows/action'
        headerstring = {"Content-Type": "application/json", "Authorization": "JWT " + token}
        body = '{"command": "cancel"}'
        response = requests.put(url,headers=headerstring, data=body)
        data = response.text
        print (data)

        if 'No active workflow graph found for node' in data:
            attempt=5

        attempt += 1


def getListNodes(token, testNodeMAC):

    apipath = '/api/2.0/nodes/'
    url = 'http://' + rackHD_IP + ':9090' + apipath
    headerstring = {"Content-Type": "application/json", "Authorization": "JWT " + token}
    response = requests.get(url,headers=headerstring)
    data_text = response.text
    data_json = json.loads(response.text, encoding='utf-8')

    return (data_text)
