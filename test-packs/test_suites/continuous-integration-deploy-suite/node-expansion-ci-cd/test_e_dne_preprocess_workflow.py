#!/usr/bin/python
# Author:
# Revision: 1.0
# Code Reviewed by:
# Description:
#
# Copyright (c) 2017 Dell Inc. or its subsidiaries.  All Rights Reserved.
# Dell EMC Confidential/Proprietary Information
#

import time
import sys
import af_support_tools
import pytest
import string
import requests
import json
import os


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

    # RackHD VM IP & Creds details
    global setup_config_file
    setup_config_file = 'continuous-integration-deploy-suite/setup_config.ini'

    global setup_config_header
    setup_config_header = 'config_details'

    # ~~~~~~~~RackHD Details
    global rackHD_IP
    rackHD_IP = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                          heading=setup_config_header,
                                                          property='rackhd_dne_ipaddress')

    global rackHD_username
    rackHD_username = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                heading=setup_config_header,
                                                                property='rackhd_username')

    global rackHD_password
    rackHD_password = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                heading=setup_config_header,
                                                                property='rackhd_password')

    global rackHD_cli_username
    rackHD_cli_username = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                    heading=setup_config_header,
                                                                    property='rackhd_cli_username')

    global rackHD_cli_password
    rackHD_cli_password = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                    heading=setup_config_header,
                                                                    property='rackhd_cli_password')

    # ~~~~~~~~Test Node IP & Creds Details
    global testNodeMAC
    testNodeMAC = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                            heading=setup_config_header,
                                                            property='dne_test_node_mac')

    global idrac_ip_address
    idrac_ip_address = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                 heading=setup_config_header,
                                                                 property='idrac_ipaddress')

    global idrac_ip_address_alternative
    idrac_ip_address_alternative = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                             heading=setup_config_header,
                                                                             property='idrac_ipaddress_alternative')

    global idrac_ip_subnetmask
    idrac_ip_subnetmask = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                    heading=setup_config_header,
                                                                    property='idrac_ip_subnetmask')

    global idrac_ip_gateway
    idrac_ip_gateway = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                 heading=setup_config_header,
                                                                 property='idrac_ip_gateway')

    global idrac_username
    idrac_username = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                               heading=setup_config_header,
                                                               property='idrac_username')

    global idrac_common_password
    idrac_common_password = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                      heading=setup_config_header,
                                                                      property='idrac_common_password')

    global idrac_factory_password
    idrac_factory_password = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                       heading=setup_config_header,
                                                                       property='idrac_factory_password')

    ####################

    global Alpha_Node
    Alpha_Node = {'Node_IP': '' + idrac_ip_address + '',
                  'Node_User': '' + idrac_username + '',
                  'Node_Pass': '' + idrac_factory_password + '',
                  'Node_GW': '' + idrac_ip_gateway + '',
                  'Node_Mask': '' + idrac_ip_subnetmask + ''}

    global Beta_Node
    Beta_Node = {'Node_IP': '' + idrac_ip_address_alternative + '',
                 'Node_User': '' + idrac_username + '',
                 'Node_Pass': '' + idrac_factory_password + '',
                 'Node_GW': '' + idrac_ip_gateway + '',
                 'Node_Mask': '' + idrac_ip_subnetmask + ''}


# ######################################################################################
@pytest.mark.dne_paqx_parent_mvp_extended
def test_pre_test_verification():
    """
    Description     :       This is a pre test check list. It checks:
                                1)
                                2)
                                3) Any other checks...

    Parameters      :       none
    Returns         :       None
    """
    ####################
    # There are 2 IP Addresses (alpha and beta) associated with the Test node.
    # Either of these may be the current IP Address of the node
    # Is alpha_node alive ? if so, set it to be the current_node
    global Current_Node
    global New_Node

    response = os.system("ping -c 1 -w2 " + Alpha_Node['Node_IP'] + " > /dev/null 2>&1")
    if response == 0:  # node is alive
        Current_Node = Alpha_Node
        New_Node = Beta_Node
    else:
        Current_Node = Beta_Node
        New_Node = Alpha_Node

    print (New_Node)

    ####################
    # Export the current bios configuration of the node to a temporary file and store the DNE relevant attributes
    # These will be used as comparison later
    response = get_BIOS_settings(Current_Node)
    assert response.status_code == 200, 'Error, pre-test BIOS Configuration export failed '
    time.sleep(60)
    # 'HddSeq' is one of the attributes that will be changed during the 'Configure Boot Device Idrac' step.
    # Here we record it's initial value when exported.
    initial_HddSeq_value = get_exported_bios_setting('HddSeq')
    initial_BiosBootSeq_value = get_exported_bios_setting('BiosBootSeq')
    print('initial_HddSeq_value', initial_HddSeq_value)
    print('initial_BiosBootSeq_value', initial_BiosBootSeq_value)
    ####################


@pytest.mark.dne_paqx_parent_mvp_extended
def test_preporcess_POST_workflow():
    """
    Title           :       Verify the POST function on /dne/preprocess API
    Description     :       Send a POST to /dne/preprocess where the body of the request is the typical DNE config
                            details body.
                            It will fail if :
                                The expected json response is not correct
    Parameters      :       none
    Returns         :       None
    Pre-requisites  :       The DNE-PAQX has already discovered a node and that it is booted into the micro-kernel
    """


    #########################
    # Prepare the Request message body with valid details: IP, Gateway, Mask
    assert update_preprocess_params_json(), 'Error: Unable to update the POST message body'

    #########################

    print('\nSend POST /dne/nodes REST API call to provision an unallocated node...\n')
    global preprocess_workflow_id  # set this value as global as it will be used in the next test.

    endpoint = '/dne/preprocess'
    url_body = protocol + ipaddress + dne_port + endpoint

    filePath = os.environ[
                   'AF_TEST_SUITE_PATH'] + '/continuous-integration-deploy-suite/node-expansion-ci-cd/fixtures/payload_preprocess.json'
    with open(filePath) as fixture:
        request_body = json.loads(fixture.read())

    try:
        response = requests.post(url_body, json=request_body, headers=headers)
        assert response.status_code == 200, 'Error: Did not get a 200 on dne/nodes'
        data = response.json()

        preprocess_workflow_id = data['workflowId']
        print ('WorkflowID: ', preprocess_workflow_id)

        error_list = []

        if data['workflow'] != 'preProcessWorkflow':
            error_list.append(data['workflow'])

        if data['status'] != 'SUBMITTED' and data['status'] != 'IN_PROGRESS':
            error_list.append(data['status'])

        if not data['workflowId']:
            error_list.append(data['workflowId'])

        assert not error_list, 'Error: missing fields from dne/preprocess response'

        print('Valid /dne/preprocess request has been sent')
        time.sleep(2)

    except Exception as err:
        # Return code error (e.g. 404, 501, ...)
        print(err, '\n')
        raise Exception(err)


@pytest.mark.skip(reason="Test not ready")
@pytest.mark.dne_paqx_parent_mvp_extended
def test_preprocess_GET_workflow_status():
    """
    Title           :       Verify the GET function on /dne/preprocess/<jobId> API
    Description     :       Send a GET to /dne/preprocess/<jobId>. The <jobId> value is the workFlowID obtained in the
                            previous test_preporcess_POST_workflow() test.
                            Each expected step in the workflow process will be checked.

                            This test will be updated as new steps are added to the workflow
                            It will fail if :
                                Any of the steps along the wat fail
    Parameters      :       none
    Returns         :       None
    """

    print("\n\nGET /dne/preprocess/<jobId> REST API call to get the nodes job status...\n")

    workflow_status = ''
    while workflow_status != 'SUCCEEDED':

        try:
            endpoint = '/dne/preprocess/'
            url_body = protocol + ipaddress + dne_port + endpoint + preprocess_workflow_id

            # Get the latest state of the workflow from the API
            data = get_latest_api_response(url_body)

            # If the process has failed immediately then fail the test outright
            assert data['status'] != 'FAILED', 'ERROR: The preprocess workflow overall status = Failed'

            workflow_step1 = 'Finding discovered Nodes'
            workflow_step2 = 'List ScaleIO Components'
            workflow_step3 = 'List VCenter Components'
            workflow_step4 = 'Discover ScaleIO'
            workflow_step5 = 'Discover VCenter'
            workflow_step6 = 'Configuring Out of Band Management'
            workflow_step7 = 'Configure Boot Device Idrac'
            workflow_step8 = 'Find vcluster'

            ######################### First task : Finding Discovered Nodes
            if data['workflowTasksResponseList'][0]['workFlowTaskName'] == workflow_step1:
                assert data['workflowTasksResponseList'][0][
                           'workFlowTaskStatus'] != 'FAILED', 'ERROR: Workflow Failed: "' + workflow_step1

                print(workflow_step1)
                timeout = 0
                while timeout < 601:

                    # Get the latest state of the workflow from the API
                    data = get_latest_api_response(url_body)

                    if data['workflowTasksResponseList'][0]['workFlowTaskStatus'] == 'IN_PROGRESS':
                        time.sleep(1)
                        timeout += 1
                        # If the task is still in progress wait and then refresh the API data

                    if data['workflowTasksResponseList'][0]['workFlowTaskStatus'] == 'SUCCEEDED':
                        # Call a function to verify this step actually did something. IE node is in the DISCOVERED state
                        assert check_step1_findNode(data, 0), 'Check on ' + workflow_step1 + ' failed'

                        print(workflow_step1 + ' successful. (Note: Task took', timeout, 'seconds to complete)')
                        print('\n*******************************************************\n')

                        time.sleep(2)
                        break

                    if data['workflowTasksResponseList'][0]['workFlowTaskStatus'] == 'FAILED':
                        print ('(Note: Task took', timeout, 'seconds to fail)\n')
                        assert data['workflowTasksResponseList'][0][
                                   'workFlowTaskStatus'] != 'FAILED', 'Error in Step 1: ' + workflow_step1 + ' failed'
                        # If the task has failed then fail the entire test.

            ######################### Second  task : List ScaleIO Components
            if data['workflowTasksResponseList'][1]['workFlowTaskName'] == workflow_step2:
                assert data['workflowTasksResponseList'][1][
                           'workFlowTaskStatus'] != 'FAILED', 'ERROR: Workflow Failed: "' + workflow_step2

                print(workflow_step2)
                timeout = 0
                while timeout < 610:

                    # Get the latest state from the API
                    data = get_latest_api_response(url_body)

                    if data['workflowTasksResponseList'][1]['workFlowTaskStatus'] == 'IN_PROGRESS':
                        time.sleep(1)
                        timeout += 1
                        # If the task is still in progress wait and then refresh the API data

                    # Check ...
                    if data['workflowTasksResponseList'][1]['workFlowTaskStatus'] == 'SUCCEEDED':
                        # Call a function to verify this step actually did something.
                        # TODO create this function

                        print(workflow_step2 + ' successful. (Note: Task took', timeout, 'seconds to complete)')
                        print('\n*******************************************************\n')

                        time.sleep(2)
                        break
                        # Validate a SUCCEEDED message by ...

                    if data['workflowTasksResponseList'][1]['workFlowTaskStatus'] == 'FAILED':
                        print ('(Note: Task took', timeout, 'seconds to fail)\n')
                        assert data['workflowTasksResponseList'][1][
                                   'workFlowTaskStatus'] != 'FAILED', 'Error in Step 2: ' + workflow_step1 + ' failed'
                        # If the task has failed then fail the entire test.

            ######################### Third  task : List VCenter Components
            if data['workflowTasksResponseList'][2]['workFlowTaskName'] == workflow_step3:
                assert data['workflowTasksResponseList'][2][
                           'workFlowTaskStatus'] != 'FAILED', 'ERROR: Workflow Failed: "' + workflow_step3

                print(workflow_step3)
                timeout = 0
                while timeout < 610:

                    # Get the latest state from the API
                    data = get_latest_api_response(url_body)

                    if data['workflowTasksResponseList'][2]['workFlowTaskStatus'] == 'IN_PROGRESS':
                        time.sleep(1)
                        timeout += 1
                        # If the task is still in progress wait and then refresh the API data

                    # Check ...
                    if data['workflowTasksResponseList'][2]['workFlowTaskStatus'] == 'SUCCEEDED':
                        # Call a function to verify this step actually did something.
                        # TODO create this function

                        print(workflow_step3 + ' successful. (Note: Task took', timeout, 'seconds to complete)')
                        print('\n*******************************************************\n')

                        time.sleep(2)
                        break
                        # Validate a SUCCEEDED message by ...

                    if data['workflowTasksResponseList'][2]['workFlowTaskStatus'] == 'FAILED':
                        print ('(Note: Task took', timeout, 'seconds to fail)\n')
                        assert data['workflowTasksResponseList'][2][
                                   'workFlowTaskStatus'] != 'FAILED', 'Error in Step 3: ' + workflow_step3 + ' failed'
                        # If the task has failed then fail the entire test.

            ######################### Forth task : Discover ScaleIO
            if data['workflowTasksResponseList'][3]['workFlowTaskName'] == workflow_step4:
                assert data['workflowTasksResponseList'][3][
                           'workFlowTaskStatus'] != 'FAILED', 'ERROR: Workflow Failed: "' + workflow_step4

                print(workflow_step4)
                timeout = 0
                while timeout < 610:

                    # Get the latest state from the API
                    data = get_latest_api_response(url_body)

                    if data['workflowTasksResponseList'][3]['workFlowTaskStatus'] == 'IN_PROGRESS':
                        time.sleep(1)
                        timeout += 1
                        # If the task is still in progress wait and then refresh the API data

                    # Check ...
                    if data['workflowTasksResponseList'][3]['workFlowTaskStatus'] == 'SUCCEEDED':
                        # Call a function to verify this step actually did something.
                        # TODO create this function

                        print(workflow_step4 + ' successful. (Note: Task took', timeout, 'seconds to complete)')
                        print('\n*******************************************************\n')

                        time.sleep(2)
                        break
                        # Validate a SUCCEEDED message by ...

                    if data['workflowTasksResponseList'][3]['workFlowTaskStatus'] == 'FAILED':
                        print ('(Note: Task took', timeout, 'seconds to fail)\n')
                        assert data['workflowTasksResponseList'][3][
                                   'workFlowTaskStatus'] != 'FAILED', 'Error in Step : ' + workflow_step4 + ' failed'
                        # If the task has failed then fail the entire test.

            ######################### Fifth task : Discover VCenter
            if data['workflowTasksResponseList'][4]['workFlowTaskName'] == workflow_step5:
                assert data['workflowTasksResponseList'][4][
                           'workFlowTaskStatus'] != 'FAILED', 'ERROR: Workflow Failed: "' + workflow_step5

                print(workflow_step5)
                timeout = 0
                while timeout < 610:

                    # Get the latest state from the API
                    data = get_latest_api_response(url_body)

                    if data['workflowTasksResponseList'][4]['workFlowTaskStatus'] == 'IN_PROGRESS':
                        time.sleep(1)
                        timeout += 1
                        # If the task is still in progress wait and then refresh the API data

                    # Check ...
                    if data['workflowTasksResponseList'][4]['workFlowTaskStatus'] == 'SUCCEEDED':
                        # Call a function to verify this step actually did something.
                        # TODO create this function

                        print(workflow_step5 + ' successful. (Note: Task took', timeout, 'seconds to complete)')
                        print('\n*******************************************************\n')

                        time.sleep(2)
                        break
                        # Validate a SUCCEEDED message by ...

                    if data['workflowTasksResponseList'][4]['workFlowTaskStatus'] == 'FAILED':
                        print ('(Note: Task took', timeout, 'seconds to fail)\n')
                        assert data['workflowTasksResponseList'][4][
                                   'workFlowTaskStatus'] != 'FAILED', 'Error in Step 5: ' + workflow_step5 + ' failed'
                        # If the task has failed then fail the entire test.

            ######################### Sixth task : Configuring Out of Band Management
            if data['workflowTasksResponseList'][5]['workFlowTaskName'] == workflow_step6:
                assert data['workflowTasksResponseList'][5][
                           'workFlowTaskStatus'] != 'FAILED', 'ERROR: Workflow Failed: "' + workflow_step6

                print(workflow_step6)
                timeout = 0
                while timeout < 610:

                    # Get the latest state from the API
                    data = get_latest_api_response(url_body)

                    if data['workflowTasksResponseList'][5]['workFlowTaskStatus'] == 'IN_PROGRESS':
                        time.sleep(1)
                        timeout += 1
                        # If the task is still in progress wait and then refresh the API data

                    # Check ...
                    if data['workflowTasksResponseList'][5]['workFlowTaskStatus'] == 'SUCCEEDED':
                        # Call a function to verify this step actually did something. IE Verify IP change
                        assert check_step6_oobmIP(New_Node), 'Check on ' + workflow_step6 + ' failed'

                        print(workflow_step6 + ' successful. (Note: Task took', timeout, 'seconds to complete)')
                        print('\n*******************************************************\n')

                        time.sleep(2)
                        break
                        # Validate a SUCCEEDED message by ...

                    if data['workflowTasksResponseList'][5]['workFlowTaskStatus'] == 'FAILED':
                        print ('(Note: Task took', timeout, 'seconds to fail)\n')
                        assert data['workflowTasksResponseList'][5][
                                   'workFlowTaskStatus'] != 'FAILED', 'Error in Step 6: ' + workflow_step6 + ' failed'
                        # If the task has failed then fail the entire test.

            ######################### Seventh task : Configure Boot Device Idrac
            if data['workflowTasksResponseList'][6]['workFlowTaskName'] == workflow_step7:
                assert data['workflowTasksResponseList'][6][
                           'workFlowTaskStatus'] != 'FAILED', 'ERROR: Workflow Failed: "' + workflow_step7

                print(workflow_step7)
                timeout = 0
                while timeout < 610:

                    # Get the latest state from the API
                    data = get_latest_api_response(url_body)

                    if data['workflowTasksResponseList'][6]['workFlowTaskStatus'] == 'IN_PROGRESS':
                        time.sleep(1)
                        timeout += 1
                        # If the task is still in progress wait and then refresh the API data

                    # Check ...
                    if data['workflowTasksResponseList'][6]['workFlowTaskStatus'] == 'SUCCEEDED':
                        # Call a function to verify this step actually did something. IE Verify bios change
                        assert check_step7_biosChange(New_Node), 'Check on ' + workflow_step7 + ' failed'

                        print(workflow_step7 + ' successful. (Note: Task took', timeout, 'seconds to complete)')
                        print('\n*******************************************************\n')

                        time.sleep(2)
                        break
                        # Validate a SUCCEEDED message by ...

                    if data['workflowTasksResponseList'][6]['workFlowTaskStatus'] == 'FAILED':
                        print ('(Note: Task took', timeout, 'seconds to fail)\n')
                        assert data['workflowTasksResponseList'][6][
                                   'workFlowTaskStatus'] != 'FAILED', 'Error in Step 7: ' + workflow_step7 + ' failed'
                        # If the task has failed then fail the entire test.

            ######################### Eight task : Discover VCenter
            if data['workflowTasksResponseList'][7]['workFlowTaskName'] == workflow_step8:
                assert data['workflowTasksResponseList'][7][
                           'workFlowTaskStatus'] != 'FAILED', 'ERROR: Workflow Failed: "' + workflow_step8

                print(workflow_step8)
                timeout = 0
                while timeout < 610:

                    # Get the latest state from the API
                    data = get_latest_api_response(url_body)

                    if data['workflowTasksResponseList'][7]['workFlowTaskStatus'] == 'IN_PROGRESS':
                        time.sleep(1)
                        timeout += 1
                        # If the task is still in progress wait and then refresh the API data

                    # Check ...
                    if data['workflowTasksResponseList'][7]['workFlowTaskStatus'] == 'SUCCEEDED':
                        # Call a function to verify this step actually did something.
                        # TODO create this function

                        print(workflow_step8 + ' successful. (Note: Task took', timeout, 'seconds to complete)')
                        print('\n*******************************************************\n')

                        time.sleep(2)
                        break
                        # Validate a SUCCEEDED message by ...

                    if data['workflowTasksResponseList'][7]['workFlowTaskStatus'] == 'FAILED':
                        print ('(Note: Task took', timeout, 'seconds to fail)\n')
                        assert data['workflowTasksResponseList'][7][
                                   'workFlowTaskStatus'] != 'FAILED', 'Error in Step 8: ' + workflow_step8 + ' failed'
                        # If the task has failed then fail the entire test.

            ######################### Done

            workflow_status = data['status']

            print('Valid /dne/nodes/{jobId} status returned')

        # Error check the response
        except Exception as err:
            # Return code error (e.g. 404, 501, ...)
            print(err)
            print('\n')
            raise Exception(err)

    time.sleep(5)


########################################################################################

# Run the api query
def get_latest_api_response(url_body):
    response = requests.get(url_body)
    assert response.status_code == 200, 'Error: Did not get a 200 response'
    data = response.text
    data = json.loads(data, encoding='utf-8')
    return data


# Update the json that will be used in the POST /dne?preprocess command with valid values
def update_preprocess_params_json():
    """
    Description:    This method will update the json file with the symphonyUuid & nodeId values. Others wil be added as needed
    Parameters:     None
    Returns:        0 or 1 (Boolean)
    """

    filePath = os.environ[
                   'AF_TEST_SUITE_PATH'] + '/continuous-integration-deploy-suite/node-expansion-ci-cd/fixtures/payload_preprocess.json'

    if (os.path.isfile(filePath) == 0):
        return 0

    with open(filePath) as json_file:
        data = json.load(json_file)
    data['idracIpAddress'] = New_Node['Node_IP']
    data['idracSubnetMask'] = New_Node['Node_Mask']
    data['idracGatewayIpAddress'] = New_Node['Node_GW']

    with open(filePath, 'w') as outfile:
        json.dump(data, outfile)

    print (data)

    return 1


######## Functions to check the steps of the workflow actually did something ###########

# Check that a node was discovered
def check_step1_findNode(data, json_num):
    node_status = data['workflowTasksResponseList'][json_num]['results']['nodeStatus']
    # assert node_status == 'DISCOVERED', 'Error, node not discovered'

    if node_status == 'DISCOVERED':
        print('Node is available in a DISCOVERED State')
        return 1
    else:
        return 0


# Verify the IP address has been changed
def check_step6_oobmIP(New_Node):
    # Contact the new IP address and check the network settings
    returned_settings = get_network_settings_from_iDRAC(New_Node)

    # verify that out new settings were correctly returned from the iDRAC
    error_list = []
    if returned_settings['IP Address'] != New_Node['Node_IP']:
        error_list.append('Error : The new IP has not been set correctly')
    if returned_settings['Subnet Mask'] != New_Node['Node_Mask']:
        error_list.append('Error : The new Subnet Mask has not been set correctly')
    if returned_settings['Default Gateway IP'] != New_Node['Node_GW']:
        error_list.append('Error : The new Gateway IP has not been set correctly')

    if error_list == []:
        print('IP crednetials have been correctly configured')
        return 1
    else:
        return 0


# Verify the bios setting has changed.
def check_step7_biosChange(New_Node):
    # export the bios configuration again and check the DNE relevant attributes have been updated
    response = get_BIOS_settings(New_Node)
    assert response.status_code == 200, 'Error, '
    updated_HddSeq_value = get_exported_bios_setting('HddSeq')
    updated_BiosBootSeq_value = get_exported_bios_setting('BiosBootSeq')

    error_list = []

    if updated_HddSeq_value != "Disk.SATAEmbedded.D-1,RAID.Integrated.1-1":
        error_list.append('Error : The new HddSeq value is not correct')

    if updated_BiosBootSeq_value != "HardDisk.List.1-1,NIC.Integrated.1-1-1":
        error_list.append('Error : The new BiosBootSeq value is not correct')

    if error_list == []:
        return 1
    else:
        return 0


######## Functions to get Node Bios Details ##########

def get_BIOS_settings(Node):
    """ Query the RHD Swagger interface """

    url = 'http://' + rackHD_IP + ':46018/api/1.0/server/configuration/export'

    header = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    body = '{"componentNames": [""], \
                "fileName": "tempExport.xml", \
                "serverIP": "' + Node['Node_IP'] + '", \
                "serverPassword": "' + Node['Node_Pass'] + '", \
                "serverUsername": "' + Node['Node_User'] + '", \
                "shareAddress": "' + rackHD_IP + '", \
                "shareName": "/opt/dell/public", \
                "shareType": 0, \
                "shutdownType": 0}'

    try:
        response = requests.post(url, headers=header, data=body)
        response.raise_for_status()
        return response

    except Exception as err:
        # Return code error (e.g. 404, 501, ...)
        print(err, '\n')
        raise Exception(err)


def get_exported_bios_setting(attribute):
    # check if the ipmitool is installed. this tool is used to communicate with the iDRAC
    grepCommand = 'grep "Name="\"' + attribute + '\"" /opt/dell/public/tempExport.xml \
                         | cut -f 2 -d ">" | cut -f 1 -d "<" '

    returnedAttributeValue = af_support_tools.send_ssh_command(
        host=rackHD_IP,
        username=rackHD_cli_username,
        password=rackHD_cli_password,
        command=grepCommand,
        return_output=True)

    return returnedAttributeValue


######## Supporting Functions ##########

def get_network_settings_from_iDRAC(node):
    """ Access the iDRAC of a node via the ipmitool and return the network settings currently configured.
        Paramters : 'node' is a dictionary containing network settings for a node
        eg. node = {'Node_IP':'10.1.10.1',
                'Node_User':'root',
                'Node_Pass':'password',
                'Node_GW':'10.1.10.225',
                'Node_Mask':'255.255.255.224'}

        Returned : A dictionary with the following key/value pairs as retrieved from the iDRAC :
        'IP Address' , 'Subnet Mask' and 'Default Gateway IP'     """

    # The 'ipmitool' is used to query the iDRAC. It may need installing on the test VM.
    check_for_and_install_ipmitool()

    # create the command to query the iDRAC network settings
    commandGetSettings = " ipmitool -I lanplus -H " + node['Node_IP'] + " -U " + node['Node_User'] + " -P " + node[
        'Node_Pass'] + " lan print 1"

    # ssh onto the test VM and run the ipmitool qury from there
    network_settings = af_support_tools.send_ssh_command(
        host=ipaddress,
        username=cli_username,
        password=cli_password,
        command=commandGetSettings,
        return_output=True)

    # create a dictionary containing just the settings we are interested in
    dictAttributes = {}
    # the returned data is one big long string. Split it before processing
    tempArray = network_settings.splitlines(True)

    # extract the network settings we are interested in
    for line in tempArray:
        if 'IP Address' in line or 'Subnet Mask' in line or 'Default Gateway IP' in line:
            (key, val) = line.split(':')
            dictAttributes[(key.strip())] = val.strip()

    return dictAttributes


def check_for_and_install_ipmitool():
    # check if the ipmitool is installed. this tool is used to communicate with the iDRAC
    commandCheckForIPMITOOL = "yum list installed | grep ipmitool"

    ipmitool_Installed = af_support_tools.send_ssh_command(
        host=ipaddress,
        username=cli_username,
        password=cli_password,
        command=commandCheckForIPMITOOL,
        return_output=True)

    # install the ipmitool if it is not already installed
    if not ipmitool_Installed:
        commandInstallIPMITOOL = "yum -y install ipmitool"
        ipmitool_Installed = af_support_tools.send_ssh_command(
            host=ipaddress,
            username=cli_username,
            password=cli_password,
            command=commandInstallIPMITOOL,
            return_output=True)


def rebootIDRAC(Node):
    commandReboot = " ipmitool -I lanplus -H " + Node['Node_IP'] + " -U " + Node['Node_User'] + " -P " + Node[
        'Node_Pass'] + " chassis power reset"
    network_settings = af_support_tools.send_ssh_command(
        host=rackHD_IP,
        username=rackHD_cli_username,
        password=rackHD_cli_password,
        command=commandReboot,
        return_output=True)


#####################################################################
# These are Negative Tests tests.
#####################################################################
@pytest.mark.parametrize('endpoint', [('/dne/preprocess/')])
@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_GETjobid_using_invalid_jobid(endpoint):
    """
    Title           :       Verify the dne REST API handles invalid job-id's correctly
    Description     :       Send a GET to /dne/nodes/{job-Id} with an invalid job-id.
                            Send a GET to /dne/preprocess/{job-Id} with an invalid job-id.
                            It will fail if :
                                The returned error exposes  java NPE details
    Parameters      :       none
    Returns         :       None
    """

    print("\n======================= invalid jobId  Test Start =======================\n")

    # Step 1: Invoke a REST API call with invalid jobId .
    print("GET /dne/{nodes/preprocess}/{job-Id} REST API call with invalid jobId\n")

    filePath = os.environ[
                   'AF_TEST_SUITE_PATH'] + '/continuous-integration-deploy-suite/node-expansion-ci-cd/fixtures/payload_addnode.json'
    with open(filePath) as fixture:
        request_body = json.loads(fixture.read())

    try:
        invalid_job_id = "ab55bf0c-73b0-4a16-acc6-1ff36b6cf655"
        url_body = protocol + ipaddress + dne_port + endpoint + invalid_job_id
        print(url_body)

        response = requests.get(url_body, json=request_body, headers=headers)
        # verify the status_code
        assert response.status_code == 404 or response.status_code == 400, \
            'Error: Did not get a 400-series error on ' + endpoint + '{invalid-job-Id}'
        data = response.json()
        print(data)

        error_list = []

        if not data['error']:
            error_list.append(data['error'])

        if 'exception' in data:
            if 'java' in data['exception']:
                error_list.append('\"java\" text should not be displayed')

        if 'message' not in data:
            error_list.append(data['message'])
        else:
            if 'java' in data['message']:
                error_list.append('\"java\" text should not be displayed')

        if not data['path']:
            error_list.append(data['path'])
        else:
            if not invalid_job_id in data['path']:
                error_list.append('the invalid job id should be listed in the path field')

        assert not error_list, 'Error: Issue found with ' + endpoint + '{invalid-jobId} Response'


    # Error check the response
    except Exception as err:
        # Return code error (e.g. 404, 501, ...)
        print(err)
        print('\n')
        raise Exception(err)

    print('\n======================= invalid jobId Test End=======================\n')


@pytest.mark.parametrize('endpoint', [('/dne/preprocess/')])
# @pytest.mark.dne_paqx_parent_mvp
# @pytest.mark.dne_paqx_parent_mvp_extended
def test_GETjobid_using_valid_but_incorrect_jobid(endpoint):
    """
    Title           :       Verify the dne REST API handles valid, but incorrect, job-id's correctly
    Description     :       Send a GET to /dne/nodes/{job-Id} with a preprocess job-id.
                            Send a GET to /dne/preprocess/{job-Id} with a nodes job-id.
                            It will fail if :
                                The returned error exposes  java NPE details
    Parameters      :       none
    Returns         :       None
    """

    print("\n======================= valid jobId but incorrect Test Start =======================\n")

    # Step 1: Invoke a REST API call with invalid jobId .
    print("GET /dne/{nodes/preprocess}/{job-Id} REST API call with an incorrect jobId\n")

    filePath = os.environ[
                   'AF_TEST_SUITE_PATH'] + '/continuous-integration-deploy-suite/node-expansion-ci-cd/fixtures/payload_addnode.json'
    with open(filePath) as fixture:
        request_body = json.loads(fixture.read())

    try:
        jobId = '14cf9e3f-b651-4e14-8f35-e0c012cb0e9c'

        url_body = protocol + ipaddress + dne_port + endpoint + jobId
        print(url_body)

        response = requests.get(url_body, json=request_body, headers=headers)
        # verify the status_code
        assert response.status_code == 400 or response.status_code == 404, \
            'Error: Did not get a 400-series error ' + endpoint + '{incorrect-job-Id}'
        data = response.json()
        print(data)

        error_list = []

        if not data['error']:
            error_list.append(data['error'])

        if 'exception' in data:
            if 'java' in data['exception']:
                error_list.append('\"java\" text should not be displayed')

        if 'message' not in data:
            error_list.append(data['message'])
        else:
            if 'java' in data['message']:
                error_list.append('\"java\" text should not be displayed')

        if not data['path']:
            error_list.append(data['path'])
        else:
            if not jobId in data['path']:
                error_list.append('the incorrect job id should be listed in the path field')

        assert not error_list, 'Error: Issue found with ' + endpoint + '{incorrect-jobId} Response'


    # Error check the response
    except Exception as err:
        # Return code error (e.g. 404, 501, ...)
        print(err)
        print('\n')
        raise Exception(err)

    print('\n======================= valid jobId but incorrect Test End=======================\n')


@pytest.mark.parametrize('endpoint', [('/dne/preprocess/step/')])
@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_POSTstepname_using_invalid_stepName(endpoint):
    """
    Title           :       Verify the dne REST API handles invalid step-names correctly
    Description     :       Send a POST to /dne/nodes/step/{stepName} with an invalid stepName
                            Send a POST to /dne/preprocess/step/{stepName} with an invalid stepName
                            It will fail if :
                                The returned error exposes  java NPE details
    Parameters      :       none
    Returns         :       None
    """

    print("\n======================= invalid stepname Test Start =======================\n")

    # Step 1: Invoke /dne/{preprocess,step}/{stepName} REST API call with invalid step name .
    print("POST /dne/../step/{step-id}} REST API call with invalid step name\n")

    filePath = os.environ[
                   'AF_TEST_SUITE_PATH'] + '/continuous-integration-deploy-suite/node-expansion-ci-cd/fixtures/payload_addnode.json'
    with open(filePath) as fixture:
        request_body = json.loads(fixture.read())

    try:
        invalid_step_name = "invalidStep"
        url_body = protocol + ipaddress + dne_port + endpoint + invalid_step_name
        print(url_body)

        response = requests.post(url_body, json=request_body, headers=headers)
        # verify the status_code
        assert response.status_code == 404 or response.status_code == 400, \
            'Error: Did not get a 400-series on ' + endpoint + '{invalid_step_name}'
        data = response.json()
        print(data)

        error_list = []

        if not data['error']:
            error_list.append(data['error'])

        if 'exception' in data:
            if 'java' in data['exception']:
                error_list.append('\"java\" text should not be displayed')

        if 'message' not in data:
            error_list.append(data['message'])
        else:
            if 'java' in data['message']:
                error_list.append('\"java\" text should not be displayed')

        if not data['path']:
            error_list.append(data['path'])
        else:
            if not invalid_step_name in data['path']:
                error_list.append('the invalid step name should be listed in the path field')

        assert not error_list, 'Error: Issue found with  ' + endpoint + '{invalid-step-name} Response'


    # Error check the response
    except Exception as err:
        # Return code error (e.g. 404, 501, ...)
        print(err)
        print('\n')
        raise Exception(err)

    print('\n======================= invalid stepname Test End=======================\n')

    #####################################################################
