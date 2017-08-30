#!/usr/bin/python
# Copyright (c) 2017 Dell Inc. or its subsidiaries.  All Rights Reserved.
# Dell EMC Confidential/Proprietary Information
#
import af_support_tools
import pytest

################################################
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

################################################
@pytest.mark.parametrize('service_name',["cpsd-node-expansion-ui", "symphony-engineering-standards-service", "symphony-dne-paqx",
                          "symphony-node-discovery-paqx", "symphony-vcenter-adapter-service",
                          "cpsd-scaleio-adapter-service", "symphony-rackhd-adapter-service", "cpsd-api-gateway"])
@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_dne_services_up(service_name, setup):
    """
    Title: Verify DNE services containers are UP
    Description: This test verifies that each DNE service containers are up
    Params: List of DNE service names
    Returns: None

    """
    print(test_dne_services_up.__doc__)

    err = []

    # for service_name in dne_dir:
    sendcommand = "docker ps --filter name=" + service_name + "  --format '{{.Status}}' | awk '{print $1}'"
    my_return_status = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                         password=setup['password'],
                                                         command=sendcommand, return_output=True)
    my_return_status = my_return_status.strip()

    if "Up" not in my_return_status:
        err.append(service_name + " not running")

    print('\n' + service_name + ' Docker Container is:', my_return_status, '\n')
    assert my_return_status == 'Up', (service_name + " not running")

    assert not err


#"symphony-node-discovery-paqx", This has been removed as there is a defect open for it
@pytest.mark.parametrize('service_name',["symphony-engineering-standards-service", "symphony-dne-paqx",
                          "symphony-vcenter-adapter-service",
                          "cpsd-scaleio-adapter-service", "symphony-rackhd-adapter-service"])
@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_dne_amqpconnection_tls_port(service_name, setup):
    """
    Title: Verify DNE services containers are connected to Rabbitmq
    Description: This test verifies that each DNE service container is connected to rabbitmq
    Params: List of DNE service names
    Returns: None

    """
    print(test_dne_amqpconnection_tls_port.__doc__)

    err = []

    # Verify services are connected to port 5671 and only once
    cmd_1 = "docker exec " + service_name + " netstat -an 2>&1 | grep 5671 | awk '{print $6}'"
    response1 = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                  password=setup['password'],
                                                  command=cmd_1, return_output=True)
    response1 = response1.splitlines()
    response_list_5671 = [response1]

    assert len(response1) == 1, 'Error: More than one connection to Port 5671'

    if any("ESTABLISHED" in s for s in response_list_5671):
        print(service_name + ": Rabbitmq connected within the container on Port 5671")
    else:
        err.append(service_name + " not connected to rabbitmq 5671")


    # Verify services are NOT connected to port 5672
    cmd2 = "docker exec " + service_name + " netstat -an 2>&1 | grep 5672 | awk '{print $6}'"
    response2 = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                  password=setup['password'],
                                                  command=cmd2, return_output=True)
    response2 = response2.splitlines()
    response_list_5672 = [response2]

    if any("ESTABLISHED" in s for s in response_list_5672):
        err.append(service_name + " is connected to rabbitmq on Port 5672")
    else:
        print(service_name + ": Not connected to rabbitmq 5672")

    assert not err


#"cpsd-node-expansion-ui", This is removed as there is a defcet open against it
@pytest.mark.parametrize('service_name',["symphony-engineering-standards-service", "symphony-dne-paqx",
                          "symphony-node-discovery-paqx", "symphony-vcenter-adapter-service",
                          "cpsd-scaleio-adapter-service", "symphony-rackhd-adapter-service", "cpsd-api-gateway"])
@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_dne_service_stop_start(service_name, setup):
    """
        Title: Verify Core services containers can be restarted with docker stop/start
        Description: This test verifies that each core service container can restart
        Params: List of Core service names
        Returns: None

    """
    print(test_dne_service_stop_start.__doc__)

    err = []


    sendcommand = "docker ps --filter name=" + service_name + "  --format '{{.Status}}' | awk '{print $1}'"
    my_return_status = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                         password=setup['password'],
                                                         command=sendcommand, return_output=True)
    if "Up" not in my_return_status:
        err.append(service_name + " not running")
    else:

        cmd = "docker stop " + service_name
        response = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                     password=setup['password'],
                                                     command=cmd, return_output=False)

        cmd2 = "docker ps -a --filter name=" + service_name + "  --format '{{.Status}}' | awk '{print $1}'"
        response2 = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                      password=setup['password'],
                                                      command=cmd2, return_output=True)
        if "Exited" not in response2:
            err.append(service_name + " has not stopped or has been removed")

    sendcommand = "docker ps -a --filter name=" + service_name + "  --format '{{.Status}}' | awk '{print $1}'"
    my_return_status = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                         password=setup['password'],
                                                         command=sendcommand, return_output=True)
    if "Exited" in my_return_status:
        cmd4 = "docker start " + service_name
        response = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                     password=setup['password'],
                                                     command=cmd4, return_output=False)

        cmd3 = "docker ps -a --filter name=" + service_name + "  --format '{{.Status}}' | awk '{print $1}'"
        response3 = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                      password=setup['password'],
                                                      command=cmd3, return_output=True)
    if "Up" not in response3:
        err.append(service_name + " has not started or has been removed")

    assert not err


@pytest.mark.parametrize('directory',["vcenter-adapter", "rackhd-adapter", "dne-paqx", "ess", "node-discovery-paqx"])
@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_dne_services_log_files_exceptions(directory, setup):
    """
    Description     :       This method tests that the ESS log files exist and contain no Exceptions.
                            It will fail:
                                If the the error and/or info log files do not exists
                                If the error log file contains AuthenticationFailureException, RuntimeException or NullPointerException.
    Parameters      :       None
    Returns         :       None
    """

    filePath = '/opt/dell/cpsd/'+ directory +'/logs/'


    infoLogFile = directory+'-info.log'

    # Need this exception as the node-discovery-paqx log file format is different to the others
    if filePath == '/opt/dell/cpsd/node-discovery-paqx/logs/':
        infoLogFile = 'node-discovery-info.log'

    # Verify the log files exist
    sendcommand = 'ls ' + filePath
    my_return_status = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                         password=setup['password'],
                                                         command=sendcommand, return_output=True)
    error_list = []

    if (infoLogFile not in my_return_status):
        error_list.append(infoLogFile)

    excep1 = 'java.net.SocketException: Socket is closed'
    excep2 = 'AuthenticationFailureException'

    # Verify there are no SocketException errors
    sendcommand = 'cat ' + filePath + infoLogFile + ' | grep \'' + excep1 + '\''
    my_return_status = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                         password=setup['password'],
                                                         command=sendcommand, return_output=True)

    if (excep1 in my_return_status):
        error_list.append(excep1)

    # Verify there are no AuthenticationFailureException errors
    sendcommand = 'cat ' + filePath + infoLogFile + ' | grep \'' + excep2 + '\''
    my_return_status = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                         password=setup['password'],
                                                         command=sendcommand, return_output=True)

    if (excep2 in my_return_status):
        error_list.append(excep2)


    assert not error_list, 'Log file missing'

    print('Valid log files exist')