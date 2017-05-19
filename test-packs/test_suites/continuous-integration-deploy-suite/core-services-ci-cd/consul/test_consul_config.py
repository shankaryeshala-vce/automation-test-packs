#!/usr/bin/python
# Author: cullia
# Revision: 1.0
# Code Reviewed by:
# Description: Testing the Consul Container.

import af_support_tools
import pytest
import json
import time
import requests
import os


##############################################################################################

@pytest.fixture(scope="module", autouse=True)
def load_test_data():

    # Set config ini file name
    global env_file
    env_file = 'env.ini'


    # Test VM Details
    global ipaddress
    ipaddress = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='hostname')
    global cli_username
    cli_username = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='username')
    global cli_password
    cli_password = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='password')


    # RMQ Details
    global rmq_username
    rmq_username = 'guest'
    global rmq_password
    rmq_password = 'guest'
    global port
    port = 5672

##############################################################################################

@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_consul_servicerunning():

    print('\n* * * Testing Consul on system:', ipaddress, '* * *\n')

    service_name = 'consul'

    sendCommand = "docker ps --filter name=" + service_name + "  --format '{{.Status}}' | awk '{print $1}'"
    my_return_status = af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password, command=sendCommand, return_output=True)
    my_return_status=my_return_status.strip()
    print('\nDocker Container is:', my_return_status,'\n')
    assert my_return_status == 'Up', (service_name + " not running")


@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_consul_verify_vault():

    verifyServiceInConsulAPI('vault')


@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_consul_verify_apigateway():

    verifyServiceInConsulAPI('api-gateway')


@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_consul_verify_dne_paqx():

    verifyServiceInConsulAPI('dne-paqx')



##############################################################################################


def verifyServiceInConsulAPI(service):

    url_body = ':8500/v1/agent/services'
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

        serviceToCheck = '"Service": "'+service+'"'
        assert serviceToCheck in the_response, ('ERROR:', service, 'is not in Consul\n')
        print(service, 'Registered in consul')

        if serviceToCheck in the_response:
            verifyServiceStatusInConsulAPI(service)



def verifyServiceStatusInConsulAPI(service):

    url_body = ':8500/v1/health/checks/'+service
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

        serviceStatus = '"Status": "passing"'
        assert serviceStatus in the_response, ('ERROR:', service, 'is not Passing in Consul\n')
        print(service, 'Status = Passing in consul\n\n')


#######################################################################################################################
