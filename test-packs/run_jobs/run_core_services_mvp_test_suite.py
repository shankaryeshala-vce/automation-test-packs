# Copyright © 2017 Dell Inc. or its subsidiaries.  All Rights Reserved
import os
os.system('py.test $AF_TEST_SUITE_PATH/ -m "core_services_mvp" --html $AF_REPORTS_PATH/all/core_services_mvp_report.html --self-contained-html --json $AF_REPORTS_PATH/all/core_services_mvp_report.json --junit-xml $AF_REPORTS_PATH/all/core_services_mvp_report.xml')