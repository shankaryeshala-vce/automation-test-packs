import os
os.system('py.test $AF_TEST_SUITE_PATH/ -m "soaking" --html $AF_REPORTS_PATH/all/soaking_test_report.html --self-contained-html --json $AF_REPORTS_PATH/all/soaking_test_report.json --junit-xml $AF_REPORTS_PATH/all/soaking_test_report.xml')
