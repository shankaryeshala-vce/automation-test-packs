import urllib3
import json
import time

http = urllib3.PoolManager()


#Function designed to wait until the log collection status changes to complete.
#Example: logcollection_waitforcompletion(host='10.3.63.215', 8080)

def logcollection_waitforcompletion(host='localhost', port=8080):
    try:
        request_data = 'http://%s:%s/api/tasks' % (host, port)
        print("REQ", request_data)
        invokeTime = int(round(time.time() * 1000))
        inn = False
        wait = True
        while wait == True:
            r = http.request('GET', request_data, headers={'Accept': 'application/json', 'Content-type': 'application/json'})
            if r.status == 200:
                    data = json.loads(r.data.decode('utf-8'))
                    for task in data:
                        if task['startTime'] >= invokeTime:
                                inn = True
                                if task['status'] == "COMPLETE":
                                        print("Log Collection is completed.")
                                        time.sleep(5)
                                        wait = False
                    if inn == False:
                        print("Log Collection not invoked")
                        wait = False
            else:
                print("ERROR: return code not 200!")
                print("Status:      ", r.status)
                print("Data:", r.data)
                for key in r.headers:
                        print("Header:", key, ":", r.headers[key])
        return True
    except:
        print('Error waiting for log collection to complete!')
        return False


#Function designed to invoke log collection for a device..
#Example: logcollection_waitforcompletion(host='10.3.63.215', port=8080, deviceid='simulateducs1')

def logcollection_invoke(host='localhost', port=8080, deviceId='Device Id recognized by log collection manager'):
    try:
        request_data = 'http://%s:%s/api/invoke' % (host, port)
        print("REQ", request_data)
        json_data  = {'deviceId': deviceId}
        encoded_data = json.dumps(json_data).encode('utf-8')
        r = http.request('POST', request_data, body=encoded_data, headers={'Accept': 'application/json', 'Content-type': 'application/json'})
        if r.status == 200:
                print("Status:      ", r.status)
                data = json.loads(r.data.decode('utf-8'))
                print("deviceId:    ", data['deviceId'])
                print("taskId:      ", data['taskId'])
                print("startTime:   ", data['startTime'])
                print("host:        ", data['host'])
                print("status:      ", data['status'])
                for key in r.headers:
                        print("Header:", key, ":", r.headers[key])
        else:
                print("ERROR: return code not 200!")
                print("Status:      ", r.status)
                print("Data:", r.data)
                for key in r.headers:
                        print("Header:", key, ":", r.headers[key])
        return True
    except:
        print('Error invoking log collection for %s!', deviceId)
        return False