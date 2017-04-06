import paramiko
import pika
import time


#Function designed to create a queue named 'firehose' and bind the queue to 'amq.rabbitmq.trace'.
#Example: create_firehose_queue(hostname='10.3.63.215')
def create_firehose_queue(hostname):
    try:
        print('\nConfiguring firehose queue:')
        credentials = pika.PlainCredentials('guest', 'guest')
        parameters = pika.ConnectionParameters(hostname, 5672,'/',credentials)
        message_properties = pika.BasicProperties(priority=0)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.queue_declare(queue='firehose', durable=True)
        channel.queue_bind(queue='firehose', exchange='amq.rabbitmq.trace', routing_key='#')
        channel.close()
        connection.close()
        print('Firehose queue created with bind "amq.rabbitmq.trace".')
        return True
    except:
        print('Error creating Firehose queue!')
        return False


def enable_firehose(hostname, username, password, format = "text"):
    try:
        print('\nEnabling firehose plugin:')
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=hostname, username=username, password=password)
        transport = paramiko.Transport(hostname)
        transport.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.put('/home/autouser/PycharmProjects/auto-framework/test_suites/performance_test_packs/libs/rabbitmq.config', '/root/rabbitmq.config')
        stdin, stdout, stderr = client.exec_command("docker cp symphony-rabbitmq:/etc/rabbitmq/rabbitmq.config orig_rabbitmq.config")
        stdin, stdout, stderr = client.exec_command("docker cp rabbitmq.config symphony-rabbitmq:/etc/rabbitmq/rabbitmq.config")
        stdin, stdout, stderr = client.exec_command("docker exec symphony-rabbitmq bash -c 'rabbitmq-plugins enable rabbitmq_management'")
        print('rabbitmq management plugin enabled')
        stdin, stdout, stderr = client.exec_command("docker exec symphony-rabbitmq bash -c 'rabbitmqctl trace_on'")

        for line in stdout:
            print(line.strip('\n'))
        stdin, stdout, stderr = client.exec_command("docker exec symphony-rabbitmq bash -c 'rabbitmq-plugins enable rabbitmq_tracing'")
        time.sleep(2)
        stdin, stdout, stderr = client.exec_command("docker exec symphony-rabbitmq bash -c 'service rabbitmq-server restart'")
        time.sleep(5)
        stdin, stdout, stderr = client.exec_command("docker start symphony-rabbitmq")
        time.sleep(5)

        if format == "json":
            stdin, stdout, stderr = client.exec_command("curl -i -u guest:guest -H \"content-type:application/json\" \
            -XPUT -d\'{\"format\":\"json\",\"pattern\":\"#\"}\' \
            http://localhost:15672/api/traces/%2f/my-new-trace")
        else:
            stdin, stdout, stderr = client.exec_command("curl -i -u guest:guest -H \"content-type:application/json\" \
            -XPUT -d\'{\"format\":\"text\",\"pattern\":\"#\"}\' \
            http://localhost:15672/api/traces/%2f/my-new-trace")

        client.close()
        print('\nFirehose plugin enabled.')
        return True
    except:
        print("Error enabling Firehose plugin!")
        return False


def delete_firehose_queue(hostname):
    try:
        print('\nDeleting firehose queue:')
        credentials = pika.PlainCredentials('guest', 'guest')
        parameters = pika.ConnectionParameters(hostname, 5672,'/',credentials)
        message_properties = pika.BasicProperties(priority=0)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.queue_delete(queue='firehose')
        channel.close()
        connection.close()
        print('Firehose queue deleted.')
        return True
    except:
        print('Error deleting Firehose queue!')
        return False


def disable_firehose(hostname, username, password):
    try:
        print('\nDisabling firehose plugin:')
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=hostname, username=username, password=password)
        stdin, stdout, stderr = client.exec_command("docker exec symphony-rabbitmq bash -c 'rabbitmq-plugins disable rabbitmq_tracing'")
        stdin, stdout, stderr = client.exec_command("docker exec symphony-rabbitmq bash -c 'rm -f /var/log/rabbitmq/trace-files/my-new-trace.log'")
        transport = paramiko.Transport(hostname)
        transport.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        stdin, stdout, stderr = client.exec_command("docker cp orig_rabbitmq.config symphony-rabbitmq:/etc/rabbitmq/rabbitmq.config")
        stdin, stdout, stderr = client.exec_command("rm -f rabbitmq.config")
        stdin, stdout, stderr = client.exec_command("rm -f orig_rabbitmq.config")
        client.close()

        print('\nFirehose plugin disabled.')
        return True
    except:
        print("Error disabling Firehose plugin!")
        return False
