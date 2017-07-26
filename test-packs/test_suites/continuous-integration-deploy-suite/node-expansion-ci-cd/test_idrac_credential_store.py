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
    global amqptooljar
    amqptooljar = str(os.environ.get('AF_RESOURCES_PATH')) + '/system-definition/amqp-post-1.0-SNAPSHOT.jar'
    # Set Vars
    global ip_address
    ip_address = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='hostname')
    global username
    username = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='username')
    global password
    password = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='password')
#####################################################################
# These are the main tests.
#####################################################################
@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_idrac_credential_store():
    """
    Description         :       This method tests whether the idrac credentials are stored in system definition service
    			it will asserts if :
    		        If IDRAC json file doesnt exists
                                If AMQP tool is not able to execute the command properly
                                If credential keys for IDRAC are not created properly
    Parameters  	:       None
    Returns             :       None
    """
    # Get the payload data from the config symphony-sds.ini file.
    the_payload = af_support_tools.get_config_file_property(config_file=payload_file,
                                                            heading=payload_header,
                                                            property=payload_property_sys)
    container_id = get_vault_container_id()
    #assert update_IDRAC_json(jsonfilepath, ip_address, the_payload), 'test failed: ' + jsonfilepath + 'doesnt exists'
    #assert run_amqp_tool(amqptooljar, jsonfilepath), 'test failed: unable to execute ' + amqptooljar
    assert check_vault_credential_keys(container_id),'test failed: idrac credentials are not stored properly'
def update_IDRAC_json(json_file_path, ipaddress, payload):
    """
    Description 	:       This method will update the json file with the host ip address 
    Parameters  	:       1. json_file_path     -       Name of the Json file (STRING)
    			2. ipaddress          -  hostname mentioned in the env.ini file
                                3. payload            - payload for the json file
    Returns             :       0 or 1 (Boolean)
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
    return 1
def get_idrac_credentials_json():
    """
    Description 	:       This method will get the idrac credentials from the json file 
    Parameters  	:       None
    Returns             :       idrac_credential_json (LIST)
    """
    with open(jsonfilepath) as json_file:
        data = json.load(json_file)
    idrac_username_json=data['body']['convergedSystem']['endpoints'][3]['credentials'][0]['credentialElements']['username']
    idrac_password_json=data['body']['convergedSystem']['endpoints'][3]['credentials'][0]['credentialElements']['password']
    idrac_username_new_json=data['body']['convergedSystem']['endpoints'][3]['credentials'][1]['credentialElements']['username']
    idrac_password_new_json=data['body']['convergedSystem']['endpoints'][3]['credentials'][1]['credentialElements']['password']
    idrac_credential_json = [idrac_username_json,idrac_password_json,idrac_username_new_json,idrac_password_new_json]
    return idrac_credential_json
def run_amqp_tool(amqp_tool_jar, system_def_json):
    """
    Description 	:       This method will run the ampq tool jar file with the given input json file 
    Parameters  	:       1. amqp_tool_jar       -       Name of the amqp tool jar file (STRING)
                                2. system_def_json     -       Name of the Json file (STRING)
    Returns             :       0 or 1 (Boolean)
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
def get_vault_container_id():    
    """    
    Description         :       This method gets the container id    
    Parameters          :       None    
    Returns             :       container_id     -       container id string coming from 'docker ps' command(STRING).    
    """    
    cmd = 'docker ps | grep vault'   
    output = af_support_tools.send_ssh_command(host=ip_address, username=username, password=password, command=cmd, return_output=True).strip()    
    assert (output != ""), 'test failed: ' + container + ' docker service is not running'    
    output_list = output.split( )    
    container_id = output_list [0]    
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
    # Adding print statements to debug
    print ("cmd:",cmd)
    output = af_support_tools.send_ssh_command(host=ip_address, username=username, password=password, command=cmd, return_output=True).strip()    
    output_list = output.split("\n")
    print ("output_list:",output_list) 
    output_length = len(output_list)
    credential_list_json = ""
    credential_list = 0
    # if credential keys are not found return, else check the credentials using Vault commands and compare with json input 
    del output_list[0]
    print ("output_list1:",output_list)
    del output_list[0]
    print ("output_list2:",output_list)
    for uuid in output_list:
        cmd1 = "docker exec " + container_id + " vault list secret/" + uuid
        output1 = af_support_tools.send_ssh_command(host=ip_address, username=username, password=password, command=cmd1, return_output=True).strip()    
        output_list1 = output1.split("\n")
        endpoint_uuid = output_list1[2]
        cmd2 = "docker exec " + container_id + " vault list secret/" + uuid + endpoint_uuid
        output2 = af_support_tools.send_ssh_command(host=ip_address, username=username, password=password, command=cmd2, return_output=True).strip()    
        output_list2 = output2.split("\n")
        output_length2 = len(output_list2)
        if (output_length2 == 3):
            continue
        else:
            idrac_uuid = output_list2[2]
            idrac_uuid_new = output_list2[3]
            cmd3 = "docker exec " + container_id + " vault read secret/" + uuid + endpoint_uuid + idrac_uuid
            output3 = af_support_tools.send_ssh_command(host=ip_address, username=username, password=password, command=cmd3, return_output=True).strip()    
            idrac_username, idrac_passwd = get_idrac_credentials(output3)
            cmd4 = "docker exec " + container_id + " vault read secret/" + uuid + endpoint_uuid + idrac_uuid_new
            output4 = af_support_tools.send_ssh_command(host=ip_address, username=username, password=password, command=cmd4, return_output=True).strip()    
            idrac_username_new, idrac_passwd_new = get_idrac_credentials(output4)
            credential_list_json=get_idrac_credentials_json()
            credential_list=[idrac_username,idrac_passwd,idrac_username_new,idrac_passwd_new]
    for element in credential_list_json:
        if (element in credential_list):
             continue
        else:
             return 0 
    os.remove(jsonfilepath)
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
