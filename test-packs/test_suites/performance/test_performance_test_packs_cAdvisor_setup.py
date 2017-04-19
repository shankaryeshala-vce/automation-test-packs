#!/usr/bin/python

# Author: SherryFeng

# Revision: 2.0

# Code Reviewed by:

# Description: Configure cAdvisor container on Symphony ova vm for soaking test enviroment.


import af_support_tools

import time

import paramiko


try:

    env_file = 'env.ini'

        # READ IN MACHINE INFO

    perf_hostname = af_support_tools.get_config_file_property(config_file=env_file, heading='PBase_OS', property='hostname')

    perf_username = af_support_tools.get_config_file_property(config_file=env_file, heading='PBase_OS', property='username')

    perf_password = af_support_tools.get_config_file_property(config_file=env_file, heading='PBase_OS', property='password')

    symphony_hostname = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='hostname')

    symphony_username = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='username')

    symphony_password = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='password')


except:

    print('Possible configuration error')


port = 9820


#######################################################################################################################
@pytest.mark.performance
def cAdvisor_Setup():


    print('Configuring cAdvisor container on Symphony system: ', symphony_hostname)


    # Create and edit the cadvisor configuration file

    dirname = '/root/cadvisor'

    filename = 'cadvisor.sh'

    file_text_1 = 'docker run --volume=/:/rootfs:ro  \\ \n'

    file_text_1 = file_text_1 + '         --volume=/var/run:/var/run:rw  \\ \n'

    file_text_1 = file_text_1 + '         --volume=/sys:/sys:ro  \\ \n'

    file_text_1 = file_text_1 + '         --volume=/var/lib/docker/:/var/lib/docker:ro  \\ \n'

    file_text_1 = file_text_1 + '         --publish=9820:9820  \\ \n'

    file_text_1 = file_text_1 + '         --detach=true  \\ \n'

    file_text_1 = file_text_1 + '         --name=cadvisor google/cadvisor:latest  \\ \n'

    file_text_1 = file_text_1 + '           -port=9820 \\ \n'

    file_text_1 = file_text_1 + '           -storage_driver=influxdb  \\ \n'

    file_text_1 = file_text_1 + '           -storage_driver_db=cadvisor  \\ \n'

    file_text_1 = file_text_1 + '           -storage_driver_user=root \\ \n'

    file_text_1 = file_text_1 + '           -storage_driver_password=root \\ \n'

    file_text_1 = file_text_1 + '           -storage_driver_host='.encode('ascii')


    file_text_2 = ':8086'.encode('ascii')


    # copy cadvisor docker compose file to symphyony ova vm

    ssh = paramiko.SSHClient()

    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ssh.connect(symphony_hostname, username=symphony_username, password=symphony_password)

    sftp = ssh.open_sftp()

    try:

        sftp.mkdir(dirname)

    except IOError:

        pass

    f = sftp.open(dirname + '/' + filename, 'w')

    f.write(file_text_1)

    f.write(perf_hostname)

    f.write(file_text_2)

    f.close()


    # check if cAdvisor is already configured

    my_return = af_support_tools.send_ssh_command(host=symphony_hostname, username=symphony_username, password=symphony_password,

                                     command='docker inspect -f {{.State.Running}} cadvisor',return_output=True)

    my_return = my_return.strip()


    if  my_return != 'true':

        af_support_tools.send_ssh_command(host=symphony_hostname, username=symphony_username, password=symphony_password,

                                     command='chmod 777 /root/cadvisor/cadvisor.sh', return_output=True)

    # Send the command to create cadvisor container

        af_support_tools.send_ssh_command(host=symphony_hostname, username=symphony_username, password=symphony_password,

                                      command='/root/cadvisor/cadvisor.sh',

                                     return_output=True)

    # Wait for cadvisor image is downloaded

        time.sleep(120)


    else:

        print('cAdvisor configuration is already configured')


  # Validate if cadvisor container is up


    my_return = af_support_tools.send_ssh_command(host=symphony_hostname, username=symphony_username, password=symphony_password,

                                     command='docker inspect -f {{.State.Running}} cadvisor',return_output=True)

    my_return = my_return.strip()


    if  my_return == 'true':

        print('cAdvisor container is up')

    else:

        print('cAdvisor configuration is failed')


    ssh.close()


　

#######################################################################################################################


cAdvisor_Setup()


　
　
