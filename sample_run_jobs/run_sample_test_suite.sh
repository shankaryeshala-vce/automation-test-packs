. $HOME/af_env.sh
py3clean .
export AF_TEST_SUITE_NAME='Sample'
python $AF_RUN_JOBS_PATH/run_sample_test_suite.py
export AF_TEST_SUITE_NAME='Test Suite Name Not Set'