import af_vapi
import configparser
import json
import os
import paramiko
import pika
import socket
import subprocess
import time
#import pdb; pdb.set_trace()

try:
    config_file_path = os.environ['AF_TEST_SUITE_PATH'] + '/config_files/'
    env_file = 'env.ini'
except:
    print('Possible Configuration Error')

def check_for_dups_in_list(dup_list):
    """
    Function designed to check for duplicate values in a list.
    Function will return True if the list contains duplicate values.
    Function will return False if the list  does not contain duplicate values.
    Function will print an error and return a None Type if what is passed to the function is not a list object type.
    Example: my_list = check_dups_from_list(my_list)
    """
    if type(dup_list) is not list:
        print('Object Passed is not a LIST')
        return
    else:
        print('Orginal List: %s' % dup_list)
        unique_list = []
        dups_found = False
        for item in dup_list:
            if item not in unique_list:
                unique_list.append(item)
            else:
                dups_found = True
                print('Duplicate value found in list: %s' % item)
        return(dups_found)

def set_config_file_property(config_file, heading, property, value):
    """
    Function designed to set given test suite config file
    Example: family_type_list = set_config_file_property(config_file='element_family_settings.ini', heading='Datacenter', property='children', value='os')
    """
    try:
        if config_file[-4:].lower() == '.ini':
            config = configparser.ConfigParser()
            if os.path.isfile(config_file_path + config_file) == True:
                config.read(config_file_path + config_file)
            heading_list = config.sections()
            if heading not in heading_list:
                config.add_section(heading)
                heading_list = config.sections()
            config.set(heading, property, value)
            with open(config_file_path + config_file, 'w') as my_file_handle:
               config.write(my_file_handle)
            return(True)
        else:
            print('Configuration File Type Unknown:')
            print('Configuration File: %s' % config_file)
            print('Configuration Heading: %s' % heading)
            print('Configuration Property: %s' % property)
            print('Configuration Value: %s' % value)
            return(False)
    except:
        print('Configuration File Error:')
        print('Configuration File: %s' % config_file)
        print('Configuration Heading: %s' % heading)
        print('Configuration Property: %s' % property)
        print('Configuration Value: %s' % value)
        return(False)
		
def get_config_file_property(config_file, heading, property):
    """
    Function designed to read a given test suite config file and return to the caller a property value from a given heading and property.
    Example: family_type_list = get_config_file_property(config_file='element_family_settings.ini', heading='Datacenter', property='children')
    """
    try:
        if os.path.isfile(config_file_path + config_file) == False:
            print('Configuration File: %s' % config_file)
            print('Configuration Heading: %s' % heading)
            print('Configuration Property: %s' % property)
            print('Configuration File Not Found')
            return
        if config_file[-4:].lower() == '.ini':
            config = configparser.ConfigParser()
            config.read(os.environ['AF_TEST_SUITE_PATH'] + '/config_files/' + config_file)
            heading_list = config.sections()
            if heading not in heading_list:
                print('Configuration File: %s' % config_file)
                print('Configuration Heading: %s' % heading)
                print('Configuration Property: %s' % property)
                print('Configuration Heading Not Found')
                return
            else:
                property_list = list(dict(config.items(heading)).keys())
            if property not in property_list:
                print('Configuration File: %s' % config_file)
                print('Configuration Heading: %s' % heading)
                print('Configuration Property: %s' % property)
                print('Configuration Property Not Found')
                return
            else:
                return(config[heading][property])
        else:
            print('Configuration File: %s' % config_file)
            print('Configuration Heading: %s' % heading)
            print('Configuration Property: %s' % property)
            print('Configuration File Type Unknown')
            return
    except:
        print('Configuration File Error:')
        print('Configuration File: %s' % config_file)
        print('Configuration Heading: %s' % heading)
        print('Configuration Property: %s' % property)
        print('Configuration File Error')
        return

def get_name_value_pair(file_name, property_name):
    """
    Function designed to...
    """
    try:
        property_value = ''
        with open(file_name, 'r') as file_handle:
            for file_line in file_handle:
                file_line = file_line.strip()
                if file_line.startswith(property_name + '='):
                    property_value = file_line.split('=', 1)
                    property_value = property_value[1]
        return(property_value)
    except Exception as e:
        print(e)
        return
		
def list_compare_all_list_one_items_found_in_list_two(list_one, list_two):
    """
    Function designed to return to the caller a True or False value based on whether or not all the values from list one are found in list two.  True will returned in the case that list two container extra values.
    Example: pass_flag = list_compare_all_list_one_items_found_in_list_two(['one','two','three'],['one','two','three','four','five'])
    """
    list_not_passed = False
    if type(list_one) is not list:
        print('Object One Passes is not a LIST')
        list_not_passed = True
    if type(list_two) is not list:
        print('Object Two Passes is not a LIST')
        list_not_passed = True
    if list_not_passed == True:
        return
    else:
        print('List One: %s' % list_one)
        print('List Two: %s' % list_two)
        pass_flag = True
        for single_item in list_one:
            if single_item not in list_two and single_item != '':
                pass_flag = False
                print('Item %s Not Found' % single_item)
        if pass_flag == True:
            print('All Items Found')
        print()
        return(pass_flag)

def remove_dups_from_list(dup_list):
    """
    Function designed to remove all duplicate values form list.
    Example: my_list = remove_dups_from_list(my_list)
    """
    if type(dup_list) is not list:
        print('Object Passes is not a LIST')
        return
    else:
        print('Orginal List: %s' % dup_list)
        no_dup_list = []
        removed_dup_list = []
        for item in dup_list:
            if item not in no_dup_list:
                no_dup_list.append(item)
            else:
                removed_dup_list.append(item)
        print('Removed Items from List: %s' % removed_dup_list)
        print('New List: %s' % no_dup_list)
        return(no_dup_list)

def rmq_bind_queue(host='not_passed', port=5672, rmq_username='not_passed', rmq_password='not_passed', queue='not_passed', exchange='not_passed', routing_key=''):
    """
    Function designed to create a Rabbit MQ queue (if it does not exist) and bind it to an exchange.  The routing key is optional.
    Will return a Boolean value of TRUE if successful and a Boolean value of FALSE if unsuccessful.
    Example: my_return_value = af_support_tools.rmq_bind_queue(host=my_hostname, port=my_port, rmq_username=my_username, rmq_password=my_password, queue=my_queue, exchange=my_exchange, routing_key=my_routing_key)
    """
    try:
        port = int(port)

        credentials = pika.PlainCredentials(rmq_username, rmq_password)
        parameters = pika.ConnectionParameters(host, port,'/',credentials)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.queue_declare(queue=queue, durable=True)
        channel.queue_bind(queue=queue, exchange=exchange, routing_key=routing_key)
        channel.close()
        connection.close()

        print('Queue Bond')
        return(True)
    except Exception as e:
        print(e)
        print('Queue Not Bond')
        return(False)

def rmq_consume_all_messages(host='not_passed', port=5672, rmq_username='not_passed', rmq_password='not_passed', queue='not_passed'):
    """
    Function designed to consume all messages within a Rabbit MQ queue.
    Will return a list of all the payload values (json or plain text)
    On error will return <class 'NoneType'>
    Example: my_return_value = af_support_tools.rmq_consume_all_messages(host=my_hostname, port=my_port, rmq_username=my_username, rmq_password=my_password, queue=my_queue)
    """
    try:
        port = int(port)
        
        my_payload_list = []
        my_message_count = rmq_message_count(host=host, port=port, rmq_username=rmq_username, rmq_password=rmq_username, queue=queue)
        
        credentials = pika.PlainCredentials(rmq_username, rmq_password)
        parameters = pika.ConnectionParameters(host, port,'/',credentials)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        for my_counter in range(0, my_message_count):
            method_frame, header_frame, body = channel.basic_get(queue=queue, no_ack=True)
            if body is not None:
                my_payload_list.append(body.decode('utf-8'))
        channel.close()
        connection.close()

        print('All Messages Consumed')
        return(my_payload_list)
    except Exception as e:
        print(e)
        print('All Messages Not Consumed')
        return

def rmq_consume_message(host='not_passed', port=5672, rmq_username='not_passed', rmq_password='not_passed', queue='not_passed', remove_message=True):
    """
    Function designed to consume messages within a Rabbit MQ queue.
    Will return the payload value (json or plain text)
    On error will return <class 'NoneType'>
    Example: my_return_value = af_support_tools.rmq_consume_message(host=my_hostname, port=my_port, rmq_username=my_username, rmq_password=my_password, queue=my_queue, remove_message=True)
    """
    try:
        port = int(port)

        credentials = pika.PlainCredentials(rmq_username, rmq_password)
        parameters = pika.ConnectionParameters(host, port,'/',credentials)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        method_frame, header_frame, body = channel.basic_get(queue=queue, no_ack=remove_message)
        channel.close()
        connection.close()
        if body is None:
            print('Message Not Consumed')
            return
        else:
            print('Message Consumed')
            return body.decode('utf-8')
    except Exception as e:
        print(e)
        print('Message Not Consumed')
        return

def rmq_delete_queue(host='not_passed', port=5672, rmq_username='not_passed', rmq_password='not_passed', queue='not_passed'):
    """
    Function designed to delete a Rabbit MQ queue.
    Will return a Boolean value of TRUE if successful and a Boolean value of FALSE if unsuccessful.  If queue does not exist a Boolean value of TRUE will be returned.
    Example: my_return_value = af_support_tools.rmq_delete_queue(host=my_hostname, port=my_port, rmq_username=my_username, rmq_password=my_password, queue=my_queue)
    """
    try:
        port = int(port)

        credentials = pika.PlainCredentials(rmq_username, rmq_password)
        parameters = pika.ConnectionParameters(host, port,'/',credentials)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.queue_delete(queue=queue)
        channel.close()
        connection.close()
        
        print('Queue Deleted')
        return(True)
    except Exception as e:
        print(e)
        print('Error Deleting to Queue')
        return(False)

def rmq_message_count(host='not_passed', port=5672, rmq_username='not_passed', rmq_password='not_passed', queue='not_passed'):
    """
    Function designed to get the message count of a Rabbit MQ queue.
    Will return a integer value that is the total number of messages in the queue.
    If there is an error reading the queue or the queue does not exist a None type will be returned.
	Example: my_return_value = af_support_tools.rmq_message_count(host=my_hostname, port=my_port, rmq_username=my_username, rmq_password=my_password, queue=my_queue)
    """
    try:
        port = int(port)

        credentials = pika.PlainCredentials(rmq_username, rmq_password)
        parameters = pika.ConnectionParameters(host, port,'/',credentials)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        responce = channel.queue_declare(queue=queue, durable=True, passive=True)
        channel.close()
        connection.close()

        return(responce.method.message_count)
    except Exception as e:
        print(e)
        print('Error Connecting to Queue')
        return

def rmq_payload_to_file(payload, filename):
    """
    Function designed to take message payloads either a payload (as a string) or list of payloads (as a list)
    Nothing is returned
    Example: af_support_tools.rmq_payload_to_file(payload=my_payload_list, filename=my_payload_filename)
    """
    if type(payload) is str:
        with open(filename, 'w') as outfile:
            outfile.write(payload)
        return(True)
    elif type(payload) is list:
        if len(payload) > 0:
            with open(filename, 'w') as outfile:
                outfile.write('[' + ', '.join(payload) + ']')
        else:
            with open(filename, 'w') as outfile:
                outfile.write('[]')
        return(True)
    else:
        print('\'payload\' must be list type or string type not %s' % type(payload))
        #with open(filename, 'w') as outfile:
        #    outfile.write('')
        return(False)

def rmq_publish_message(host='not_passed', port=5672, rmq_username='not_passed', rmq_password='not_passed', exchange='not_passed', routing_key='', headers={}, payload={}, payload_type='json', priority=0, delivery_mode=2, correlation_id={}, reply_to={}):
    """
    Function designed to publish a message to a Rabbit MQ queue.
    Will return a Boolean value of TRUE if successful and a Boolean value of FALSE if unsuccessful.
    Example: my_return_value = af_support_tools.rmq_publish_message(host=my_hostname, port=my_port, rmq_username=my_username, rmq_password=my_password, exchange=my_exchange, routing_key=my_routing_key, headers=my_headers, payload=t1_payload, payload_type='json', priority=0, delivery_mode=2, correlation_id=my_correlation_id, reply_to=my_reply_to)
    """
    try:
        port = int(port)
        priority = int(priority)
        delivery_mode = int(delivery_mode)
        correlation_id = str(correlation_id)
        reply_to = str(reply_to)
        if type(headers) is str:
            headers = json.loads(headers)
        if payload_type == 'json':
            payload_type = 'application/json'
        else:
            payload_type = 'text/plain'

        credentials = pika.PlainCredentials(rmq_username, rmq_password)
        parameters = pika.ConnectionParameters(host, port,'/',credentials)
        message_properties = pika.BasicProperties(content_type=payload_type, headers=headers, delivery_mode=delivery_mode, priority=priority, correlation_id=correlation_id, reply_to=reply_to)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.basic_publish(exchange=exchange, routing_key=routing_key, body=payload, properties=message_properties)
        channel.close()
        connection.close()
        
        print('Message Published')
        return(True)
    except Exception as e:
        print(e)
        print('Message Not Published')
        return(False)

def rmq_purge_queue(host='not_passed', port=5672, rmq_username='not_passed', rmq_password='not_passed', queue='not_passed'):
    """
    Function designed to purge a Rabbit MQ queue.
    Will return a Boolean value of TRUE if successful and a Boolean value of FALSE if unsuccessful.  If queue does not exist a Boolean value of FALSE will be returned.
    Example: my_return_value = af_support_tools.rmq_purge_queue(host=my_hostname, port=my_port, rmq_username=my_username, rmq_password=my_password, queue=my_queue)
    """
    try:
        port = int(port)

        credentials = pika.PlainCredentials(rmq_username, rmq_password)
        parameters = pika.ConnectionParameters(host, port,'/',credentials)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.queue_declare(queue=queue, durable=True, passive=True)
        channel.queue_purge(queue=queue)
        channel.close()
        connection.close()
        
        print('Queue Purged')
        return(True)
    except Exception as e:
        print(e)
        print('Queue Not Purged')
        return(False)

def rmq_unbind_queue(host='not_passed', port=5672, rmq_username='not_passed', rmq_password='not_passed', queue='not_passed', exchange='not_passed', routing_key=''):
    """
    Function designed to create a Rabbit MQ queue (if it does not exist) and bind it to an exchange.  The routing key is optional.
    Will return a Boolean value of TRUE if successful and a Boolean value of FALSE if unsuccessful.
    Example: my_return_value = af_support_tools.rmq_purge_queue(host=my_hostname, port=my_port, rmq_username=my_username, rmq_password=my_password, queue=my_queue, exchange=my_exchange, routing_key=my_routing_key)
    """
    try:
        port = int(port)
        
        credentials = pika.PlainCredentials(rmq_username, rmq_password)
        parameters = pika.ConnectionParameters(host, port,'/',credentials)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.queue_declare(queue=queue, durable=True, passive=True)
        channel.queue_unbind(queue=queue, exchange=exchange, routing_key=routing_key)
        channel.close()
        connection.close()
        
        print('Queue Unbond')
        return(True)
    except Exception as e:
        print(e)
        print('Queue Not Unbond')
        return(False)
		
def send_ssh_command(host='not_passed', port=22, username='not_passed', password='not_passed', command='not_passed', return_output=False):
    """
    Function designed to send a command line over ssh.
    Example: my_return_value = send_ssh_command(host='mymachine.mpe.lab.vce.com', username='root', password='V1rtu@1c3!', command='ls -l', return_output=False)
    """
    try:
        port = int(port)

        my_return_value = ''
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port=port, username=username, password=password)
        stdin,stdout,stderr = ssh.exec_command(command)
        if return_output == True:
            for line in stdout.readlines():
                my_return_value = my_return_value + line
        else:
            my_return_value = stdout.channel.recv_exit_status()
        ssh.close()
        return(my_return_value)
    except Exception as e:
        print(e)
        print('Connection Failed')
        return

def wait_for_port(host='not_passed', port='not_passed', wait_time='not_passed', check_interval='not_passed'):
    """
    Function designed to wait for a port to open.
    Example: my_return_value = wait_for_port(host='127.0.0.1', port=80, wait_time=120, check_interval=30):
    """
    print('Wait for port...')
    print('Host:           %s' % host)
    print('Port:           %s' % port)
    print('Wait Time:      %s' % wait_time)
    print('Check Interval:  %s' % check_interval)
    print()
	
    host = str(host)
    port = int(port)
    wait_time = int(wait_time)
    check_interval = int(check_interval)

    try:
        waited_time = 0
        while waited_time <= wait_time:
            print('Waiting, %s seconds out of %s' % (waited_time,wait_time))
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex((host,port))
            sock.close()
            if result == 0:
                print('Port is open')
                my_return_value = True
                waited_time = wait_time + 1
            else:
                print('Port is not open')
                my_return_value = False
                if waited_time < wait_time:
                    time.sleep(check_interval)
                waited_time = waited_time + check_interval
        return(my_return_value)
    except Exception as e:
        if '[Errno -2] Name or service not known' in str(e):
            print('ERROR: Host not know')
        elif 'port must be 0-65535' in str(e):
            print('ERROR: Port must be 0-65535')
        else:
            print(e)
        return(False)
