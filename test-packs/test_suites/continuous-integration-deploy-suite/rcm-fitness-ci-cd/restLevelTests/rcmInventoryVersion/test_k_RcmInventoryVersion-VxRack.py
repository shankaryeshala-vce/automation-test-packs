#!/usr/bin/env python
import json
import pika
import sys
import logging
import requests
import pytest
import os
import re
import af_support_tools
from collections import Counter


@pytest.fixture(scope="module", autouse=True)
def load_test_data():
    global path
    path = "/home/autouser/PycharmProjects/auto-framework/test_suites/continuous-integration-deploy-suite/rcm-fitness-ci-cd/restLevelTests/rcmInventory/"
    ensurePathExists(path)
    purgeOldOutput(path, "rcmDef")

    global ssl_options
    ssl_options = {"ca_certs":"/etc/rabbitmq/certs/testca/cacert.pem","certfile":"/etc/rabbitmq/certs/certs/client/cert.pem","keyfile":"/etc/rabbitmq/certs/certs/client/key.pem","cert_reqs":"ssl.CERT_REQUIRED","ssl_version":"ssl.PROTOCOL_TLSv1_2"}

    # Set config ini file name
    global env_file
    env_file = 'env.ini'

    global host
    host = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='hostname')

    ensurePathExists(path)
    purgeOldOutput(path, "rcmInventoryVer")

def ensurePathExists(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

def purgeOldOutput(dir, pattern):
    for f in os.listdir(dir):
        if re.search(pattern, f) and f.endswith(".json"):
            os.remove(os.path.join(dir, f))
            print("Old output files successfully deleted.")
        else:
            print('Unable to locate output files to remove.')


def getAvailableRCMs(family, model, train, version):
        # print(data)

    option = "ORIGINAL"
    optionAdd = "ADDENDUM"
    optionManu = "MANUFACTURING"

    exception = "No rcm definitions for system family"
    url = 'http://' + host + ':19080/rcm-fitness-api/api/rcm/inventory/' + family + "/" + model + "/" + train + "/" + version + "/"
    print(url)
    resp = requests.get(url)
    data = json.loads(resp.text)
    rcm = data["rcmInventoryItems"]

    assert resp.status_code == 200, "Request has not been acknowledged as expected."

    if data != "":
        if data["message"] == None:
            #print(data)
#            if
            with open(path + 'rcmInventoryVersion.json', 'w') as outfile:
                json.dump(data, outfile, sort_keys=True, indent=4, ensure_ascii=False)

            print("\nStarting to verify a sample of the returned data....")
            assert len(rcm) > 0
            print("\nRequesting all RCMs for family: %s" % train)
            print("Number of RCMs found: %d" % len(rcm))

            lastRCM = len(rcm)
            midRCM = (len(rcm))/2
            midRCM = int(midRCM)
            # print(data["rcms"][0]["viewOption"])
            assert rcm[0]["rcmVersion"] == version
            assert rcm[(lastRCM-1)]["rcmVersion"] == version
            assert rcm[0]["rcmTrain"] == train
            assert rcm[(lastRCM-1)]["rcmTrain"] == train
            assert rcm[0]["systemModelFamily"] == model
            assert rcm[(lastRCM-1)]["systemModelFamily"] == model
            assert rcm[0]["systemProductFamily"] == family
            assert rcm[(lastRCM-1)]["systemProductFamily"] == family
            assert (rcm[0]["viewOption"] == option) or (rcm[0]["viewOption"] == optionAdd) or (rcm[0]["viewOption"] == optionManu)
            assert (rcm[(lastRCM-1)]["viewOption"] == option) or (rcm[(lastRCM-1)]["viewOption"] == optionAdd) or (rcm[(lastRCM-1)]["viewOption"] == optionManu)
        else:
            combo = str(family + "/" + model + "/" + train)
            print("\nNo RCMs found for product/model/train combination: %s" % combo)
            print(data["message"])
            assert exception in data["message"], ("No RCMs returned for model:" + train)


        print("\nReturned data has completed all defined checks successfully......")

def getAvailableRCMs_Invalid(family, model, train, version):
        # print(data)

    option = "ORIGINAL"
    optionAdd = "ADDENDUM"
    optionManu = "MANUFACTURING"

    exception = "No rcm definitions for system family"
    url = 'http://' + host + ':19080/rcm-fitness-api/api/rcm/inventory/' + family + "/" + model + "/" + train + "/" + version + "/"
    print(url, "\n")
    resp = requests.get(url)
    data = json.loads(resp.text)
    rcm = data["rcmInventoryItems"]

    assert resp.status_code == 200, "Request has not been acknowledged as expected."

    if not rcm:
        if ("message") in data.keys():
            print(data["message"])
            assert ('RFCA1021I') in (data["message"]), "Returned Error Message does not reflect expected Error Code."
            assert (family) in (data["message"]), "Returned Error Message does not include expected Family."
            assert (model) in (data["message"]), "Returned Error Message does not include expected Model."
            assert (train) in (data["message"]), "Returned Error Message does not include expected Train."
            assert (version) in (data["message"]), "Returned Error Message does not include expected Version."

    print("\nReturned data has completed all defined checks successfully......")

def getAvailableRCMs_Null(family, model, train, version):
    url = 'http://' + host + ':19080/rcm-fitness-api/api/rcm/inventory/' + family + "/" + model + "/" + train + '/' + version + '/'
    print(url, "\n")
    resp = requests.get(url)

    #print("Requesting a NULL train ....")
    print(resp.status_code)
    assert resp.status_code == 404, "Request has not been acknowledged as expected."

@pytest.mark.rcm_fitness_mvp_extended
def test_getRCM1():
    getAvailableRCMs("VxRack", "FLEX", "9.2", "9.2.33.1")
@pytest.mark.rcm_fitness_mvp_extended
def test_getRCM2():
    getAvailableRCMs_Invalid("VxRack", "FLEX", "9.2", "9.2.99")
@pytest.mark.rcm_fitness_mvp_extended
def test_getRCM3():
    getAvailableRCMs_Invalid("VxRack", "FLEX", "9.9", "9.2.33")
@pytest.mark.rcm_fitness_mvp_extended
def test_getRCM4():
    getAvailableRCMs_Invalid("VxRack", "999", "9.2", "9.2.33")
@pytest.mark.rcm_fitness_mvp_extended
def test_getRCM7():
    getAvailableRCMs_Null("VxRack", "FLEX", "9.2", "")
@pytest.mark.rcm_fitness_mvp_extended
def test_getRCM8():
    getAvailableRCMs_Null("VxRack", "FLEX", "", "9.2.33")
@pytest.mark.rcm_fitness_mvp_extended
def test_getRCM9():
    getAvailableRCMs_Null("VxRack", "", "9.2", "9.2.33")
@pytest.mark.rcm_fitness_mvp_extended
def test_getRCM10():
    getAvailableRCMs_Null("", "1000 FLEX", "9.2", "9.2.33")
@pytest.mark.rcm_fitness_mvp_extended
def test_getRCM11():
    getAvailableRCMs_Null("", "", "", "")
#@pytest.mark.TC546560_Empty
#def test_getRCM7():
#    getAvailableRCMs_Invalid("", "", "")
