#!/usr/bin/python
# Author:
# Revision: 1.0
# Code Reviewed by:
# Description: Testing the simple Info Node Expansion APIs both local & via api-gateway
#
# Copyright (c) 2017 Dell Inc. or its subsidiaries.  All Rights Reserved.
# Dell EMC Confidential/Proprietary Information
#
import af_support_tools
import pytest
import requests
import os


##############################################################################################

@pytest.fixture(scope="module", autouse=True)
def load_test_data():
    import cpsd
    global cpsd

    af_support_tools.rmq_get_server_side_certs(host_hostname=cpsd.props.base_hostname,
                                               host_username=cpsd.props.base_username,
                                               host_password=cpsd.props.base_password, host_port=22,
                                               rmq_certs_path=cpsd.props.rmq_cert_path)

    # Set config ini file name
    global env_file
    env_file = 'env.ini'

    # Test VM Details
    global ipaddress
    ipaddress = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='hostname')

    global protocol
    protocol = 'http://'

    global dne_port
    dne_port = ':8071'

    global gateway_port
    gateway_port = ':10000'


#####################################################################
# These are the main tests.
#####################################################################

@pytest.mark.parametrize('dne_url_body, expected_response', [
    ('/dne/about', 'Node Expansion API v0.1'),
    ('/swagger-ui.html#', '<!DOCTYPE html>')
])
@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_node_expansion_api_local_dne(dne_url_body, expected_response):
    """
    Title           :       Verify the Node Expansion Local APIs
    Description     :       This methind tests that the expected local Node Expansion APIs are returning as expected.
                            It will fail if :
                                A 200 response is not received
    Parameters      :       1. The URL Body 2. The expected output
    Returns         :       None
    """

    my_dne_url = protocol + ipaddress + dne_port + dne_url_body

    print('GET:', my_dne_url)

    try:
        url_response = requests.get(my_dne_url)
        url_response.raise_for_status()

        # A 200 has been received
        print(url_response)

        the_response = url_response.text  # Save the body of the response to a variable
        assert expected_response in the_response, ('ERROR:', expected_response, 'is not returned\n')


    # Error check the response
    except Exception as err:
        # Return code error (e.g. 404, 501, ...)
        print(err)
        print('\n')
        raise Exception(err)


@pytest.mark.skip(reason='Defect: ESTS-128946')
@pytest.mark.parametrize('dne_url_body, expected_response', [
    ('/dne-paqx/dne/about', 'Node Expansion API v0.1'),
    ('/dne-paqx/swagger-ui.html#', '<!DOCTYPE html>')
])
@pytest.mark.dne_paqx_parent_mvp
@pytest.mark.dne_paqx_parent_mvp_extended
def test_node_expansion_api_gateway_dne(dne_url_body, expected_response):
    """
    Title           :       Verify the Node Expansion api-gateway APIs
    Description     :       This methind tests that the expected  Node Expansion APIs are returning as expected via
                            the API-gateway.
                            It will fail if :
                                A 200 response is not received
    Parameters      :       1. The URL Body 2. The expected output
    Returns         :       None
    """

    my_dne_url = protocol + ipaddress + gateway_port + dne_url_body

    print('GET:', my_dne_url)

    try:
        url_response = requests.get(my_dne_url)
        url_response.raise_for_status()

        # A 200 has been received
        print(url_response)

        the_response = url_response.text  # Save the body of the response to a variable
        assert expected_response in the_response, ('ERROR:', expected_response, 'is not returned\n')


    # Error check the response
    except Exception as err:
        # Return code error (e.g. 404, 501, ...)
        print(err)
        print('\n')
        raise Exception(err)

        ##############################################################################################
