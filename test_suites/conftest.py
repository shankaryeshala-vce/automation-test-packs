import configparser
import os
import pytest

@pytest.fixture(autouse=True)
def _environment(request):
    # af_info.ini
	
	# Test Suite Name
    try:
        my_test_suite_name = os.environ['AF_TEST_SUITE_NAME']
    except:
        my_test_suite_name = 'Test Suite Name Not Set'
    
	# TAF Build Date / # TAF Build Number
    my_info_file = os.environ['AF_BASE_PATH'] + '/af_info.ini'
    if os.path.isfile(my_info_file) == True:
        config = configparser.ConfigParser()
        config.read(my_info_file)

        # TAF Build Date
        heading = 'build_info'
        property = 'build_date'
        heading_list = config.sections()
        if heading not in heading_list:
            my_af_build_date = 'Heading Not Found: Unknown'
        else:
            property_list = list(dict(config.items(heading)).keys())
        if property not in property_list:
            my_af_build_date = 'Property Not Found: Unknown'
        else:
            my_af_build_date = config[heading][property]

        # TAF Build Number
        heading = 'build_info'
        property = 'build_number'
        heading_list = config.sections()
        if heading not in heading_list:
            my_af_build_number = 'Heading Not Found: Unknown'
        else:
            property_list = list(dict(config.items(heading)).keys())
        if property not in property_list:
            my_af_build_number = 'Property Not Found: Unknown'
        else:
            my_af_build_number = config[heading][property]

    # TAF PIP List
    os.system('pip list --format=legacy > my_pip_list.txt')
    file = open('my_pip_list.txt', 'r')
    my_pip_list = file.read()
    file.close()
    os.remove('my_pip_list.txt')
    my_pip_list = my_pip_list.replace('\n', " | ")

    # TAF Platform
    my_vm_template_version_file = os.environ['HOME'] + '/vm-template-version.txt'
    my_docker_version_file = os.environ['HOME'] + '/docker-version.txt'
    if os.path.isfile(my_vm_template_version_file) == True:
        file = open(my_vm_template_version_file, 'r')
        my_taf_platform_version = file.read()
        file.close()
        my_taf_platform_version = my_taf_platform_version.split('=')
        my_taf_platform_version = 'VM / ' + my_taf_platform_version[1]
    elif os.path.isfile(my_docker_version_file) == True:
        file = open(my_docker_version_file, 'r')
        my_taf_platform_version = file.read()
        file.close()
        my_taf_platform_version = my_taf_platform_version.split('=')
        my_taf_platform_version = 'Docker / ' + my_taf_platform_version[1]
    else:
        my_taf_platform_version = 'Unknown'

    request.config._environment.append((' Test Suite Name', my_test_suite_name))
    request.config._environment.append(('Platform Type / Build Date', my_taf_platform_version))
    request.config._environment.append(('TAF Build Date', my_af_build_date))
    request.config._environment.append(('TAF Build Number', my_af_build_number))
    request.config._environment.append(('TAF PIP List', my_pip_list))

@pytest.fixture(scope='session')
def sample_af_fixture():
    """
    This is a sample auto-framework global fixture that will return ‘hello world’ variables. 
    """
    my_message_1 = 'Hello World'
    my_message_2 = 'Here is a sample of an automation framework pytest fixture'
    my_message_3 = 'It returns 3 values'
    return(my_message_1, my_message_2, my_message_3)