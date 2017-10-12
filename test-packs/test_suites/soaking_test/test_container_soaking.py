#!/usr/bin/python
# Copyright © 2017 Dell Inc. or its subsidiaries.  All Rights Reserved
# Author: SherryFeng
# Revision: 2.0
# Code Reviewed by:
# Description: Configure cAdvisor container on Symphony ova vm for soaking test enviroment.

import af_support_tools
import pytest
#import time
#import paramiko


@pytest.fixture(scope="module", autouse=True)
def load_test_data():
    # Set CPSD common props as global var
    import cpsd
    global cpsd

    # Set config ini file name
    # These can be set inside the individual tests and do not need to be made global
    global config_file
    config_file = 'soaking_test/soaking.ini'

    # Set Vars
    global symphony_hostname
    symphony_hostname = cpsd.props.base_hostname
    global symphony_username
    symphony_username = cpsd.props.base_username
    global symphony_password
    symphony_password = cpsd.props.base_password

    global containers
    containers = af_support_tools.get_config_file_property(config_file=config_file, heading='soaking', property='container_list')
    containers = containers.split(',')

#######################################################################################################################
@pytest.mark.soaking
def test_maliska():
    print('List of Containers')
    print(containers)
    print(type(containers))
    assert 5 == 5

#######################################################################################################################
@pytest.mark.soaking
def test_containers_soaking():
    print('Check all containers up on Symphony system: ', symphony_hostname)
    test_all_containers_up()
    test_Container_CPU_MEM()

#######################################################################################################################

#1. Check all container up
@pytest.mark.soaking
def test_all_containers_up():
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

#2. Check each container CPU and Memory usages
@pytest.mark.soaking
def test_Container_CPU_MEM():
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


def checkContainerStats(service, ipaddress):
    #cpu_cmd = "docker stats --no-stream " + service + " | grep -v CPU | awk \'{print $2}\' | cut -f1 -d\'%\' "
    cpu_cmd = "docker stats --no-stream " + service + " | grep -v CPU | awk '{print $2}' | cut -f1 -d'%' "
    #mem_cmd = "docker stats --no-stream " + service + " | grep -v MEM | awk \'{print $8}\' | cut -f1 -d\'%\' "
    mem_cmd = "docker stats --no-stream " + service + " | grep -v MEM | awk '{print $8}' | cut -f1 -d'%' "
    cpu_resp = af_support_tools.send_ssh_command(host=symphony_hostname, username=symphony_username, password=symphony_password, command=cpu_cmd, return_output=True)
    mem_resp = af_support_tools.send_ssh_command(host=symphony_hostname, username=symphony_username, password=symphony_password, command=mem_cmd, return_output=True)
    return float(cpu_resp), float(mem_resp)
