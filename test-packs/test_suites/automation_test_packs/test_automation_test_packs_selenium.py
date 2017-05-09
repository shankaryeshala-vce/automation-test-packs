import af_support_tools
import os
import pytest
import selenium
    
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
def test_sample_selenium():
    """
    This sample test is designed to demonstrate a simple selenium test.
    This test also demonstrate a data driven test by reading properties from a configuration file.
    """

    print()
    print('Username: %s' % my_username)
    print('Password: %s' % my_password)
    print()

    # Get data from config file
    my_url = af_support_tools.get_config_file_property(config_file=config_file, heading='google', property='url')
    my_title = af_support_tools.get_config_file_property(config_file=config_file, heading='google', property='title')
    
    # Open selenium webdriver object
    s_driver = selenium.webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true', '--ssl-protocol=any'])
    s_driver.set_window_size(1024, 768)
    s_driver.get(my_url)
    
    # Run selenium test
    try:
        assert my_title.lower() in s_driver.title.lower(), '\'' + my_title.lower() + '\' not found within ' + '\'' + s_driver.title.lower() + '\''
    except:
        s_driver.close()
        print ('\'' + my_title.lower() + '\' not found within ' + '\'' + s_driver.title.lower() + '\'')
        raise
    print ('\'' + my_title.lower() + '\' found within ' + '\'' + s_driver.title.lower() + '\'')
    
    # Close selenium webdriver object
    s_driver.close()