. $HOME/af_env.sh
py3clean .
export AF_TEST_SUITE_NAME='Collection Only'
python $AF_RUN_JOBS_PATH/run_collection_only.py
export AF_TEST_SUITE_NAME='Test Suite Name Not Set'