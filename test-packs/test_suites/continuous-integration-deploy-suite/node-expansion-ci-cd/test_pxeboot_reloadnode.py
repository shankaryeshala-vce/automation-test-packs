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
    global idrac_hostname 
    idrac_hostname = af_support_tools.get_config_file_property(config_file=setup_config_file, heading=setup_config_header, property='idrac_ipaddress') 
    global idrac_username 
    idrac_username = af_support_tools.get_config_file_property(config_file=setup_config_file, heading=setup_config_header, property='idrac_username') 
    global idrac_factory_password 
    idrac_factory_password = af_support_tools.get_config_file_property(config_file=setup_config_file, heading=setup_config_header, property='idrac_factory_password') 
#####################################################################
# These is the main script.
#####################################################################
@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_reload_node_from_rackHD():
    token = retrieveRHDToken()          # Get the RackHD Authentication Token
    testNodeIdentifier = getNodeIdentifier(token, testNodeMAC) #Get the "id" value for the Node
    ###################
    # This is where we need to send a workflow to reboot the node in PXE boot. See email for details of steps taken
    # so far.
    # Call method to reboot node. This is not written yet.
    # A delay might be needed here. Not sure how long this takes to trigger.
    ###################
    # While the node is rebooting we need to remove it from RackHD
    print ('The node id: ', testNodeIdentifier)
    obmsId = putObms(token, testNodeIdentifier)   # Call method to register Obms service to the node
    print("obmsId = ", obmsId)
    assert getObms(token, testNodeIdentifier, obmsId), 'test failed,obms service not registered to the node'   # Call method to get the Obms service to the node 
    time.sleep(20)
    graphId = postWorkflow(token, testNodeIdentifier)   # Call method to post workflow
    print("graphId =", graphId)
    assert getWorkflow(token, testNodeIdentifier,graphId), 'test failed, set pxe boot and reload didnt work as expected' # Call method to get workflow
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
def putObms(token, testNodeIdentifier):
    """
    Description:    This method will enable ipmi-obm-service on the node id 
    Parameters:     1. token     - Name of the token for Rackhd (STRING)
                    2. testNodeIdentifier          - Id of the Idrac Node (STRING)
    Returns:        obms_id (STRING) 
    """ 
    apipath = '/api/2.0/obms/'
    url = 'http://' + rackHD_IP + ':9090' + apipath
    headerstring = {"Content-Type": "application/json", "Authorization": "JWT " + token}
    body = '{"nodeId": "' + testNodeIdentifier + '","service": "ipmi-obm-service","config": {"host": "' + idrac_hostname +'" ,"user": "' + idrac_username + '","password": "' + idrac_factory_password + '"}}'
    print ('putObms body =', body)
    response = requests.put(url,headers=headerstring, data=body)
    data = response.text
    data_json = json.loads(response.text, encoding='utf-8')
    obms_id = data_json['id']
    return obms_id
def getObms(token, testNodeIdentifier, obms_id):
    """
    Description:    This method will get the status of  ipmi-obm-service on the node id 
    Parameters:     1. token     - Name of the token for Rackhd (STRING)
                    2. testNodeIdentifier          - Id of the Idrac Node (STRING)
                    3. obms_id        - OBMS ID (STRING)
    Returns:        0 or 1 (Boolean)
    """ 
    apipath = '/api/2.0/obms/' + obms_id
    url = 'http://' + rackHD_IP + ':9090' + apipath
    headerstring = {"Content-Type": "application/json", "Authorization": "JWT " + token}
    response = requests.get(url,headers=headerstring)
    data_text = response.text
    data_json = json.loads(response.text, encoding='utf-8')
    if (testNodeIdentifier not in data_text):
         print ("test failed")
         return 0
    else:
         return 1
def postWorkflow( token, testNodeIdentifier):
    """
    Description:    This method will post the workflow with the given graph_name on the node id 
    Parameters:     1. token     - Name of the token for Rackhd (STRING)
                    2. testNodeIdentifier          - Id of the Idrac Node (STRING)
    Returns:        graphID (STRING) 
    """ 
    apipath = '/api/2.0/nodes/' + testNodeIdentifier + '/workflows/'
    url = 'http://' + rackHD_IP + ':9090' + apipath
    headerstring = {"Content-Type": "application/json", "Authorization": "JWT " + token}
    body = '{ "name": "Graph.SetPxeAndReboot", "options": { "defaults": { "graphOptions": {}}}}'
    resp = requests.post(url, headers=headerstring, data=body)
    data = resp.text
    data_json = json.loads(resp.text, encoding='utf-8')
    graphID = data_json['logContext']['graphInstance']
    print ("graphID =", graphID)
    return graphID
def getWorkflow( token, testNodeIdentifier, graphID):
    """
    Description:    This method will get the workflow with the given graph_id and Validate
    Parameters:     1. token     - Name of the token for Rackhd (STRING)
                    2. testNodeIdentifier          - Id of the Idrac Node (STRING)
                    3. graphID            - ID of the graph  (STRING)
    Returns:        0 or 1 (Boolean)
    """ 
    time.sleep(60)  
    apipath = '/api/2.0/nodes/'+ testNodeIdentifier +'/workflows/'
    #apipath = '/api/2.0/nodes/workflows/'
    url = 'http://' + rackHD_IP + ':9090' + apipath
    headerstring = {"Content-Type": "application/json", "Authorization": "JWT " + token}
    response = requests.get(url,headers=headerstring)
    data_text = response.text
    data_json = json.loads(response.text, encoding='utf-8')
    print ('_status', data_json[1]['_status'])
    if (data_json[1]['_status'] != 'succeeded'):
         print ("failed")
         return 0
    else:
         return 1
def getListNodes(token, testNodeMAC):
    apipath = '/api/2.0/nodes/'
    url = 'http://' + rackHD_IP + ':9090' + apipath
    headerstring = {"Content-Type": "application/json", "Authorization": "JWT " + token}
    response = requests.get(url,headers=headerstring)
    data_text = response.text
    data_json = json.loads(response.text, encoding='utf-8')
    return (data_text)
