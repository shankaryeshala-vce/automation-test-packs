import re
from datetime import datetime, timedelta
import paramiko

def get_trace_file(hostname,username, password):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=hostname, username=username, password=password)
        stdin, stdout, stderr = client.exec_command("docker cp symphony-rabbitmq:/var/log/rabbitmq/trace-files/my-new-trace.log file.log")
        transport = paramiko.Transport(hostname)
        transport.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.get('/root/file.log', 'file.log')
        print("Retrieved trace file as file.log")
        return True

    except:
        print("Unable to retrieve trace file.")
        return False

def calculate_total_time():
    try:
        reg_exp = re.compile('\d{4}[-]\d{2}[-]\d{2} \d{1,2}:\d{2}:\d{2}:\d{3}')
        list_of_matches = []
        with open("file.log") as f:
            for line in f:
                hit = reg_exp.findall(line)
                if hit:
                    list_of_matches.append(hit)
        list_to_string = []
        for match in list_of_matches:
            list_to_string.append("".join(match))
        timestamps = []
        for item in list_to_string:
            d = datetime.strptime(item, "%Y-%m-%d %H:%M:%S:%f")
            timestamps.append(d)
        timestamps = sorted(timestamps)
        delta = timestamps[len(timestamps)-1] - timestamps[0]
        print("\n")
        print("Time is seconds:")
        print(timedelta.total_seconds(delta))
        return timedelta.total_seconds(delta)
        
    except:
        print("Unable to calculate total time taken.")
        return 0
