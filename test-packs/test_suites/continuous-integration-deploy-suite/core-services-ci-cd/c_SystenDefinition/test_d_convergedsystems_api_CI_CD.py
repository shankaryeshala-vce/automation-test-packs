import af_support_tools
import pytest
import os
import json
import requests

@pytest.fixture(scope="module", autouse=True)
def load_test_data():
    # Update config ini files at runtime
    my_data_file = os.environ.get('AF_RESOURCES_PATH') + '/continuous-integration-deploy-suite/symphony-sds.properties'
    af_support_tools.set_config_file_property_by_data_file(my_data_file)

    # Set config ini file name
    global env_file
    env_file = 'env.ini'

    # Set Vars for the JSON payload
    global payload_file
    payload_file = 'continuous-integration-deploy-suite/symphony-sds.ini'
    global payload_header
    payload_header = 'payload'
    global payload_property_amqp
    payload_property_amqp = 'sys_payload'

    #Get values from ip address
    global ipaddress
    ipaddress = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='hostname')
    global cli_username
    cli_username = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS',
                                                             property='username')
    global cli_password
    cli_password = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS',
                                                             property='password')

@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
def test_convergedsystem_api_identity():
    err=[]


    api_url = 'http://' + ipaddress + ':8088/convergedsystems'

    the_payload = af_support_tools.get_config_file_property(config_file=payload_file, heading= payload_header,
                                                            property= payload_property_amqp )
    sysadd = json.loads(the_payload)

    header = {'Content-Type': 'application/json', 'Accept': 'application/json'}

    r = requests.get(api_url, headers = header,  data=the_payload)
    resp = json.loads(r.text)

    ## Validating contents of json file and message returned from Converged System Rest API
    ## Testing story

    if resp == None:
        err.append("Error---System not added successfully")
    assert not err


    if sysadd["convergedSystem"]["identity"]["identifier"] != resp[0]['identity']['identifier']:
         err.append("Error---Correct identifier not returned")
    assert not err

    if sysadd["convergedSystem"]["identity"]["serialNumber"] != resp[0]['identity']['serialNumber']:
         err.append("Error---Correct Serial number not returned")
    assert not err

    if sysadd["convergedSystem"]["definition"]["productFamily"] != resp[0]['definition']['productFamily']:
         err.append("Error---Correct Product Family not returned")
    assert not err

    if sysadd["convergedSystem"]["definition"]["model"] != resp[0]['definition']['model']:
         err.append("Error---Correct model not returned")
    assert not err






















