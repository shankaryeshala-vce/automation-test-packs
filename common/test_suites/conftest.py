# Copyright © 2017 Dell Inc. or its subsidiaries.  All Rights Reserved
import af_support_tools
import os
import pytest

@pytest.fixture(autouse=True, scope='session')
def cpsd_common_properties():
    # Update env.ini file with cpsd common properties at runtime
    my_data_file = os.environ.get('AF_RESOURCES_PATH') + '/cpsd-common/cpsd_common.properties'
    af_support_tools.set_config_file_property_by_data_file(my_data_file)
