
cd $AF_LIB_PATH
python $AF_LIB_PATH/setup.py build
python $AF_LIB_PATH/setup.py install
. $AF_LIB_PATH/lib_testing/run_lib_testing_test_suite.sh