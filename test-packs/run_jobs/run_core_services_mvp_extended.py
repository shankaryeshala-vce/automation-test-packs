import os
os.system('py.test $AF_TEST_SUITE_PATH/ -m "core_services_mvp_extended" --html $AF_REPORTS_PATH/all/core_services_mvp_extended_report.html --self-contained-html --json $AF_REPORTS_PATH/all/core_services_mvp_extended_report.json --junit-xml $AF_REPORTS_PATH/all/core_services_mvp_extended_report.xml')
