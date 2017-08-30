import af_support_tools
import os
import pytest
import json
import time


@pytest.fixture(scope="module", autouse=True)
def load_test_data():
    # Set config ini file name
    global env_file
    env_file = 'env.ini'
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
    # Set Vars
    global ip_address
    ip_address = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='hostname')
    global username
    username = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='username')
    global password
    password = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='password')
    # Update setup_config.properties file at runtime
    data_file = os.environ.get('AF_RESOURCES_PATH') + '/continuous-integration-deploy-suite/setup_config.properties'
    af_support_tools.set_config_file_property_by_data_file(data_file)
    # IDrac Server IP & Creds details
    global setup_config_file
    setup_config_file = 'continuous-integration-deploy-suite/setup_config.ini'
    global setup_config_header
    setup_config_header = 'config_details'
    global idrac_hostname
    idrac_hostname = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                               heading=setup_config_header, property='idrac_ipaddress')
    global idrac_username
    idrac_username = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                               heading=setup_config_header, property='idrac_username')
    global idrac_common_password
    idrac_common_password = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                      heading=setup_config_header,
                                                                      property='idrac_common_password')
    global idrac_factory_password
    idrac_factory_password = af_support_tools.get_config_file_property(config_file=setup_config_file,
                                                                       heading=setup_config_header,
                                                                       property='idrac_factory_password')


#####################################################################
# These are the main tests.
#####################################################################
#@pytest.mark.dne_paqx_parent_mvp
#@pytest.mark.dne_paqx_parent_mvp_extended
def test_idrac_credential_store():
    """
    Description :   This method tests whether the idrac credentials are stored in system definition service
                    it will asserts if :
                    If IDRAC json file doesnt exists
                    If AMQP tool is not able to execute the command properly
                    If credential keys for IDRAC are not created properly
    Parameters  :   None
    Returns     :   None
    """
    # Get the payload data from the config symphony-sds.ini file.
    the_payload = af_support_tools.get_config_file_property(config_file=payload_file,
                                                            heading=payload_header,
                                                            property=payload_property_sys)
    container_id = get_vault_container_id()
    assert check_vault_credential_keys(container_id), 'test failed: idrac credentials are not stored properly'


def get_vault_container_id():
    """    
    Description         :       This method gets the container id    
    Parameters          :       None    
    Returns             :       container_id     -       container id string coming from 'docker ps' command(STRING).    
    """
    cmd = 'docker ps | grep vault'
    output = af_support_tools.send_ssh_command(host=ip_address, username=username, password=password, command=cmd,
                                               return_output=True).strip()
    assert (output != ""), 'test failed: ' + container + ' docker service is not running'
    output_list = output.split()
    container_id = output_list[0]
    return container_id


def check_vault_credential_keys(container_id):
    """
    Description         :       This method checks whether the credentials are created for IDRAC in system definition
                                also This method will delete the IDRAC.json file
    Parameters          :       1. container_id    -       Container id of Vault (STRING)
    Returns             :       output_length      -       if the credential keys are not found (INTEGER)
                                0 or 1 (Boolean)
    """
    cmd = "docker exec " + container_id + " vault list secret"
    print ("cmd:", cmd)
    output = af_support_tools.send_ssh_command(host=ip_address, username=username, password=password, command=cmd,
                                               return_output=True).strip()
    output_list = output.split("\n")
    print ("output_list:", output_list)
    output_length = len(output_list)
    credential_list_json = ""
    credential_list = 0
    # if credential keys are not found return, else check the credentials using Vault commands and compare with json input 
    del output_list[0]
    print ("output_list1:", output_list)
    del output_list[0]
    print ("output_list2:", output_list)
    for uuid in output_list:
        cmd1 = "docker exec " + container_id + " vault list secret/" + uuid
        print ("cmd1:", cmd1)
        output1 = af_support_tools.send_ssh_command(host=ip_address, username=username, password=password, command=cmd1,
                                                    return_output=True).strip()
        output_list1 = output1.split("\n")
        endpoint_uuid = output_list1[2]
        cmd2 = "docker exec " + container_id + " vault list secret/" + uuid + endpoint_uuid
        print ("cmd2;", cmd2)
        output2 = af_support_tools.send_ssh_command(host=ip_address, username=username, password=password, command=cmd2,
                                                    return_output=True).strip()
        output_list2 = output2.split("\n")
        output_length2 = len(output_list2)
        print ("output_length:", output_length2)
        if (output_length2 == 3):
            continue
        else:
            print ("output_list2:", output_list2)
            idrac_uuid = output_list2[2]
            idrac_uuid_new = output_list2[3]
            cmd3 = "docker exec " + container_id + " vault read secret/" + uuid + endpoint_uuid + idrac_uuid
            print ("cmd3:", cmd3)
            output3 = af_support_tools.send_ssh_command(host=ip_address, username=username, password=password,
                                                        command=cmd3, return_output=True).strip()
            idrac_usrname, idrac_passwd = get_idrac_credentials(output3)
            cmd4 = "docker exec " + container_id + " vault read secret/" + uuid + endpoint_uuid + idrac_uuid_new
            print ("cmd4:", cmd4)
            output4 = af_support_tools.send_ssh_command(host=ip_address, username=username, password=password,
                                                        command=cmd4, return_output=True).strip()
            idrac_username_new, idrac_passwd_new = get_idrac_credentials(output4)
            credential_list_json = [idrac_username, idrac_factory_password, idrac_username, idrac_common_password]
            print ("credential_list_json:", credential_list_json)
            credential_list = [idrac_usrname, idrac_passwd, idrac_username_new, idrac_passwd_new]
            print ("credential_list:", credential_list)
            if credential_list:
                break
    for element in credential_list_json:
        if (element in credential_list):
            continue
        else:
            return 0
    return 1


def get_idrac_credentials(command_output):
    """
    Description         :       This method processes the command output and gets the idrac username and password
    Parameters          :       1. command_output    -       Command output to be processed (STRING)
    Returns             :       idracUsername        -       IDRAC username (STRING)
                                idracPassword        -       IDRAC password (STRING)
    """
    output_list = command_output.split("\n")
    idrac_username_list = output_list[5].split("\t")
    idracUsername = idrac_username_list[1]
    idrac_passwd_list = output_list[4].split("\t")
    idracPasswd = idrac_passwd_list[1]
    return idracUsername, idracPasswd
