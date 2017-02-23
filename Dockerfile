FROM ubuntu:latest
# FROM ubuntu:14.04
# Prerequisites
RUN apt-get update && \
 #apt-get install -y apt-utils && \
 apt-get install -y python3 && \
 apt-get install -y sudo && \
 apt-get install -y zip && \
 apt-get install -y build-essential && \
 apt-get install -y libssl-dev && \
 apt-get install -y libffi-dev && \
 apt-get install -y python3-dev && \
 apt-get install -y python-pip && \
 apt-get install -y vim && \
 apt-get install -y wget && \
 apt-get install -y build-essential && \
 apt-get install -y chrpath && \
 apt-get install -y libssl-dev && \
 apt-get install -y libxft-dev && \
 apt-get install -y libfreetype6 && \
 apt-get install -y libfreetype6-dev && \
 apt-get install -y libfontconfig1 && \
 apt-get install -y libfontconfig1-dev && \
 apt-get install -y dos2unix && \
 pip install virtualenv && \

# PhantomJS
 cd ~  && \
 rm -f phantomjs-1.9.8-linux-x86_64.tar.bz2 && \
 wget --no-check-certificate https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-1.9.8-linux-x86_64.tar.bz2 && \
 tar xvjf phantomjs-1.9.8-linux-x86_64.tar.bz2 && \
 mv phantomjs-1.9.8-linux-x86_64 /usr/local/share && \
 ln -sf /usr/local/share/phantomjs-1.9.8-linux-x86_64/bin/phantomjs /usr/local/bin && \
 rm -f phantomjs-1.9.8-linux-x86_64.tar.bz2 && \
 rm -rf phantomjs-1.9.8-linux-x86_64 && \

# Open SSH 
 apt-get install -y openssh-server && \
 mkdir /var/run/sshd && \
 echo 'root:V1rtu@1c3!' | chpasswd && \
 adduser autouser && \
 echo 'autouser:Password01!' | chpasswd && \
 usermod -aG sudo autouser && \
 sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \
 sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd && \
 apt-get install -y sshpass && \

# ENV VARS
 echo "export VISIBLE=now" >> /etc/profile && \
 echo "export AF_TEST_SUITE_NAME=Test_Suite_Name_Not_Set;" >> /etc/profile && \
 echo "export AF_LIB_PATH=/home/autouser/PycharmProjects/auto-framework/libs;" >> /etc/profile && \
 echo "export AF_TEST_SUITE_PATH=/home/autouser/PycharmProjects/auto-framework/test_suites;" >> /etc/profile && \
 echo "export AF_REPORTS_PATH=/home/autouser/PycharmProjects/auto-framework/test_suites/reports;" >> /etc/profile && \
 echo "export AF_RUN_JOBS_PATH=/home/autouser/PycharmProjects/auto-framework/run_jobs;" >> /etc/profile && \
 echo "export AF_BASE_PATH=/home/autouser/PycharmProjects/auto-framework;" >> /etc/profile && \
 echo "export PYTEST_ADDOPTS=-v" >> /etc/profile && \
 echo "export DISPLAY=:0;" >> /etc/profile && \

 echo "VISIBLE=now" >> /etc/environment && \
 echo "AF_TEST_SUITE_NAME=Test_Suite_Name_Not_Set" >> /etc/environment && \
 echo "AF_LIB_PATH=/home/autouser/PycharmProjects/auto-framework/libs" >> /etc/environment && \
 echo "AF_TEST_SUITE_PATH=/home/autouser/PycharmProjects/auto-framework/test_suites" >> /etc/environment && \
 echo "AF_REPORTS_PATH=/home/autouser/PycharmProjects/auto-framework/test_suites/reports" >> /etc/environment && \
 echo "AF_RUN_JOBS_PATH=/home/autouser/PycharmProjects/auto-framework/run_jobs" >> /etc/environment && \
 echo "AF_BASE_PATH=/home/autouser/PycharmProjects/auto-framework" >> /etc/environment && \
 echo "PYTEST_ADDOPTS=-v" >> /etc/environment && \
 echo "DISPLAY=:0" >> /etc/environment && \

# TAF Platform
 echo "Version=$(date)" > /home/autouser/docker-version.txt && \
 
# Install Test Automation Framework
 echo "cd" > /af_install.sh && \
 echo "rm auto-framework.zip" >> /af_install.sh && \
 echo "wget http://ci-build.mpe.lab.vce.com:8080/view/All/job/auto-framework-zip.pytest/ws/auto-framework.zip" >> /af_install.sh && \
 echo "chmod +x auto-framework.zip" >> /af_install.sh && \
 echo "mkdir -p /home/autouser/PycharmProjects/auto-framework" >> /af_install.sh && \
 echo "unzip -o auto-framework.zip -d /home/autouser/PycharmProjects/auto-framework" >> /af_install.sh && \
 echo ". /home/autouser/PycharmProjects/auto-framework/env_setup/af_setup_docker.sh" >> /af_install.sh && \
 su autouser /af_install.sh

# Startup
ENV NOTVISIBLE "in users profile"
EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]
