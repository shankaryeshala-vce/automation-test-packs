. $HOME/af_env.sh
py3clean .
export AF_TEST_SUITE_NAME='Teat Automation Framework MVP Extended'
python $AF_RUN_JOBS_PATH/run_taf_mvp_extended_test_suite.py
export AF_TEST_SUITE_NAME='Test Suite Name Not Set'