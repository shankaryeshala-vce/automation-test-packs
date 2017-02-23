
### sudo user password: Password01! ###

### Post Install (Non-Docker Image Only) 
# PhantomJS
echo Password01! | sudo -s --stdin cd ~
echo Password01! | sudo -s --stdin rm -f phantomjs-1.9.8-linux-x86_64.tar.bz2
echo Password01! | sudo -s --stdin wget --no-check-certificate https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-1.9.8-linux-x86_64.tar.bz2
echo Password01! | sudo -s --stdin tar xvjf phantomjs-1.9.8-linux-x86_64.tar.bz2
echo Password01! | sudo -s --stdin mv phantomjs-1.9.8-linux-x86_64 /usr/local/share
echo Password01! | sudo -s --stdin ln -sf /usr/local/share/phantomjs-1.9.8-linux-x86_64/bin/phantomjs /usr/local/bin
echo Password01! | sudo -s --stdin rm -f phantomjs-1.9.8-linux-x86_64.tar.bz2
echo Password01! | sudo -s --stdin rm -rf phantomjs-1.9.8-linux-x86_64

### Automation Framework Install ###
rm -rf /home/autouser/Documents/virt_envs/af_env
virtualenv /home/autouser/Documents/virt_envs/af_env -p python3
source /home/autouser/Documents/virt_envs/af_env/bin/activate
pip install -r $AF_BASE_PATH/env_setup/pip_freeze_v_1.txt

echo "import pytest" > $AF_BASE_PATH/test_af_sanity.py
echo "" >> $AF_BASE_PATH/test_af_sanity.py
echo "@pytest.mark.af_sanity" >> $AF_BASE_PATH/test_af_sanity.py
echo "def test_sanity():" >> $AF_BASE_PATH/test_af_sanity.py
echo "    assert 5 == 5" >> $AF_BASE_PATH/test_af_sanity.py
echo "    print ('Sanity Test')" >> $AF_BASE_PATH/test_af_sanity.py
chmod +x $AF_BASE_PATH/test_af_sanity.py

echo "source /home/autouser/Documents/virt_envs/af_env/bin/activate" > /home/autouser/af_env.sh
echo "cd $AF_BASE_PATH" >> /home/autouser/af_env.sh
echo "py.test $AF_BASE_PATH/test_af_sanity.py --html $AF_REPORTS_PATH/af_sanity/af_sanity_report.html --self-contained-html" >> /home/autouser/af_env.sh
chmod +x /home/autouser/af_env.sh

cd $AF_LIB_PATH
python $AF_LIB_PATH/setup.py build
python $AF_LIB_PATH/setup.py install

cd $AF_BASE_PATH
py.test $AF_BASE_PATH/test_af_sanity.py --html $AF_REPORTS_PATH/af_sanity/af_sanity_report.html --self-contained-html

### Sample Run Jobs
cp -R $AF_BASE_PATH/sample_run_jobs/* $AF_RUN_JOBS_PATH

### Sample Test Suite
cp -R $AF_BASE_PATH/sample_test_suite/* $AF_TEST_SUITE_PATH
