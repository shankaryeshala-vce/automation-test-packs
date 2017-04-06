import pytest
import selenium
import af_vapi
import af_support_tools
    
try:
    config_file = 'performance/core_config.ini'
    env_file = 'env.ini'
except:
    print('Possible Configuration Error')
    
@pytest.mark.performance
def test_sample_fixture(sample_local_fixture, sample_af_fixture):
    """
    This sample test is designed to demonstrate py test fixtures.
    One py test fixture is local to the sample test suite while the other is global to the auto-framework.
    The point is to show test designers their ability to utilize approved auto-framework fixtures while also maintaining their own fixtures.
    Fixtures which are deemed universal can be checked into the auto-framework by the automation team.
    This test is designed to pass.
    """
    
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
    
@pytest.mark.performance
def test_sample_read_config_file_pass():
    """
    This sample test is designed to demonstrate a data driven test by reading properties from a configuration file.
    While demonstrating the list compare function a mocked API call is used to provide sample json data.
    This test is designed to pass.
    """
    
    # Get attributes
    widget_attributes_list = af_support_tools.get_config_file_property(config_file=config_file, heading='widget_class_1', property='attributes')
    widget_attributes_list = widget_attributes_list.split(',')
    
    # Mock call to API to retrieve data
    mock_data_attributes_list = ['description', 'model_number' ,'name' ,'serial_number', 'uid' ,'class_1_only_attribute']
    
    # Sample 'assert'
    pass_flag = af_support_tools.list_compare_all_list_one_items_found_in_list_two(mock_data_attributes_list,widget_attributes_list)
    assert pass_flag == True
    
@pytest.mark.performance
def test_sample_read_config_file_fail():
    """
    This sample test is designed to demonstrate a data driven test by reading properties from a configuration file.
    While demonstrating the list compare function a mocked API call is used to provide sample json data.
    This test is designed to fail.
    """
    
    # Get attributes
    widget_attributes_list = af_support_tools.get_config_file_property(config_file=config_file, heading='widget_class_2', property='attributes')
    widget_attributes_list = widget_attributes_list.split(',')
    
    # Mock call to API to retrieve data
    mock_data_attributes_list = ['description', 'model_number' ,'name' ,'serial_number', 'uid' ,'class_1_only_attribute']
    
    # Sample 'assert'
    pass_flag = af_support_tools.list_compare_all_list_one_items_found_in_list_two(mock_data_attributes_list,widget_attributes_list)
    assert pass_flag == True
    
@pytest.mark.performance
@pytest.mark.parametrize('my_var', ['A','B','C','D','Bad Data'])
def test_sample_parametrize_vars(my_var):
    """
    This sample test is designed to demonstrate how to parametrizes a single test which will result in producing multiple tests being reported, one for each parameter passed.
    This test is designed to pass, fail and skip demonstrating how parametrized data changes that tests results.
    """
    
    # Loop through each parametrized variable checking for data equal to ‘C’ or ‘Bad Data’
    print ('Testing %s' % my_var)
    if my_var == 'C':
        pytest.skip('I don\'t like the letter C so please skip')
    else:
        assert my_var != 'Bad Data'
