# Copyright © 2017 Dell Inc. or its subsidiaries.  All Rights Reserved
import af_support_tools
import os
import pytest
import subprocess


@pytest.fixture(autouse=True, scope='session')
def cpsd_common_properties():
    # Update env.ini file with cpsd common properties at runtime
    my_data_file = os.environ.get('AF_RESOURCES_PATH') + '/cpsd-common/cpsd_common.properties'
    af_support_tools.set_config_file_property_by_data_file(my_data_file)


# def get_certificates_for_tls():
#     result = subprocess.Popen('./tls-enable.sh', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#     result_status = result.wait()
#     print(result_status)


# @pytest.fixture(autouse=True, scope='session')
# def get_tls_certs():
#     print('Getting tls certs from tls_service')
#     tls_file = '/home/autouser/PycharmProjects/auto-framework/test_suites/tls_certs_exist'
#     if os.path.isfile(tls_file):
#         print('TLS Certs exist already')
#     else:
#         result = subprocess.check_output([". /home/autouser/PycharmProjects/auto-framework/run_jobs/tls_enable.sh"], stderr=subprocess.STDOUT)
#         print(result)
#         f = open(tls_file,'w')
#         print >>f, 'whatever'