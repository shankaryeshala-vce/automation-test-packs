import pytest
from Ssh_Connect import ssh

def pytest_addoption(parser):
    parser.addoption("--hostname", action="store", default="", help="FQDN of test host")
    parser.addoption("--username", action="store", default="", help="SSH username of test host")
    parser.addoption("--password", action="store", default="", help="SSH password of test host")

@pytest.fixture
def connection():
    return ssh(pytest.config.getoption("--hostname"), pytest.config.getoption("--username"), pytest.config.getoption("--password"))

