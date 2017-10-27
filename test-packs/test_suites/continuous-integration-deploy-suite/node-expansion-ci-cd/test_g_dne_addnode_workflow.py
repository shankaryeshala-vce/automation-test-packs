#!/usr/bin/python
# Author:
# Revision: 1.0
# Code Reviewed by:
# Description: This test should only be run once a day.
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
from requests.auth import HTTPBasicAuth
import json
import os
from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect
import atexit
import argparse
import ssl


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




    # ~~~~~~~~ScaleIO Details
    global scaleio_IP
    scaleio_IP = af_support_tools.get_config_file_property(config_file=setup_config_file, heading=setup_config_header,
                                                           property='scaleio_integration_ipaddress')

    global scaleio_username
    scaleio_username = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                 heading=setup_config_header,
                                                                 property='scaleio_username')

    global scaleio_password
    scaleio_password = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                 heading=setup_config_header,
                                                                 property='scaleio_password')



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

    global vcenter_IP
    vcenter_IP = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                           heading=setup_config_header,
                                                           property='vcenter_dne_ipaddress_customer')

    global vcenter_port
    vcenter_port = '443'

    global vcenter_username
    vcenter_username = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                 heading=setup_config_header,
                                                                 property='vcenter_username')
    global vcenter_password
    vcenter_password = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                 heading=setup_config_header,
                                                                 property='vcenter_password_fra')


    global esxiManagementHostname
    esxiManagementHostname = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                       heading=setup_config_header,
                                                                       property='esxi_management_hostname')

    global esxiManagementIpAddress
    esxiManagementIpAddress = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                       heading=setup_config_header,
                                                                       property='esxi_management_ipaddress')

    global domainName
    domainName = '.lab.vce.com'


    global scaleio_svm_ip
    scaleio_svm_ip = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                     heading=setup_config_header,
                                                                     property='scaleio_vm_ip')

    global scaleio_svm_username
    scaleio_svm_username = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                       heading=setup_config_header,
                                                                       property='scaleio_vm_common_username')

    global scaleio_svm_password
    scaleio_svm_password = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                        heading=setup_config_header,
                                                                        property='scaleio_vm_common_password')

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
    Description     :       This is a pre-test check list. It checks:
                                1) which of the 2 allocated IP addres for this node are active currently
                                2) whether this node already has an obm setting for the ipmi-service.
                                   If it does, it deletes the setting
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
        New_Node = Alpha_Node
    else:
        Current_Node = Beta_Node
        New_Node = Beta_Node

    print (New_Node)

    global scaleIoToken
    scaleIoToken = retrieveScaleIoToken()

    global RHDtoken
    RHDtoken = retrieveRHDToken()


@pytest.mark.dne_paqx_parent_mvp_extended
def test_addNode_POST_workflow():
    """
    Title           :       Verify the POST function on /dne/nodes API
    Description     :       Send a POST to /dne/nodes where the body of the request is the typical DNE config
                            details body.
                            It will fail if :
                                The expected json response is not correct
    Parameters      :       none
    Returns         :       None
    Pre-requisites  :       The DNE-PAQX has already run thepreprocess workflow
    """


    #########################
    # Prepare the Request message body with valid details: IP, Gateway, Mask
    #assert update_addNode_params_json(), 'Error: Unable to update the POST message body'

    #########################

    print('\nSend POST /dne/nodes REST API call to provision an unallocated node...\n')
    global addNode_workflow_id  # set this value as global as it will be used in the next test.

    endpoint = '/dne/nodes'
    url_body = protocol + ipaddress + dne_port + endpoint

    filePath = os.environ[
                   'AF_TEST_SUITE_PATH'] + '/continuous-integration-deploy-suite/node-expansion-ci-cd/fixtures/payload_addnode.json'
    with open(filePath) as fixture:
        request_body = json.loads(fixture.read())

    try:
        response = requests.post(url_body, json=request_body, headers=headers)
        assert response.status_code == 200, 'Error: Did not get a 200 on dne/nodes'
        data = response.json()

        addNode_workflow_id = data['workflowId']
        print ('WorkflowID: ', addNode_workflow_id)

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

    except Exception as err:
        # Return code error (e.g. 404, 501, ...)
        print(err, '\n')
        raise Exception(err)


@pytest.mark.dne_paqx_parent_mvp_extended
def test_addnode_GET_workflow_status():
    """
    Title           :       Verify the GET function on /dne/addnode<jobId> API
    Description     :       Send a GET to /dne/addnode/<jobId>. The <jobId> value is the workFlowID obtained in the
                            previous test_addNode_POST_workflow() test.
                            Each expected step in the workflow process will be checked.

                            This test will be updated as new steps are added to the workflow
                            It will fail if :
                                Any of the steps along the wat fail
    Parameters      :       none
    Returns         :       None
    """

    print("\n\nGET /dne/nodes/<jobId> REST API call to get the nodes job status...\n")
    workflow_status = ''
    #addNode_workflow_id =''  #This can be used for test purposes
    json_number = 0

    workflow_step1 = 'Retrieve default ESXi host credential details'
    workflow_step2 = 'Install ESXi'
    workflow_step3 = 'Add host to vCenter cluster'
    workflow_step4 = 'Apply ESXi license'
    workflow_step5 = 'Rename datastore'
    workflow_step6 = 'Exit host maintenance mode'
    workflow_step7 = 'Enable PCI passthrough ESXi host'
    workflow_step8 = 'Install SDC vSphere Installation Bundle (VIB)'
    workflow_step9 = 'Enter host maintenance mode'
    workflow_step10 = 'Reboot Host'
    workflow_step11 = 'Exit host maintenance mode'
    workflow_step12 = 'Configure SDC vSphere Installation Bundle (VIB)'
    workflow_step13 = 'Configure SDC profile for high performance'
    workflow_step14 = 'Add ESXi host to cluster DVSwitch'
    workflow_step15 = 'Clone and deploy ScaleIO VM'
    workflow_step16 = 'Configure PCI passthrough ScaleIO VM'
    workflow_step17 = 'Configure ScaleIO VM network settings'
    workflow_step18 = 'Configure PXE boot'
    workflow_step19 = 'Change ScaleIO VM credentials'
    workflow_step20 = 'Install SDS and Light Installation Agent (LIA) packages'
    workflow_step21 = 'Performance tune the ScaleIO VM'
    workflow_step22 = 'Add host to protection domain'
    workflow_step23 = 'Update System Definition'
    workflow_step24 = 'Notify node discovery to update status'


    endpoint = '/dne/nodes/'
    url_body = protocol + ipaddress + dne_port + endpoint + addNode_workflow_id

    while workflow_status != 'SUCCEEDED':

        try:
            # Get the latest state of the workflow from the API
            data = get_latest_api_response(url_body)

            # If the process has failed immediately then fail the test outright
            #assert data['status'] != 'FAILED', 'ERROR: The addNode workflow overall status = Failed'

            # retrieveEsxiDefaultCredentialDetails
            if data['workflowTasksResponseList'][json_number]['workFlowTaskName'] == workflow_step1:
                check_the_workflow_task(url_body, data, json_number, workflow_step1)
                # Extended check not needed as no change is made
                json_number += 1

            data = get_latest_api_response(url_body)

            # installEsxi
            if data['workflowTasksResponseList'][json_number]['workFlowTaskName'] == workflow_step2:
                check_the_workflow_task(url_body, data, json_number, workflow_step2)
                assert check_installEsxi(), 'Check on ' + workflow_step2 + ' failed'
                json_number += 1

            data = get_latest_api_response(url_body)

            # addHostToVcenter
            if data['workflowTasksResponseList'][json_number]['workFlowTaskName'] == workflow_step3:
                check_the_workflow_task(url_body, data, json_number, workflow_step3)
                assert check_addHostToVcenter(), 'Check on ' + workflow_step3 + ' failed'
                json_number += 1

            data = get_latest_api_response(url_body)

            # applyEsxiLicense
            if data['workflowTasksResponseList'][json_number]['workFlowTaskName'] == workflow_step4:
                check_the_workflow_task(url_body, data, json_number, workflow_step4)
                assert check_applyEsxiLicense(), 'Check on ' + workflow_step4 + ' failed'
                json_number += 1

            data = get_latest_api_response(url_body)

            # datastoreRename
            if data['workflowTasksResponseList'][json_number]['workFlowTaskName'] == workflow_step5:
                check_the_workflow_task(url_body, data, json_number, workflow_step5)
                assert check_datastoreRename(), 'Check on ' + workflow_step5 + ' failed'
                json_number += 1

            data = get_latest_api_response(url_body)

            # exitHostMaintenanceMode1
            if data['workflowTasksResponseList'][json_number]['workFlowTaskName'] == workflow_step6:
                check_the_workflow_task(url_body, data, json_number, workflow_step6)
                assert check_exitHostMaintenanceMode(), 'Check on ' + workflow_step6 + ' failed'
                json_number += 1

            data = get_latest_api_response(url_body)

            # enablePciPassthroughHost
            if data['workflowTasksResponseList'][json_number]['workFlowTaskName'] == workflow_step7:
                check_the_workflow_task(url_body, data, json_number, workflow_step7)
                assert check_enablePciPassthroughHost(), 'Check on ' + workflow_step6 + ' failed'
                json_number += 1

            data = get_latest_api_response(url_body)

            # installScaleIoVib
            if data['workflowTasksResponseList'][json_number]['workFlowTaskName'] == workflow_step8:
                check_the_workflow_task(url_body, data, json_number, workflow_step8)
                # We cannot check this step until the node has been rebooted and is out of maintenance mode
                print('This step will be verified after the host is rebooted and put of maintenance mode')
                json_number += 1

            data = get_latest_api_response(url_body)

            # enterHostMaintenanceMode
            if data['workflowTasksResponseList'][json_number]['workFlowTaskName'] == workflow_step9:
                check_the_workflow_task(url_body, data, json_number, workflow_step9)
                #assert check_enterHostMaintenanceMode(), 'Check on ' + workflow_step9 + ' failed'
                json_number += 1

            data = get_latest_api_response(url_body)

            # rebootHost
            if data['workflowTasksResponseList'][json_number]['workFlowTaskName'] == workflow_step10:
                check_the_workflow_task(url_body, data, json_number, workflow_step10)
                json_number += 1

            data = get_latest_api_response(url_body)

            # exitHostMaintenanceMode2
            if data['workflowTasksResponseList'][json_number]['workFlowTaskName'] == workflow_step11:
                check_the_workflow_task(url_body, data, json_number, workflow_step11)
                assert check_exitHostMaintenanceMode(), 'Check on ' + workflow_step11 + ' failed'
                assert check_installScaleIoVib(), 'Check on ' + workflow_step6 + ' failed'
                json_number += 1

            data = get_latest_api_response(url_body)

            # configureScaleIoVib
            if data['workflowTasksResponseList'][json_number]['workFlowTaskName'] == workflow_step12:
                check_the_workflow_task(url_body, data, json_number, workflow_step12)
                assert check_configureScaleIoVib(), 'Check on ' + workflow_step12 + ' failed'
                json_number += 1

            data = get_latest_api_response(url_body)

            # updateSdcPerformanceProfile
            if data['workflowTasksResponseList'][json_number]['workFlowTaskName'] == workflow_step13:
                check_the_workflow_task(url_body, data, json_number, workflow_step13)
                assert check_updateSdcPerformanceProfile(), 'Check on ' + workflow_step13 + ' failed'
                json_number += 1

            data = get_latest_api_response(url_body)

            # addHostToDvSwitch
            if data['workflowTasksResponseList'][json_number]['workFlowTaskName'] == workflow_step14:
                check_the_workflow_task(url_body, data, json_number, workflow_step14)
                assert check_addHostToDvSwitch(), 'Check on ' + workflow_step14 + ' failed'
                json_number += 1

            data = get_latest_api_response(url_body)

            # deploySVM
            if data['workflowTasksResponseList'][json_number]['workFlowTaskName'] == workflow_step15:
                check_the_workflow_task(url_body, data, json_number, workflow_step15)
                assert check_deploySVM(), 'Check on ' + workflow_step15 + ' failed'
                json_number += 1

            data = get_latest_api_response(url_body)

            # setPciPassthroughSioVm
            if data['workflowTasksResponseList'][json_number]['workFlowTaskName'] == workflow_step16:
                check_the_workflow_task(url_body, data, json_number, workflow_step16)
                assert check_setPciPassthroughSioVm(), 'Check on ' + workflow_step16 + ' failed'
                json_number += 1

            data = get_latest_api_response(url_body)

            # configureVmNetworkSettings
            if data['workflowTasksResponseList'][json_number]['workFlowTaskName'] == workflow_step17:
                check_the_workflow_task(url_body, data, json_number, workflow_step17)
                json_number += 1

            data = get_latest_api_response(url_body)

            # configurePxeBoot
            if data['workflowTasksResponseList'][json_number]['workFlowTaskName'] == workflow_step18:
                check_the_workflow_task(url_body, data, json_number, workflow_step18)
                json_number += 1

            data = get_latest_api_response(url_body)

            # changeSvmCredentials
            if data['workflowTasksResponseList'][json_number]['workFlowTaskName'] == workflow_step19:
                check_the_workflow_task(url_body, data, json_number, workflow_step19)
                assert check_changeSvmCredentials(), 'Check on ' + workflow_step19 + ' failed'
                check_changeSvmCredentials()
                json_number += 1

            data = get_latest_api_response(url_body)

            # installSvmPackages
            if data['workflowTasksResponseList'][json_number]['workFlowTaskName'] == workflow_step20:
                check_the_workflow_task(url_body, data, json_number, workflow_step20)
                json_number += 1

            data = get_latest_api_response(url_body)

            # performanceTuneSvm
            if data['workflowTasksResponseList'][json_number]['workFlowTaskName'] == workflow_step21:
                check_the_workflow_task(url_body, data, json_number, workflow_step21)
                json_number += 1

            data = get_latest_api_response(url_body)

            # addHostToProtectionDomain
            if data['workflowTasksResponseList'][json_number]['workFlowTaskName'] == workflow_step22:
                check_the_workflow_task(url_body, data, json_number, workflow_step22)
                assert check_addHostToProtectionDomain(), 'Check on ' + workflow_step22 + ' failed'
                json_number += 1

            data = get_latest_api_response(url_body)

            # updateSystemDefinition
            if data['workflowTasksResponseList'][json_number]['workFlowTaskName'] == workflow_step23:
                check_the_workflow_task(url_body, data, json_number, workflow_step23)
                json_number += 1

            data = get_latest_api_response(url_body)

            # notifyNodeDiscoveryToUpdateStatus
            if data['workflowTasksResponseList'][json_number]['workFlowTaskName'] == workflow_step24:
                check_the_workflow_task(url_body, data, json_number, workflow_step24)
                json_number += 1

            data = get_latest_api_response(url_body)


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
    # re-run an api status request

    try:
        response = requests.get(url_body)
        assert response.status_code == 200, 'Error: Did not get a 200 response'
    # Error check the response
    except Exception as err:
        # Return code error (e.g. 404, 501, ...)
        print(err)
        print('\n')
        raise Exception(err)

    data = response.text
    data = json.loads(data, encoding='utf-8')
    return data

######################
# This is the main response workflow test

def check_the_workflow_task(url_body, data, json_number, workflow_step):
    """
    Description     :       This function will monitor the status of a particular step in the workflow every ~3 secs.
                            Whilst the status of the step is 'IN_PROGRESS' it will continue monitoring.
                            If the status goes to 'SUCCEEDED', the fucntion is exited.
                            if the status goes to 'FAILED', fail the entire flow (ie. test)
    Parameters      :       url_body - the status request url
                            data - the most recent response to the status request for this flow
                            json_number - the number assigned to this step of the flow  in the json response msg
                            workflow_step - the stepname that we are currently monitoring
    Returns         :       None
    """

    print('\n*******************************************************\n')
    if data['workflowTasksResponseList'][json_number]['workFlowTaskName'] == workflow_step:
        assert data['workflowTasksResponseList'][json_number][
                   'workFlowTaskStatus'] != 'FAILED', 'ERROR: Workflow Failed: "' + workflow_step

        print(workflow_step)
        timeout = 0
        while timeout < 2701:

            # Get the latest state of the workflow from the API
            data = get_latest_api_response(url_body)

            if data['workflowTasksResponseList'][json_number]['workFlowTaskStatus'] == 'IN_PROGRESS':
                time.sleep(1)
                timeout += 1
                # If the task is still in progress wait and then refresh the API data

            if data['workflowTasksResponseList'][json_number]['workFlowTaskStatus'] == 'SUCCEEDED':
                print(workflow_step + ' successful. (Note: Task took', timeout, 'seconds to complete)')
                time.sleep(1)
                break
                # If the task has succeeded, return to the calling test

            if data['workflowTasksResponseList'][json_number]['workFlowTaskStatus'] == 'FAILED':
                print ('(Note: Task took', timeout, 'seconds to fail)\n')
                print (data['workflowTasksResponseList'][json_number]['errors'])
                assert data['workflowTasksResponseList'][json_number][
                           'workFlowTaskStatus'] != 'FAILED', 'Error in Step: ' + workflow_step + ' failed'
                # If the task has failed then fail the entire test.


######## Check Functions
# 2. Install ESXi - log into server and check ESXi version
def check_installEsxi():

    version = 'VMware ESXi 6.0.0'

    sendCommand = 'vmware -vl'

    my_return_status = af_support_tools.send_ssh_command(host=esxiManagementIpAddress, username='root', password=vcenter_password,
                                                         command=sendCommand, return_output=True)

    if version in my_return_status :
        print('ESXi Installation validated: '+ my_return_status)
        return 1
    else :
        return 0


# 3. Add Host to VCenter
def check_addHostToVcenter():

    """" Check that the new ESXi host has been added to the Scaleio VCenter """
    content = getVcenterContent()

    # Search the Vcenter for a host with an IP = the ESXi Manangement IP we used
    # parameters for the search are (specific datacenter, IP Address, False => find hosts only and not vm's)
    addedHost = content.searchIndex.FindByIp(None, esxiManagementIpAddress, False)


    expectedHostName = esxiManagementHostname + domainName

    if addedHost :
        if addedHost.name == expectedHostName :
            print('Host added to vCenter Cluster: '+expectedHostName)
            return 1
    else :
        return 0


# 4. Apply ESXi License
def check_applyEsxiLicense():

    """" Check that the correct license has been applied to the new ESXi host """
    content = getVcenterContent()

    # Search the Vcenter for a host with an IP = the ESXi Manangement IP
    # parameters for the search are (specific datacenter, IP Address, False => find hosts only and not vm's)
    addedHost = content.searchIndex.FindByIp(None, esxiManagementIpAddress, False)

    if addedHost:
        if ("VMware ESX Server" in addedHost.summary.config.product.licenseProductName) \
                and ("6.0" in addedHost.summary.config.product.licenseProductVersion):
            print('ESXi License Configured')
            return 1
    else:
        return 0


# 5. Datastore rename
def check_datastoreRename():
    """" Verify that the datastore associated with the newly added ESXi host has been
        renamed. The new name should be of the form 'DASxx', where 'xx' are the last two digits of the
        the new hostname.
    """
    content = getVcenterContent()

    # Search the Vcenter for a host with an IP = the ESXi Manangement IP
    # parameters for the search are (specific datacenter, IP Address, False => find hosts only and not vm's)
    addedHost = content.searchIndex.FindByIp(None, esxiManagementIpAddress, False)

    dataStoreList = []

    # iterate through the storage volumes associated with the host and record those
    # of type VMFS to the dataStore list
    if addedHost:
        if addedHost.configManager.storageSystem:
            host_file_sys_vol_mount_info = addedHost.configManager.storageSystem.fileSystemVolumeInfo.mountInfo
            for host_mount_info in host_file_sys_vol_mount_info:
                # Extract only VMFS volumes
                if host_mount_info.volume.type == "VMFS":
                    dataStoreList.append(host_mount_info.volume.name)

    expectedDataStoreName = "DAS" + esxiManagementHostname[-2:]
    print('Expected Datastore Name :', expectedDataStoreName)

    # Check that a datastore with the expected name has been mounted
    if expectedDataStoreName in dataStoreList:
        print('Datastore rename validated: '+ expectedDataStoreName)
        return 1
    else:
        return 0


# 6. & 11. Exit Host Maintenance Mode
def check_exitHostMaintenanceMode():
    """" Verify that the newly added host is no longer in maintenance mode
    """
    content = getVcenterContent()

    # Search the Vcenter for a host with an IP = the ESXi Manangement IP
    # parameters for the search are (specific datacenter, IP Address, False => find hosts only and not vm's)
    addedHost = content.searchIndex.FindByIp(None, esxiManagementIpAddress, False)

    if addedHost:
        # check for maintenance status
        if addedHost.runtime.inMaintenanceMode == False :
            print('Node is not in Maintenance Mode')
            return 1
        else:
            return 0
    else:
        return 0


# 7. Enable PCI Passthrough ESXi host
def check_enablePciPassthroughHost():

    time.sleep(20) #Wait for the config to be complete
    content = getVcenterContent()

    # Search the Vcenter for a host with an IP = the ESXi Manangement IP we used
    # parameters for the search are (specific datacenter, IP Address, False => find hosts only and not vm's)
    addedHost = content.searchIndex.FindByIp(None, esxiManagementIpAddress, False)

    setting = addedHost.config.pciPassthruInfo

    for item in setting:
        if item.id == '0000:02:00.0':   # Its always going to be 0000:02:00.0
            if item.passthruEnabled == True:
                print('Host PCI Passthrough configuration: ', item.passthruEnabled)
                return 1
            else:
                return 0


# 8. Install SDC VIB (this will be checked afetr the node is rebooted)
def check_installScaleIoVib():

    expected1 = 'scaleio-sdc-esx6.0'

    sendCommand = 'esxcli software vib list | grep sdc'

    my_return_status = af_support_tools.send_ssh_command(host=esxiManagementIpAddress, username='root', password=vcenter_password,
                                                         command=sendCommand, return_output=True)

    if expected1 in my_return_status:
        print('Install SDC VIB now verified: \n'+ my_return_status)
        return 1
    else:
        return 0


# 9. Enter Host Maintenance Mode
def check_enterHostMaintenanceMode():
    """" Verify that the newly added host is no longer in maintenance mode
    """
    content = getVcenterContent()

    # Search the Vcenter for a host with an IP = the ESXi Manangement IP
    # parameters for the search are (specific datacenter, IP Address, False => find hosts only and not vm's)
    addedHost = content.searchIndex.FindByIp(None, esxiManagementIpAddress, False)

    if addedHost:
        # check for maintenance status
        if addedHost.runtime.inMaintenanceMode == True :
            print('Node is in Maintenance Mode')
            return 1
        else:
            return 0
    else:
        return 0


# 12. Configure SDC VIB
def check_configureScaleIoVib():
    # Get the actual SDC List from Scaleio
    currentSDCList = retrieveScaleIOSdc(scaleIoToken)

    # Verify the new node IP is in the list
    for item in currentSDCList:
        if item['sdcIp'] == esxiManagementIpAddress:
            print('SDC Present '+ esxiManagementIpAddress)
            return 1

    else:
        return 0


# 13. Configure SDC profile for High Performance
def check_updateSdcPerformanceProfile():
    sdcDetails = retrieveScaleIOSdc(scaleIoToken)

    for item in sdcDetails:
        if item['sdcIp'] == esxiManagementIpAddress:
            if item['currProfilePerfParams']['perfProfile']=='HighPerformance':
                print('High Performance Configured')
                return 1
            else:
                return 0


# 14. ESXi Host DVSwitch Configuration
def check_addHostToDvSwitch():

    dvs_0 = 'dvswitch0'
    dvs_1 = 'dvswitch1'
    dvs_2 = 'dvswitch2'

    sendCommand = 'esxcli network vswitch dvs vmware list'

    my_return_status = af_support_tools.send_ssh_command(host=esxiManagementIpAddress, username='root', password=vcenter_password,
                                                         command=sendCommand, return_output=True)

    if dvs_0 in my_return_status and dvs_1 in my_return_status and dvs_2 in my_return_status:
        print('Node configured on all 3 DVSwitches')
        return 1
    else:
        return 0


# 15. Clone and Deploy ScaleIO VM
def check_deploySVM():
    content = getVcenterContent()

    # Search the Vcenter for a host with an IP = the ESXi Manangement IP
    # parameters for the search are (specific datacenter, IP Address, False => find hosts only and not vm's)
    addedHost = content.searchIndex.FindByIp(None, esxiManagementIpAddress, False)

    vmList = addedHost.vm

    for item in vmList:
        if item.name == 'ScaleIO-'+scaleio_svm_ip:
            print('ScaleIO VM: ScaleIO-'+scaleio_svm_ip+' deployed')
            return 1
        else:
            return 0


# 16. Configure PCI passthrough ScaleIO VM
def check_setPciPassthroughSioVm():

    time.sleep(20) #Wait for the config to be complete

    content = getVcenterContent()
    # Search the Vcenter for a host with an IP = the ESXi Manangement IP we used
    # parameters for the search are (specific datacenter, IP Address, False => find hosts only and not vm's)
    addedHost = content.searchIndex.FindByIp(None, esxiManagementIpAddress, False)
    svm = addedHost.vm

    for eachItem in svm:
        if eachItem.name == 'ScaleIO-'+scaleio_svm_ip:
            thingtotest = eachItem.config.extraConfig
            for nextItem in thingtotest:
                if nextItem.key == 'pciPassthru0.present':
                    if nextItem.value == 'true':
                        print('VM PCI Passthrough configuration on ScaleIO VM: '+ nextItem.valueex)
                        return 1
                    else:
                        return 0


# 19. Change ScaleIO VM Credentials
def check_changeSvmCredentials():

    sendCommand = 'hostname'

    my_return_status = af_support_tools.send_ssh_command(host=scaleio_svm_ip, username=scaleio_svm_username, password=scaleio_svm_password,
                                                         command=sendCommand, return_output=True)

    modified_scaleio_svm_ip = scaleio_svm_ip.replace('.', '-')

    my_return_status = my_return_status.strip('\n')

    if my_return_status == 'ScaleIO-'+modified_scaleio_svm_ip:
        print('Verifed new credentials work')
        return 1
    else:
        return 0


# 22. Add Host To Protection Domain
def check_addHostToProtectionDomain():
    # Get the actual Protection Domain List from Scaleio
    currentPdList = retrieveScaleIOProtectionDomain(scaleIoToken)

    # Verify the new node IP is in the list
    for item in currentPdList:
        if item['name'] == esxiManagementHostname + domainName +'-ESX':
            print( esxiManagementHostname + ' Node in Protection Domain')
            return 1

    else:
        return 0


#####################################################################
# RackHD Functions
def retrieveRHDToken():
    """"
    Description :       retrieve the rackHD token allowing api querying
    parameters :        nodeId - the rackhd asssigned id of the node to be Added
    returns :           Text string = "no obm configured" if no OBM is found
                        The OBM Id if an OBM with service = ipmi is found
    """


    url = "http://" + rackHD_IP + ":32080/login"
    header = {'Content-Type': 'application/json'}
    body = '{"username": "' + rackHD_username + '", "password": "' + rackHD_password + '"}'

    try:
        resp = requests.post(url, headers=header, data=body)
    # Error check the response
    except Exception as err:
        # Return code error (e.g. 404, 501, ...)
        print(err)
        print('\n')
        raise Exception(err)


    tokenJson = json.loads(resp.text, encoding='utf-8')
    token = tokenJson["token"]
    return token


def getNodeIdentifier(token, testNodeMAC):
    # Get the node Identifier value

    apipath = '/api/2.0/nodes/'
    url = 'http://' + rackHD_IP + ':32080' + apipath
    headerstring = {"Content-Type": "application/json", "Authorization": "JWT " + RHDtoken}

    try:
        response = requests.get(url, headers=headerstring)
    # Error check the response
    except Exception as err:
        # Return code error (e.g. 404, 501, ...)
        print(err)
        print('\n')
        raise Exception(err)

    data_text = response.text
    data_json = json.loads(response.text, encoding='utf-8')
    assert testNodeMAC in data_text, 'Error: Node not in Rackhd'
    for nodes in data_json:
        if testNodeMAC.rstrip() in nodes['identifiers']:
            testNodeIdentifier = nodes['id']
            return testNodeIdentifier

#####################################################################
# ScaleIO Functions
def retrieveScaleIoToken():
    # grab a token
    url = 'https://' + scaleio_IP +'/api/login'
    header = {'Content-Type': 'application/json'}
    resp = requests.get(url, auth=(scaleio_username, scaleio_password), verify=False)
    scaleIoToken = resp.text
    scaleIoToken = scaleIoToken.strip('"')
    print(scaleIoToken)
    return scaleIoToken


def retrieveScaleIOProtectionDomain(scaleIoToken):
    url = 'https://' + scaleio_IP +'/api/types/ProtectionDomain/instances'
    header = {'Content-Type': 'application/json'}
    resp = requests.get(url, auth=(scaleio_username, scaleIoToken), verify=False)
    respJson = json.loads(resp.text, encoding='utf-8')

    # Get the ProtectionDomainID from the Jsom Msg Body
    filePath = os.environ[
                   'AF_TEST_SUITE_PATH'] + '/continuous-integration-deploy-suite/node-expansion-ci-cd/fixtures/payload_addnode.json'
    with open(filePath) as fixture:
        request_body = json.loads(fixture.read())

        protectionDomainID = request_body['protectionDomainId']

    url = 'https://' + scaleio_IP +'/api/instances/ProtectionDomain::'+protectionDomainID+'/relationships/Sds'
    header = {'Content-Type': 'application/json'}
    resp = requests.get(url, auth=(scaleio_username, scaleIoToken), verify=False)
    respJson = json.loads(resp.text, encoding='utf-8')

    return respJson


def retrieveScaleIOStoragePool(scaleIoToken):
    url = 'https://' + scaleio_IP +'/api/types/StoragePool/instances'
    header = {'Content-Type': 'application/json'}
    resp = requests.get(url, auth=(scaleio_username, scaleIoToken), verify=False)
    respJson = json.loads(resp.text, encoding='utf-8')
    print(respJson)


def retrieveScaleIOSdc(scaleIoToken):
    url = 'https://' + scaleio_IP +'/api/types/Sdc/instances'
    header = {'Content-Type': 'application/json'}
    resp = requests.get(url, auth=(scaleio_username, scaleIoToken), verify=False)
    respJson = json.loads(resp.text, encoding='utf-8')
    return respJson

#####################################################################
# Vcenter Functions
def getVcenterContent():

    try:
        # Disabling urllib3 ssl warnings
        requests.packages.urllib3.disable_warnings()

        # Disabling SSL certificate verification
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        context.verify_mode = ssl.CERT_NONE

        # connect this thing
        si = SmartConnect(
            host=vcenter_IP,
            user=vcenter_username,
            pwd=vcenter_password,
            port=vcenter_port,
            sslContext=context)

        # disconnect this thing
        atexit.register(Disconnect, si)

        # Get the vcenter content
        content = si.RetrieveContent()

        return content

    except Exception as err:
        # Return code error (e.g. 404, 501, ...)
        print(err)
        print('\n')
        raise Exception(err)

