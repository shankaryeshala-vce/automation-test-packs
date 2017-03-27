import pytest
from time import sleep

services_running = 0

@pytest.mark.parametrize("service_name", [
    "dell-credential",
    "dell-system-definition",
    "dell-hal-orchestrator",
    "dell-rcm-compliance-data",
    "dell-rcm-definition",
    "dell-rcm-evaluation",
    "dell-rcm-fitness-api"
])
def test_servicerunning(service_name, connection):
    svrrun_err = []
    global services_running

    status = connection.sendCommand("service " + service_name + " status")
    if "running" not in status:
        svrrun_err.append(service_name + " not running")

    pid = connection.sendCommand("service " + service_name + " status | grep -i \"Main PID\" | awk \'{print $3}\'")
    pid = pid.strip('\n')
    
    rabbit_connection = connection.sendCommand("netstat -ntp | grep -i \"{}/java\"".format(pid))
    
    if "ESTABLISHED" not in rabbit_connection:
        svrrun_err.append(service_name + "rabbit connection not established")

    assert not svrrun_err

    services_running = connection.sendCommand("netstat -ntp | grep -i \":5672 .*ESTABLISHED .*java\" | wc -l")
    services_running = int(services_running.strip('\n'))

    print("Successful status check performed on: %s" % service_name)

@pytest.mark.parametrize("service_name, pid", [
    ("dell-credential", "services/credential/"),
    ("dell-system-definition", "services/system-definition/"),
    ("dell-hal-orchestrator", "services/hal-orchestrator/"),
    ("dell-rcm-compliance-data", "services/rcm-compliance-data/"),
    ("dell-rcm-definition", "services/rcm-definition/"),
    ("dell-rcm-evaluation", "services/rcm-evaluation/")
])
#("dell-rcm-fitness-api", "api/")
def test_servicestopstart(service_name, pid, connection):
    svrstpstrt_err = []

    intialservices = connection.sendCommand("netstat -ntp | grep -i \":5672 .*ESTABLISHED .*java\" | wc -l")
    intialservices = int(intialservices.strip('\n'))

    intialpid1 = connection.sendCommand("service " + service_name + " status | grep -i \"Main PID\" | awk \'{print $3}\'")
    intialpid2 = connection.sendCommand("ps -ef | grep -i \"[/]rcm-fitness/" + pid + "\" | awk \'FNR == 1 {print$2}\'")

    if (intialpid1 == intialpid2) and (intialservices == services_running):
        connection.sendCommand("service " + service_name + " stop")
    else:
        assert intialservices == services_running
        assert intialpid1 == intialpid2

    status = connection.sendCommand("service " + service_name + " status")
    if "Active: failed" not in status:
        svrstpstrt_err.append(service_name + " still running")

    postservices = connection.sendCommand("netstat -ntp | grep -i \":5672 .*ESTABLISHED .*java\" | wc -l")
    if intialservices == postservices:
        svrstpstrt_err.append("Number of services running: {} Should be: 6 ".format(postservices))

    connection.sendCommand("service " + service_name + " start")
    status = connection.sendCommand("service " + service_name + " status")
    if "running" not in status:
        svrstpstrt_err.append(service_name + " not running")

    sleep(70)
    postservices = connection.sendCommand("netstat -ntp | grep -i \":5672 .*ESTABLISHED .*java\" | wc -l")
    postservices = int(postservices.strip('\n'))

    postpid1 = connection.sendCommand("service " + service_name + " status | grep -i \"Main PID\" | awk \'{print $3}\'")
    postpid2 = connection.sendCommand("ps -ef | grep -i \"[/]rcm-fitness/" + pid + "\" | awk \'FNR == 1 {print$2}\'")

    if (postpid1 != postpid2) or (postservices != services_running):
        svrstpstrt_err.append("PID1 = {} PID2 = {} Number of services running = {}".format(postpid1, postpid2, postservices))

    assert not svrstpstrt_err

    print("Successful stop and start performed on: %s" % service_name)

@pytest.mark.parametrize("service_name, pid", [
    ("dell-credential", "services/credential/"),
    ("dell-system-definition", "services/system-definition/"),
    ("dell-hal-orchestrator", "services/hal-orchestrator/"),
    ("dell-rcm-compliance-data", "services/rcm-compliance-data/"),
    ("dell-rcm-definition", "services/rcm-definition/"),
    ("dell-rcm-evaluation", "services/rcm-evaluation/"),
    ("dell-rcm-fitness-api", "api/")
])
def test_servicerestart(service_name, pid, connection):
    svrst_err = []

    intialservices = connection.sendCommand("netstat -ntp | grep -i \":5672 .*ESTABLISHED .*java\" | wc -l")
    intialservices = int(intialservices.strip('\n'))


    intialpid1 = connection.sendCommand("service " + service_name + " status | grep -i \"Main PID\" | awk \'{print $3}\'")
    intialpid2 = connection.sendCommand("ps -ef | grep -i \"[/]rcm-fitness/" + pid + "\" | awk \'FNR == 1 {print$2}\'")

    if (intialpid1 == intialpid2) and (intialservices == services_running):
        connection.sendCommand("service " + service_name + " restart")
    else:
        assert intialservices == services_running
        assert intialpid1 == intialpid2

    status = connection.sendCommand("service " + service_name + " status")
    if "running" not in status:
        svrst_err.append(service_name + " not running post restart")

    sleep(70)
    postservices = connection.sendCommand("netstat -ntp | grep -i \":5672 .*ESTABLISHED .*java\" | wc -l")
    postservices = int(postservices.strip('\n'))

    postpid1 = connection.sendCommand("service " + service_name + " status | grep -i \"Main PID\" | awk \'{print $3}\'")
    postpid2 = connection.sendCommand("ps -ef | grep -i \"[/]rcm-fitness/" + pid + "\" | awk \'FNR == 1 {print$2}\'")

    if (postpid1 != postpid2) or (postservices != services_running):
        svrst_err.append("PID1 = {} PID2 = {} Number of services running = {}".format(postpid1, postpid2, postservices))

    assert not svrst_err

    print("Successful restart performed on: %s" % service_name)

@pytest.mark.rabbitrunning
def test_rabbitrunning(connection):
    rab_err = []

    status = connection.sendCommand("service rabbitmq-server status")
    if "running" not in status:
        rab_err.append("rabbitmq-server not running")

    assert not rab_err
