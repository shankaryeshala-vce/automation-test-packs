#!/usr/bin/python
# Author: cullia
# Revision: 2.0
# Code Reviewed by:
# Description:Testing the Node Expansion Teams, VCenter Cluster Discovery.

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


#######################################################################################################################

@pytest.fixture(scope="module", autouse=True)
def load_test_data():
    # Update config ini files at runtime
    my_data_file = os.environ.get('AF_RESOURCES_PATH') + '/continuous-integration-deploy-suite/config_capreg.properties'
    af_support_tools.set_config_file_property_by_data_file(my_data_file)

    # Set config ini file name
    global env_file
    env_file = 'env.ini'
    global capreg_config_file
    capreg_config_file = 'continuous-integration-deploy-suite/config_capreg.ini'
    global capreg_config_header
    capreg_config_header = 'config_details'

    # Set Vars
    global payload_file
    payload_file = 'continuous-integration-deploy-suite/symphony-sds.ini'

    global ipaddress
    ipaddress = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='hostname')
    global cli_username
    cli_username = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS',
                                                             property='username')
    global cli_password
    cli_password = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS',
                                                             property='password')

    global rmq_username
    rmq_username = 'guest'
    global rmq_password
    rmq_password = 'guest'
    global port
    port = 5672

    global vCenterFQDN
    vCenterFQDN = af_support_tools.get_config_file_property(config_file=capreg_config_file,
                                                            heading=capreg_config_header, property='vcenter')
    global vCenterUser
    vCenterUser = af_support_tools.get_config_file_property(config_file=capreg_config_file,
                                                            heading=capreg_config_header, property='vcenter_user')
    global vCenterPassword
    vCenterPassword = af_support_tools.get_config_file_property(config_file=capreg_config_file,
                                                                heading=capreg_config_header,
                                                                property='vcenter_password')
    global vCenterPort
    vCenterPort = '443'


#######################################################################################################################

@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_vcenter_discover_cluters():
    print('\nRunning test on Symphony system:', ipaddress, 'and Test vCenter:', vCenterFQDN, '\n')

    cleanup()
    bindQueus()

    print('Prerequisite: Configuring VCenter Adapter application.properties file & registering with Consul')

    # TODO Remove these when system-definition integration is complete
    #vCenterConfigApplicationProperties()
    vCenterRegistrationMsg()
    time.sleep(20)

    print('\nVering RMQ Binding')
    test_queues_on_exchange('exchange.cpsd.controlplane.vcenter.request',
                            'queue.dell.cpsd.controlplane.vcenter.cluster.discover')

    print('*******************************************************')
    print('\nStep 1: Data direct from Test vCenter')
    # Get a list of the actual clusters direct from the test vCenter Server
    actualvCenterClusterList = getRealVcenterInfo()
    numOfClustersInList = len(actualvCenterClusterList)  # Get the number of clusters in the list

    print('Total Number of Clusters:', numOfClustersInList)
    print(actualvCenterClusterList, '\n')

    # Purge the queue to ensure the test response query is empty
    af_support_tools.rmq_purge_queue(host=ipaddress, port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                     queue='test.vcenter.response')

    # Get the data in the dne/clusters API and compare it to the actual data
    print('\nStep 2: Send an API GET to /dne/nodes this triggers the VCenter Discover CLuster Message')
    apiResponseData = listvCenterClustersAPI()
    apiResponseData_json = json.loads(apiResponseData, encoding='utf-8')

    assert apiResponseData_json == actualvCenterClusterList
    print('Symphony API Response Data matches Source Data\n')

    # Consume the vcenter.cluster.discover.response message
    waitForMsg('test.vcenter.response')
    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
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

    print('\nTest Pass')
    print('\n*******************************************************')

    cleanup()


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
            host=vCenterFQDN,
            user=vCenterUser,
            pwd=vCenterPassword,
            port=vCenterPort,
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
    # print('\nListing vCenter Clusters on API')

    url_body = ':8071/dne/clusters'
    my_url = 'http://' + ipaddress + url_body

    print('GET:', my_url)

    try:
        url_response = requests.get(my_url)
        url_response.raise_for_status()

    except requests.exceptions.HTTPError as err:
        # Return code error (e.g. 404, 501, ...)
        print(err)
        print('\n')
        assert False

    except requests.exceptions.Timeout as err:
        # Not an HTTP-specific error (e.g. connection refused)
        print(err)
        print('\n')
        assert False

    else:
        # 200
        print(url_response)

        the_response = url_response.text

        print('API Return Data:', the_response)

        return the_response


#######################################################################################################################

# These are functions needed to manually configure vcenter with Consul & the config.properties file.

# def vCenterConfigApplicationProperties():
#     # We need a way for the Vcenter Cluster Discover code to be able to get the VCenter Credentials. Currently the only
#     # way to do this is with a application.properties file in the vcenter-adapter container that has the name &
#     # credentials. This function writes that file and restarts the container.
#
#     applicationProperties = 'spring.rabbitmq.host=localhost' \
#                             '\nspring.rabbitmq.port=5672' \
#                             '\nspring.rabbitmq.username=guest' \
#                             '\nspring.rabbitmq.password=guest' \
#                             '\nserver.port=0' \
#                             '\n' \
#                             '\n#TO BE REMOVED: this is temp solution. Will get these from credential service once it is ready and remove this file.' \
#                             '\n#put this file under here QA can change the vcenter credential without rebuild code.' \
#                             '\n#vcenter.address=https://<iporHost>:443' \
#                             '\nvcenter.address=https://' + vCenterFQDN + ':443' \
#                                                                          '\nvcenter.username=' + vCenterUser + '' \
#                                                                                                                '\nvcenter.password=' + vCenterPassword + ''
#
#     # Get the containerID and and remove the file.
#     vCenterContainerID = getdockerID('cpsd-vcenter-adapter-service')
#     sendCommand = 'docker exec -i ' + vCenterContainerID + ' sh -c "rm application.properties"'
#     af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
#                                       command=sendCommand, return_output=False)
#
#     time.sleep(1)
#
#     # Write to the application.properties file specifying the vcenter name & credentials.
#     sendCommand = 'docker exec -i ' + vCenterContainerID + ' sh -c "echo -e \'' + applicationProperties + '\' >> application.properties"'
#     af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
#                                       command=sendCommand, return_output=False)
#
#     # Restart the vcenter doocker container.
#     sendCommand = 'docker restart ' + vCenterContainerID
#     af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
#                                       command=sendCommand, return_output=False)
#
#     time.sleep(3)


def vCenterRegistrationMsg():
    # Until there is a way to automatically register a vcenter we need to register it manually by sending this message.

    af_support_tools.rmq_purge_queue(host=ipaddress, port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                     queue='test.controlplane.vcenter.response')

    af_support_tools.rmq_purge_queue(host=ipaddress, port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                     queue='test.endpoint.registration.event')

    the_payload = '{"messageProperties":{"timestamp":"2010-01-01T12:00:00Z","correlationId":"vcenter-registtration-corr-id","replyTo":"localhost"},"registrationInfo":{"address":"https://' + vCenterFQDN + ':443","username":"' + vCenterUser + '","password":"' + vCenterPassword + '"}}'

    af_support_tools.rmq_publish_message(host=ipaddress, rmq_username=rmq_username, rmq_password=rmq_password,
                                         exchange='exchange.cpsd.controlplane.vcenter.request',
                                         routing_key='controlplane.hypervisor.vcenter.endpoint.register',
                                         headers={
                                             '__TypeId__': 'com.dell.cpsd.vcenter.registration.info.request'},
                                         payload=the_payload)

    waitForMsg('test.controlplane.vcenter.response')
    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.controlplane.vcenter.response',
                                                          remove_message=True)
    checkForErrors(return_message)
    return_json = json.loads(return_message, encoding='utf-8')
    assert return_json['responseInfo']['message'] == 'SUCCESS', 'ERROR: Vcenter validation failure'

    waitForMsg('test.endpoint.registration.event')
    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.endpoint.registration.event',
                                                          remove_message=True)

    checkForErrors(return_message)
    return_json = json.loads(return_message, encoding='utf-8')
    # assert return_json['endpoint']['type'] == 'vcenter', 'vcenter not registered with endpoint'
    # TODO above is commented out as its consumming the wrong message


#######################################################################################################################
# These are common functions that are used throughout the main test.


def cleanup():
    # Delete the test queues
    print('Cleaning up...')

    af_support_tools.rmq_delete_queue(host=ipaddress, port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                      queue='test.vcenter.response')

    af_support_tools.rmq_delete_queue(host=ipaddress, port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                      queue='test.endpoint.registration.event')

    af_support_tools.rmq_delete_queue(host=ipaddress, port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                      queue='test.controlplane.vcenter.response')


def bindQueus():
    print('\nCreating test Queues')
    af_support_tools.rmq_bind_queue(host=ipaddress,
                                    port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                    queue='test.vcenter.response',
                                    exchange='exchange.cpsd.controlplane.vcenter.response',
                                    routing_key='#')

    af_support_tools.rmq_bind_queue(host=ipaddress,
                                    port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                    queue='test.endpoint.registration.event',
                                    exchange='exchange.dell.cpsd.endpoint.registration.event',
                                    routing_key='#')

    af_support_tools.rmq_bind_queue(host=ipaddress,
                                    port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                    queue='test.controlplane.vcenter.response',
                                    exchange='exchange.cpsd.controlplane.vcenter.response',
                                    routing_key='#')


def waitForMsg(queue):
    q_len = 0
    timeout = 0

    while q_len < 1:
        time.sleep(1)
        timeout += 1

        q_len = af_support_tools.rmq_message_count(host=ipaddress,
                                                   port=port,
                                                   rmq_username=rmq_username,
                                                   rmq_password=rmq_password,
                                                   queue=queue)

        if timeout > 50:
            print('ERROR: Message took to long to return. Something is wrong')
            checkForErrorMsg()


def checkForErrors(return_message):
    checklist = 'errors'
    if checklist in return_message:
        print('\nBUG: Error in Response Message\n')
        assert False  # This assert is to fail the test


def getdockerID(imageName):
    image = imageName

    sendCommand = 'docker ps | grep ' + image + ' | awk \'{print $1}\''
    containerID = af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                                    command=sendCommand, return_output=True)

    containerID = containerID.strip()
    return (containerID)


def rest_queue_list(user=None, password=None, host=None, port=None, virtual_host=None, exchange=None):
    url = 'http://%s:%s/api/exchanges/%s/%s/bindings/source' % (host, port, virtual_host, exchange)
    response = requests.get(url, auth=(user, password))
    queues = [q['destination'] for q in response.json()]
    return queues


def test_queues_on_exchange(suppliedExchange, suppliedQueue):
    queues = rest_queue_list(user=rmq_username, password=rmq_password, host=ipaddress, port=15672, virtual_host='%2f',
                             exchange=suppliedExchange)
    queues = json.dumps(queues)

    assert suppliedQueue in queues, 'The queue "' + suppliedQueue + '" is not bound to the exchange "' + suppliedExchange + '"'
    print(suppliedExchange, '\nis bound to\n', suppliedQueue, '\n')

#######################################################################################################################
