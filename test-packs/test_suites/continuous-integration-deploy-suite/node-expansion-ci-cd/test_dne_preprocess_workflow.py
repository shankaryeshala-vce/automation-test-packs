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


#####################################################################
# These are the main tests.
#####################################################################
@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_preprocess_request_workflows():
    """
    Title           :       Verify the POST function on /dne/preprocess API
    Description     :       Send a POST to /dne/preprocess where the body of the request is the typical DNE config
                            details body.
                            It will fail if :
                                The expected json response is not correct
    Parameters      :       none
    Returns         :       None
    """

    print("\n=======================Preprocess Work Flow Test Start=======================\n")

    # Step 1: Invoke /dne/preprocess REST API call to gather the info that will be needed for add node.
    print("POST /dne/preprocess REST API call to gather the info that will be needed for add node...\n")

    global preprocess_workflow_id  # set this value as global as it will be used in the next test.

    filePath = os.environ[
                   'AF_TEST_SUITE_PATH'] + '/continuous-integration-deploy-suite/node-expansion-ci-cd/fixtures/payload_addnode.json'
    with open(filePath) as fixture:
        request_body = json.loads(fixture.read())

    try:
        endpoint = '/dne/preprocess'
        url_body = protocol + ipaddress + dne_port + endpoint
        response = requests.post(url_body, json=request_body, headers=headers)
        # verify the status_code
        assert response.status_code == 200, 'Error: Did not get a 200 on dne/preprocess'
        data = response.json()

        preprocess_workflow_id = data['workflowId']

        error_list = []

        if data['workflow'] != 'preProcessWorkflow':
            error_list.append('workflow')

        if data['status'] != 'SUBMITTED':
            error_list.append('status')

        if not data['workflowId']:
            error_list.append('workflowID')

        assert not error_list, 'Error: missing fields from den/preprocess response'

        for link in data['links']:
            if link['rel'] is 'self':
                assert link[
                           'href'] == "/nodes/" + preprocess_workflow_id + "/startPreProcessWorkflow", 'Error: Invalid href in dne/preprocess response'

        print('Valid /dne/preprocess request sent')
        time.sleep(2)

    # Error check the response
    except Exception as err:
        # Return code error (e.g. 404, 501, ...)
        print(err)
        print('\n')
        raise Exception(err)


@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_preprocess_status_workflow():
    """
    Title           :       Verify the GET function on /dne/preprocess/<jobId> API
    Description     :       Send a GET to /dne/preprocess/<jobId>. The <jobId> value is the workFlowID obtained in the
                            previous test_preprocess_request_workflows() test.
                            It will fail if :
                                The expected json response is not correct
    Parameters      :       none
    Returns         :       None
    """
    # Step 2: Invoke /dne/preprocess/{jobId} REST API call to get the status
    print("\n\nGET /dne/preprocess/<jobId> REST API call to get the preprocess job status...\n")

    try:
        endpoint = '/dne/preprocess/'
        url_body = protocol + ipaddress + dne_port + endpoint + preprocess_workflow_id
        response = requests.get(url_body)
        # verify the status_code
        assert response.status_code == 200, 'Error: 200 not returned from dne\preprocess'
        data = response.json()

        error_list = []

        if data['workflowId'] != preprocess_workflow_id:
            error_list.append(data['workflowId'])

        if not data['workflow']:
            error_list.append(data['workflow'])

        if not data['status']:
            error_list.append(data['status'])

        if not data['workflowTasksResponseList']:
            error_list.append(data['workflowTasksResponseList'])

        if not data['links']:
            error_list.append(data['links'])

        assert not error_list, 'Error: Not all tasks returned in /dne/preprocess'
        # Note: we are not asserting on the contents of "workflowTasksResponseList": [] as this is changeable.

        print('Valid /dne/preprocess/{jobId} status returned')

    # Error check the response
    except Exception as err:
        # Return code error (e.g. 404, 501, ...)
        print(err)
        print('\n')
        raise Exception(err)


@pytest.mark.parametrize('stepName', [('findAvailableNodes'), ('configIdrac'), ('findVCluster')])
@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_preprocess_step_workflow(stepName):
    """
    Title           :       Verify the POST function on /dne/preprocess/step/{stepName} API
    Description     :       Send a POST to /dne/preprocess/step/{stepName}. The 3 {stepName} values are "findAvailableNodes"
                            "configIdrac" & "findVCluster"
                            It will fail if :
                                The expected json response is not correct
    Parameters      :       none
    Returns         :       None
    """

    # Step 3: Invoke /dne/preprocess/step/{stepName} REST API call to get the status
    print("\n\nPOST /dne/preprocess/step/{stepName} REST API call to get the step status...\n")

    filePath = os.environ[
                   'AF_TEST_SUITE_PATH'] + '/continuous-integration-deploy-suite/node-expansion-ci-cd/fixtures/payload_addnode.json'
    with open(filePath) as fixture:
        request_body = json.loads(fixture.read())

    try:
        endpoint = '/dne/preprocess/step/'
        url_body = protocol + ipaddress + dne_port + endpoint + stepName

        print (url_body)
        response = requests.post(url_body, json=request_body, headers=headers)
        # verify the status_code
        assert response.status_code == 200, 'Error: 200 not returned from dne\preprocess'
        data = response.json()

        error_list = []

        if not data['correlationId']:
            error_list.append(data['correlationId'])

        if not data['workflowId']:
            error_list.append(data['workflowId'])

        if not data['workflow']:
            error_list.append(data['workflow'])

        if not data['status']:
            error_list.append(data['status'])

        if not data['links']:
            error_list.append(data['links'])

        assert not error_list, 'Error: Not all tasks returned in /dne/preprocess'
        # Note: we are not asserting on the contents of "workflowTasksResponseList": [] as this is changeable.

        print('Valid /dne/preprocess/step' + stepName + ' status returned')

    # Error check the response
    except Exception as err:
        # Return code error (e.g. 404, 501, ...)
        print(err)
        print('\n')
        raise Exception(err)
