. $HOME/af_env.sh
py3clean .
export AF_TEST_SUITE_NAME='RCM Fitness MVP EXTENDED'
python $AF_RUN_JOBS_PATH/run_rcm_fitness_mvp_extended_test_suite.py
export AF_TEST_SUITE_NAME='Test Suite Name Not Set'
