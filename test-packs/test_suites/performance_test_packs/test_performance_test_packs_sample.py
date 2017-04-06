import pytest
import selenium
import af_vapi
import af_support_tools
import libs.rabbitmqConfigLib as rabbitmqConfigLib
import libs.logcollectionLib as logcollectionLib
import libs.latency as latency


try:
    config_file = 'sample_config.ini'
    env_file = 'env.ini'
except:
    print('Possible Configuration Error')

hostname = '10.3.63.215'
username='root'
password='Acadia123'
format='text'
device='simulateducs1'

@pytest.mark.logcollection
def test_sample_logcollection():
    '''
    This test is designed to configure rabbitmq, invoke a log collection, collect latency info and revert the system to its original state.
    '''
    print('Running Performance tests for Log Collection')
    assert rabbitmqConfigLib.create_firehose_queue(hostname) == True
    assert rabbitmqConfigLib.enable_firehose(hostname, username, password, format) == True
    assert logcollectionLib.logcollection_invoke(hostname, 8080, device) == True
    assert logcollectionLib.logcollection_waitforcompletion(hostname, 8080) == True
    assert latency.get_trace_file(hostname, username, password) == True
    print('Total time taken for logcollection of ' + device + ' is ' + str(latency.calculate_total_time()) + ' seconds.')
    assert rabbitmqConfigLib.delete_firehose_queue(hostname) == True
    assert rabbitmqConfigLib.disable_firehose(hostname, username, password) == True
