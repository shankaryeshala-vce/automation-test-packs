# Copyright © 2017 Dell Inc. or its subsidiaries.  All Rights Reserved
import os
os.system('py.test $AF_TEST_SUITE_PATH/ -m "rcm_fitness_mvp" --html $AF_REPORTS_PATH/all/rcm_fitness_mvp_test_suite_report.html --self-contained-html --json $AF_REPORTS_PATH/all/rcm_fitness_mvp_test_suite_report.json --junit-xml $AF_REPORTS_PATH/all/rcm_fitness_mvp_test_suite_report.xml')