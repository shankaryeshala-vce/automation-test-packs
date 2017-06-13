#!/usr/bin/python
# Copyright © 01 April 2017 Dell Inc. or its subsidiaries.  All Rights Reserved.
#
# Author: russed5
# Revision: 1.0
# Code Reviewed by: olearj10
# Description: see https://wiki.ent.vce.com/display/VSE/Endpoint+Registry+Testing

import pytest
import requests
import json
import time
import af_support_tools

@pytest.fixture(scope="module", autouse=True)
def load_test_data():

    try:
        global env_file
        env_file = 'env.ini'
        global ipaddress
        ipaddress = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='hostname')
    except:
        print('Possible configuration error.')

    #Use this to by-pass the env.ini file
    #ipaddress = '10.3.62.105'
    global new_service_name
    new_service_name = "testService"
    global new_service_id
    new_service_id = "testService1"
    global new_service_host
    new_service_host = ipaddress
    global new_service_port
    new_service_port = 200
    global new_service_tag_1
    new_service_tag_1 = "testTag1"
    global new_service_tag_2
    new_service_tag_2 = "testTag2"

    global crhost
    crhost = ipaddress      # capabilities registry host
    global cohost
    cohost = ipaddress      # consul host
    global rabbitHost
    rabbitHost = ipaddress  # rabbitmq host
    global rabbiturl
    rabbiturl = "http://" + rabbitHost + ":15672"

    global capabilitiesExchange
    capabilitiesExchange = "exchange.dell.cpsd.hdp.capability.registry.control"
    global endpointExchange
    endpointExchange = "exchange.dell.cpsd.endpoint.registration.event"

    global rmq_username
    rmq_username = 'test'
    global rmq_password
    rmq_password = 'test'

    global port
    port = 5672

    # *******************************************************************************************
    # the payload data used to register services with consul

    global regData
    regData = {"ID": new_service_id, "Name": new_service_name, "Address": new_service_host, "Port": new_service_port,
           "Tags": [new_service_tag_1], "Check": {"HTTP": rabbiturl, "Interval": "2s"}}

    global regDataNoAddress
    regDataNoAddress = {"ID": new_service_id, "Name": new_service_name,
                    "Tags": [new_service_tag_1], "Check": {"HTTP": rabbiturl, "Interval": "5s"}}

    global regDataNoPort
    regDataNoPort = {"ID": new_service_id, "Name": new_service_name, "Address": new_service_host,
                 "Tags": [new_service_tag_1], "Check": {"HTTP": rabbiturl, "Interval": "5s"}}

    global regDataNoHealthCheck
    regDataNoHealthCheck = {"ID": new_service_id, "Name": new_service_name, "Address": new_service_host, "Port": new_service_port,
                        "Tags": [new_service_tag_1]}

    global regDataWithCheckFailure
    regDataWithCheckFailure = {"ID": new_service_id, "Name": new_service_name, "Address": new_service_host,
                           "Tags": [new_service_tag_1],
                           "Check": {"DeregisterCriticalServiceAfter": "20s", "HTTP": "http://3.3.3.3:15672", "Interval": "5s"}}

# *******************************************************************************************
#
@pytest.mark.core_services_mvp_extended
def test_registerServiceWithNoAddress():
    # Testing that even tho Consul accepts a registration with no Address field, the Endpoint Registry
    # does not advertise its existence

    # setup, delete any lingering AMQP testQueue and create a new one before any messaging starts
    cleanup(new_service_id)
    ssetup(endpointExchange, 'dell.cpsd.endpoint.discovered')

    status_code = execRegisterService(regDataNoAddress)
    assert status_code == 200, "The Register Service task was unsuccessful"

    # check on the AMQP bus that a discovered endpoint event was NOT raised for thsi service
    event = verifyEventOnBus(rabbitHost, endpointExchange, "dell.cpsd.endpoint.discovered")
    assert not event, 'An event was raised when it should not have been'

    #cleanup(new_service_id)
    time.sleep(10)     # allow time between service status change
# # *******************************************************************************************
#
@pytest.mark.core_services_mvp_extended
def test_registerServiceWithNoPort():
    # Testing that even tho Consul accepts a registration with no Address field, the Endpoint Registry
    # does not advertise its existence

    # setup, delete any lingering AMQP testQueue and create a new one before any messaging starts
    cleanup(new_service_id)
    ssetup(endpointExchange, 'dell.cpsd.endpoint.discovered')

    status_code = execRegisterService(regDataNoPort)
    assert status_code == 200, "The Register Service task was unsuccessful"

    # check on the AMQP bus that a discovered endpoint event was NOT raised for thsi service
    event = verifyEventOnBus(rabbitHost, endpointExchange, "dell.cpsd.endpoint.discovered")
    assert not event, 'An event was raised when it should not have been'

    # cleanup(new_service_id)
    time.sleep(10)     # allow time between service status change

# # *******************************************************************************************

@pytest.mark.core_services_mvp_extended
def test_registerServiceWithNoHealthCheck():
    # Testing that even tho Consul accepts a registration with no Address field, the Endpoint Registry
    # does not advertise its existence

    # setup, delete any lingering AMQP testQueue and create a new one before any messaging starts
    cleanup(new_service_id)
    ssetup(endpointExchange, 'dell.cpsd.endpoint.discovered')

    status_code = execRegisterService(regDataNoHealthCheck)
    assert status_code == 200, "The Register Service task was unsuccessful"

    # check on the AMQP bus that a discovered endpoint event was NOT raised for thsi service
    event = verifyEventOnBus(rabbitHost, endpointExchange, "dell.cpsd.endpoint.discovered")
    assert not event, 'An event was raised when it should not have been'

    # cleanup(new_service_id)
    time.sleep(10)     # allow time between service status change
#
# # # **************************************************************************************

@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_registerServiceSuccess():
    # This test verifies that a succful service register in Consul prompts the Endpoint Registry
    # to publish an endpoint.discovered event to the AMQP bus

    errors_list = []
    # setup, delete any lingering AMQP testQueue and create a new one before any messaging starts
    cleanup(new_service_id)
    ssetup(endpointExchange, 'dell.cpsd.endpoint.discovered')

    status_code = execRegisterService(regData)
    assert status_code == 200, "The Register Service task was unsuccessful"

    # double-check in consul if the registration was successful
    data_check = verifyRegisterServiceSuccess(new_service_name, new_service_id, new_service_host, new_service_tag_1)
    assert data_check == "Success", "The new Service is not correctly registered in Consul"

    # check on the AMQP bus that a discovered endpoint event was raised with correct payload
    event = verifyEventOnBus(rabbitHost, endpointExchange, "dell.cpsd.endpoint.discovered")
    #cleanup(new_service_id)

    if new_service_name not in event['endpoint']['type']:
        errors_list.append("Service Name on the AMQP Bus is incorrect")
    if new_service_host not in event['endpoint']['instances'][0]['url']:
        errors_list.append("Service Address on the AMQP Bus is incorrect")
    if new_service_tag_1 not in event['endpoint']['instances'][0]['tags'][0]:
        errors_list.append("Service Tag on the AMQP Bus is incorrect")

    assert not errors_list

    time.sleep(10)     # allow time between service status change
# #
# # # **************************************************************************************

@pytest.mark.core_services_mvp_extended
def test_registerTwoServicesSameName():
    # this test verifies that the same service can be registered twice, but with differing endpoints

    errors_list = []
    cleanup("duplicateService1")
    cleanup("duplicateService2")

    time.sleep(20)

    ssetup(endpointExchange, 'dell.cpsd.endpoint.discovered')

    # perform initial registration
    regData1 = {"ID": "duplicateService1", "Name": "duplicateService","Address": "3.3.3.3", "Port": 300,
                "Tags": ["duplicate1"], "Check": {"HTTP": rabbiturl, "Interval": "2s"}}
    status_code = execRegisterService(regData1)
    assert status_code == 200, "The Register Service task was unsuccessful"

    data_check = verifyRegisterServiceSuccess("duplicateService", "duplicateService1", "3.3.3.3", "duplicate1")
    assert data_check == "Success", "The new Service is not correctly registered in Consul"

    event = verifyEventOnBus(rabbitHost, endpointExchange, 'dell.cpsd.endpoint.discovered')

    if 'duplicateService' not in event['endpoint']['type']:
        errors_list.append("Service Name on the AMQP Bus is incorrect")
    if '3.3.3.3' not in event['endpoint']['instances'][0]['url']:
        errors_list.append("Service Address on the AMQP Bus is incorrect")
    if 'duplicate1' not in event['endpoint']['instances'][0]['tags'][0]:
        errors_list.append("Service Tag on the AMQP Bus is incorrect")

    assert not errors_list

    time.sleep(20)    # necessary whilst ER uses pollinginstead of 'watch'

    errors_list = []

    # add a second service, duplicate name
    ssetup(endpointExchange, 'dell.cpsd.endpoint.discovered')
    regData2 = {"ID": "duplicateService2", "Name": "duplicateService","Address": "4.4.4.4", "Port": 301,
                "Tags": ["duplicate2"], "Check": {"HTTP": rabbiturl, "Interval": "2s"}}
    status_code = execRegisterService(regData2)
    assert status_code == 200, "The Register Service task was unsuccessful"

    data_check = verifyRegisterServiceSuccess("duplicateService", "duplicateService2", "4.4.4.4", "duplicate2")
    assert data_check == "Success", "The new Service is not correctly registered in Consul"

    # april 4th - 2 events are recieved when second service added. The first indicates a change to first service
    # we don't examine the first.
    # the second details the second service added, that is the one that we check
    RMQVerifyEventTest()
    event = verifyEventOnBus(rabbitHost, endpointExchange, 'dell.cpsd.endpoint.discovered')


    if 'duplicateService' not in event['endpoint']['type']:
        errors_list.append("Service Name on the AMQP Bus is incorrect")
    if '3.3.3.3' not in event['endpoint']['instances'][0]['url']:
        errors_list.append("Service Address on the AMQP Bus is incorrect")
    if '4.4.4.4' not in event['endpoint']['instances'][1]['url']:
        errors_list.append("Service Address on the AMQP Bus is incorrect")
    if 'duplicate1' not in event['endpoint']['instances'][0]['tags'][0]:
        errors_list.append("Service Tag on the AMQP Bus is incorrect")
    if 'duplicate2' not in event['endpoint']['instances'][1]['tags'][0]:
        errors_list.append("Service Tag on the AMQP Bus is incorrect")

    assert not errors_list

    # cleanup("duplicateService1")
    # cleanup("duplicateService2")
    time.sleep(200)     # necessary whilst ER uses pollinginstead of 'watch'

# # **************************************************************************************

@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_deRegisterServiceSuccess():
    # This test verifies that deregistering a service at Consul prompts the Endpoint Registry to publish
    # an endpoint.unavailable event
    cleanup(new_service_id)
    ssetup(endpointExchange, 'dell.cpsd.endpoint.discovered')

    time.sleep(20)

    # perform initial registration so we have a service to deregister
    status_code = execRegisterService(regData)
    event_check = verifyEventOnBus(rabbitHost, endpointExchange, "dell.cpsd.endpoint.discovered")
    assert status_code == 200, "The Register Service task was unsuccessful"

    time.sleep(20)     # necessary whilst ER uses pollinginstead of 'watch'

    # setup a test queue for endpoint.unavailable
    ssetup(endpointExchange, 'dell.cpsd.endpoint.unavailable')
    time.sleep(40)     # necessary whilst ER uses pollinginstead of 'watch'
    status_code = execDeRegisterService(new_service_id)
    assert status_code == 200, "The deRegister Service task was unsuccessful"

    # verify with Consul that the service is no longer listed
    data_check = verifyServiceNotRegistered(new_service_id)
    assert data_check == "True", "The Service is incorrectly still registered in Consul"

    event = verifyEventOnBus(rabbitHost, endpointExchange, "dell.cpsd.endpoint.unavailable")
    assert new_service_name in event['type'],        "Service Name on the AMQP Bus is incorrect"

    #cleanup(new_service_id)
    time.sleep(20)     # necessary whilst ER uses pollinginstead of 'watch'

#  **************************************************************************************

@pytest.mark.core_services_mvp_extended
def test_deregisterOneOfTwoSameServices():
    # This test verifies what happens if there is a service with 2 instances registered and
    # one of those services deregisters. An 'endpoint.discovered' event is published listing just details of the
    # remaining instance

    errors_list = []
    cleanup("duplicateService1")
    cleanup("duplicateService2")
    ssetup(endpointExchange, 'dell.cpsd.endpoint.discovered')

    # perform initial registration
    regData1 = {"ID": "duplicateService1", "Name": "duplicateService","Address": "3.3.3.3", "Port": 300,
                "Tags": ["duplicate1"], "Check": {"HTTP": rabbiturl, "Interval": "2s"}}
    status_code = execRegisterService(regData1)
    event_check = verifyEventOnBus(rabbitHost, endpointExchange, 'dell.cpsd.endpoint.discovered')
    assert status_code == 200, "The Register Service task was unsuccessful"

    time.sleep(12)     # necessary whilst ER uses pollinginstead of 'watch'

    # add a second service, duplicate name
    ssetup(endpointExchange, 'dell.cpsd.endpoint.discovered')
    regData2 = {"ID": "duplicateService2", "Name": "duplicateService","Address": "4.4.4.4", "Port": 402,
                "Tags": ["duplicate2"], "Check": {"HTTP": rabbiturl, "Interval": "2s"}}
    status_code = execRegisterService(regData2)
    event_check = verifyEventOnBus(rabbitHost, endpointExchange, 'dell.cpsd.endpoint.discovered')
    assert status_code == 200, "The Register Service task was unsuccessful"

    time.sleep(12)     # necessary whilst ER uses pollinginstead of 'watch'

    # deregister one of the services
    ssetup(endpointExchange, 'dell.cpsd.endpoint.discovered')
    status_code = execDeRegisterService("duplicateService1")
    assert status_code == 200, "The deRegister Service task was unsuccessful"

    data_check = verifyServiceNotRegistered("duplicateService1")
    assert data_check == "True", "The Service is incorrectly still registered in Consul"

    event = verifyEventOnBus(rabbitHost, endpointExchange, 'dell.cpsd.endpoint.discovered')

    if 'duplicateService' not in event['endpoint']['type']:
        errors_list.append("Service Name on the AMQP Bus is incorrect")
    if '4.4.4.4' not in event['endpoint']['instances'][0]['url']:
        errors_list.append("Service Address on the AMQP Bus is incorrect")
    if 'duplicate2' not in event['endpoint']['instances'][0]['tags'][0]:
        errors_list.append("Service Tag on the AMQP Bus is incorrect")

    assert not errors_list

    data_check = verifyRegisterServiceSuccess("duplicateService", "duplicateService2", "4.4.4.4", "duplicate2")
    assert data_check == "Success", "The remaining Service, duplicate2, should still be registered in Consul"

    cleanup("duplicateService1")
    cleanup("duplicateService2")

    #time.sleep(10)     # necessary whilst ER uses pollinginstead of 'watch'

# # *****************************************************************************************************

@pytest.mark.core_services_mvp_extended
def test_deregisterTwoOfTwoSameServices():
    # This test verifies what happens when all instances of a service (in this case 2) are deregistered
    # An 'endpoint.unavailable' event is expected listing the service.

    errors_list = []
    cleanup("duplicateService1")
    cleanup("duplicateService2")
    ssetup(endpointExchange, 'dell.cpsd.endpoint.discovered')

    # perform initial registration to setup the first instance
    regData1 = {"ID": "duplicateService1", "Name": "duplicateService", "Address": "3.3.3.3", "Port": 300,
                "Tags": ["duplicate1"], "Check": {"HTTP": rabbiturl, "Interval": "2s"}}
    status_code = execRegisterService(regData1)
    event_check = verifyEventOnBus(rabbitHost, endpointExchange, 'dell.cpsd.endpoint.discovered')
    assert status_code == 200, "The Register Service task was unsuccessful"

    time.sleep(12)

    # add a second instance, duplicate name
    ssetup(endpointExchange, 'dell.cpsd.endpoint.discovered')
    regData2 = {"ID": "duplicateService2", "Name": "duplicateService","Address": "4.4.4.4", "Port": 403,
                "Tags": ["duplicate2"], "Check": {"HTTP": rabbiturl, "Interval": "2s"}}
    status_code = execRegisterService(regData2)
    event_check = verifyEventOnBus(rabbitHost, endpointExchange, 'edell.cpsd.endpoint.discovered')
    assert status_code == 200, "The Register Service task was unsuccessful"

    time.sleep(12)     # necessary whilst ER uses pollinginstead of 'watch'

    # deregister instance 1
    ssetup(endpointExchange, 'dell.cpsd.endpoint.discovered')
    status_code = execDeRegisterService("duplicateService1")
    assert status_code == 200, "The deRegister Service task was unsuccessful for duplicateService1"
    data_check = verifyServiceNotRegistered("duplicateService1")
    assert data_check == "True", "The Service is incorrectly still registered in Consul"
    event = verifyEventOnBus(rabbitHost, endpointExchange, 'dell.cpsd.endpoint.discovered')

    if 'duplicateService' not in event['endpoint']['type']:
        errors_list.append("Service Name on the AMQP Bus is incorrect")
    if '4.4.4.4' not in event['endpoint']['instances'][0]['url']:
        errors_list.append("Service Address on the AMQP Bus is incorrect")
    if 'duplicate2' not in event['endpoint']['instances'][0]['tags'][0]:
        errors_list.append("Service Tag on the AMQP Bus is incorrect")

    assert not errors_list

    time.sleep(10)     # necessary whilst ER uses pollinginstead of 'watch'

    # deregisterinstance 2
    ssetup(endpointExchange, 'dell.cpsd.endpoint.unavailable')
    status_code = execDeRegisterService("duplicateService2")
    assert status_code == 200, "The deRegister Service task was unsuccessful for duplicateService2"
    data_check = verifyServiceNotRegistered("duplicateService2")
    assert data_check == "True", "The Service is incorrectly still registered in Consul"
    event = verifyEventOnBus(rabbitHost, endpointExchange, 'dell.cpsd.endpoint.unavailable')
    assert "duplicateService" in event['type'],        "Service Name on the AMQP Bus is incorrect"

    cleanup("duplicateService1")
    cleanup("duplicateService2")

# #
# *****************************************************************************************************
#  Helper functions


def ssetup(e,r):
    # clean system required .. delete any lingering testQueue and bind a new testQueue
    af_support_tools.rmq_delete_queue(rabbitHost,"5672", "test", "test", "testQueue")
    time.sleep(3)
    af_support_tools.rmq_bind_queue(rabbitHost,
                                    port="5672", rmq_username="test", rmq_password="test",
                                    queue='testQueue',
                                    exchange=e,
                                    routing_key=r)
    time.sleep(3)
    return None


def execRegisterService(apidata):
    # request Consul to register a new service
    apipath = "/v1/agent/service/register"
    apiheaders = {"content-type": "application/json"}
    url = 'http://' + cohost + ':8500' + apipath
    resp = requests.put(url, data=json.dumps(apidata), headers = apiheaders)
    return resp.status_code


def verifyRegisterServiceSuccess(service_name, service_id, service_host, service_tag_1):
    # check the contents stored for the service in Consul
    apipath = "/v1/agent/services"
    url = 'http://' + cohost + ':8500' + apipath
    resp = requests.get(url)
    data = json.loads(resp.text)
    assert service_name in data[service_id]['Service']
    assert service_id in data[service_id]['ID']
    assert service_host in data[service_id]['Address']
    assert service_tag_1 in data[service_id]['Tags']
    return "Success"


def verifyServiceNotRegistered(service_id):
    # check the contents stored for the service in Consul
    apipath = "/v1/agent/services"
    url = 'http://' + cohost + ':8500' + apipath
    resp = requests.get(url)
    data = json.loads(resp.text)
    assert service_id not in data, "The Service should not be registered at this time"
    return "True"


def verifyHealthCheckSuccess(service_name):
    # check the contents stored for the health check associated with new service
    apipath = "/v1/health/checks/" + new_service_name
    url = 'http://' + cohost + ':8500' + apipath
    resp = requests.get(url)
    data = json.loads(resp.text)
    print(data[0]['Name'])
    assert service_name in data[0]['Name']
    assert "200 OK" in data[0]['Output']
    return "Success"


def execDeRegisterService(serviceID):
    # deregister the service at consul
    apipath = "/v1/agent/service/deregister/" + serviceID
    url = 'http://' + cohost + ':8500' + apipath
    resp = requests.put(url)
    return resp.status_code


def cleanup(service_id):
    # deregister the service at Consul ?
    execDeRegisterService(service_id)
    time.sleep(10)


def verifyEventOnBus(rmqaddress, exchange, route):
    global ipaddress
    ipaddress = rmqaddress
    global eventroute
    eventroute = route

    # cleanup any lingering queues from previous testing
    # cleanup()

    # Call the function to create your test queues.
    # bindQueues(exchange, route)
    # wait for the event in case it has not yet been broadcast
    # waitForMsg()
    # now consume the event
    event = RMQVerifyEventTest()

    # teardown the queue
    #Qcleanup()

    return event


def RMQVerifyEventTest():
    # Consume the RMQ Event message (if one is expected)
    return_message = ""
    waitForMsg()
    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='testQueue')
    if return_message :
        # Convert the returned message to json format and run asserts on the expected output.
        return_event = json.loads(return_message, encoding='utf-8')
    else :
        return_event = ""

    # check that the payload is not empty

    time.sleep(1)

    return return_event


def bindQueues(exchangeName, routeName):
    # Create & bind the test queues
    af_support_tools.rmq_bind_queue(host=ipaddress,
                                    port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                    queue='testQueue',
                                    exchange=exchangeName,
                                    routing_key=routeName)


def Qcleanup():
    # Delete the test queues
    print('Cleaning up...')
    af_support_tools.rmq_delete_queue(host=ipaddress, port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                      queue='testQueue')


def waitForMsg():
    # This function keeps looping until a message is in the specified queue. We do need it to timeout and throw an error
    # if a message never arrives. Once a message appears in the queue the function is complete and main continues.

    # The length of the queue, it will start at 0 but as soon as we get a response it will increase
    q_len = 0

    # Represents the number of seconds that have gone by since the method started
    timeout = 0

    # Max number of seconds to wait
    max_timeout = 40

    # Amount of time in seconds that the loop is going to wait on each iteration
    sleeptime = 1

    while q_len < 1:
        time.sleep(sleeptime)
        timeout += sleeptime

        q_len = af_support_tools.rmq_message_count(host=ipaddress,
                                                   port=port,
                                                   rmq_username=rmq_username,
                                                   rmq_password=rmq_password,
                                                   queue='testQueue')

        if timeout > max_timeout:
            print('ERROR: Message took too long to return. Something is wrong')
            #Qcleanup()
            break
