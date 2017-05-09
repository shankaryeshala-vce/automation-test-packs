import af_support_tools
import os
import pytest

@pytest.fixture(scope="module", autouse=True)
def load_test_data():
    # Update config ini files at runtime
    # This can be used to update ini files with sensitive data such as passwords an IP addresses
    my_data_file = os.environ.get('AF_RESOURCES_PATH') + '/data_sensitive_vars.properties'
    af_support_tools.set_config_file_property_by_data_file(my_data_file)

    # Set config ini file name
    # These can be set inside the individual tests and do not need to be made global
    global config_file
    config_file = 'sample_config.ini'
    global env_file
    env_file = 'env.ini'

    # Set Vars
    # These can be read inside the individual tests and do not need to be made global
    global my_username
    my_username = af_support_tools.get_config_file_property(config_file=config_file, heading='data_sensitive_vars', property='username')
    global my_password
    my_password = af_support_tools.get_config_file_property(config_file=config_file, heading='data_sensitive_vars', property='password')
    
@pytest.mark.automation_test_packs
@pytest.mark.taf_mvp
def test_sample_fixture(sample_local_fixture, sample_af_fixture):
    """
    This sample test is designed to demonstrate py test fixtures.
    One py test fixture is local to the sample test suite while the other is global to the auto-framework.
    The point is to show test designers their ability to utilize approved auto-framework fixtures while also maintaining their own fixtures.
    Fixtures which are deemed universal can be checked into the auto-framework by the automation team.
    This test is designed to pass.
    """

    print()
    print('Username: %s' % my_username)
    print('Password: %s' % my_password)
    print()

    # Unpack vars from a local pytest fixture file
    local_messge_1, local_messge_2, local_messge_3 = sample_local_fixture
    
    # Unpack vars from the Automation Framework fixture file
    af_messge_1, af_messge_2, af_messge_3 = sample_af_fixture
    
    # Print out vars
    print(local_messge_1)
    print(local_messge_2)
    print(local_messge_3)
    print()
    print(af_messge_1)
    print(af_messge_2)
    print(af_messge_3)
    
    # Sample 'assert'
    assert 5 == 5
    
@pytest.mark.automation_test_packs
@pytest.mark.taf_mvp
def test_sample_read_config_file_pass():
    """
    This sample test is designed to demonstrate a data driven test by reading properties from a configuration file.
    While demonstrating the list compare function a mocked API call is used to provide sample json data.
    This test is designed to pass.
    """

    print()
    print('Username: %s' % my_username)
    print('Password: %s' % my_password)
    print()

    # Get attributes
    widget_attributes_list = af_support_tools.get_config_file_property(config_file=config_file, heading='widget_class_1', property='attributes')
    widget_attributes_list = widget_attributes_list.split(',')
    
    # Mock call to API to retrieve data
    mock_data_attributes_list = ['description', 'model_number' ,'name' ,'serial_number', 'uid' ,'class_1_only_attribute']
    
    # Sample 'assert'
    pass_flag = af_support_tools.list_compare_all_list_one_items_found_in_list_two(mock_data_attributes_list,widget_attributes_list)
    assert pass_flag == True
    
@pytest.mark.automation_test_packs
def test_sample_read_config_file_fail():
    """
    This sample test is designed to demonstrate a data driven test by reading properties from a configuration file.
    While demonstrating the list compare function a mocked API call is used to provide sample json data.
    This test is designed to fail.
    """

    print()
    print('Username: %s' % my_username)
    print('Password: %s' % my_password)
    print()

    # Get attributes
    widget_attributes_list = af_support_tools.get_config_file_property(config_file=config_file, heading='widget_class_2', property='attributes')
    widget_attributes_list = widget_attributes_list.split(',')
    
    # Mock call to API to retrieve data
    mock_data_attributes_list = ['description', 'model_number' ,'name' ,'serial_number', 'uid' ,'class_1_only_attribute']
    
    # Sample 'assert'
    pass_flag = af_support_tools.list_compare_all_list_one_items_found_in_list_two(mock_data_attributes_list,widget_attributes_list)
    assert pass_flag == True
    
@pytest.mark.automation_test_packs
@pytest.mark.parametrize('my_var', ['A','B','C','D','Bad Data'])
def test_sample_parametrize_vars(my_var):
    """
    This sample test is designed to demonstrate how to parametrizes a single test which will result in producing multiple tests being reported, one for each parameter passed.
    This test is designed to pass, fail and skip demonstrating how parametrized data changes that tests results.
    """

    print()
    print('Username: %s' % my_username)
    print('Password: %s' % my_password)
    print()

    # Loop through each parametrized variable checking for data equal to ‘C’ or ‘Bad Data’
    print ('Testing %s' % my_var)
    if my_var == 'C':
        pytest.skip('I don\'t like the letter C so please skip')
    else:
        assert my_var != 'Bad Data'
