#!/usr/bin/python
# Author:
# Revision:
# Code Reviewed by:
# Description: This is a setup scrip that will configure Symphony with a valid system definition file
#
# Copyright (c) 2017 Dell Inc. or its subsidiaries.  All Rights Reserved.
# Dell EMC Confidential/Proprietary Information

import af_support_tools
import os
import pytest
import json
import time

@pytest.fixture(scope="module", autouse=True)
def load_test_data():
    import cpsd
    global cpsd

    # Set config ini file name
    global env_file
    env_file = 'env.ini'

    # Set Vars
    global ip_address
    ip_address = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='hostname')

    global username
    username = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='username')

    global password
    password = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='password')

    # Update config ini files at runtime
    my_data_file = os.environ.get('AF_RESOURCES_PATH') + '/continuous-integration-deploy-suite/symphony-sds.properties'
    af_support_tools.set_config_file_property_by_data_file(my_data_file)

    # Set Vars
    global payload_file
    payload_file = 'continuous-integration-deploy-suite/symphony-sds.ini'

    global payload_header
    payload_header = 'payload'

    global payload_property_sys
    payload_property_sys = 'sys_payload_idrac_node_exp'

    global jsonfilepath
    jsonfilepath = 'IDRAC.json'

    global amqptooljar
    amqptooljar = str(os.environ.get('AF_RESOURCES_PATH')) + '/system-definition/amqp-post-1.0-SNAPSHOT.jar'



#####################################################################

@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_idrac_credential_store():
    """
    Description:    This method tests whether the idrac credentials are stored in system definition service
                    it will asserts if :
                    If IDRAC json file doesnt exists
                    If AMQP tool is not able to execute the command properly
    Parameters:     None
    Returns:        None
    """

    # Get the payload data from the config symphony-sds.ini file.
    the_payload = af_support_tools.get_config_file_property(config_file=payload_file,
                                                            heading=payload_header,
                                                            property=payload_property_sys)

    assert update_IDRAC_json(jsonfilepath, ip_address, the_payload), 'test failed: ' + jsonfilepath + 'doesnt exists'

    assert run_amqp_tool(amqptooljar, jsonfilepath), 'test failed: unable to execute ' + amqptooljar


def update_IDRAC_json(json_file_path, ipaddress, payload):
    """
    Description:    This method will update the json file with the host ip address
    Parameters:     1. json_file_path     - Name of the Json file (STRING)
                    2. ipaddress          - hostname mentioned in the env.ini file
                    3. payload            - payload for the json file
    Returns:        0 or 1 (Boolean)
    """
    with open(json_file_path,'w') as outfile:
        outfile.write(payload)
    outfile.close()

    if (os.path.isfile(json_file_path) == 0):
        return 0

    with open(json_file_path) as json_file:
        data = json.load(json_file)
    data['configuration']['host'] = ipaddress 

    with open(json_file_path,'w') as outfile:
        json.dump(data,outfile)

    print ('next')
    print (data)
    return 1


def run_amqp_tool(amqp_tool_jar, system_def_json):
    """
    Description:    This method will run the ampq tool jar file with the given input json file
    Parameters:     1. amqp_tool_jar       -    Name of the amqp tool jar file (STRING)
                    2. system_def_json     -    Name of the Json file (STRING)
    Returns:        0 or 1 (Boolean)
    """
    test_status = "pass"
    cmd = 'java -jar ' + amqp_tool_jar + ' ' + system_def_json

    output = os.system(cmd)

    # Adding sleepp to debug if it is timing issue
    time.sleep(10)

    if (output != 0):
        test_status = "fail"

    if (test_status == "fail"):
        return 0

    else:
        return 1


