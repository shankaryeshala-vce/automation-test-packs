#!/usr/bin/python
# Author: SherryFeng
# Revision: 1.0
# Code Reviewed by:
# Description: Configure cAdvisor container on Symphony ova vm for soaking test enviroment.

import af_support_tools
import time
import paramiko

cli_username = 'root'
cli_password = 'V1rtu@1c3!'

port = 9820

# this ipadress is symphony ova vm IP
ipaddress = '10.3.60.230'
AF_host_ipaddress = '10.3.60.225'

#######################################################################################################################
def cAdvisor_Setup():

    print('Configuring cAdvisor container on Symphony system: ', ipaddress)

    # Create and edit the cadvisor configuration file
    dirname = '/root/cadvisor'
    filename = 'cadvisor.sh'
    file_text = 'docker run --volume=/:/rootfs:ro  \
           --volume=/var/run:/var/run:rw  \
           --volume=/sys:/sys:ro  \
           --volume=/var/lib/docker/:/var/lib/docker:ro  \
           --publish=9820:9820  \
           --detach=true  \
           --name=cadvisor google/cadvisor:latest  \
             -port=9820 \
             -storage_driver=influxdb  \
             -storage_driver_db=cadvisor  \
             -storage_driver_user=root \
             -storage_driver_password=root \
             -storage_driver_host=10.3.60.225:8086'.encode('ascii')

    # copy cadvisor docker compose file to symphyony ova vm
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ipaddress, username=cli_username, password=cli_password)
    sftp = ssh.open_sftp()
    try:
        sftp.mkdir(dirname)
    except IOError:
        pass
    f = sftp.open(dirname + '/' + filename, 'w')
    f.write(file_text)
    f.close()

    # check if cAdvisor is already configured
    my_return = af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                     command='docker inspect -f {{.State.Running}} cadvisor',return_output=True)
    my_return = my_return.strip()

    if  my_return != 'true':
        af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                     command='chmod 777 /root/cadvisor/cadvisor.sh', return_output=True)
    # Send the command to create cadvisor container
        af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                      command='/root/cadvisor/cadvisor.sh',
                                     return_output=True)
    # Wait for cadvisor image is downloaded
        time.sleep(120)

    else:
        print('cAdvisor configuration is already configured')

  # Validate if cadvisor container is up

    my_return = af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                     command='docker inspect -f {{.State.Running}} cadvisor',return_output=True)
    my_return = my_return.strip()

    if  my_return == 'true':
        print('cAdvisor container is up')
    else:
        print('cAdvisor configuration is failed')


    ssh.close()


#######################################################################################################################

cAdvisor_Setup()