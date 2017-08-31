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
    ''' Fixture to get names of service containers'''
    err = []
    core_dir = ["common-ui", "consul", "hal-orchestrator-service", "rabbitmq", "identity-service",
               "capability-registry-service", "endpoint-registration-service", "vault", "system-definition-service"]
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



@pytest.mark.common_ui_mvp
def test_common_ui_install(setup):
    """
    Title: Verify that the common-ui rpm is installed correctly
    Description: This test verifies that the common-ui service is installed correctly
    Params: List of service names
    Returns: None
    """
    print(test_common_ui_install.__doc__)

    err = []

    common_ui = "dell-cpsd-common-ui"

    sendcommand = "yum install -y " + common_ui
    my_return_status = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                             password=setup['password'],
                                                             command=sendcommand, return_output=True)

    rpmcheck_ui = af_support_tools.check_for_installed_rpm(host=setup['IP'], username=setup['user'],
                                                             password=setup['password'], rpm_name=common_ui)

    if rpmcheck_ui != True:
        err.append(common_ui+ " did not install properly")
    assert not err


@pytest.mark.common_ui_mvp
def test_allservicesup(core_services, setup):
    """
        Title: Verify that the common-ui service and it's dependent containers are installed correctly
        Description: This test verifies that the common-ui and dependent service is installed correctly
        Params: List of service names
        Returns: None
    """
    print(test_allservicesup.__doc__)

    err = []
    for service in core_services:

        sendcommand = "docker ps --filter name=" + service + "  --format '{{.Status}}' | awk '{print $1}'"
        my_return_status = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                             password=setup['password'],
                                                             command=sendcommand, return_output=True)

        if "Up" not in my_return_status:
            err.append(service + " not running")
    assert not err


@pytest.mark.common_ui_mvp
def test_common_ui_serviceremove(core_services, setup):
    """
    Title: Verify that the common-ui service and it's dependent containers are installed correctly
    Description: This test verifies that the common-ui service is installed correctly
    Params: List of service names
    Returns: None
    """
    err = []
    core_rm_ui=[]

    sendcommand = "yum remove -y dell-cpsd-common-ui"
    my_return_status = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                             password=setup['password'],
                                                             command=sendcommand, return_output=True)
    for service in core_services:
        core_rm_ui.append(service)

    ui = core_rm_ui.pop(0)
    print ('common UI dell ' +ui)

    sendcommand = "docker ps --filter name=" + ui + "  --format '{{.Status}}' | awk '{print $1}'"
    my_return_status = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                             password=setup['password'],
                                                             command=sendcommand, return_output=True)

    if "Up" not in my_return_status:
        print (ui + ' is stopped')
    else:
        err.append(ui + " is still running")
    assert not err

    # ## 'dell-cpsd-common-ui' service is stopped at this point ans the list 'core_rm_ui' won't have this service any more in it
    #
    # ## check if all other services are still running
    for service in core_rm_ui:

        sendcommand = "docker ps --filter name=" + service + "  --format '{{.Status}}' | awk '{print $1}'"
        my_return_status = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                             password=setup['password'],
                                                             command=sendcommand, return_output=True)

        if "Up" not in my_return_status:
            err.append(service + " not running")
    assert not err
