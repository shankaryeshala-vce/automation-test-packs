#!/usr/bin/python
# Author: cullia
# Revision: 1.1
# Code Reviewed by:
# Description: Testing the Consul Container.
#
# Copyright (c) 2017 Dell Inc. or its subsidiaries.  All Rights Reserved.
# Dell EMC Confidential/Proprietary Information
#
import pytest
import requests
import json
import time
import af_support_tools
import os


##############################################################################################

@pytest.fixture(scope="module", autouse=True)
def load_test_data():
    # Update config ini files at runtime
    my_data_file = os.environ.get('AF_RESOURCES_PATH') + '/continuous-integration-deploy-suite/symphony-sds.properties'
    af_support_tools.set_config_file_property_by_data_file(my_data_file)

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


##############################################################################################

@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_consul_servicerunning():
    """
    Test Case Title :       Verify Consul Service is running
    Description     :       This method tests that consul docker container is running
                            It will fail if :
                                The the container is not running
    Parameters      :       none
    Returns         :       None
    """
    print('\n* * * Testing Consul on system:', ipaddress, '* * *\n')

    service_name = 'consul'

    sendCommand = "docker ps --filter name=" + service_name + "  --format '{{.Status}}' | awk '{print $1}'"
    my_return_status = af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                                         command=sendCommand, return_output=True)
    my_return_status = my_return_status.strip()
    print('\nDocker Container is:', my_return_status, '\n')
    assert my_return_status == 'Up', (service_name + " not running")


@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_consul_verify_Consul_registered():
    """
    Test Case Title :       Verify Consul is registered with Consul
    Description     :       This method tests that consul is registered in the Consul API http://{SymphonyIP}:8500/v1/agent/services
                            It will fail if :
                                The line 'Service: "consul"' is not present
    Parameters      :       none
    Returns         :       None
    Note            :       It's expected that Consul has no Status so there is no Status test.
    """

    service = 'consul'

    url_body = ':8500/v1/agent/services'
    my_url = 'http://' + ipaddress + url_body

    print('GET:', my_url)

    try:
        url_response = requests.get(my_url)
        url_response.raise_for_status()

        # A 200 has been received
        print(url_response)

        the_response = url_response.text

        # Create the sting as it should appear in the API
        serviceToCheck = '"Service": "' + service + '"'

        assert serviceToCheck in the_response, ('ERROR:', service, 'is not in Consul\n')

        print(service, 'Registered in Consul')

    # Error check the response
    except Exception as err:
        # Return code error (e.g. 404, 501, ...)
        print(err)
        print('\n')
        raise Exception(err)


@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_consul_verify_Vault_registered():
    """
    Test Case Title :       Verify Vault is registered with Consul
    Description     :       This method tests that vault is registered in the Consul API http://{SymphonyIP}:8500/v1/agent/services
                            It will fail if :
                                The line 'Service: "vault"' is not present
    Parameters      :       none
    Returns         :       None
    """

    service = 'vault'

    url_body = ':8500/v1/agent/services'
    my_url = 'http://' + ipaddress + url_body

    print('GET:', my_url)

    try:
        url_response = requests.get(my_url)
        url_response.raise_for_status()

        # A 200 has been received
        print(url_response)

        the_response = url_response.text

        # Create the sting as it should appear in the API
        serviceToCheck = '"Service": "' + service + '"'

        assert serviceToCheck in the_response, ('ERROR:', service, 'is not in Consul\n')

        print(service, 'Registered in Consul')

    # Error check the response
    except Exception as err:
        # Return code error (e.g. 404, 501, ...)
        print(err)
        print('\n')
        raise Exception(err)


@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_consul_verify_Vault_status():
    """
    Test Case Title :       Verify Vault is Passing in Consul
    Description     :       This method tests that vault has a passing status in the Consul API http://{SymphonyIP}:8500/v1/health/checks/vault
                            It will fail if :
                                The line '"Status": "passing"' is not present
    Parameters      :       none
    Returns         :       None
    """
    service = 'vault'

    url_body = ':8500/v1/health/checks/' + service
    my_url = 'http://' + ipaddress + url_body

    print('GET:', my_url)

    try:
        url_response = requests.get(my_url)
        url_response.raise_for_status()

        # A 200 has been received
        print(url_response)
        the_response = url_response.text

        serviceStatus = '"Status": "passing"'
        assert serviceStatus in the_response, ('ERROR:', service, 'is not Passing in Consul\n')
        print(service, 'Status = Passing in consul\n\n')

    # Error check the response
    except Exception as err:
        # Return code error (e.g. 404, 501, ...)
        print(err)
        print('\n')
        raise Exception(err)


@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_consul_verify_api_gateway_registered():
    """
    Test Case Title :       Verify api-gateway is registered with Consul
    Description     :       This method tests that api-gateway is registered in the Consul API http://{SymphonyIP}:8500/v1/agent/services
                            It will fail if :
                                The line 'Service: "api-gateway"' is not present
    Parameters      :       none
    Returns         :       None
    """

    service = 'api-gateway'

    url_body = ':8500/v1/agent/services'
    my_url = 'http://' + ipaddress + url_body

    print('GET:', my_url)

    try:
        url_response = requests.get(my_url)
        url_response.raise_for_status()

        # A 200 has been received
        print(url_response)

        the_response = url_response.text

        # Create the sting as it should appear in the API
        serviceToCheck = '"Service": "' + service + '"'

        assert serviceToCheck in the_response, ('ERROR:', service, 'is not in Consul\n')

        print(service, 'Registered in Consul')

    # Error check the response
    except Exception as err:
        # Return code error (e.g. 404, 501, ...)
        print(err)
        print('\n')
        raise Exception(err)


@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_consul_verify_api_gateway_status():
    """
    Test Case Title :       Verify api-gateway is Passing in Consul
    Description     :       This method tests that api-gateway has a passing status in the Consul API http://{SymphonyIP}:8500/v1/health/checks/api-gateway
                            It will fail if :
                                The line '"Status": "passing"' is not present
    Parameters      :       none
    Returns         :       None
    """
    service = 'api-gateway'

    url_body = ':8500/v1/health/checks/' + service
    my_url = 'http://' + ipaddress + url_body

    print('GET:', my_url)

    try:
        url_response = requests.get(my_url)
        url_response.raise_for_status()

        # A 200 has been received
        print(url_response)
        the_response = url_response.text

        serviceStatus = '"Status": "passing"'
        assert serviceStatus in the_response, ('ERROR:', service, 'is not Passing in Consul\n')
        print(service, 'Status = Passing in consul\n\n')

    except Exception as err:
        # Return code error (e.g. 404, 501, ...)
        print(err)
        print('\n')
        raise Exception(err)

##############################################################################################
