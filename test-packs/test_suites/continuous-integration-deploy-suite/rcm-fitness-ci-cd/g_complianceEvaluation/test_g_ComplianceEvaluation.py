import json
import requests
import pytest
import af_support_tools


@pytest.fixture(scope="module", autouse=True)
def load_test_data():
    global ssl_options
    ssl_options = {"ca_certs": "/etc/rabbitmq/certs/testca/cacert.pem",
                   "certfile": "/etc/rabbitmq/certs/certs/client/cert.pem",
                   "keyfile": "/etc/rabbitmq/certs/certs/client/key.pem", "cert_reqs": "ssl.CERT_REQUIRED",
                   "ssl_version": "ssl.PROTOCOL_TLSv1_2"}

    # Set config ini file name
    global env_file
    env_file = 'env.ini'

    global host
    host = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='hostname')


@pytest.fixture()
def sys():
    url = 'http://' + host + ':19080/rcm-fitness-api/api/system/definition/'
    response = requests.get(url)
    assert response.status_code == 200, "Request has not been acknowledged as expected."
    data = response.json()

    assert data["systems"][0]["uuid"] != ""
    print("\nExtracting systemUUID from response....\n")
    uuidlist = []
    for k, v in data.items():
        if isinstance(v, list):
            for system in v:
                uuidlist.append(system["uuid"])
                print(uuidlist)

    return uuidlist


@pytest.fixture()
def rcmid():
    # Returns the first rcm uuid listed
    url = 'http://' + host + ':19080/rcm-fitness-api/api/rcm/inventory/vxrack/FLEX'
    response = requests.get(url)
    assert response.status_code == 200, "Request has not been acknowledged as expected."
    data = response.json()

    assert data["rcmInventoryItems"][0]["uuid"] != ""
    train = data["rcmInventoryItems"][0]["rcmTrain"]
    version = data["rcmInventoryItems"][0]["rcmVersion"]
    print("\nExtracting rcmUUID from response....\n")
    rcmuuid = data["rcmInventoryItems"][0]["uuid"]
    print(rcmuuid)
    return rcmuuid


@pytest.fixture()
def train():
    # returns the train of first rcm listed
    url = 'http://' + host + ':19080/rcm-fitness-api/api/rcm/inventory/vxrack/FLEX'
    response = requests.get(url)
    assert response.status_code == 200, "Request has not been acknowledged as expected."
    data = response.json()
    rcmTrain = data["rcmInventoryItems"][0]["rcmTrain"]
    print(rcmTrain)
    return rcmTrain


@pytest.fixture()
def version():
    # returns the version of first rcm listed
    url = 'http://' + host + ':19080/rcm-fitness-api/api/rcm/inventory/vxrack/FLEX'
    response = requests.get(url)
    assert response.status_code == 200, "Request has not been acknowledged as expected."
    data = response.json()
    rcmVersion = data["rcmInventoryItems"][0]["rcmVersion"]
    print(rcmVersion)
    return rcmVersion


@pytest.mark.rcm_fitness_mvp
@pytest.mark.rcm_fitness_mvp_extended
@pytest.mark.parametrize(("type", "model", "identifier", "fileName"), [
    ("iDRAC", "630", "Integrated Remote Access Controller", "iDRAC"),
    ("NIC", "630", "Intel(R) Ethernet 10G 4P X520/I350 rNDC -", "Network"),
    ("NIC", "630", "Intel(R) Ethernet 10G 2P X520 Adapter -", "Network"),
    ("BIOS", "630", "BIOS", "BIOS"),
    ("RAID", "630", "PERC H730P Mini", "RAID"),
    ("iDRAC", "730", "Integrated Remote Access Controller", "iDRAC"),
    ("NIC", "730", "Intel(R) Ethernet 10G 4P X520/I350 rNDC -", "Network"),
    ("NIC", "730", "Intel(R) Ethernet 10G 2P X520 Adapter -", "Network"),
    ("BIOS", "730", "BIOS", "BIOS"),
    ("RAID", "730", "PERC H730P Mini", "RAID")])
def test_post_eval(sys, rcmid, train, version, type, model, identifier, fileName):
    url = 'http://' + host + ':19080/rcm-fitness-api/api/rcm/evaluation/'
    body = {'systemUuid': sys[0], 'rcmUuid': rcmid}
    data_json = json.dumps(body)
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    response = requests.post(url, data_json, headers=headers)
    assert response.status_code == 200, "Request has not been acknowledged as expected."
    data = response.json()
    datas = json.dumps(data)
    # print(datas)
    evals = len(data['rcmEvaluationResults'])
    assert evals != 0, "No evaluation results found, has Collectcomponentversion been executed??"
    results = 0
    deviceIDlist = []
    instances = 0

    while results < evals:
        deviceIDlist.append(data['rcmEvaluationResults'][results]['evaluatedVersionDatum']['deviceUuid'])
        results += 1

    print(deviceIDlist)

    results = 0

    deviceID = data['rcmEvaluationResults'][0]['evaluatedVersionDatum']['deviceUuid']
    deviceID2 = data['rcmEvaluationResults'][1]['evaluatedVersionDatum']['deviceUuid']
    print("Server ID: %s" % deviceID)
    print("Train: %s" % train)
    print("Version: %s" % version)

    while results < evals:
        if data['rcmEvaluationResults'][results]['evaluatedVersionDatum']['definition'][
            'modelFamily'] == model and identifier in \
                data['rcmEvaluationResults'][results]['evaluatedVersionDatum']['identity']['identifier']:
            if data['rcmEvaluationResults'][results]['evaluatedVersionDatum']['identity']['elementType'] == type:
                # instances += 1
                # print('Results for :', type, model)
                assert data['rcmEvaluationResults'][results]['evaluatedRcmDatum']['rcmUuid'] == rcmid
                assert data['rcmEvaluationResults'][results]['evaluatedRcmDatum']['rcmTrain'] == train
                assert data['rcmEvaluationResults'][results]['evaluatedRcmDatum']['rcmVersion'] == version
                assert data['rcmEvaluationResults'][results]['elementUuid'] == \
                       data['rcmEvaluationResults'][results]['evaluatedVersionDatum']['componentUuid']
                assert type in data['rcmEvaluationResults'][results]['evaluatedVersionDatum']['identity'][
                    'serialNumber']
                assert data['rcmEvaluationResults'][results]['evaluatedRcmDatum']['productFamily'] == \
                       data['rcmEvaluationResults'][results]['evaluatedVersionDatum']['definition']['productFamily']
                assert data['rcmEvaluationResults'][results]['evaluatedRcmDatum']['product'] == \
                       data['rcmEvaluationResults'][results]['evaluatedVersionDatum']['definition']['product']
                # assert data['rcmEvaluationResults'][results]['evaluatedRcmDatum']['modelFamily'] == data['rcmEvaluationResults'][results]['evaluatedVersionDatum']['definition']['modelFamily']
                # assert data['rcmEvaluationResults'][results]['evaluatedRcmDatum']['model'] == data['rcmEvaluationResults'][results]['evaluatedVersionDatum']['definition']['model']
                assert data['rcmEvaluationResults'][results]['evaluatedVersionDatum']['versions'][0]['version'] == \
                       data['rcmEvaluationResults'][results]['actualValue']
                assert data['rcmEvaluationResults'][results]['evaluatedRcmDatum']['versions'][0] == \
                       data['rcmEvaluationResults'][results]['expectedValues'][0]
                assert data['rcmEvaluationResults'][results]['evaluatedVersionDatum'][
                           'deviceUuid'] == deviceID or deviceID2
                actual = data['rcmEvaluationResults'][results]['actualValue']
                expected = data['rcmEvaluationResults'][results]['expectedValues'][0]
                print(
                'Component UUID:', data['rcmEvaluationResults'][results]['evaluatedVersionDatum']['componentUuid'])
                print('Actual value:', data['rcmEvaluationResults'][results]['actualValue'])
                print('Expected value:', data['rcmEvaluationResults'][results]['expectedValues'][0])
                print('Message:', data['rcmEvaluationResults'][results]['evaluationMessage'])
                if actual == expected:
                    assert (data['rcmEvaluationResults'][results]['evaluationResult']) == "match", "Expect a match"
                    print("Returned result: %s" % data['rcmEvaluationResults'][results]['evaluationResult'])
                else:
                    assert (
                           data['rcmEvaluationResults'][results]['evaluationResult']) == "mismatch", "Expect a mismatch"
                    print("Returned result: %s" % data['rcmEvaluationResults'][results]['evaluationResult'])

                print("Stripping both expected and actual version strings......")
                stripActual = actual.strip("0")
                stripExpected = expected.strip("0")
                if stripActual == stripExpected:
                    print("Returned result: %s" % data['rcmEvaluationResults'][results]['evaluationResult'])
                    print('Actual stripped:', stripActual)
                    print('Expected stripped:', stripExpected)
                    assert (data['rcmEvaluationResults'][results]['evaluationResult']) == "match", "Expect a match"
                else:
                    print("Returned result: %s" % data['rcmEvaluationResults'][results]['evaluationResult'])
                    print('Actual stripped:', stripActual)
                    print('Expected stripped:', stripExpected)
                    assert (
                           data['rcmEvaluationResults'][results]['evaluationResult']) == "mismatch", "Expect a mismatch"

                if "versionFileName" in data['rcmEvaluationResults'][results]['evaluatedRcmDatum']:
                    assert fileName in data['rcmEvaluationResults'][results]['evaluatedRcmDatum'][
                        "versionFileName"], "Unexpected fileName returned."
                    assert data['rcmEvaluationResults'][results]['evaluatedRcmDatum'][
                               "versionFileHash"] != "", "Unexpected fileHash returned."
            instances += 1
        # instances == 0

        elif instances == 0:
            print('Specified type not found:', type)

        results += 1