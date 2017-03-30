import pytest
import selenium
import af_vapi
import af_support_tools
    
try:
    config_file = 'automation_test_packs/selenium_config.ini'
    env_file = 'env.ini'
except:
    print('Possible Configuration Error')
    
@pytest.mark.automation_test_packs
@pytest.mark.taf_mvp
def test_sample_selenium():
    """
    This sample test is designed to demonstrate a simple selenium test.
    This test also demonstrate a data driven test by reading properties from a configuration file.
    """
    
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