#!/usr/bin/python
# Author: Toqeer Akhtar
# Revision:2.0
# Code Reviewed by: 
# Description: This script will runt against newly deployed OVA and perform a sanitu check for Dockerise servecies.
########################################################################################################################

import af_support_tools
import pytest
import time
import pika

try:
    env_file = 'env.ini'
    ipaddress = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='hostname')
    cli_user = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='username')
    cli_password = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='password')

except:
    print('Possible configuration error')

# ipaddress = '10.3.8.54'
########################################################################################################################


#getting core services conatiner names from docker compose file
@pytest.fixture
def get_core_services():

    core_dir = ["system-definition-service", "credential", "hal-orchestrator-service", "identity-service", "capability-registry-service", "endpoint-registration-service"]
    core_list = []
    
    for service in core_dir:
        sendcommand_core= "cat /opt/dell/cpsd/" + service + "/install/docker-compose.yml | grep container_name| cut -f 2 -d ':'"
        my_return_status_core = af_support_tools.send_ssh_command(host=ipaddress, username=cli_user, password=cli_password, command=sendcommand_core, return_output=True)
        containerName= my_return_status_core.strip()
        core_list.append(containerName)
    return core_list

#getting rcm services conatiner names from docker compose file
@pytest.fixture
def get_rcm_services ():
    sendcommand_rcm= "cat /opt/dell/cpsd/rcm-fitness/common/install/docker-compose.yml | grep container_name | cut -f 2 -d ':' "
    my_return_status_rcm = af_support_tools.send_ssh_command(host=ipaddress, username=cli_user, password=cli_password, command=sendcommand_rcm, return_output=True)
    rcm_list=[a.strip() for a in my_return_status_rcm.strip().split("\n")]
    return rcm_list

########################################################################################################################
##Checking Core Services_mvp
########################################################################################################################
core_list = get_core_services()
@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
@pytest.mark.parametrize("service_name", core_list)

# checking if all core servises are up. Assert if services are not up
def test_Core_servicerunning(service_name):
    """
    Verify Core services are running for mvp

    """
    print (test_Core_servicerunning.__doc__)

    svrrun_err = []

    print (service_name)
    sendCommand = "docker ps --filter name=" + service_name + "  --format '{{.Status}}' | awk '{print $1}'"
    my_return_status = af_support_tools.send_ssh_command(host=ipaddress, username=cli_user, password=cli_password, command=sendCommand, return_output=True)

    if "Up" not in my_return_status:
        svrrun_err.append(service_name + " not running")

    service_name_pid = service_name.replace("symphony-","").replace("-service","").replace("-registry","").replace("-registration","")
    sendCommand_pid = "ps -ef | grep " + service_name_pid +" |grep java | awk '{print $2}'"
    my_return_pid = af_support_tools.send_ssh_command(host=ipaddress, username=cli_user, password=cli_password, command=sendCommand_pid, return_output=True)
    pid = my_return_pid.strip('\n')

    sendCommand_netstat = "netstat -ntp | grep -i \"{}/java\"".format(pid)
    my_return_netstat = af_support_tools.send_ssh_command(host=ipaddress, username=cli_user, password=cli_password, command=sendCommand_netstat, return_output=True)
    if "ESTABLISHED" not in my_return_netstat:
        svrrun_err.append(service_name + " rabbit connection not established")

    assert not svrrun_err

    print("Successful status check performed on: %s" % service_name)


########################################################################################################################
##Checking rcm Services_mvp
########################################################################################################################
rcm_list = get_rcm_services()
@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
@pytest.mark.parametrize("service_name", rcm_list)

# checking if all dockter container servises are up. Assert if services are not up
def test_rcm_servicerunning(service_name):
    svrrun_err = []
    print (service_name)

    sendCommand = "docker ps --filter name=" + service_name + "  --format '{{.Status}}' | awk '{print $1}'"
    my_return_status = af_support_tools.send_ssh_command(host=ipaddress, username=cli_user, password=cli_password, command=sendCommand, return_output=True)

    if "Up" not in my_return_status:
        svrrun_err.append(service_name + " not running")

    service_name_pid = service_name.replace("symphony-remediation-adapter-rackhd", "").replace("symphony-","").replace("-service","").replace("-registration","").replace("-registry","")
    sendCommand_pid = "ps -ef | grep " + service_name_pid +" |grep java | awk '{print $2}'"
    my_return_pid = af_support_tools.send_ssh_command(host=ipaddress, username=cli_user, password=cli_password, command=sendCommand_pid, return_output=True)
    pid = my_return_pid.strip('\n')

    sendCommand_netstat = "netstat -ntp | grep -i \"{}/java\"".format(pid)
    my_return_netstat = af_support_tools.send_ssh_command(host=ipaddress, username=cli_user, password=cli_password, command=sendCommand_netstat, return_output=True)
    if "ESTABLISHED" not in my_return_netstat:
        svrrun_err.append(service_name + " rabbit connection not established")

    assert not svrrun_err

    print("Successful status check performed on: %s" % service_name)



########################################################################################################################
#Checking Core_services_cd.
# Ths is a stop/start test for core services
########################################################################################################################


core_pid_list = ["/cpsd/system-definition/", "/cpsd/credential/", "/cpsd/hal-orchestrator/", "/cpsd/identity-service/",
                 "/cpsd/registration-services/capability-registry/", "/cpsd/registration-services/endpoint-registration/" ]

core_services = list(zip(core_list, core_pid_list))


@pytest.mark.core_services_mvp_extended
@pytest.mark.parametrize("service_name, pid", core_services)
def test_servicestopstart_core(service_name, pid):
    svrstpstrt_err = []


    sendCommand_pid = "ps -ef | grep -i " + pid + "| grep -v grep |grep java | awk \'FNR == 1 {print$2}\'"
    my_return_pid = af_support_tools.send_ssh_command(host=ipaddress, username=cli_user, password=cli_password, command=sendCommand_pid, return_output=True)
    initial_pid = my_return_pid.rstrip('\n')
    print ("ps pid " +initial_pid)

    get_pid = "netstat -ntp | grep -i \":5672.*ESTABLISHED.*{}/java\"".format(initial_pid)
    sendCommand_netstat = ""+ get_pid +" | awk \'{print $7}\'"
    return_netstat_pid = af_support_tools.send_ssh_command(host=ipaddress, username=cli_user, password=cli_password, command=sendCommand_netstat, return_output=True)
    return_netstat_pid = return_netstat_pid.replace("/java", "") .split("\n")[0]
    print ("netstat pid " +return_netstat_pid)


    service_name_1 = service_name.replace('symphony', 'dell')
    service_name_2 = service_name_1.replace ('registry', 'registration')
    service_name_3 = service_name_2.replace ('identity', 'element-identity')
    dell_core = service_name_3.replace('-service', '')


    #Stoppping service individually
    if initial_pid == return_netstat_pid:
        print ("core services")
        sendCommand_stop = "systemctl stop " + dell_core
        return_stop = af_support_tools.send_ssh_command(host=ipaddress, username=cli_user, password=cli_password, command=sendCommand_stop, return_output=True)

        sendcommand_status = "systemctl status " + dell_core
        return_status = af_support_tools.send_ssh_command(host=ipaddress, username=cli_user, password=cli_password, command=sendcommand_status, return_output=True)
        if "active (running)" in return_status:
            svrstpstrt_err.append(service_name + " still running")

        sendCommand_start = "systemctl start " + dell_core
        return_start = af_support_tools.send_ssh_command(host=ipaddress, username=cli_user, password=cli_password, command=sendCommand_start, return_output=True)

        sendcommand_status = "systemctl status " + dell_core
        return_status = af_support_tools.send_ssh_command(host=ipaddress, username=cli_user, password=cli_password, command=sendcommand_status, return_output=True)

    if "active (running)" not in return_status:
            svrstpstrt_err.append(service_name + " not running")


    assert not svrstpstrt_err

    print("Successful stop and start performed on: %s" % service_name)
########################################################################################################################
#Checking Rcm_services_cd.
# Ths is a stop/start test for RCM services
########################################################################################################################
rcm_pid_lst = ["/cpsd/hal/providers/hdp-cisco-network/", "/cpsd/hal/providers/hdp-poweredge-compute/", "cpsd/rcm-fitness/rcm-definition/",
           "/cpsd/rcm-fitness/rcm-compliance-data/", "cpsd/rcm-fitness/rcm-evaluation/", "rcm-fitness-client", "remediation-adapter",
           "dne-paqx", "/node-discovery-paqx/"]

rcm_pid_test = ["/cpsd/rcm-fitness/rcm-compliance-data/", "cpsd/rcm-fitness/rcm-evaluation/"]
rcm_list_test = ['symphony-rcm-compliance-data-service', 'symphony-rcm-evaluation-service']

rcm_pid_lst.remove("remediation-adapter")

rcm_services = list(zip(rcm_list,rcm_pid_lst))



@pytest.mark.rcm_fitness_mvp_extended
@pytest.mark.parametrize("service_name, pid", rcm_services)

def test_servicestopstart_rcm(service_name, pid):
    svrstpstrt_err = []
    print (service_name)


    #sendCommand_pid = "ps -ef | grep " + service_name_pid +" |grep java | awk '{print $2}'"
    sendCommand_pid = "ps -ef | grep -i " + pid + "| grep -v grep |grep java | awk \'FNR == 1 {print$2}\'"
    my_return_pid = af_support_tools.send_ssh_command(host=ipaddress, username=cli_user, password=cli_password, command=sendCommand_pid, return_output=True)
    initial_pid = my_return_pid.rstrip('\n')
    print ("ps pid " +initial_pid)

    get_pid = "netstat -ntp | grep -i \":5672.*ESTABLISHED.*{}/java\"".format(initial_pid)
    sendCommand_netstat = ""+ get_pid +" | awk \'{print $7}\'"
    return_netstat_pid = af_support_tools.send_ssh_command(host=ipaddress, username=cli_user, password=cli_password, command=sendCommand_netstat, return_output=True)
    return_netstat_pid = return_netstat_pid.replace("/java", "") .split("\n")[0]
    print ("netstat pid " +return_netstat_pid)


    #Saving the ContainerIds in the list Container_id
    sendCommand_ContainerID = "docker ps --filter name=" + service_name + "  --format '{{.ID}}'"
    return_ContainerID = af_support_tools.send_ssh_command(host=ipaddress, username=cli_user, password=cli_password, command=sendCommand_ContainerID, return_output=True)
    Container_id = return_ContainerID
    print ("Container id" + Container_id)

    #Stoppping service individually
    if initial_pid == return_netstat_pid:
        print ("stopping docker Container")
        sendCommand_stop = "docker stop " + Container_id
        return_stop = af_support_tools.send_ssh_command(host=ipaddress, username=cli_user, password=cli_password, command=sendCommand_stop, return_output=True)

        sendCommand = "docker ps --filter name=" + service_name + "  --format '{{.Status}}' | awk '{print $1}'"
        my_return_status = af_support_tools.send_ssh_command(host=ipaddress, username=cli_user, password=cli_password, command=sendCommand, return_output=True)
        print ("docker status "+ my_return_status)

        if "Up" in my_return_status:
            svrstpstrt_err.append(service_name + " still running")

        print ("Container id" + Container_id)
        print ("starting docker container")
        sendCommand_start = "docker start " + Container_id
        return_start = af_support_tools.send_ssh_command(host=ipaddress, username=cli_user, password=cli_password, command=sendCommand_start, return_output=True)


    sendCommand = "docker ps --filter name=" + service_name + "  --format '{{.Status}}' | awk '{print $1}'"
    my_return_status = af_support_tools.send_ssh_command(host=ipaddress, username=cli_user, password=cli_password, command=sendCommand, return_output=True)
    print ("docker Status " +my_return_status )


    if "Up" not in my_return_status:
        svrstpstrt_err.append(service_name + " not started")

    sendCommand_pid = "ps -ef | grep -i " + pid + "| grep -v grep |grep java | awk \'FNR == 1 {print$2}\'"
    my_return_pid = af_support_tools.send_ssh_command(host=ipaddress, username=cli_user, password=cli_password, command=sendCommand_pid, return_output=True)
    post_pid = my_return_pid.rstrip('\n')
    print (post_pid)

    time.sleep(25)
    #sendCommand_netstat2 = "netstat -ntp | grep -i \"{}/java\"".format(post_pid)
    sendCommand_netstat2 = "netstat -ntp | grep -i \":5672.*ESTABLISHED.*{}/java\"".format(post_pid)
    my_return_netstat2 = af_support_tools.send_ssh_command(host=ipaddress, username=cli_user, password=cli_password, command=sendCommand_netstat2, return_output=True)
    print (my_return_netstat2)

    if "ESTABLISHED" not in my_return_netstat2:
        time.sleep(70)
        #print (my_return_netstat2)
        if "ESTABLISHED" not in my_return_netstat2:
            svrstpstrt_err.append(service_name + " rabbit connection not established")


            assert not svrstpstrt_err

########################################################################################################################
#test_servicestopstart

def test_servicestop_rcm_yml():
    #stop/start docker containers using yml file
    print ("stopping docker container using yml")
    sendCommand_yml_down = "docker-compose -f /opt/dell/rcm-fitness/common/install/docker-compose.yml down"
    my_return_down = af_support_tools.send_ssh_command(host=ipaddress, username=cli_user, password=cli_password, command=sendCommand_yml_down, return_output=True)

@pytest.mark.rcm_fitness_mvp_extended
@pytest.mark.parametrize("service_name" ,rcm_list)

def test_chkupStatus_yml(service_name):
    chkup_err = []

    print ("checking yml up status TBD")
    sendCommand = "docker ps --filter name=" + service_name + "  --format '{{.Status}}' | awk '{print $1}'"
    my_return_status1 = af_support_tools.send_ssh_command(host=ipaddress, username=cli_user, password=cli_password, command=sendCommand, return_output=True)

    if "Up" in my_return_status1:
        chkup_err.append(service_name + " still running")


def test_servicestart_rcm_yml():
    print ("starting docker container using yml")
    sendCommand_yml_up = "docker-compose -f /opt/dell/rcm-fitness/common/install/docker-compose.yml up -d"
    my_return_up = af_support_tools.send_ssh_command(host=ipaddress, username=cli_user, password=cli_password, command=sendCommand_yml_up, return_output=True)
    time.sleep(60)

@pytest.mark.rcm_fitness_mvp_extended
@pytest.mark.parametrize("service_name, pid", rcm_services)

def test_chkStatus_rcm_yml(service_name, pid):
    svrstpstrt_yml_err = []


    sendCommand = "docker ps --filter name=" + service_name + "  --format '{{.Status}}' | awk '{print $1}'"
    my_return_status2 = af_support_tools.send_ssh_command(host=ipaddress, username=cli_user, password=cli_password, command=sendCommand, return_output=True)

    if "Up" not in my_return_status2:
        svrstpstrt_yml_err.append(service_name + " not started")

    sendCommand_pid = "ps -ef | grep -i " + pid + "| grep -v grep |grep java | awk \'FNR == 1 {print$2}\'"
    my_return_pid = af_support_tools.send_ssh_command(host=ipaddress, username=cli_user, password=cli_password, command=sendCommand_pid, return_output=True)
    post_pid = my_return_pid.rstrip('\n')

    sendCommand_netstat2 = "netstat -ntp | grep -i \"{}/java\"".format(post_pid)
    my_return_netstat2 = af_support_tools.send_ssh_command(host=ipaddress, username=cli_user, password=cli_password, command=sendCommand_netstat2, return_output=True)
    print (my_return_netstat2)
    #time.sleep(10)
    if "ESTABLISHED" not in my_return_netstat2:
        svrstpstrt_yml_err.append(service_name + " rabbit connection not established")

    assert not svrstpstrt_yml_err


    print("Successful stop and start performed on: %s" % service_name)


########################################################################################################################
@pytest.mark.core_services_mvp
@pytest.mark.core_services_mvp_extended
@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
@pytest.mark.rabbitrunning
def test_rabbitrunning():
    rab_err = []

    sendCommand = "service rabbitmq-server status"
    rabbit_status = af_support_tools.send_ssh_command(host=ipaddress, username=cli_user, password=cli_password, command=sendCommand, return_output=True)

    if "running" not in rabbit_status:
        rab_err.append("rabbitmq-server not running")

    assert not rab_err

#####################################################END OF TEST########################################################
