#!/usr/bin/python

import pytest
import json
import af_support_tools


class NoMessageConsumedException(Exception):
    def __init__(self, message):
        super().__init__(self, message)


class RabbitMqConnection:
    def __init__(self, ipAddress, port, username, password):
        self.ipAddress = ipAddress
        self.port = port
        self.url = "http://{}:15672".format(self.ipAddress)
        self.username = username
        self.password = password

    def bindQueueWithKey(self, exchange, queue, routingKey):
        self.deleteQueue(queue)
        print("INFO: binding queue {} to exchange {} with key {}".format(queue, exchange, routingKey))
        af_support_tools.rmq_bind_queue(self.ipAddress, self.port, self.username, self.password, queue, exchange,
                                        routingKey)

    def deleteQueue(self, queue):
        print("INFO: deleting queue", queue)
        af_support_tools.rmq_delete_queue(self.ipAddress, self.port, self.username, self.password, queue)

    def consumeMessageFromQueue(self, queue):
        messageFound = af_support_tools.rmq_wait_for_messages_in_queue(self.ipAddress, self.port, self.username,
                                                                       self.password,
                                                                       queue, wait_time=300, check_interval=5)
        if messageFound:
            message = af_support_tools.rmq_consume_message(self.ipAddress, self.port, self.username, self.password,
                                                           queue)
            print("INFO message consumed from queue {}: {}".format(queue, message))
            return json.loads(message, encoding='utf-8')
        else:
            raise NoMessageConsumedException("failed to consume message from queue: \'{}\'".format(queue))


@pytest.fixture(scope="session")
def hostIpAddress():
    import cpsd
    global cpsd
    return cpsd.props.base_hostname


@pytest.fixture(scope="session")
def rabbitMqConnection(hostIpAddress):
    import cpsd
    global cpsd
    port = cpsd.props.rmq_port
    username = cpsd.props.rmq_username
    password = cpsd.props.rmq_password
    return RabbitMqConnection(hostIpAddress, port, username, password)


@pytest.fixture(scope="session")
def setup():
    parameters = {}
    env_file = 'env.ini'
    ipaddress = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS',
                                                          property='hostname')
    parameters['IP'] = ipaddress
    cli_user = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS',
                                                         property='username')
    parameters['user'] = cli_user
    cli_password = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS',
                                                             property='password')
    parameters['password'] = cli_password
    return parameters

