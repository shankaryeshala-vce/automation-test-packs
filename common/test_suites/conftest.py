# Copyright © 2017 Dell Inc. or its subsidiaries.  All Rights Reserved
import af_support_tools
import os
import pytest
import subprocess
# from common.common_libs import cpsd
#
#
# passwords = cpsd.get_rmq_credentials()
# print(passwords)


@pytest.fixture(autouse=True, scope='session')
def cpsd_common_properties():
    # Update env.ini file with cpsd common properties at runtime
    my_data_file = os.environ.get('AF_RESOURCES_PATH') + '/cpsd-common/cpsd_common.properties'
    af_support_tools.set_config_file_property_by_data_file(my_data_file)


# def get_certificates_for_tls():
#     result = subprocess.Popen('./tls-enable.sh', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#     result_status = result.wait()
#     print(result_status)


@pytest.fixture(autouse=True, scope='session')
def get_tls_certs():
    print('Getting tls certs from tls_service')
    tls_file = '/home/autouser/PycharmProjects/auto-framework/test_suites/tls_certs_exist'
    if os.path.isfile(tls_file):
        print('TLS Certs exist already')
    else:
        ex = subprocess.Popen('chmod +x tls_enable.sh', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        ex = ex.wait()
        o = subprocess.check_output('ls')
        with open(tls_file,'w') as f:
            f.write(o.decode("utf-8") )
        print (o)
        p = subprocess.check_output('./test_suites/tls_enable.sh')
        # p = subprocess.Popen('./tls-enable.sh', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # p.wait()
        # out, err = p.communicate()
        print(p)
