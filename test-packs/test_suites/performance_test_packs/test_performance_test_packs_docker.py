import pytest
import selenium
import af_support_tools
    
try:
    #config_file = 'performance/docker_config.ini'
    env_file = 'env.ini'
	# READ IN MACHINE INFO
    perf_hostname = af_support_tools.get_config_file_property(config_file=env_file, heading='PBase_OS', property='hostname')
    perf_username = af_support_tools.get_config_file_property(config_file=env_file, heading='PBase_OS', property='username')
    perf_password = af_support_tools.get_config_file_property(config_file=env_file, heading='PBase_OS', property='password')
    symphony_hostname = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='hostname')
    symphony_username = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='username')
    symphony_password = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='password')
except:
    print('Possible Configuration Error')
    
@pytest.mark.performance
def test_deploy_docker_container():
    # Wait for port 22 on perf machine
    wait_for_port(host=perf_hostname, port=22, wait_time=300, check_interval=15)
    # Copy over docker compose file
    # Run Docker Compose file
    

    # Sample 'assert'
    assert 5 == 5
