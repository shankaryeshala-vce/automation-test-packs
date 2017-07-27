#!/usr/bin/python
#
# Copyright (c) 2017 Dell Inc. or its subsidiaries.  All Rights Reserved.
# Dell EMC Confidential/Proprietary Information
#
import af_support_tools
import json
import os
import pytest
import requests
import time
import paramiko
@pytest.fixture(scope="module", autouse=True)
def load_test_data():
    import cpsd
    global cpsd
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
    # Common API details
    global headers
    headers = {'Content-Type': 'application/json'}
    global protocol
    protocol = 'http://'
    global dne_port
    dne_port = ':8071'
    # Update setup_config.properties file at runtime  
    my_data_file = os.environ.get('AF_RESOURCES_PATH') + '/continuous-integration-deploy-suite/setup_config.properties'
    af_support_tools.set_config_file_property_by_data_file(my_data_file)
    # IDrac Server IP & Creds details
    global setup_config_file    
    setup_config_file = 'continuous-integration-deploy-suite/setup_config.ini'
    global setup_config_header
    setup_config_header = 'config_details'
    global idrac_hostname
    idrac_hostname = af_support_tools.get_config_file_property(config_file=setup_config_file, heading=setup_config_header, property='idrac_ipaddress')
    global idrac_username
    idrac_username = af_support_tools.get_config_file_property(config_file=setup_config_file, heading=setup_config_header, property='idrac_username')
    global idrac_common_password
    idrac_common_password = af_support_tools.get_config_file_property(config_file=setup_config_file, heading=setup_config_header, property='idrac_common_password')
    global idrac_factory_password
    idrac_factory_password = af_support_tools.get_config_file_property(config_file=setup_config_file, heading=setup_config_header, property='idrac_factory_password')
def check_ssh(ip,usrname,passwd):
    """
    Title           :       Check SSH connection to the idrac server node
    Description     :       Check SSH connection to the idrac server node with the given credentials
                            It will fail if :
                                Unable to establish the ssh connection with the given credentials
    Parameters      :       1. ip of the idrac server node
  			    2. username of the idrac server
  			    3. password of the idrac server
    Returns         :       None
    """
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip,username=usrname,password=passwd)
        print ("\n\nSucessfully connected to " + ip + "using password: " + passwd)
        return True
    except:
        print ("could not connect to " + ip + "using password: " + passwd)
        return False
#####################################################################
# These are the main tests.
#####################################################################
#@pytest.mark.dne_paqx_parent_mvp_extended
def test_nodes_GET_workflows():
    """
    Title           :       Verify the GET function on /dne/nodes API
    Description     :       Send a GET to /dne/nodes details body.
                            We are not asserting on the content of the response as this is variable.
                            It will fail if :
                                The expected json response is not correct
    Parameters      :       none
    Returns         :       None
    """
    # Test ssh connection to idrac before starting the workflow with default password
    assert check_ssh(idrac_hostname,idrac_username,idrac_factory_password), 'ERROR: unable to log-in to iDrac'
    time.sleep(5)
    print('\n=======================Add Node Work Flow Test Begin=======================\n')
    # Invoke /dne/nodes REST API call to gather the info that will be needed for add node.
    print('GET /dne/nodes REST API call to get the discovered node and it\'s uuid...\n')
    try:
        endpoint = '/dne/nodes'
        url_body = protocol + ipaddress + dne_port + endpoint
        response = requests.get(url_body)
        # verify the status_code
        assert response.status_code == 200, 'Error: Did not get a 200 on dne/nodes'
        data = response.json()
        print('Valid /dne/nodes GET sent')
        time.sleep(1)
    # Error check the response
    except Exception as err:
        # Return code error (e.g. 404, 501, ...)
        print(err)
        print('\n')
        raise Exception(err)
#@pytest.mark.skip(reason='These requires a dedicated node to run on')
#@pytest.mark.dne_paqx_parent_mvp_extended
def test_nodes_request_workflows():
    """
    Title           :       Verify the POST function on /dne/nodes API
    Description     :       Send a POST to /dne/nodes where the body of the request is the typical DNE config
                            details body.
                            It will fail if :
                                The expected json response is not correct
    Parameters      :       none
    Returns         :       None
    """
    # Invoke POST /dne/nodes REST API
    print('POST /dne/nodes REST API call to provision an unallocated node...\n')
    global nodes_workflow_id  # set this value as global as it will be used in the next test.
    filePath = os.environ[
                   'AF_TEST_SUITE_PATH'] + '/continuous-integration-deploy-suite/node-expansion-ci-cd/fixtures/payload_addnode.json'
    with open(filePath) as fixture:
        request_body = json.loads(fixture.read())
    try:
        endpoint = '/dne/nodes'
        url_body = protocol + ipaddress + dne_port + endpoint
        response = requests.post(url_body, json=request_body, headers=headers)
        # verify the status_code
        assert response.status_code == 200, 'Error: Did not get a 200 on dne/nodes'
        data = response.json()
        nodes_workflow_id = data['workflowId']
        error_list = []
        if data['workflow'] != 'addNode':
            error_list.append(data['workflow'])
        if data['status'] != 'SUBMITTED' and data['status'] != 'IN_PROGRESS':
            error_list.append(data['status'])
        if not data['workflowId']:
            error_list.append(data['workflowId'])
        assert not error_list, 'Error: missing fields from dne/nodes response'
        for link in data['links']:
            if link['rel'] is 'self':
                assert link[
                           'href'] == "/nodes/" + nodes_workflow_id + "/startAddNodeWorkflow", 'Error: Invalid href in dne/nodes response'
        print('Valid /dne/nodes request sent')
        time.sleep(2)
    # Error check the response
    except Exception as err:
        # Return code error (e.g. 404, 501, ...)
        print(err)
        print('\n')
        raise Exception(err)
#@pytest.mark.skip(reason='These requires a dedicated node to run on')
#@pytest.mark.dne_paqx_parent_mvp_extended
def test_nodes_status_workflow():
    """
    Title           :       Verify the GET function on /dne/nodes/<jobId> API
    Description     :       Send a GET to /dne/nodes/<jobId>. The <jobId> value is the workFlowID obtained in the
                            previous test_nodes_request_workflows() test.
                            It will fail if :
                                The expected json response is not correct
    Parameters      :       none
    Returns         :       None
    """
    # Step 2: Invoke /dne/nodes/{jobId} REST API call to get the status
    print("\n\nGET /dne/nodes/<jobId> REST API call to get the nodes job status...\n")
    try:
        endpoint = '/dne/nodes/'
        url_body = protocol + ipaddress + dne_port + endpoint + nodes_workflow_id
        response = requests.get(url_body)
        # verify the status_code
        assert response.status_code == 200, 'Error: 200 not returned from dne\\nodes'
        data = response.json()
        error_list = []
        if data['workflowId'] != nodes_workflow_id:
            error_list.append(data['workflowId'])
        if not data['workflow']:
            error_list.append(data['workflow'])
        if not data['status']:
            error_list.append(data['status'])
        if not data['workflowTasksResponseList']:
            error_list.append(data['workflowTasksResponseList'])
        if not data['links']:
            error_list.append(data['links'])
        assert not error_list, 'Error: Not all tasks returned in /dne/nodes'
        # Note: we are not asserting on the contents of "workflowTasksResponseList": [] as this is changeable.
        print('Valid /dne/nodes/{jobId} status returned')
    # Error check the response
    except Exception as err:
        # Return code error (e.g. 404, 501, ...)
        print(err)
        print('\n')
        raise Exception(err)
    time.sleep(5)
    # Test ssh connection to idrac at the end of the workflow with new password
    assert check_ssh(idrac_hostname,idrac_username,idrac_common_password), 'ERROR: unable to log-in to iDrac'
