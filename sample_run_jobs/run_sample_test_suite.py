import os
os.system('py.test $AF_TEST_SUITE_PATH/sample/test_sample.py --html $AF_REPORTS_PATH/sample_test_suite/sample_report.html --self-contained-html --json $AF_REPORTS_PATH/sample_test_suite/sample_report.json --junit-xml $AF_REPORTS_PATH/sample_test_suite/sample_report.xml')
