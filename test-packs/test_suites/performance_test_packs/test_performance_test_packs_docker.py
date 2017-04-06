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
def test_sample():
    assert 5 == 5
    
@pytest.mark.performance
def test_deploy_docker_container():
    # Wait for port 22 on perf machine
    my_return_value = af_support_tools.wait_for_port(host=perf_hostname, port=22, wait_time=300, check_interval=15)
    # Copy over docker compose file
    my_return_value = af_support_tools.file_copy_put(host=perf_hostname, port=22, username=perf_username, password=perf_password, source_file='home/autouser/PycharmProjects/auto-framework/test_suites/performance_test_packs/docker-compose-influx-grafana.yml', destination_file='docker-compose-influx-grafana.yml')
    print(my_return_value)
    # Run Docker Compose file
    my_return_value = af_support_tools.send_ssh_command(host=perf_hostname, port=22, username=perf_username, password=perf_password, command='docker-compose -f docker-compose-influx-grafana.yml up -d', return_output=True)
    print(my_return_value)

    #docker-compose -f docker-compose-influx-grafana.yml up -d

    # Sample 'assert'
    assert 5 == 5
