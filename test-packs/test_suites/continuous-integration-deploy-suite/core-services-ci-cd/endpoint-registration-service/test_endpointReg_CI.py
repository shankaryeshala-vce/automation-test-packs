#!/usr/bin/python
# Author: russed5
# Revision: 1.0
# Code Reviewed by:
# Description: see https://wiki.ent.vce.com/display/VSE/Endpoint+Registry+Testing

import pytest
import requests
import json
import time
import af_support_tools

try:
    env_file = 'env.ini'
    ipaddress = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='hostname')

except:
    print('Possible configuration error')

#ipaddress = "10.3.62.137"

new_service_name = "testService"
new_service_id = "testService1"
new_service_host = ipaddress
new_service_tag_1 = "testTag1"
new_service_tag_2 = "testTag2"

crhost = ipaddress      # capabilities registry host
cohost = ipaddress      # consul host
rabbitHost = ipaddress  # rabbitmq host
rabbiturl = "http://" + rabbitHost + ":15672"

capabilitiesExchange = "exchange.dell.cpsd.hdp.capability.registry.control"
endpointExchange = "exchange.dell.cpsd.endpoint.registration.event"

rmq_username = 'test'
rmq_password = 'test'

port = 5672

# *******************************************************************************************
# the payload data used to register services with consul

regData = {"ID": new_service_id, "Name": new_service_name, "Address": new_service_host, \
             "Tags": [ new_service_tag_1 ] }

# *******************************************************************************************
@pytest.mark.core_services_mvp
def test_registerServiceSuccess():
    af_support_tools.mark_defect(defect_id='DE12419', user_id='toqeer.akhtar@vce.com', comments='hal layer')
    # This test verifies that a succful service register in Consul prompts the Endpoint Registry
    # to publish an endpoint.discovered event to the AMQP bus

    # setup, delete any lingering AMQP testQueue and create a new one before any messaging starts
    ssetup(endpointExchange, 'dell.cpsd.endpoint.discovered')

    status_code = execRegisterService(regData)
    assert status_code == 200, "The Register Service task was unsuccessful"

    # double-check in consul if the registration was successful
    data_check = verifyRegisterServiceSuccess(new_service_name, new_service_id, new_service_host, new_service_tag_1)
    assert data_check == "Success", "The new Service is not correctly registered in Consul"

    # check on the AMQP bus that a discovered endpoint event was raised with correct payload
    event = verifyEventOnBus(rabbitHost, endpointExchange, "dell.cpsd.endpoint.discovered")


    assert new_service_name in event['endpoint']['type'],                     "Service Name on the AMQP Bus is incorrect"
    assert new_service_host in event['endpoint']['instances'][0]['url'],      "Service Address on the AMQP Bus is incorrect"
    assert new_service_tag_1 in event['endpoint']['instances'][0]['tags'][0], "Service Tag on the AMQP Bus is incorrect"

    cleanup(new_service_id)
    time.sleep(30)      # necessary whilst ER uses polling instead of 'watch'

# **************************************************************************************
@pytest.mark.core_services_mvp
def test_deRegisterServiceSuccess():
    af_support_tools.mark_defect(defect_id='DE12419', user_id='toqeer.akhtar@vce.com', comments='hal layer')
    # This test verifies that deregistering a service at Consul prompts the Endpoint Registry to publish
    # an endpoint.unavailable event

    ssetup(endpointExchange, 'dell.cpsd.endpoint.discovered')
    # perform initial registration so we have a service to deregister
    status_code = execRegisterService(regData)
    event_check = verifyEventOnBus(rabbitHost, endpointExchange, "dell.cpsd.endpoint.discovered")

    # setup a test queue for endpoint.unavailable
    ssetup(endpointExchange, 'dell.cpsd.endpoint.unavailable')
    status_code = execDeRegisterService(new_service_id)
    assert status_code == 200, "The deRegister Service task was unsuccessful"

    # verify with Consul that the service is no longer listed
    data_check = verifyServiceNotRegistered(new_service_id)
    assert data_check == "True", "The Service is incorrectly still registered in Consul"

    event = verifyEventOnBus(rabbitHost, endpointExchange, "dell.cpsd.endpoint.unavailable")
    assert new_service_name in event['type'],        "Service Name on the AMQP Bus is incorrect"

    cleanup(new_service_id)
    time.sleep(30)      # necessary whilst ER uses pollinginstead of 'watch'


# *****************************************************************************************************
#  Helper functions

def ssetup(e,r):
    # clean system required .. delete any lingering testQueue and bind a new testQueue
    af_support_tools.rmq_delete_queue(rabbitHost,"5672", "test", "test", "testQueue")
    af_support_tools.rmq_bind_queue(rabbitHost,
                                    port="5672", rmq_username="test", rmq_password="test",
                                    queue='testQueue',
                                    exchange=e,
                                    routing_key=r)
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

    #teardown the queue
    Qcleanup()

    return event

def RMQVerifyEventTest():
    # Consume the RMQ Event message (if one is expected)
    waitForMsg()
    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='testQueue')

    # Convert the returned message to json format and run asserts on the expected output.
    return_json = json.loads(return_message, encoding='utf-8')

    # check that the payload is not empty
    assert return_json
    time.sleep(1)

    return return_json

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
    # This function keeps looping untill a message is in the specified queue. We do need it to timeout and throw an error
    # if a message never arrives. Once a message appears in the queue the function is complete and main continues.

    # The length of the queue, it will start at 0 but as soon as we get a response it will increase
    q_len = 0

    # Represents the number of seconds that have gone by since the method started
    timeout = 0

    # Max number of seconds to wait
    max_timeout = 100

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
            cleanup()
            break


