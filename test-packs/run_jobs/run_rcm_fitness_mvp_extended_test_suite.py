import os
os.system('py.test $AF_TEST_SUITE_PATH/ -m "rcm_fitness_mvp_extended" --html $AF_REPORTS_PATH/all/rcm_fitness_mvp_extended_test_suite_report.html --self-contained-html --json $AF_REPORTS_PATH/all/rcm_fitness_mvp_extended_test_suite_report.json --junit-xml $AF_REPORTS_PATH/all/rcm_fitness_mvp_extended_test_suite_report.xml')
