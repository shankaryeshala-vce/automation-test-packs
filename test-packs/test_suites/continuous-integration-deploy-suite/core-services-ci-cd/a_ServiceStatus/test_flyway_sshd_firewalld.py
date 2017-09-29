#!/usr/bin/python
# Author: Shane McGowan (6/April/2017)
# Copyright © 2017 Dell Inc. or its subsidiaries.  All Rights Reserved
# Updated by:
# Revision:1.0
# Code Reviewed by:Toqeer
# Description: This script will run against newly deployed OVA and perform a sanity check for flyway, sshd and firewalld services.
########################################################################################################################

import af_support_tools
import pytest
import time
import pika

@pytest.fixture(scope="module", autouse=True)
def load_test_data():
    global env_file 
    env_file = 'env.ini'
    global ipaddress
    ipaddress = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='hostname')
    global cli_user
    cli_user = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='username')
    global cli_password
    cli_password = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='password')

#ipaddress = '10.3.60.67'
########################################################################################################################
@pytest.mark.skip(reason="Not Needed at present")
def test_flywayrunning():
    flyway_err = []

    sendCommand = "flyway | grep 'Flyway 4.1.2 by Boxfuse'"
    flyway_status = af_support_tools.send_ssh_command(host=ipaddress, username=cli_user, password=cli_password, command=sendCommand, return_output=True)

    if "4.1.2" not in flyway_status:
        flyway_err.append("Error: Flyway service not running")

    else:
        print(flyway_status)
    assert not flyway_err

#####################################################END OF test_flywayrunning() TEST########################################################


@pytest.mark.core_services_mvp
@pytest.mark.core_services_cd
def test_sshdrunning():
    sshd_err = []

    sendCommand = "systemctl status sshd | grep 'Active:'"
    sshd_status = af_support_tools.send_ssh_command(host=ipaddress, username=cli_user, password=cli_password, command=sendCommand, return_output=True)

    if "running" not in sshd_status:
        sshd_err.append("Error: SSHd service not running")
    else:
        print("SSHd Service Status -"+ sshd_status)
    assert not sshd_err

#####################################################END OF test_sshdrunning() TEST########################################################


@pytest.mark.skip(reason="Not Needed at present")
def test_firewalldrunning():
    firewalld_err = []

    sendCommand = "systemctl status firewalld | grep 'Active:'"
    firewalld_status = af_support_tools.send_ssh_command(host=ipaddress, username=cli_user, password=cli_password, command=sendCommand, return_output=True)

    if "inactive" not in firewalld_status:
        firewalld_err.append("Error: Firewalld service is running")
    else:
        print("Firewalld Service Status -"+ firewalld_status)
    assert not firewalld_err

#####################################################END OF test_firewalldrunning() TEST########################################################
#test_flywayrunning()
#test_sshdrunning()
#test_firewalldrunning()
