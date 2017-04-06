import os
os.system('py.test $AF_TEST_SUITE_PATH/ -m "logcollection" --html $AF_REPORTS_PATH/all/performance_test_packs_report.html --self-contained-html --json $AF_REPORTS_PATH/all/performance_test_packs_report.json --junit-xml $AF_REPORTS_PATH/all/performance_test_packs_report.xml')
