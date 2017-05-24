#!/usr/bin/python

# Author: SherryFeng

# Revision: 2.0

# Code Reviewed by:

# Description: Configure cAdvisor container on Symphony ova vm for soaking test enviroment.

import pytest
import af_support_tools
import time
import paramiko


try:
    env_file = 'env.ini'
    symphony_hostname = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='hostname')
    symphony_username = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='username')
    symphony_password = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='password')
except:
    print('Possible configuration error')

try:
    container_file = '/home/autouser/automation-test-packs/test-packs/test_suites/config_files/performance/container_list.ini'
    with open (container_file) as f:
        containers = f.read().splitlines()
    print(containers)
except:
    print('Possible container list error')


#######################################################################################################################

def test_containers_soaking():
    print('Check all containers up on Symphony system: ', symphony_hostname)
    Check_all_containers_up()
    Check_Container_CPU_MEM()


#######################################################################################################################
#1. Check all container up
def Check_all_containers_up():

    with open (container_file) as f:
        containers = f.read().splitlines()
    print(containers)

    container_up = []
    container_down = []
    container_up_num = 0
    container_down_num = 0

  # Validate if containers are up
    if (len(containers)):

       for i in range(len(containers)):
           container_name = containers[i]
           print('This container is')
           print(container_name)
           send_command = 'docker inspect -f {{.State.Running}} ' + container_name
           my_return = af_support_tools.send_ssh_command(host=symphony_hostname, username=symphony_username, password=symphony_password,

                                     command=send_command,return_output=True)
           my_return = my_return.strip()
           print('my_return:')
           print(my_return)
           if  my_return == 'true':
               print('Container ',container_name,' is up \n')
               container_up.append(container_name)
               container_up_num = container_up_num + 1
           else:
               print('Container ',container_name,'is down \n')
               container_down.append(container_name)
               container_down_num = container_down_num + 1

    print('Total ',container_up_num,' containers up list:',container_up,' \n')
    print('Total ',container_down_num,' containers down list:',container_down,' \n')

    assert not container_down_num

#######################################################################################################################


#2. check all container stats
def checkContainerStats(service, ipaddress):
    #cpu_cmd = "docker stats --no-stream " + service + " | grep -v CPU | awk \'{print $2}\' | cut -f1 -d\'%\' "
    cpu_cmd = "docker stats --no-stream " + service + " | grep -v CPU | awk '{print $2}' | cut -f1 -d'%' "
    #mem_cmd = "docker stats --no-stream " + service + " | grep -v MEM | awk \'{print $8}\' | cut -f1 -d\'%\' "
    mem_cmd = "docker stats --no-stream " + service + " | grep -v MEM | awk '{print $8}' | cut -f1 -d'%' "
    cpu_resp = af_support_tools.send_ssh_command(host=symphony_hostname, username=symphony_username, password=symphony_password, command=cpu_cmd, return_output=True)
    mem_resp = af_support_tools.send_ssh_command(host=symphony_hostname, username=symphony_username, password=symphony_password, command=mem_cmd, return_output=True)
    return float(cpu_resp), float(mem_resp)

###################################################################################################
#3. Check each container CPU and Memory usages
def Check_Container_CPU_MEM():
    # start by printing docker stats for all services for posterity
    services = containers
    print('Check all the containers: \n',services)
    #all_cmd = "docker stats --no-stream \$\(docker ps --format \'{{.Names}}\'\)"
    all_cmd = "docker stats --no-stream $(docker ps --format '{{.Names}}')"
    all_resp = af_support_tools.send_ssh_command(host=symphony_hostname, username=symphony_username, password=symphony_password, command=all_cmd, return_output=True)
    print(all_resp)

    # then check each service individually
    for servicename in services:
        cpuPercent, memPercent = checkContainerStats(servicename, symphony_hostname)
        print(servicename,'cpuPercent ',cpuPercent,'memPercent ',memPercent)
        assert cpuPercent <= 50.0, "The docker container CPU usage is over 50% for"  + servicename
        assert memPercent <= 50.0, "The docker container memory usage is over 50% for "  + servicename

####################################################################################################
