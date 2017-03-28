#!/usr/bin/python
# Author: Toqeer Akhtar
# Updated by: Linjong Fogarty
# Revision:2.0
# Code Reviewed by: Joe, Trevor
# Description: This script will runt against newly deployed OVA and perform a sanitu check for Dockerise servecies.
########################################################################################################################

import af_support_tools
import pytest
import time
import pika

try:
    env_file = 'env.ini'
    ipaddress = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='hostname')

except:
    print('Possible configuration error')

# # Only one if these ipaddress lines should be enabled at any one time
# ipaddress = '10.3.8.54'
# # ipaddress = sys.argv[1]
# port = 5672

########################################################################################################################

@pytest.mark.rcm_fitness_mvp
@pytest.mark.parametrize("service_name" , [
    "symphony-credential-service",
    "symphony-system-definition-service",
    "symphony-hal-orchestrator-service",
    "symphony-rcm-compliance-data-service",
    "symphony-rcm-definition-service",
    "symphony-rcm-evaluation-service",
    "symphony-identity-service",
    "symphony-rcm-fitness-client",
    "symphony-capability-registration-service",
    "symphony-endpoint-registration-service",
    "symphony-hdp-cisco-network-service",
    "symphony-hdp-poweredge-compute",
    "symphony-dne-paqx"

])
# checking if all dockter container servises are up. Assert if services are not up
def test_servicerunning(service_name):
    svrrun_err = []
    global services_running

    sendCommand = "docker ps --filter name=" + service_name + "  --format '{{.Status}}' | awk '{print $1}'"
    my_return_status = af_support_tools.send_ssh_command(host=ipaddress, username='root', password='V1rtu@1c3!', command=sendCommand, return_output=True)

    if "Up" not in my_return_status:
        svrrun_err.append(service_name + " not running")

    service_name_pid = service_name.replace("symphony-","").replace("-service","").replace("-registration","")
    sendCommand_pid = "ps -ef | grep " + service_name_pid +" |grep java | awk '{print $2}'"
    my_return_pid = af_support_tools.send_ssh_command(host=ipaddress, username='root', password='V1rtu@1c3!', command=sendCommand_pid, return_output=True)
    pid = my_return_pid.strip('\n')

    sendCommand_netstat = "netstat -ntp | grep -i \"{}/java\"".format(pid)
    my_return_netstat = af_support_tools.send_ssh_command(host=ipaddress, username='root', password='V1rtu@1c3!', command=sendCommand_netstat, return_output=True)
    if "ESTABLISHED" not in my_return_netstat:
        svrrun_err.append(service_name + " rabbit connection not established")

    assert not svrrun_err

    print("Successful status check performed on: %s" % service_name)

########################################################################################################################

@pytest.mark.rcm_fitness_mvp
@pytest.mark.rabbitrunning
def test_rabbitrunning():
    rab_err = []

    sendCommand = "service rabbitmq-server status"
    rabbit_status = af_support_tools.send_ssh_command(host=ipaddress, username='root', password='V1rtu@1c3!', command=sendCommand, return_output=True)

    if "running" not in rabbit_status:
        rab_err.append("rabbitmq-server not running")

    assert not rab_err

#####################################################END OF TEST########################################################