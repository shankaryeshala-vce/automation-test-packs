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
import af_support_tools

@pytest.mark.daily_status
@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_consul_is_running(hostConnection):
    """
    Test Case Title :       Verify Consul Service is running
    Description     :       This method tests that consul docker container is running
                            It will fail if :
                                The the container is not running
    Parameters      :       none
    Returns         :       None
    """
    print('\n* * * Testing Consul on system:', hostConnection.ipAddress, '* * *\n')

    service_name = 'consul'

    ssh_command = "docker ps --filter name=" + service_name + "  --format '{{.Status}}' | awk '{print $1}'"
    my_return_status = af_support_tools.send_ssh_command(host=hostConnection.ipAddress, username=hostConnection.username,
                                                         password=hostConnection.password,
                                                         command=ssh_command, return_output=True)
    my_return_status = my_return_status.strip()
    print('\nDocker Container is:', my_return_status, '\n')
    assert my_return_status == 'Up', (service_name + " not running")


@pytest.mark.daily_status
@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
@pytest.mark.parametrize("service", ["consul", "vault", "api-gateway"])
def test_service_is_registered_with_consul(hostConnection, service):
    """
    Test Case Title :       Verify Consul is registered with Consul
    Description     :       This method tests that consul is registered in the Consul API http://{SymphonyIP}:8500/v1/agent/services
                            It will fail if :
                                The line 'Service: "consul"' is not present
    Parameters      :       none
    Returns         :       None
    Note            :       It's expected that Consul has no Status so there is no Status test.
    """

    url = 'http://' + hostConnection.ipAddress + ':8500/v1/agent/services'
    print('sending GET request:', url)
    response = requests.get(url)

    # Create the string as it should appear in the API
    service_to_check = '"Service": "' + service + '"'

    assert response.status_code == 200
    assert service_to_check in response.text, ('ERROR:', service, 'is not in Consul\n')


@pytest.mark.daily_status
@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
@pytest.mark.parametrize("service", ["vault", "api-gateway"])
def test_service_status_is_healthy_in_consul(hostConnection, service):
    """
    Test Case Title :       Verify Vault is Passing in Consul
    Description     :       This method tests that vault has a passing status in the Consul API http://{SymphonyIP}:8500/v1/health/checks/vault
                            It will fail if :
                                The line '"Status": "passing"' is not present
    Parameters      :       none
    Returns         :       None
    """

    url = 'http://' + hostConnection.ipAddress + ':8500/v1/health/checks/' + service
    print('GET:', url)

    response = requests.get(url)
    service_status = '"Status": "passing"'

    assert response.status_code == 200
    assert service_status in response.text, ('ERROR:', service, 'is not Passing in Consul\n')
