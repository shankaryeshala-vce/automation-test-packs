import af_support_tools
#import os

class props(object):
    # Set env.ini file name
    env_file = 'env.ini'
    
    # Set CPSD common global vars
    # Base OS    
    base_hostname = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='hostname')
    base_username = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='username')
    base_password = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='password')

    # Rabbit MQ
    rmq_username = af_support_tools.get_config_file_property(config_file=env_file, heading='RabbitMQ', property='username')
    rmq_password = af_support_tools.get_config_file_property(config_file=env_file, heading='RabbitMQ', property='password')
    rmq_ssl_enabled = af_support_tools.get_config_file_property(config_file=env_file, heading='RabbitMQ', property='ssl_enabled')
    if rmq_ssl_enabled == 'True':
        rmq_ssl_enabled = True
        rmq_port = af_support_tools.get_config_file_property(config_file=env_file, heading='RabbitMQ', property='ssl_port')
        rmq_cert_path = af_support_tools.get_config_file_property(config_file=env_file, heading='RabbitMQ', property='cert_path')
    else:
        rmq_ssl_enabled = False
        rmq_port = af_support_tools.get_config_file_property(config_file=env_file, heading='RabbitMQ', property='port')
        rmq_cert_path = af_support_tools.get_config_file_property(config_file=env_file, heading='RabbitMQ', property='cert_path')
