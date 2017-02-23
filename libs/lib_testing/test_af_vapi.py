import pytest
import af_vapi
import af_support_tools
import os

try:
    config_file = 'lib_testing_config.ini'
    config_file = 'lib_testing_config.json'
    env_file = 'env.ini'
except:
    print('Possible Configuration Error')

########## get_auth ##########
@pytest.mark.af_vapi
@pytest.mark.get_auth
@pytest.mark.skip(reason='This Test is Hardware/Software Dependent')
def test_get_auth():
    print('Test: get_auth')
    assert 5 == 5

########## build_url_request_json ##########
@pytest.mark.af_vapi
@pytest.mark.build_url_request_json
@pytest.mark.skip(reason='This Test is Hardware/Software Dependent')
def test_build_url_request_json():
    print('Test: build_url_request_json')
    assert 5 == 5

########## get_json_by_query ##########
@pytest.mark.af_vapi
@pytest.mark.get_json_by_query
@pytest.mark.skip(reason='This Test is Hardware/Software Dependent')
def test_get_json_by_query():
    print('Test: get_json_by_query')
    assert 5 == 5