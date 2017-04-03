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

#@pytest.mark.rcm_fitness_mvp
@pytest.mark.core_services_mvp
@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_cd
@pytest.mark.core_services_cd
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

@pytest.mark.core_services_cd
@pytest.mark.rcm_fitness_cd
@pytest.mark.parametrize("service_name, pid", [
    ("symphony-system-definition-service", "/cpsd/system-definition/"),
    ("symphony-hal-orchestrator-service", "/cpsd/hal-orchestrator/"),
    ("symphony-credential-service", "/cpsd/credential/"),
    ("symphony-rcm-compliance-data-service", "/cpsd/rcm-fitness/rcm-compliance-data/"),
    ("symphony-rcm-definition-service", "cpsd/rcm-fitness/rcm-definition/"),
    ("symphony-rcm-evaluation-service", "cpsd/rcm-fitness/rcm-evaluation/"),
    ("symphony-identity-service" , "/cpsd/identity-service/"),
    ("symphony-rcm-fitness-client", "rcm-fitness-client"),
    ("symphony-capability-registration-service", "/cpsd/registration-services/capability-registry/"),
    ("symphony-endpoint-registration-service", "/cpsd/registration-services/endpoint-registration/"),
    ("symphony-hdp-cisco-network-service", "/cpsd/hal/providers/hdp-cisco-network/"),
    ("symphony-hdp-poweredge-compute", "/cpsd/hal/providers/hdp-poweredge-compute/"),
    ("symphony-dne-paqx", "dne-paqx")


])


# @pytest.mark.parametrize("service_name, pid", [
#     ("symphony-credential-service", "services/credential/")
# ])

def test_servicestopstart(service_name, pid):
    svrstpstrt_err = []


    #sendCommand_pid = "ps -ef | grep " + service_name_pid +" |grep java | awk '{print $2}'"
    sendCommand_pid = "ps -ef | grep -i " + pid + "| grep -v grep |grep java | awk \'FNR == 1 {print$2}\'"
    my_return_pid = af_support_tools.send_ssh_command(host=ipaddress, username='root', password='V1rtu@1c3!', command=sendCommand_pid, return_output=True)
    initial_pid = my_return_pid.rstrip('\n')
    print ("ps pid " +initial_pid)

    get_pid = "netstat -ntp | grep -i \":5672.*ESTABLISHED.*{}/java\"".format(initial_pid)
    sendCommand_netstat = ""+ get_pid +" | awk \'{print $7}\'"
    return_netstat_pid = af_support_tools.send_ssh_command(host=ipaddress, username='root', password='V1rtu@1c3!', command=sendCommand_netstat, return_output=True)
    return_netstat_pid = return_netstat_pid.replace("/java", "") .split("\n")[0]
    print ("netstat pid " +return_netstat_pid)


    #Saving the ContainerIds in the list Container_id
    sendCommand_ContainerID = "docker ps --filter name=" + service_name + "  --format '{{.ID}}'"
    return_ContainerID = af_support_tools.send_ssh_command(host=ipaddress, username='root', password='V1rtu@1c3!', command=sendCommand_ContainerID, return_output=True)
    Container_id = return_ContainerID

    #Stoppping service individually
    if initial_pid == return_netstat_pid:
        print ("stopping docker Container")
        sendCommand_stop = "docker stop " + Container_id
        return_stop = af_support_tools.send_ssh_command(host=ipaddress, username='root', password='V1rtu@1c3!', command=sendCommand_stop, return_output=True)

        sendCommand = "docker ps --filter name=" + service_name + "  --format '{{.Status}}' | awk '{print $1}'"
        my_return_status = af_support_tools.send_ssh_command(host=ipaddress, username='root', password='V1rtu@1c3!', command=sendCommand, return_output=True)


        if "Up" in my_return_status:
            svrstpstrt_err.append(service_name + " still running")

        print ("starting docker container")
        sendCommand_start = "docker start " + Container_id
        return_start = af_support_tools.send_ssh_command(host=ipaddress, username='root', password='V1rtu@1c3!', command=sendCommand_start, return_output=True)

    #time.sleep(60)
    sendCommand = "docker ps --filter name=" + service_name + "  --format '{{.Status}}' | awk '{print $1}'"
    my_return_status = af_support_tools.send_ssh_command(host=ipaddress, username='root', password='V1rtu@1c3!', command=sendCommand, return_output=True)
    print ("docker Status " +my_return_status )


    if "Up" not in my_return_status:
        svrstpstrt_err.append(service_name + " not started")

    sendCommand_pid = "ps -ef | grep -i " + pid + "| grep -v grep |grep java | awk \'FNR == 1 {print$2}\'"
    my_return_pid = af_support_tools.send_ssh_command(host=ipaddress, username='root', password='V1rtu@1c3!', command=sendCommand_pid, return_output=True)
    post_pid = my_return_pid.rstrip('\n')
    print (post_pid)

    time.sleep(25)
    #sendCommand_netstat2 = "netstat -ntp | grep -i \"{}/java\"".format(post_pid)
    sendCommand_netstat2 = "netstat -ntp | grep -i \":5672.*ESTABLISHED.*{}/java\"".format(post_pid)
    my_return_netstat2 = af_support_tools.send_ssh_command(host=ipaddress, username='root', password='V1rtu@1c3!', command=sendCommand_netstat2, return_output=True)
    print (my_return_netstat2)

    if "ESTABLISHED" not in my_return_netstat2:
        time.sleep(70)
        #print (my_return_netstat2)
        if "ESTABLISHED" not in my_return_netstat2:
            svrstpstrt_err.append(service_name + " rabbit connection not established")


            assert not svrstpstrt_err

########################################################################################################################

def test_servicestop_yml():
    #stop/start docker containers using yml file
    print ("stopping docker container using yml")
    sendCommand_yml_down = "docker-compose -f /opt/dell/rcm-fitness/common/install/docker-compose.yml down"
    my_return_down = af_support_tools.send_ssh_command(host=ipaddress, username='root', password='V1rtu@1c3!', command=sendCommand_yml_down, return_output=True)

@pytest.mark.core_services_cd
@pytest.mark.rcm_fitness_cd
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
def test_chkupStatus_yml(service_name):
    chkup_err = []

    print ("checking yml up status TBD")
    sendCommand = "docker ps --filter name=" + service_name + "  --format '{{.Status}}' | awk '{print $1}'"
    my_return_status1 = af_support_tools.send_ssh_command(host=ipaddress, username='root', password='V1rtu@1c3!', command=sendCommand, return_output=True)

    if "Up" in my_return_status1:
        chkup_err.append(service_name + " still running")


def test_servicestart_yml():
    print ("starting docker container using yml")
    sendCommand_yml_up = "docker-compose -f /opt/dell/rcm-fitness/common/install/docker-compose.yml up -d"
    my_return_up = af_support_tools.send_ssh_command(host=ipaddress, username='root', password='V1rtu@1c3!', command=sendCommand_yml_up, return_output=True)
    time.sleep(60)

@pytest.mark.core_services_cd
@pytest.mark.rcm_fitness_cd
@pytest.mark.parametrize("service_name, pid", [
    ("symphony-system-definition-service", "/cpsd/system-definition/"),
    ("symphony-hal-orchestrator-service", "/cpsd/hal-orchestrator/"),
    ("symphony-credential-service", "/cpsd/credential/"),
    ("symphony-rcm-compliance-data-service", "/cpsd/rcm-fitness/rcm-compliance-data/"),
    ("symphony-rcm-definition-service", "cpsd/rcm-fitness/rcm-definition/"),
    ("symphony-rcm-evaluation-service", "cpsd/rcm-fitness/rcm-evaluation/"),
    ("symphony-identity-service" , "/cpsd/identity-service/"),
    ("symphony-rcm-fitness-client", "rcm-fitness-client"),
    ("symphony-capability-registration-service", "/cpsd/registration-services/capability-registry/"),
    ("symphony-endpoint-registration-service", "/cpsd/registration-services/endpoint-registration/"),
    ("symphony-hdp-cisco-network-service", "/cpsd/hal/providers/hdp-cisco-network/"),
    ("symphony-hdp-poweredge-compute", "/cpsd/hal/providers/hdp-poweredge-compute/"),
    ("symphony-dne-paqx", "dne-paqx")

])
def test_chkStatus_yml(service_name, pid):
    svrstpstrt_yml_err = []


    sendCommand = "docker ps --filter name=" + service_name + "  --format '{{.Status}}' | awk '{print $1}'"
    my_return_status2 = af_support_tools.send_ssh_command(host=ipaddress, username='root', password='V1rtu@1c3!', command=sendCommand, return_output=True)

    if "Up" not in my_return_status2:
        svrstpstrt_yml_err.append(service_name + " not started")

    sendCommand_pid = "ps -ef | grep -i " + pid + "| grep -v grep |grep java | awk \'FNR == 1 {print$2}\'"
    my_return_pid = af_support_tools.send_ssh_command(host=ipaddress, username='root', password='V1rtu@1c3!', command=sendCommand_pid, return_output=True)
    post_pid = my_return_pid.rstrip('\n')

    sendCommand_netstat2 = "netstat -ntp | grep -i \"{}/java\"".format(post_pid)
    my_return_netstat2 = af_support_tools.send_ssh_command(host=ipaddress, username='root', password='V1rtu@1c3!', command=sendCommand_netstat2, return_output=True)
    print (my_return_netstat2)
    #time.sleep(10)
    if "ESTABLISHED" not in my_return_netstat2:
        svrstpstrt_yml_err.append(service_name + " rabbit connection not established")

    assert not svrstpstrt_yml_err


    print("Successful stop and start performed on: %s" % service_name)


########################################################################################################################

@pytest.mark.core_services_mvp
@pytest.mark.rcm_fitness_mvp
@pytest.mark.core_services_cd
@pytest.mark.rcm_fitness_cd
def test_rabbitrunning():
    rab_err = []

    sendCommand = "service rabbitmq-server status"
    rabbit_status = af_support_tools.send_ssh_command(host=ipaddress, username='root', password='V1rtu@1c3!', command=sendCommand, return_output=True)

    if "running" not in rabbit_status:
        rab_err.append("rabbitmq-server not running")

    assert not rab_err

#####################################################END OF TEST########################################################