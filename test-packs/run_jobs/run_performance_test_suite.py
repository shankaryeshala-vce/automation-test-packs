# Copyright © 2017 Dell Inc. or its subsidiaries.  All Rights Reserved
import os
os.system('py.test $AF_TEST_SUITE_PATH/ -m "performance" --html $AF_REPORTS_PATH/all/performance_report.html --self-contained-html --json $AF_REPORTS_PATH/all/performance_report.json --junit-xml $AF_REPORTS_PATH/all/performance_report.xml')
