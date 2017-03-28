from paramiko import client
from time import sleep


class ssh:
    client = None

    def __init__(self, address, username, password):
        print("Connecting to server: " + address)
        self.client = client.SSHClient()
        self.client.set_missing_host_key_policy(client.AutoAddPolicy())
        self.client.connect(address, username=username, password=password, look_for_keys=False)
        self.response = []

    def sendCommand(self, command):
        if(self.client):
            stdin, stdout, sterr = self.client.exec_command(command)
            while not stdout.channel.exit_status_ready():
                sleep(0.1)
                if stdout.channel.recv_ready():
                    alldata = stdout.channel.recv(1024)
                    while stdout.channel.recv_ready():
                        alldata += stdout.channel.recv(1024)
                    self.response = str(alldata, "utf8")
                    return self.response
        else:
            print("Connection not opened.")
