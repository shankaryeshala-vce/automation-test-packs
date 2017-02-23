import pytest
import af_vapi
import af_support_tools
import os

try:
    config_file = 'lib_testing_config.ini'
    env_file = 'env.ini'
except:
    print('Possible Configuration Error')

########## get_config_file_property ##########
@pytest.mark.af_support_tools
@pytest.mark.get_config_file_property
def test_get_config_file_property():
    print('Test: get_config_file_property')
    config_file = 'lib_testing_config.ini'
    os.system('cp $AF_LIB_PATH/lib_testing/' + config_file + ' $AF_TEST_SUITE_PATH/config_files/' + config_file)
    widget_attributes_list = []
    widget_attributes_list = af_support_tools.get_config_file_property(config_file=config_file, heading='widget_class_1', property='attributes')
    widget_attributes_list = widget_attributes_list.split(',')
    # Test Condition
    try:
        assert widget_attributes_list == [ 'description', 'model_number', 'name', 'serial_number' ,'uid', 'class_1_only_attribute' ]
        os.system('rm $AF_TEST_SUITE_PATH/config_files/' + config_file)
    except:
        os.system('rm $AF_TEST_SUITE_PATH/config_files/' + config_file)
        raise

@pytest.mark.af_support_tools
@pytest.mark.get_config_file_property
def test_get_config_file_property_config_heading_not_found():
    print('Test: get_config_file_property - Configuration Heading Not Found')
    config_file = 'lib_testing_config.ini'
    os.system('cp $AF_LIB_PATH/lib_testing/' + config_file + ' $AF_TEST_SUITE_PATH/config_files/' + config_file)
    widget_attributes_list = []
    widget_attributes_list = af_support_tools.get_config_file_property(config_file=config_file, heading='missing_heading', property='attributes')
    if widget_attributes_list is not None:
        widget_attributes_list = widget_attributes_list.split(',')
    # Test Condition
    try:
        assert widget_attributes_list is None
        os.system('rm $AF_TEST_SUITE_PATH/config_files/' + config_file)
    except:
        os.system('rm $AF_TEST_SUITE_PATH/config_files/' + config_file)
        raise

@pytest.mark.af_support_tools
@pytest.mark.get_config_file_property
def test_get_config_file_property_config_property_not_found():
    print('Test: get_config_file_property - Configuration Property Not Found')
    config_file = 'lib_testing_config.ini'
    os.system('cp $AF_LIB_PATH/lib_testing/' + config_file + ' $AF_TEST_SUITE_PATH/config_files/' + config_file)
    widget_attributes_list = []
    widget_attributes_list = af_support_tools.get_config_file_property(config_file=config_file, heading='widget_class_1', property='missing_property')
    if widget_attributes_list is not None:
        widget_attributes_list = widget_attributes_list.split(',')
    # Test Condition
    try:
        assert widget_attributes_list is None
        os.system('rm $AF_TEST_SUITE_PATH/config_files/' + config_file)
    except:
        os.system('rm $AF_TEST_SUITE_PATH/config_files/' + config_file)
        raise

@pytest.mark.af_support_tools
@pytest.mark.get_config_file_property
def test_get_config_file_property_config_file_not_found():
    print('Test: get_config_file_property - Configuration File Not Found')
    config_file = 'missing_lib_testing_config.ini'
    widget_attributes_list = []
    widget_attributes_list = af_support_tools.get_config_file_property(config_file=config_file, heading='widget_class_1', property='attributes')
    if widget_attributes_list is not None:
        widget_attributes_list = widget_attributes_list.split(',')
    # Test Condition
    try:
        assert widget_attributes_list is None
    except:
        raise

@pytest.mark.af_support_tools
@pytest.mark.get_config_file_property
def test_af_support_tools_get_config_file_config_file_type_unknown():
    print('Test: af_support_tools.get_config_file_property - Configuration File Type Unknown')
    config_file = 'lib_testing_config.xml'
    os.system('cp $AF_LIB_PATH/lib_testing/' + config_file + ' $AF_TEST_SUITE_PATH/config_files/' + config_file)
    widget_attributes_list = []
    widget_attributes_list = af_support_tools.get_config_file_property(config_file='lib_testing_config.xml', heading='widget_class_1', property='attributes')
    if widget_attributes_list is not None:
        widget_attributes_list = widget_attributes_list.split(',')
    # Test Condition
    try:
        assert widget_attributes_list is None
        os.system('rm $AF_TEST_SUITE_PATH/config_files/' + config_file)
    except:
        os.system('rm $AF_TEST_SUITE_PATH/config_files/' + config_file)
        raise

########## list_compare_all_list_one_items_found_in_list_two ##########
@pytest.mark.af_support_tools
@pytest.mark.list_compare_all_list_one_items_found_in_list_two
def test_list_compare_all_list_one_items_found_in_list_two_true():
    print('Test: list_compare_all_list_one_items_found_in_list_two - True')
    list_one = [ 'a', 'b', 'c', 'd' ]
    list_two = [ 'a', 'b', 'c', 'd', 'e', 'f', 'g' ]
    pass_flag = af_support_tools.list_compare_all_list_one_items_found_in_list_two(list_one,list_two)
    # Test Condition
    try:
        assert pass_flag == True
    except:
        raise

@pytest.mark.af_support_tools
@pytest.mark.list_compare_all_list_one_items_found_in_list_two
def test_list_compare_all_list_one_items_found_in_list_two_false():
    print('Test: list_compare_all_list_one_items_found_in_list_two - False')
    list_one = [ 'a', 'b', 'c', 'd', 'e', 'f', 'g' ]
    list_two = [ 'a', 'b', 'c', 'd' ]
    pass_flag = af_support_tools.list_compare_all_list_one_items_found_in_list_two(list_one,list_two)
    # Test Condition
    try:
        assert pass_flag == False
    except:
        raise

@pytest.mark.af_support_tools
@pytest.mark.list_compare_all_list_one_items_found_in_list_two
def test_list_compare_all_list_one_items_found_in_list_two_list_one_empty():
    print('Test: list_compare_all_list_one_items_found_in_list_two - List One Empty')
    list_one = [ ]
    list_two = [ 'a', 'b', 'c', 'd', 'e', 'f', 'g' ]
    pass_flag = af_support_tools.list_compare_all_list_one_items_found_in_list_two(list_one,list_two)
    # Test Condition
    try:
        assert pass_flag == True
    except:
        raise

@pytest.mark.af_support_tools
@pytest.mark.list_compare_all_list_one_items_found_in_list_two
def test_list_compare_all_list_one_items_found_in_list_two_list_two_empty():
    print('Test: list_compare_all_list_one_items_found_in_list_two - List Two Empty')
    list_one = [ 'a', 'b', 'c', 'd' ]
    list_two = [ ]
    pass_flag = af_support_tools.list_compare_all_list_one_items_found_in_list_two(list_one,list_two)
    # Test Condition
    try:
        assert pass_flag == False
    except:
        raise

@pytest.mark.af_support_tools
@pytest.mark.list_compare_all_list_one_items_found_in_list_two
def test_list_compare_all_list_one_items_found_in_list_two_list_non_list_object_one():
    print('Test: list_compare_all_list_one_items_found_in_list_two - Non List Object One Passed')
    list_one = 'Non List Object'
    list_two = [ 'a', 'b', 'c', 'd', 'e', 'f', 'g' ]
    pass_flag = af_support_tools.list_compare_all_list_one_items_found_in_list_two(list_one,list_two)
    # Test Condition
    try:
        assert pass_flag is None
    except:
        raise

@pytest.mark.af_support_tools
@pytest.mark.list_compare_all_list_one_items_found_in_list_two
def test_list_compare_all_list_one_items_found_in_list_two_list_non_list_object_two():
    print('Test: list_compare_all_list_one_items_found_in_list_two - Non List Object Two Passed')
    list_one = [ 'a', 'b', 'c', 'd' ]
    list_two = 'Non List Object'
    pass_flag = af_support_tools.list_compare_all_list_one_items_found_in_list_two(list_one,list_two)
    # Test Condition
    try:
        assert pass_flag is None
    except:
        raise

@pytest.mark.af_support_tools
@pytest.mark.list_compare_all_list_one_items_found_in_list_two
def test_list_compare_all_list_one_items_found_in_list_two_list_non_list_object_one_and_two():
    print('Test: list_compare_all_list_one_items_found_in_list_two - Non List Object One and Two Passed')
    list_one = 'Non List Object'
    list_two = 'Non List Object'
    pass_flag = af_support_tools.list_compare_all_list_one_items_found_in_list_two(list_one,list_two)
    # Test Condition
    try:
        assert pass_flag is None
    except:
        raise

########## remove_dups_from_list ##########
@pytest.mark.af_support_tools
@pytest.mark.remove_dups_from_list
def test_remove_dups_from_list_no_dups_found():
    print('Test: remove_dups_from_list - No Duplicate Items Found')
    my_list = [ 1, 'a', [1,2,3], (1,2,3), {'a':1,'b':2,'c':3} ]
    my_list = af_support_tools.remove_dups_from_list(my_list)
    # Test Condition
    try:
        assert my_list == [ 1, 'a', [1,2,3], (1,2,3), {'a':1,'b':2,'c':3} ]
    except:
        raise

@pytest.mark.af_support_tools
@pytest.mark.remove_dups_from_list
def test_remove_dups_from_list_dups_found():
    print('Test: remove_dups_from_list - Duplicate Items Found')
    my_list = [ 1, 1, 'a', 'a', [1,2,3], [1,2,3], (1,2,3), (1,2,3), {'a':1,'b':2,'c':3}, {'a':1,'b':2,'c':3} ]
    my_list = af_support_tools.remove_dups_from_list(my_list)
    # Test Condition
    try:
        assert my_list == [ 1, 'a', [1,2,3], (1,2,3), {'a':1,'b':2,'c':3} ]
    except:
        raise

@pytest.mark.af_support_tools
@pytest.mark.remove_dups_from_list
def test_remove_dups_from_list_dups_non_list_object():
    print('Test: remove_dups_from_list - Non List Object Passed')
    my_list = 'Not a List'
    my_list = af_support_tools.remove_dups_from_list(my_list)
    # Test Condition
    try:
        assert my_list is None
    except:
        raise