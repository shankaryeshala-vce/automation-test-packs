# Copyright © 2017 Dell Inc. or its subsidiaries.  All Rights Reserved
. $HOME/af_env.sh
py3clean .
export AF_TEST_SUITE_NAME='Core Services MVP EXTENDED'
python $AF_RUN_JOBS_PATH/run_core_services_mvp_extended_test_suite.py
export AF_TEST_SUITE_NAME='Test Suite Name Not Set'
