
### sudo user password: Password01!

### Post Install (Non-Docker Image Only) 
# PhantomJS
#echo Password01! | sudo -s --stdin cd ~
#echo Password01! | sudo -s --stdin rm -f phantomjs-1.9.8-linux-x86_64.tar.bz2
#echo Password01! | sudo -s --stdin wget --no-check-certificate https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-1.9.8-linux-x86_64.tar.bz2
#echo Password01! | sudo -s --stdin tar xvjf phantomjs-1.9.8-linux-x86_64.tar.bz2
#echo Password01! | sudo -s --stdin mv phantomjs-1.9.8-linux-x86_64 /usr/local/share
#echo Password01! | sudo -s --stdin ln -sf /usr/local/share/phantomjs-1.9.8-linux-x86_64/bin/phantomjs /usr/local/bin
#echo Password01! | sudo -s --stdin rm -f phantomjs-1.9.8-linux-x86_64.tar.bz2
#echo Password01! | sudo -s --stdin rm -rf phantomjs-1.9.8-linux-x86_64

### Automation Framework Install ###
rm -rf /home/autouser/Documents/virt_envs/af_env
virtualenv /home/autouser/Documents/virt_envs/af_env -p python3
source /home/autouser/Documents/virt_envs/af_env/bin/activate
pip install -r /home/autouser/PycharmProjects/auto-framework/env_setup/pip_freeze_v_1.txt

echo "import pytest" > /home/autouser/PycharmProjects/auto-framework/test_af_sanity.py
echo "" >> /home/autouser/PycharmProjects/auto-framework/test_af_sanity.py
echo "@pytest.mark.af_sanity" >> /home/autouser/PycharmProjects/auto-framework/test_af_sanity.py
echo "def test_sanity():" >> /home/autouser/PycharmProjects/auto-framework/test_af_sanity.py
echo "    assert 5 == 5" >> /home/autouser/PycharmProjects/auto-framework/test_af_sanity.py
echo "    print ('Sanity Test')" >> /home/autouser/PycharmProjects/auto-framework/test_af_sanity.py
chmod +x /home/autouser/PycharmProjects/auto-framework/test_af_sanity.py

echo "source /home/autouser/Documents/virt_envs/af_env/bin/activate" > /home/autouser/af_env.sh
echo "cd /home/autouser/PycharmProjects/auto-framework" >> /home/autouser/af_env.sh
echo "py.test /home/autouser/PycharmProjects/auto-framework/test_af_sanity.py --html /home/autouser/PycharmProjects/auto-framework/test_suites/reports/af_sanity/af_sanity_report.html --self-contained-html" >> /home/autouser/af_env.sh
chmod +x /home/autouser/af_env.sh

cd /home/autouser/PycharmProjects/auto-framework/libs
python /home/autouser/PycharmProjects/auto-framework/libs/setup.py build
python /home/autouser/PycharmProjects/auto-framework/libs/setup.py install

cd /home/autouser/PycharmProjects/auto-framework
py.test /home/autouser/PycharmProjects/auto-framework/test_af_sanity.py --html /home/autouser/PycharmProjects/auto-framework/test_suites/reports/af_sanity/af_sanity_report.html --self-contained-html

### Sample Run Jobs
cp -R /home/autouser/PycharmProjects/auto-framework/sample_run_jobs/* /home/autouser/PycharmProjects/auto-framework/run_jobs

### Sample Test Suite
cp -R /home/autouser/PycharmProjects/auto-framework/sample_test_suite/* /home/autouser/PycharmProjects/auto-framework/test_suites
