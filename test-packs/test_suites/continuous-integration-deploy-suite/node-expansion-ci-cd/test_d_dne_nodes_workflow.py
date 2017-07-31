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
    idrac_hostname = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                               heading=setup_config_header, property='idrac_ipaddress')

    global idrac_username
    idrac_username = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                               heading=setup_config_header, property='idrac_username')

    global idrac_common_password
    idrac_common_password = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                      heading=setup_config_header,
                                                                      property='idrac_common_password')

    global idrac_factory_password
    idrac_factory_password = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                       heading=setup_config_header,
                                                                       property='idrac_factory_password')


#####################################################################
# These are the main tests.
#####################################################################

@pytest.mark.skip(reason='These requires a dedicated node to run on')
@pytest.mark.dne_paqx_parent_mvp_extended
def test_pre_test_verification():
    """
    Description     :       This is a pre test check list. It checks:
                                1) Factory Creds are valid
                                2) Default Creds are invalid
                                3) Any other checks...

    Parameters      :       none
    Returns         :       None
    """
    # Test ssh connection to idrac before starting the workflow with Factory configured password
    assert check_ssh(idrac_hostname, idrac_username, idrac_factory_password), 'ERROR: unable to log-in to iDrac with Factory Creds'
    time.sleep(3)

    # Test ssh connection to idrac before starting the workflow with Common configured password - should not allow connection
    assert not check_ssh(idrac_hostname, idrac_username, idrac_common_password), 'ERROR: able to log-in to iDrac with Common creds'
    time.sleep(3)


@pytest.mark.skip(reason='These requires a dedicated node to run on')
@pytest.mark.dne_paqx_parent_mvp_extended
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

    print('\n=======================Add Node Work Flow Test Begin=======================\n')

    # Step 1: Invoke /dne/nodes REST API call to gather the info that will be needed for add node.
    print('Send GET /dne/nodes REST API call to verify the discovered node\n')

    try:
        endpoint = '/dne/nodes'
        url_body = protocol + ipaddress + dne_port + endpoint
        response = requests.get(url_body)
        # verify the status_code
        assert response.status_code == 200, 'Error: Did not get a 200 on dne/nodes'
        data = response.json()

        assert data['nodeStatus'] == 'DISCOVERED', 'Error: Node not in a doscovered state'

        print('Valid /dne/nodes Response received')
        time.sleep(1)

    # Error check the response
    except Exception as err:
        # Return code error (e.g. 404, 501, ...)
        print(err)
        print('\n')
        raise Exception(err)


@pytest.mark.skip(reason='These requires a dedicated node to run on')
@pytest.mark.dne_paqx_parent_mvp_extended
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

    # Step 2: Invoke POST /dne/nodes REST API to provission the node
    print('Send POST /dne/nodes REST API call to provision an unallocated node...\n')

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
        print (nodes_workflow_id)

        error_list = []

        if data['workflow'] != 'addNode':
            error_list.append(data['workflow'])

        if data['status'] != 'SUBMITTED' and data['status'] != 'IN_PROGRESS':
            error_list.append(data['status'])

        if not data['workflowId']:
            error_list.append(data['workflowId'])

        assert not error_list, 'Error: missing fields from dne/nodes response'

        print('Valid /dne/nodes request has been sent')
        time.sleep(2)

    # Error check the response
    except Exception as err:
        # Return code error (e.g. 404, 501, ...)
        print(err)
        print('\n')
        raise Exception(err)


@pytest.mark.skip(reason='These requires a dedicated node to run on')
@pytest.mark.dne_paqx_parent_mvp_extended
def test_nodes_status_workflow():
    """
    Title           :       Verify the GET function on /dne/nodes/<jobId> API
    Description     :       Send a GET to /dne/nodes/<jobId>. The <jobId> value is the workFlowID obtained in the
                            previous test_nodes_request_workflows() test.
                            Each expected step in the workflow process will be checked.
                                1. Finding discovered Nodes
                                2. Change Out of Band Management Credentials
                                n-1. Update System Definition
                                n. Notify Node Discovery To Update Status
                            This tes will be updated as new steps are added to the workflow
                            It will fail if :
                                Any of the steps along the wat fail
    Parameters      :       none
    Returns         :       None
    """
    # Step 3: Invoke /dne/nodes/{jobId} REST API call to get the status
    print("\n\nSend GET /dne/nodes/<jobId> REST API call to get the addnodes job status...\n")

    workflow_status = ''
    while workflow_status != 'SUCCEEDED':

        try:
            endpoint = '/dne/nodes/'
            url_body = protocol + ipaddress + dne_port + endpoint + nodes_workflow_id
            response = requests.get(url_body)
            assert response.status_code == 200, 'Error: 200 not returned from dne\\nodes'  # verify the status_code
            data = response.text
            data = json.loads(data, encoding='utf-8')

            # If the process has failed immediately then fail the test outright
            assert data['status'] != 'FAILED', 'ERROR: The addnode workflow overall status = Failed'

            ######################### Finding discovered Nodes
            if data['workflowTasksResponseList'][0]['workFlowTaskName'] == 'Finding discovered Nodes':
                assert data['workflowTasksResponseList'][0][
                           'workFlowTaskStatus'] != 'FAILED', 'ERROR: Workflow "Finding discovered Nodes" Failed'

                timeout = 0
                while timeout < 100:
                    # Get the latest state from the API
                    response = requests.get(url_body)
                    data = response.text
                    data = json.loads(data, encoding='utf-8')

                    if data['workflowTasksResponseList'][0]['workFlowTaskStatus'] == 'IN_PROGRESS':
                        time.sleep(1)
                        timeout += 1
                        # If the task is still in progress wait and then refresh the API data

                    if data['workflowTasksResponseList'][0]['workFlowTaskStatus'] == 'SUCCEEDED':
                        assert data['workflowTasksResponseList'][0]['results'][
                                   'nodeStatus'] == 'DISCOVERED', 'Error: Node not is a discovered state'
                        print('Step 1: New node discoverd')
                        time.sleep(5)
                        break
                        # Validate a SUCCEEDED message by checking the status on the node.

                    if data['workflowTasksResponseList'][0]['workFlowTaskStatus'] == 'FAILED':
                        assert data['workflowTasksResponseList'][0][
                                   'workFlowTaskStatus'] == 'FAILED', 'Error: Failed to doscover a new node'
                        # If the task has failed then fail the entire test.


            ######################### Change Out of Band Management Credentials
            if data['workflowTasksResponseList'][1]['workFlowTaskName'] == 'Change Out of Band Management Credentials':
                assert data['workflowTasksResponseList'][1][
                           'workFlowTaskStatus'] != 'FAILED', 'ERROR: Workflow "Change Out of Band Management Credentials" Failed'

                timeout = 0
                while timeout < 100:
                    # Get the latest state from the API
                    response = requests.get(url_body)
                    data = response.text
                    data = json.loads(data, encoding='utf-8')

                    if data['workflowTasksResponseList'][1]['workFlowTaskStatus'] == 'IN_PROGRESS':
                        time.sleep(1)
                        timeout += 1
                        # If the task is still in progress wait and then refresh the API data

                    # Check that new credentials do allow user to log into server
                    if data['workflowTasksResponseList'][1]['workFlowTaskStatus'] == 'SUCCEEDED':
                        assert check_ssh(idrac_hostname, idrac_username,
                                         idrac_common_password), 'ERROR: unable to log-in to iDrac'
                        assert not check_ssh(idrac_hostname, idrac_username,
                                             idrac_factory_password), 'ERROR: still able to log-in to iDrac with Factory Creds'
                        print ('Step2: Change Out of Band Management Credentials has Succeeded\n')
                        time.sleep(5)
                        break
                        # Validate a SUCCEEDED message by checking ssh connection to idrac at the end of the workflow with new password

                    if data['workflowTasksResponseList'][1]['workFlowTaskStatus'] == 'FAILED':
                        assert data['workflowTasksResponseList'][1][
                                   'workFlowTaskStatus'] != 'FAILED', 'Error: failed to change iDrac credentials'
                        # If the task has failed then fail the entire test.


            ######################### Update System Definition
            if data['workflowTasksResponseList'][2]['workFlowTaskName'] == 'Update System Definition':
                assert data['workflowTasksResponseList'][2][
                           'workFlowTaskStatus'] != 'FAILED', 'ERROR: Workflow "Update System Definition" Failed'

                timeout = 0
                while timeout < 100:
                    # Get the latest state from the API
                    response = requests.get(url_body)
                    data = response.text
                    data = json.loads(data, encoding='utf-8')

                    if data['workflowTasksResponseList'][2]['workFlowTaskStatus'] == 'IN_PROGRESS':
                        time.sleep(1)
                        timeout += 1
                        # If the task is still in progress wait and then refresh the API data

                    # Check something
                    if data['workflowTasksResponseList'][2]['workFlowTaskStatus'] == 'SUCCEEDED':
                        # TODO need to figure out how to test this
                        print ('Step n-1: Update System Definition has Succeeded\n')
                        break
                        # Validate a SUCCEEDED message by checking something??

                    if data['workflowTasksResponseList'][2]['workFlowTaskStatus'] == 'FAILED':
                        assert data['workflowTasksResponseList'][2][
                                   'workFlowTaskStatus'] != 'FAILED', 'Error: failed to update system defnition'
                        # If the task has failed then fail the entire test.


            ######################### Notify Node Discovery To Update Status
            if data['workflowTasksResponseList'][3]['workFlowTaskName'] == 'Notify Node Discovery To Update Status':
                assert data['workflowTasksResponseList'][3][
                           'workFlowTaskStatus'] != 'FAILED', 'ERROR: Workflow "Notify Node Discovery To Update Status" Failed'

                timeout = 0
                while timeout < 100:
                    # Get the latest state from the API
                    response = requests.get(url_body)
                    data = response.text
                    data = json.loads(data, encoding='utf-8')

                    if data['workflowTasksResponseList'][3]['workFlowTaskStatus'] == 'IN_PROGRESS':
                        time.sleep(1)
                        timeout += 1
                        # If the task is still in progress wait and then refresh the API data

                    # Check the status of the node is now "ADDED" in GET /dne/nodes
                    if data['workflowTasksResponseList'][3]['workFlowTaskStatus'] == 'SUCCEEDED':
                        endpoint = '/dne/nodes'
                        url_body = protocol + ipaddress + dne_port + endpoint
                        response = requests.get(url_body)
                        data2 = response.text
                        data2 = json.loads(data2, encoding='utf-8')

                        assert data2[0]['nodeStatus'] == 'ADDED', 'Error: Node status has not been updated'
                        print ('Step n: Node status has changed to "ADDED"\n')
                        break
                        # Validate a SUCCEEDED message by checking the node state has changed to ADDED

                    if data['workflowTasksResponseList'][3]['workFlowTaskStatus'] == 'FAILED':
                        assert data['workflowTasksResponseList'][3][
                                   'workFlowTaskStatus'] != 'FAILED', 'Error: failed to update system defnition'
                        # If the task has failed then fail the entire test.

            workflow_status = data['status']

            print('Test Pass: Node added successfully')

        # Error check the response
        except Exception as err:
            # Return code error (e.g. 404, 501, ...)
            print(err)
            print('\n')
            raise Exception(err)

    time.sleep(5)

    print('\n=======================Add Node Work Flow Test Complete=======================\n')


#####################################################################
def check_ssh(ip, usrname, passwd):
    """
    Title           : Check SSH connection to the idrac server node
    Description     : Check SSH connection to the idrac server node with the given credentials
                      It will fail if :
                      Unable to establish the ssh connection with the given credentials
    Parameters      : 1. ip of the idrac server node
    		          2. username of the idrac server
    		          3. password of the idrac server
    Returns         : Boolean
    """
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=usrname, password=passwd)
        print ("\nSucessfully connected to " + ip + " using password: " + passwd)
        return True
    except:
        print ("could not connect to " + ip + "using password: " + passwd)
        return False
