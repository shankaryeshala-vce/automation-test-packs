#!/usr/bin/python

import pytest
import json
import af_support_tools


class NoMessageConsumedException(Exception):
    def __init__(self, message):
        super().__init__(self, message)


class Connection:
    def __init__(self, ip_address, username, password):
        self.ipAddress = ip_address
        self.username = username
        self.password = password


class RmqConnection(Connection):
    def __init__(self, ip_address, username, password, port):
        super(ip_address, username, password)
        self.port = port
        self.url = "http://{}:15672".format(self.ipAddress)


class Message:
    def __init__(self, headers, payload, payload_type):
        self.headers = headers;
        self.payload = payload
        self.payloadType = payload_type


class JsonMessage(Message):
    def __init__(self, headers, payload):
        super().__init__(headers, payload, payload_type='json')


class RabbitMq:
    def __init__(self, connection):
        self.connection = connection

    def bind_queue_with_key(self, exchange, queue, routing_key):
        self.delete_queue(queue)
        print("INFO: binding queue {} to exchange {} with key {}".format(queue, exchange, routing_key))
        af_support_tools.rmq_bind_queue(self.connection.ipAddress, self.connection.port, self.connection.username,
                                        self.connection.password, queue, exchange, routing_key)

    def delete_queue(self, queue):
        print("INFO: deleting queue", queue)
        af_support_tools.rmq_delete_queue(self.connection.ipAddress, self.connection.port, self.connection.username,
                                          self.connection.password, queue)

    def consume_message_from_queue(self, queue):
        message_found = af_support_tools.rmq_wait_for_messages_in_queue(self.connection.ipAddress, self.connection.port,
                                                                       self.connection.username, self.connection.password,
                                                                       queue, wait_time=300, check_interval=5)
        if message_found:
            message = af_support_tools.rmq_consume_message(self.connection.ipAddress, self.connection.port,
                                                           self.connection.username, self.connection.password,
                                                           queue)
            print("INFO message consumed from queue {}: {}".format(queue, message))
            return json.loads(message, encoding='utf-8')
        else:
            raise NoMessageConsumedException("failed to consume message from queue: \'{}\'".format(queue))

    def publish_message(self, exchange, routing_key, message):
        af_support_tools.rmq_publish_message(self.connection.ipAddress, self.connection.port,
                                             self.connection.username, self.connection.password,
                                             exchange, routing_key,
                                             message.headers, message.payload, message.payloadType)


@pytest.fixture(scope="session")
def hostIpAddress():
    import cpsd
    global cpsd
    return cpsd.props.base_hostname

@pytest.fixture(scope="session")
def hostConnection(hostIpAddress):
    import cpsd
    global cpsd
    username = cpsd.props.base_username
    password = cpsd.props.base_password

    return Connection(hostIpAddress, username, password)


@pytest.fixture(scope="session")
def rabbitMq(hostIpAddress):
    import cpsd
    global cpsd
    port = cpsd.props.rmq_port
    username = cpsd.props.rmq_username
    password = cpsd.props.rmq_password

    rmq_connection = RmqConnection(hostIpAddress, username, password, port)
    return RabbitMq(rmq_connection)


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

