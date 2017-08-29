#!/usr/bin/python
# Author:
# Revision: 2.0
# Code Reviewed by:
# Description:Testing the Node Expansion Teams, VCenter Cluster Discovery.
#
# Copyright (c) 2017 Dell Inc. or its subsidiaries.  All Rights Reserved.
# Dell EMC Confidential/Proprietary Information


from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect
import atexit
import argparse
import getpass
import ssl
import requests
import af_support_tools
import json
import time
import pytest
import os
import uuid


#######################################################################################################################

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

    # Update setup_config.ini file at runtime
    my_data_file = os.environ.get('AF_RESOURCES_PATH') + '/continuous-integration-deploy-suite/setup_config.properties'
    af_support_tools.set_config_file_property_by_data_file(my_data_file)

    # vCenter VM IP & Creds details
    global setup_config_file
    setup_config_file = 'continuous-integration-deploy-suite/setup_config.ini'

    global setup_config_header
    setup_config_header = 'config_details'

    global vcenter_IP
    vcenter_IP = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                           heading=setup_config_header,
                                                           property='vcenter_ipaddress')
    global vcenter_username
    vcenter_username = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                 heading=setup_config_header,
                                                                 property='vcenter_username')
    global vcenter_password
    vcenter_password = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                 heading=setup_config_header,
                                                                 property='vcenter_password')
    global vcenter_port
    vcenter_port = '443'

    global protocol
    protocol = 'http://'

    global dne_port
    dne_port = ':8071'


#######################################################################################################################

#@pytest.mark.dne_paqx_parent_mvp
#@pytest.mark.dne_paqx_parent_mvp_extended
def test_vcenter_discover_cluters():
    print('\nRunning test on Symphony system:', ipaddress, 'and Test vCenter:', vcenter_IP, '\n')

    # Prerequisite check - ensure the 'vcenter-discover-cluster' is present, if its not call the function to manually
    # send in a message to register it
    readyToTest = False

    while readyToTest == False:
        if vcenter_adapter_ListCapabilities() == True:
            readyToTest = True


    cleanup('test.vcenter.response')
    cleanup('test.endpoint.registration.event')
    cleanup('test.controlplane.vcenter.response')

    bindQueues('exchange.cpsd.controlplane.vcenter.response', 'test.vcenter.response')
    bindQueues('exchange.dell.cpsd.endpoint.registration.event', 'test.endpoint.registration.event')
    bindQueues('exchange.cpsd.controlplane.vcenter.response', 'test.controlplane.vcenter.response')

    ###################################################

    print('\nStep 1: Data direct from Test vCenter to compare against')

    # # Get a list of the actual clusters direct from the test vCenter Server
    actualvCenterClusterList = getRealVcenterInfo()
    numOfClustersInList = len(actualvCenterClusterList)  # Get the number of clusters in the list

    print('Total Number of Clusters:', numOfClustersInList)
    print(actualvCenterClusterList, '\n')

    ##################################################

    # Purge the queue to ensure the test response query is empty
    af_support_tools.rmq_purge_queue(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                     rmq_username=cpsd.props.rmq_username,
                                     rmq_password=cpsd.props.rmq_password,ssl_enabled=cpsd.props.rmq_ssl_enabled,
                                     queue='test.vcenter.response')

    # Get the data in the dne/clusters API and compare it to the actual data
    print('\nStep 2: Send an API GET to /dne/clusters this triggers the VCenter Discover Cluster Message')
    apiResponseData = listvCenterClustersAPI()
    apiResponseData_json = json.loads(apiResponseData, encoding='utf-8')
    print (apiResponseData)
    assert apiResponseData_json == actualvCenterClusterList
    print('Symphony API Response Data matches Source Data\n')

    ###################################################
    # Consume the published vcenter.cluster.discover.response message and compare this also to the actual data
    assert waitForMsg('test.vcenter.response'), 'ERROR: No responce message reveived listing clusters'

    return_message = af_support_tools.rmq_consume_message(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                                          rmq_username=cpsd.props.rmq_username,
                                                          rmq_password=cpsd.props.rmq_password,ssl_enabled=cpsd.props.rmq_ssl_enabled,
                                                          queue='test.vcenter.response', remove_message=False)

    return_json = json.loads(return_message, encoding='utf-8')
    clusterInfo = return_json['discoverClusterResponseInfo']['clusters']

    print('\nData from Symphony RMQ Message:')
    countNumOfClusters = 0

    for cluster in clusterInfo:
        assert cluster in actualvCenterClusterList, 'Error: unexpected cluster'  # Check that each cluster is in the source list
        print(cluster, 'Verified valid at source')
        countNumOfClusters += 1

    assert countNumOfClusters == numOfClustersInList, 'Not all clusters returned'  # Check that Symphony has the same number of clusters that source has

    print('\nNumber of Clusters at source: ', numOfClustersInList,
          '\nNumber of Clusters returned by Symphony: ', countNumOfClusters)

    print('\nSymphony RMQ Data matches Source data')

    cleanup('test.vcenter.response')
    cleanup('test.endpoint.registration.event')
    cleanup('test.controlplane.vcenter.response')


################################################
# Test case to apply ESS rules to all discovered clusters
#@pytest.mark.dne_paqx_parent_mvp
#@pytest.mark.dne_paqx_parent_mvp_extended
def test_ess_vcenter_rules():
    actualvCenterClusterList = getRealVcenterInfo()
    numOfClustersInList = len(actualvCenterClusterList)

    return_message = readVcenterResponse()

    print("\nValidate vcenter cluster with ESS rules:")
    validated_clusters = applyESSRules(return_message)
    validedclusters = validated_clusters['clusters']
    faliedclusters = validated_clusters['failedCluster']

    validatedClusterCount = 0
    for validatedCluster in validedclusters:
        assert validatedCluster in actualvCenterClusterList, 'Error: valid cluster but unexpected'
        print (validatedCluster, '\nVerified with Enginerring Standards')
        validatedClusterCount += 1

    assert len(faliedclusters) == 0, len(faliedclusters) + "Clusters failed ESS validation rules"
    assert validatedClusterCount == numOfClustersInList, "Not All cluster passed ESS rules"

    print('\nNumber of cluster falied ESS rules: '+ str(len(faliedclusters)) + " out of valid cluster: " + str(validatedClusterCount))


# Read Vcenter response
def readVcenterResponse():
    cleanup('test.vcenter.response')
    bindQueues('exchange.cpsd.controlplane.vcenter.response', 'test.vcenter.response')
    # Purge the queue to ensure the test response query is empty
    af_support_tools.rmq_purge_queue(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                     rmq_username=cpsd.props.rmq_username,
                                     rmq_password=cpsd.props.rmq_password, ssl_enabled=cpsd.props.rmq_ssl_enabled,
                                     queue='test.vcenter.response')
    # /dne/clusters this triggers the VCenter Discover Cluster Message
    listvCenterClustersAPI()
    ###################################################
    # Consume the published vcenter.cluster.discover.response message and compare this also to the actual data
    assert waitForMsg('test.vcenter.response'), 'ERROR: No responce message reveived listing clusters'
    return_message = af_support_tools.rmq_consume_message(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                                          rmq_username=cpsd.props.rmq_username,
                                                          rmq_password=cpsd.props.rmq_password,
                                                          ssl_enabled=cpsd.props.rmq_ssl_enabled,
                                                          queue='test.vcenter.response', remove_message=False)
    cleanup('test.vcenter.response')
    return return_message


#######################################################################################################################

# These functions get the info direct from the specified vcenter
def get_obj(content, vimtype, name=None):
    return [item for item in content.viewManager.CreateContainerView(
        content.rootFolder, [vimtype], recursive=True).view]


def getRealVcenterInfo():
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

    content = si.RetrieveContent()

    clusterList = []

    for cluster_obj in get_obj(content, vim.ComputeResource):
        cluster = {'name': (cluster_obj.name), 'numberOfHosts': (len(cluster_obj.host))}
        clusterList.append(cluster)

    return clusterList


# This function gets the data from the Symphony dne/clusters API
def listvCenterClustersAPI():
    dne_url_body = '/dne/clusters'
    my_dne_url = protocol + ipaddress + dne_port + dne_url_body

    print('GET:', my_dne_url)

    try:
        url_response = requests.get(my_dne_url)
        url_response.raise_for_status()

        # A 200 has been received
        print(url_response)

        the_response = url_response.text  # Save the body of the response to a variable

    # Error check the response
    except Exception as err:
        # Return code error (e.g. 404, 501, ...)
        print(err)
        print('\n')
        raise Exception(err)

    return the_response


# apply Engineering Standard rules to all discovered clusters
# This will return all - valid clusters and failed clusters
def applyESSRules(return_message):
    cleanup('test.ess.service.response')
    bindQueues('exchange.dell.cpsd.service.ess.response', 'test.ess.service.response')

    print('\n Validate vcenter cluster request message:')
    print('\n publishing vcenter cluster request message:')
    ess_routing_key = 'ess.service.request.' + str(uuid.uuid4())
    the_payload = return_message
    print(the_payload)

    af_support_tools.rmq_publish_message(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                         rmq_username=cpsd.props.rmq_username, rmq_password=cpsd.props.rmq_password,
                                         exchange='exchange.dell.cpsd.service.ess.request',
                                         routing_key=ess_routing_key,
                                         headers={'__TypeId__': 'com.dell.cpsd.vcenter.validateClusterRequest'},
                                         payload=the_payload,
                                         payload_type='json',
                                         ssl_enabled=cpsd.props.rmq_ssl_enabled)

    # Consume the published ess message and compare this also to the actual data
    assert waitForMsg('test.ess.service.response'), 'ERROR: No response message received from ess queues'
    ess_return_message = af_support_tools.rmq_consume_message(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                                          rmq_username=cpsd.props.rmq_username,
                                                          rmq_password=cpsd.props.rmq_password,
                                                          ssl_enabled=cpsd.props.rmq_ssl_enabled,
                                                          queue='test.ess.service.response', remove_message=False)
    cluster_json = json.loads(ess_return_message, encoding='utf-8')
    cleanup('test.ess.service.response')

    print(json.dumps(cluster_json))

    return cluster_json


#######################################################################################################################

# These are functions needed to manually configure vcenter with Consul & the config.properties file.

def vcenter_adapter_ListCapabilities():
    """
    Title           :       Verify the registry.list.capability Message returns all vcenter-adapter capabilities
    Description     :       A registry.list.capability message is sent.  It is expected that a response is returned that
                            includes a list of all the vcenter-adapter capabilities.
                            It will fail if :
                               No capability.registry.response is received.
                               The vcenter-adapter is not in the response.
                               The vcenter-adapter capabilites are not in the response.
    Parameters      :       none
    Returns         :       None
    """
    cleanup('test.capability.registry.response')
    bindQueues('exchange.dell.cpsd.hdp.capability.registry.response', 'test.capability.registry.response')

    print("\nTest: Send in a list capabilities message and to verify all vCenter Adapter capabilities are present")

    # Send in a "list capabilities message"
    originalcorrelationID = 'capability-registry-list-vcenter-adapter-corID'
    the_payload = '{}'

    af_support_tools.rmq_publish_message(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                         rmq_username=cpsd.props.rmq_username, rmq_password=cpsd.props.rmq_password,
                                         exchange='exchange.dell.cpsd.hdp.capability.registry.request',
                                         routing_key='dell.cpsd.hdp.capability.registry.request',
                                         headers={
                                             '__TypeId__': 'com.dell.cpsd.hdp.capability.registry.list.capability.providers'},
                                         payload=the_payload,
                                         payload_type='json',
                                         correlation_id={originalcorrelationID}, ssl_enabled=cpsd.props.rmq_ssl_enabled)

    # Wait for and consume the Capability Response Message
    assert waitForMsg('test.capability.registry.response'), 'ERROR: No List Capabilities Message returned'
    return_message = af_support_tools.rmq_consume_message(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                                          rmq_username=cpsd.props.rmq_username,
                                                          rmq_password=cpsd.props.rmq_password,
                                                          queue='test.capability.registry.response',
                                                          ssl_enabled=cpsd.props.rmq_ssl_enabled)

    time.sleep(5)
    # Verify the vcenter Adapter Response has the 'vcenter-discover-cluster' capability
    identity = 'vcenter-adapter'
    capabilities1 = 'vcenter-discover-cluster'

    error_list = []

    if (identity not in return_message):
        error_list.append(identity)
    if (capabilities1 not in return_message):
        error_list.append(capabilities1)

    # If the capability isnt there then call the function t register the vcenter
    if error_list:
        print('Need to register a vcenter, calling function...')
        registerVcenter()

    cleanup('test.capability.registry.response')
    print('vcenter-discover-cluster available')
    return True


def registerVcenter():
    # Until consul is  working properly & integrated with the vcenter adapter in the same environment we need to register
    # it manually by sending this message.

    cleanup('test.controlplane.vcenter.response')
    cleanup('test.endpoint.registration.event')
    bindQueues('exchange.cpsd.controlplane.vcenter.response', 'test.controlplane.vcenter.response')
    bindQueues('exchange.dell.cpsd.endpoint.registration.event', 'test.endpoint.registration.event')

    time.sleep(2)

    af_support_tools.rmq_purge_queue(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                     rmq_username=cpsd.props.rmq_username, rmq_password=cpsd.props.rmq_password,
                                     ssl_enabled=cpsd.props.rmq_ssl_enabled,
                                     queue='test.controlplane.vcenter.response')

    af_support_tools.rmq_purge_queue(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                     rmq_username=cpsd.props.rmq_username, rmq_password=cpsd.props.rmq_password,
                                     ssl_enabled=cpsd.props.rmq_ssl_enabled,
                                     queue='test.endpoint.registration.event')

    the_payload = '{"messageProperties":{"timestamp":"2010-01-01T12:00:00Z","correlationId":"vcenter-registtration-corr-id","replyTo":"localhost"},"registrationInfo":{"address":"https://' + vcenter_IP + ':' + vcenter_port + '","username":"' + vcenter_username + '","password":"' + vcenter_password + '"}}'
    print(the_payload)
    af_support_tools.rmq_publish_message(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                         rmq_username=cpsd.props.rmq_username, rmq_password=cpsd.props.rmq_password,
                                         ssl_enabled=cpsd.props.rmq_ssl_enabled,
                                         exchange='exchange.cpsd.controlplane.vcenter.request',
                                         routing_key='controlplane.hypervisor.vcenter.endpoint.register',
                                         headers={
                                             '__TypeId__': 'com.dell.cpsd.vcenter.registration.info.request'},
                                         payload=the_payload)

    # Verify the vcenter is validated
    assert waitForMsg('test.controlplane.vcenter.response'), 'ERROR: No validation Message Returned'
    return_message = af_support_tools.rmq_consume_message(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                                          rmq_username=cpsd.props.rmq_username,
                                                          rmq_password=cpsd.props.rmq_password,
                                                          ssl_enabled=cpsd.props.rmq_ssl_enabled,
                                                          queue='test.controlplane.vcenter.response',
                                                          remove_message=True)
    return_json = json.loads(return_message, encoding='utf-8')
    print (return_json)
    assert return_json['responseInfo']['message'] == 'SUCCESS', 'ERROR: Vcenter validation failure'

    # Verify the system triggers a msg to register vcenter with consul
    assert waitForMsg('test.endpoint.registration.event'), 'ERROR: No message to register with Consul sent'
    return_message = af_support_tools.rmq_consume_message(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                                          rmq_username=cpsd.props.rmq_username,
                                                          rmq_password=cpsd.props.rmq_password,
                                                          ssl_enabled=cpsd.props.rmq_ssl_enabled,
                                                          queue='test.endpoint.registration.event',
                                                          remove_message=True)

    return_json = json.loads(return_message, encoding='utf-8')
    print (return_json)
    assert return_json['endpoint']['type'] == 'vcenter', 'vcenter not registered with endpoint'

    cleanup('test.controlplane.vcenter.response')
    cleanup('test.endpoint.registration.event')

    print ('vcenter registerd')
    time.sleep(3)



#######################################################################################################################
# These are common functions that are used throughout the main test.
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
    q_len = 0
    timeout = 0

    while q_len < 1:
        time.sleep(1)
        timeout += 1

        q_len = af_support_tools.rmq_message_count(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                                   rmq_username=cpsd.props.rmq_username,
                                                   rmq_password=cpsd.props.rmq_password,
                                                   ssl_enabled=cpsd.props.rmq_ssl_enabled,
                                                   queue=queue)

        if timeout > 600:
            print('ERROR: Message took to long to return. Something is wrong')
            return False

    return True

#######################################################################################################################
