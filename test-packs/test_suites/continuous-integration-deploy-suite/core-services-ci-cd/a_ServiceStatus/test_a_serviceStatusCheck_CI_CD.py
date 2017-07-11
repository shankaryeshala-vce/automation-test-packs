#!/usr/bin/python
# Copyright (c) 2017 Dell Inc. or its subsidiaries.  All Rights Reserved.
# Dell EMC Confidential/Proprietary Information
#
import af_support_tools
import pytest


@pytest.fixture()
def setup():
    parameters = {}
    env_file = 'env.ini'
    ipaddress = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS',
                                                          property='hostname')
    parameters['IP'] = ipaddress
    cli_user = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS',
                                                         property='username')
    parameters['user'] = cli_user
    cli_password = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS',
                                                             property='password')
    parameters['password'] = cli_password
    return parameters


@pytest.fixture
def core_services(setup):
    ''' Fixture to get names of core service containers'''
    core_dir = ["system-definition-service", "credentials", "hal-orchestrator-service", "identity-service",
                "capability-registry-service", "endpoint-registration-service", "hal-mediation-services",
                "hdp-poweredge-compute", "rackhd-adapter", "hal-data-provider-vcenter"]
    core_list = []

    for service in core_dir:
        sendcommand_core = "cat /opt/dell/cpsd/" + service + "/install/docker-compose.yml | grep container_name| cut -f 2 -d ':'"
        my_return_status_core = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                                  password=setup['password'], command=sendcommand_core,
                                                                  return_output=True)
        containerName = my_return_status_core.strip()
        num_of_services = containerName.count('\n')
        if num_of_services > 1:
            containerName = my_return_status_core.splitlines()
            for container in map(str.strip, containerName):
                core_list.append(container)
        else:
            core_list.append(containerName)

    return core_list


@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_core_serviceup(core_services, setup):
    """
    Title: Verify Core services containers are UP
    Description: This test verifies that each core service container is up
    Params: List of Core service names
    Returns: None

    """
    print(test_core_serviceup.__doc__)

    err = []
    for service in core_services:

        sendcommand = "docker ps --filter name=" + service + "  --format '{{.Status}}' | awk '{print $1}'"
        my_return_status = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                             password=setup['password'],
                                                             command=sendcommand, return_output=True)

        if "Up" not in my_return_status:
            err.append(service + " not running")
    assert not err


@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_coreamqpconnection(core_services, setup):
    """
    Title: Verify Core services containers are connected to Rabbitmq
    Description: This test verifies that each core service container is connected to rabbitmq
    Params: List of Core service names
    Returns: None

    """
    print(test_coreamqpconnection.__doc__)

    err = []
    for service in core_services:

        cmd_1 = "docker exec " + service + " netstat -an 2>&1 | grep 5672 | awk '{print $6}'"
        response1 = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                      password=setup['password'],
                                                      command=cmd_1, return_output=True)
        response1 = response1.splitlines()
        if "ESTABLISHED" in response1:
            print(service + " connected on port 5672")

        cmd2 = "docker exec " + service + " netstat -an 2>&1 | grep 5671 | awk '{print $6}'"
        response2 = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                      password=setup['password'],
                                                      command=cmd2, return_output=True)
        response2 = response2.splitlines()
        if "ESTABLISHED" in response2:
            print(service + " connected on port 5671")

        response_list = [response1, response2]

        if any("ESTABLISHED" in s for s in response_list):
            print(service + " :Rabbitmq connected within the container")
        else:
            err.append(service + " not connected to rabbitmq")

    assert not err


@pytest.mark.skip(reason="Disabled until every service uses port 5671")
@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_coreamqptls(core_services, setup):
    """
    Title: Verify Core services containers are connected to TLS port for Rabbit
    Description: This test verifies that each core service container is connected to rabbitmq TLS Port
    Params: List of Core service names
    Returns: None

    """
    print(test_coreamqptls.__doc__)

    err = []
    for service in core_services:

        sendcommand_amqp = "docker exec " + service + " netstat -an 2>&1 | grep 5671 | awk '{print $6}'"
        response = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                     password=setup['password'],
                                                     command=sendcommand_amqp, return_output=True)
        if "ESTABLISHED" not in response:
            err.append(service + " Rabbit not connected on TLS Port")

    assert not err


#@pytest.mark.skip(reason="Needs work")
@pytest.mark.core_services_mvp_extended
def test_core_stop(core_services, setup):
    """
        Title: Verify Core services containers can be restarted with docker stop/start
        Description: This test verifies that each core service container can restart
        Params: List of Core service names
        Returns: None

    """
    print(test_core_stop.__doc__)

    err = []

    for service in core_services:
        sendcommand = "docker ps --filter name=" + service + "  --format '{{.Status}}' | awk '{print $1}'"
        my_return_status = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                             password=setup['password'],
                                                             command=sendcommand, return_output=True)
        if "Up" not in my_return_status:
            err.append(service + " not running")
        else:

            cmd = "docker stop " + service
            response = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                     password=setup['password'],
                                                     command=cmd, return_output=False)
            assert response == 0, 'docker stop did not execute correctly on ' + service

            cmd2 = "docker ps -a --filter name=" + service + "  --format '{{.Status}}' | awk '{print $1}'"
            response2 = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                      password=setup['password'],
                                                      command=cmd2, return_output=True)
            if "Exited" not in response2:
                err.append(service + " has not stopped or has been removed")

    assert not err


#@pytest.mark.skip(reason="Needs work")
@pytest.mark.core_services_mvp_extended
def test_core_start(core_services, setup):
    """
            Title: Verify Core services containers can be restarted with docker stop/start
            Description: This test verifies that each core service container can restart
            Params: List of Core service names
            Returns: None

        """
    print(test_core_start.__doc__)

    err = []

    for service in core_services:

        sendcommand = "docker ps --filter name=" + service + "  --format '{{.Status}}' | awk '{print $1}'"
        my_return_status = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                             password=setup['password'],
                                                             command=sendcommand, return_output=True)
        if "Up" not in my_return_status:


            cmd4 = "docker start " + service
            response = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                     password=setup['password'],
                                                     command=cmd4, return_output=False)
            assert response == 0, 'docker start did not execute correctly' + service

            cmd3 = "docker ps -a --filter name=" + service + "  --format '{{.Status}}' | awk '{print $1}'"
            response3 = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                      password=setup['password'],
                                                      command=cmd3, return_output=True)
        if "Up" not in response3:
            err.append(service + " has not started or has been removed")

    assert not err
