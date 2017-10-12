#!/usr/bin/python
# Author:
# Revision:
# Code Reviewed by:
# Description: This is a setup scrip that will configure Symphony for DNE with a valid system definition file
#
# Copyright (c) 2017 Dell Inc. or its subsidiaries.  All Rights Reserved.
# Dell EMC Confidential/Proprietary Information

import af_support_tools
import os
import pytest
import json
import time

@pytest.fixture(scope="module", autouse=True)
def load_test_data():
    import cpsd
    global cpsd

    # Set config ini file name
    global env_file
    env_file = 'env.ini'

    # Set Vars
    global ip_address
    ip_address = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='hostname')

    global username
    username = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='username')

    global password
    password = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='password')

    # Update config ini files at runtime
    my_data_file = os.environ.get('AF_RESOURCES_PATH') + '/continuous-integration-deploy-suite/symphony-sds.properties'
    af_support_tools.set_config_file_property_by_data_file(my_data_file)

    # Set Vars
    global payload_file
    payload_file = 'continuous-integration-deploy-suite/symphony-sds.ini'

    global payload_header
    payload_header = 'payload'

    global payload_property_sys
    payload_property_sys = 'sys_payload_node_exp'

    global jsonfilepath
    jsonfilepath = 'IDRAC.json'

    global amqptooljar
    amqptooljar = str(os.environ.get('AF_RESOURCES_PATH')) + '/system-definition/amqp-post-1.0-SNAPSHOT.jar'


    # Update setup_config.ini file at runtime
    my_data_file = os.environ.get('AF_RESOURCES_PATH') + '/continuous-integration-deploy-suite/setup_config.properties'
    af_support_tools.set_config_file_property_by_data_file(my_data_file)

    # RackHD VM IP & Creds details. These will be used to register the RackHD Endpoint
    global setup_config_file
    setup_config_file = 'continuous-integration-deploy-suite/setup_config.ini'

    global setup_config_header
    setup_config_header = 'config_details'

    global rackHD_IP
    rackHD_IP = af_support_tools.get_config_file_property(config_file=setup_config_file, heading=setup_config_header,
                                                          property='rackhd_dne_ipaddress')

    global rackHD_username
    rackHD_username = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                heading=setup_config_header,
                                                                property='rackhd_username')
    global rackHD_password
    rackHD_password = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                heading=setup_config_header,
                                                                property='rackhd_password')

    global rackHD_body
    rackHD_body = ':32080/ui/'

    global vcenter_IP
    vcenter_IP = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                           heading=setup_config_header,
                                                           property='vcenter_dne_ipaddress_scaleio')

    global vcenter_port
    vcenter_port = '443'

    global vcenter_username
    vcenter_username = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                 heading=setup_config_header,
                                                                 property='vcenter_username')
    global vcenter_password
    vcenter_password = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                 heading=setup_config_header,
                                                                 property='vcenter_password_rtp')

    global scaleIO_IP
    scaleIO_IP = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                           heading=setup_config_header,
                                                           property='scaleio_integration_ipaddress')

    global scaleIO_username
    scaleIO_username = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                 heading=setup_config_header,
                                                                 property='scaleio_username')
    global scaleIO_password
    scaleIO_password = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                 heading=setup_config_header,
                                                                 property='scaleio_password')


#####################################################################

@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_dne_setup_system():
    """
    Description:    This script will configure a System with a json file.
                    It will also register the rackhd & vcenter endpoints
    Parameters:     None
    Returns:        None
    """

    # Get the payload data from the config symphony-sds.ini file.
    the_payload = af_support_tools.get_config_file_property(config_file=payload_file,
                                                            heading=payload_header,
                                                            property=payload_property_sys)

    assert update_IDRAC_json(jsonfilepath, ip_address, the_payload), 'test failed: ' + jsonfilepath + 'doesnt exists'

    enable_rabbitmq_management_plugin()
    time.sleep(3)

    assert run_amqp_tool(amqptooljar, jsonfilepath), 'test failed: unable to execute ' + amqptooljar


@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_dne_RegisterRackHD():
    assert registerRackHD(), 'Error: unable to register the RackHD endpoint'


@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_dne_RegisterVcenter():
    assert registerVcenter(), 'Error: unable to register the vCenter endpoint'


#@pytest.mark.dne_paqx_parent_mvp
#@pytest.mark.dne_paqx_parent_mvp_extended
def test_dne_RegisterScaleIO():
    assert registerScaleIO(), 'Error: unable to register the ScaleIO endpoint'


#####################################################################

def update_IDRAC_json(json_file_path, ipaddress, payload):
    """
    Description:    This method will update the json file with the host ip address
    Parameters:     1. json_file_path     - Name of the Json file (STRING)
                    2. ipaddress          - hostname mentioned in the env.ini file
                    3. payload            - payload for the json file
    Returns:        0 or 1 (Boolean)
    """
    with open(json_file_path,'w') as outfile:
        outfile.write(payload)
    outfile.close()

    if (os.path.isfile(json_file_path) == 0):
        return 0

    with open(json_file_path) as json_file:
        data = json.load(json_file)
    data['configuration']['host'] = ipaddress 

    with open(json_file_path,'w') as outfile:
        json.dump(data,outfile)

    print ('next')
    print (data)
    return 1


def run_amqp_tool(amqp_tool_jar, system_def_json):
    """
    Description:    This method will run the ampq tool jar file with the given input json file
    Parameters:     1. amqp_tool_jar       -    Name of the amqp tool jar file (STRING)
                    2. system_def_json     -    Name of the Json file (STRING)
    Returns:        0 or 1 (Boolean)
    """
    test_status = "pass"
    cmd = 'java -jar ' + amqp_tool_jar + ' ' + system_def_json

    output = os.system(cmd)

    # Adding sleepp to debug if it is timing issue
    time.sleep(10)

    if (output != 0):
        test_status = "fail"

    if (test_status == "fail"):
        return 0

    else:
        print ('System Configured')
        return 1


def registerRackHD():
    # Until consul is  working properly & integrated with the rackhd adapter in the same environment we need to register
    # it manually by sending this message.  This test is a prerequisite to getting the full list of

    cleanup('test.controlplane.rackhd.response')
    cleanup('test.endpoint.registration.event')
    bindQueues('exchange.dell.cpsd.controlplane.rackhd.response', 'test.controlplane.rackhd.response')
    bindQueues('exchange.dell.cpsd.endpoint.registration.event', 'test.endpoint.registration.event')

    time.sleep(2)

    af_support_tools.rmq_purge_queue(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                     rmq_username=cpsd.props.rmq_username, rmq_password=cpsd.props.rmq_password,
                                     ssl_enabled=cpsd.props.rmq_ssl_enabled,
                                     queue='test.controlplane.rackhd.response')

    af_support_tools.rmq_purge_queue(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                     rmq_username=cpsd.props.rmq_username, rmq_password=cpsd.props.rmq_password,
                                     ssl_enabled=cpsd.props.rmq_ssl_enabled,
                                     queue='test.endpoint.registration.event')

    the_payload = '{"messageProperties":{"timestamp":"2017-06-14T12:00:00Z","correlationId":"manually-reg-rackhd-3fb0-9696-3f7d28e17f72"},"registrationInfo":{"address":"http://' + rackHD_IP + rackHD_body + '","username":"' + rackHD_username + '","password":"' + rackHD_password + '"}}'
    print(the_payload)

    af_support_tools.rmq_publish_message(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                         rmq_username=cpsd.props.rmq_username, rmq_password=cpsd.props.rmq_password,
                                         exchange='exchange.dell.cpsd.controlplane.rackhd.request',
                                         routing_key='controlplane.rackhd.endpoint.register',
                                         headers={
                                             '__TypeId__': 'com.dell.cpsd.rackhd.registration.info.request'},
                                         payload=the_payload, ssl_enabled=cpsd.props.rmq_ssl_enabled)

    # Verify the RackHD account can be validated
    assert waitForMsg('test.controlplane.rackhd.response'), 'Error: No RackHD validation message received'
    return_message = af_support_tools.rmq_consume_message(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                                          rmq_username=cpsd.props.rmq_username,
                                                          rmq_password=cpsd.props.rmq_password,
                                                          ssl_enabled=cpsd.props.rmq_ssl_enabled,
                                                          queue='test.controlplane.rackhd.response',
                                                          remove_message=True)
    return_json = json.loads(return_message, encoding='utf-8')
    print (return_json)
    assert return_json['responseInfo']['message'] == 'SUCCESS', 'ERROR: RackHD validation failure'

    # Verify that an event to register the rackHD with endpoint registry is triggered
    assert waitForMsg('test.endpoint.registration.event'), 'Error: No message to register with Consul sent by system'
    return_message = af_support_tools.rmq_consume_message(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                                          rmq_username=cpsd.props.rmq_username,
                                                          rmq_password=cpsd.props.rmq_password,
                                                          ssl_enabled=cpsd.props.rmq_ssl_enabled,
                                                          queue='test.endpoint.registration.event',
                                                          remove_message=True)

    return_json = json.loads(return_message, encoding='utf-8')
    print (return_json)
    #assert return_json['endpoint']['type'] == 'rackhd', 'rackhd not registered with endpoint'
    # Removing this assert as the messages from the different adapters are interfering with one another.
    cleanup('test.controlplane.rackhd.response')
    cleanup('test.endpoint.registration.event')

    print ('rackHD registerd')

    time.sleep(3)
    return 1


def registerVcenter():
    # Until consul is  working properly & integrated with the vcenter adapter in the same environment we need to register
    # it manually by sending this message.

    cleanup('test.controlplane.vcenter.response')
    cleanup('test.endpoint.registration.event')
    bindQueues('exchange.dell.cpsd.controlplane.vcenter.response', 'test.controlplane.vcenter.response')
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
                                         exchange='exchange.dell.cpsd.controlplane.vcenter.request',
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
    #assert return_json['endpoint']['type'] == 'vcenter', 'vcenter not registered with endpoint'
    # Removing this assert as the messages from the different adapters are interfering with one another.
    cleanup('test.controlplane.vcenter.response')
    cleanup('test.endpoint.registration.event')

    print ('vcenter registerd')

    time.sleep(3)
    return 1


def registerScaleIO():
    # Until consul is  working properly & integrated with the vcenter adapter in the same environment we need to register
    # it manually by sending this message.

    cleanup('test.controlplane.scaleio.response')
    cleanup('test.endpoint.registration.event')
    bindQueues('exchange.dell.cpsd.controlplane.scaleio.response', 'test.controlplane.scaleio.response')
    bindQueues('exchange.dell.cpsd.endpoint.registration.event', 'test.endpoint.registration.event')

    time.sleep(2)

    af_support_tools.rmq_purge_queue(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                     rmq_username=cpsd.props.rmq_username, rmq_password=cpsd.props.rmq_password,
                                     ssl_enabled=cpsd.props.rmq_ssl_enabled,
                                     queue='test.controlplane.scaleio.response')

    af_support_tools.rmq_purge_queue(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                     rmq_username=cpsd.props.rmq_username, rmq_password=cpsd.props.rmq_password,
                                     ssl_enabled=cpsd.props.rmq_ssl_enabled,
                                     queue='test.endpoint.registration.event')

    the_payload = '{"messageProperties":{"timestamp":"2010-01-01T12:00:00Z","correlationId":"scaleio-full-abcd-abcdabcdabcd"},"registrationInfo":{"address":"https://' + scaleIO_IP + ':443","username":"' + scaleIO_username + '","password":"' + scaleIO_password + '"}}'
    print(the_payload)

    af_support_tools.rmq_publish_message(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                         rmq_username=cpsd.props.rmq_username, rmq_password=cpsd.props.rmq_password,
                                         exchange='exchange.dell.cpsd.controlplane.scaleio.request',
                                         routing_key='dell.cpsd.scaleio.consul.register.request',
                                         headers={
                                             '__TypeId__': 'com.dell.cpsd.scaleio.registration.info.request'},
                                         payload=the_payload, ssl_enabled=cpsd.props.rmq_ssl_enabled)

    # Verify the vcenter is validated
    assert waitForMsg('test.controlplane.scaleio.response'), 'ERROR: No validation Message Returned'
    return_message = af_support_tools.rmq_consume_message(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                                          rmq_username=cpsd.props.rmq_username,
                                                          rmq_password=cpsd.props.rmq_password,
                                                          ssl_enabled=cpsd.props.rmq_ssl_enabled,
                                                          queue='test.controlplane.scaleio.response',
                                                          remove_message=True)
    return_json = json.loads(return_message, encoding='utf-8')
    print (return_json)
    assert return_json['responseInfo']['message'] == 'SUCCESS', 'ERROR: ScaleIO validation failure'

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
    #assert return_json['endpoint']['type'] == 'scaleio', 'scaleio not registered with endpoint'
    # Removing this assert as the messages from the different adapters are interfering with one another.
    cleanup('test.controlplane.scaleio.response')
    cleanup('test.endpoint.registration.event')

    print ('scaleio registerd')

    time.sleep(3)
    return 1

#####################################################################

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
    # This function keeps looping untill a message is in the specified queue. We do need it to timeout and throw an error
    # if a message never arrives. Once a message appears in the queue the function is complete and main continues.

    # The length of the queue, it will start at 0 but as soon as we get a response it will increase
    q_len = 0

    # Represents the number of seconds that have gone by since the method started
    timeout = 0

    # Max number of seconds to wait
    max_timeout = 500

    # Amount of time in seconds that the loop is going to wait on each iteration
    sleeptime = 1

    while q_len < 1:
        time.sleep(sleeptime)
        timeout += sleeptime

        q_len = af_support_tools.rmq_message_count(host=cpsd.props.base_hostname, port=cpsd.props.rmq_port,
                                                   rmq_username=cpsd.props.rmq_username,
                                                   rmq_password=cpsd.props.rmq_password,
                                                   ssl_enabled=cpsd.props.rmq_ssl_enabled,
                                                   queue=queue)

        if timeout > max_timeout:
            print('ERROR: Message took too long to return. Something is wrong')
            return False

    return True

def enable_rabbitmq_management_plugin():
    """ A function to enable the rabbitmq_management plugin
    It won't cause any errrors if it is already enabled"""
    command = 'docker exec -d amqp rabbitmq-plugins enable rabbitmq_management'
    af_support_tools.send_ssh_command(
        host=ip_address,
        username=username,
        password=password,
        command=command,
        return_output=False)
