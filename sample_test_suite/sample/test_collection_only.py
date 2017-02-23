import af_support_tools
import os
import pytest

try:
    config_file = 'collection_only_config.ini'
    env_file = 'env.ini'
except:
    print('Possible Configuration Error')

@pytest.mark.collection_only
def test_collection_only():
    """
    This test is check for pytest collection errors.
    """
    my_working_dir = os.environ['AF_BASE_PATH']
    my_error_code = af_support_tools.get_config_file_property(config_file=config_file, heading='collection_only', property='error_code')
    my_file = open(my_working_dir + '/collection_only.txt','r')
    my_text_from_file = my_file.read()

    print(my_text_from_file)

    if my_error_code in my_text_from_file:
        my_pass_flag = False
    else:
        my_pass_flag = True

    assert my_pass_flag == True