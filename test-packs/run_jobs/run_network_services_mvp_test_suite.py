import os
os.system('py.test $AF_TEST_SUITE_PATH/ -s -m "network_services_mvp" --html $AF_REPORTS_PATH/all/network_services_mvp_test_suite_report.html --self-contained-html --json $AF_REPORTS_PATH/all/network_services_mvp_test_suite_report.json --junit-xml $AF_REPORTS_PATH/all/network_services_mvp_test_suite_report.xml')
