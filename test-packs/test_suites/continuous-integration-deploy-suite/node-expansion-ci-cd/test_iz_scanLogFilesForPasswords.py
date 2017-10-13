#!/usr/bin/python
# Author:
# Revision:
# Code Reviewed by:
# Description:
#
# Copyright (c) 2017 Dell Inc. or its subsidiaries.  All Rights Reserved.
# Dell EMC Confidential/Proprietary Information
#
import af_support_tools
import pytest
import os


##############################################################################################

@pytest.fixture(scope="module", autouse=True)
def load_test_data():
    import cpsd
    global cpsd

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

    # Get the typically used passwords
    global setup_config_file
    setup_config_file = 'continuous-integration-deploy-suite/setup_config.ini'

    global setup_config_header
    setup_config_header = 'config_details'

    global rackHD_password
    rackHD_password = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                heading=setup_config_header,
                                                                property='rackhd_password')

    global rtp_password
    rtp_password = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                             heading=setup_config_header,
                                                             property='vcenter_password_rtp')

    global fra_password
    fra_password = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                             heading=setup_config_header,
                                                             property='vcenter_password_fra')


#####################################################################
# These are the main tests.
#####################################################################

@pytest.mark.parametrize('filePath, infoLogFile',
                            [('/opt/dell/cpsd/rackhd-adapter/logs/', 'rackhd-adapter-info.log'),
                            ('/opt/dell/cpsd/vcenter-adapter/logs/', 'vcenter-adapter-info.log'),
                            ('/opt/dell/cpsd/scaleio-adapter/logs/', 'scaleio-adapter-info.log'),
                            ('/opt/dell/cpsd/dne-paqx/logs/', 'dne-paqx-info.log'),
                            ('/opt/dell/cpsd/node-discovery-paqx/logs/', 'node-discovery-info.log'),
                            ('/opt/dell/cpsd/ess/logs/', 'ess-info.log')])
@pytest.mark.daily_status
@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_dne_log_files_free_of_passwords(filePath, infoLogFile):
    """
    Description     :       This method tests that the log files have none of the common Lab passwords.
                            It will fail:
                                If the info log files has any plain text passwords.
    Parameters      :       File path & log file name
    Returns         :       None
    """

    password1 = fra_password
    password2 = rtp_password
    password3 = rackHD_password

    error_list = []

    # Verify there are no plaintext passwords
    sendCommand = 'cat ' + filePath + infoLogFile + ' | grep \'' + password1 + '\''
    my_return_status = af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                                         command=sendCommand, return_output=True)
    if (password1 in my_return_status):
        error_list.append(password1)

    # Verify there are no plaintext passwords
    sendCommand = 'cat ' + filePath + infoLogFile + ' | grep \'' + password2 + '\''
    my_return_status = af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                                         command=sendCommand, return_output=True)
    if (password2 in my_return_status):
        error_list.append(password2)

    # Verify there are no plaintext passwords
    sendCommand = 'cat ' + filePath + infoLogFile + ' | grep \'' + password3 + '\''
    my_return_status = af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                                         command=sendCommand, return_output=True)
    if (password3 in my_return_status):
        error_list.append(password3)

    assert not error_list, 'Plain-Text Passwords in log files, Review the ' + infoLogFile + ' file'

    print('No plain text passwords in log files\n')

##############################################################################################
