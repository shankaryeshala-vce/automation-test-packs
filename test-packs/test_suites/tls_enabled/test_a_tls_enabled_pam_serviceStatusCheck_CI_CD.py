#!/usr/bin/python
# Copyright (c) 2017 Dell Inc. or its subsidiaries.  All Rights Reserved.
# Dell EMC Confidential/Proprietary Information
# Author -Catherine Hurley

import af_support_tools
import pytest

pam = "dell-cpsd-core-pam-service"

@pytest.mark.tls_enabled
def test_pam_uninstall(setup):
    """
    Title: Verify the persistence asset manager service can be uninstalled
    Description: This test verifies that the persistence asset manager can be uninstalled successfully
    Params: dell-cpsd-core-pam-service
    Returns: None

    """

    print(test_pam_install.__doc__)

    err = []


    sendcommand = "yum -y remove " + pam

    af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                             password=setup['password'],
                                                             command=sendcommand, return_output=True)

    rpmcheck_ui = af_support_tools.check_for_installed_rpm(host=setup['IP'], username=setup['user'],
                                                             password=setup['password'], rpm_name=pam)

    if rpmcheck_ui != 0:
        err.append(pam + " did not uninstall properly")
    assert not err



@pytest.mark.tls_enabled
def test_pam_install(setup):
    #this test is working (TW)
    """
    Title: Verify the persistence asset manager service can be installed
    Description: This test verifies that the persistence asset manager can be installed successfully
    Params: List of Core service names
    Returns: None

    """

    print(test_pam_install.__doc__)

    err = []

#    pam = "dell-cpsd-core-pam-service"

    expirecache = "yum clean expire-cache"
    makecache = "yum makecache fast"
    sendcommand = "yum install -y " + pam

    af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                         password=setup['password'],
                                                         command=expirecache, return_output=True)

    af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                         password=setup['password'],
                                                         command=makecache, return_output=True)


    af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                             password=setup['password'],
                                                             command=sendcommand, return_output=True)

    rpmcheck_ui = af_support_tools.check_for_installed_rpm(host=setup['IP'], username=setup['user'],
                                                             password=setup['password'], rpm_name=pam)




    if rpmcheck_ui != True:
        err.append(pam + " did not install properly")
    assert not err

@pytest.mark.tls_enabled
def test_pam_serviceup(setup):
    """
    Title: Verify the PAM services containers are UP
    Description: This test verifies that the pam container is up
    Params: List of Core service names
    Returns: None

    """

    print(test_pam_serviceup.__doc__)
    assert pam, "container name not found"

    sendcommand = "docker ps --filter name=" + pam + "  --format '{{.Status}}' | awk '{print $1}'"

    print(sendcommand)

    my_return_status = af_support_tools.send_ssh_command(host=setup['IP'], username=setup['user'],
                                                         password=setup['password'],
                                                         command=sendcommand, return_output=True)


    assert "Up" in my_return_status, " %s is not up" % service




