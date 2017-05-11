#!/usr/bin/python
# Author: cullia
# Revision: 2.0
# Code Reviewed by:
# Description:

import af_support_tools
import pytest
import json
import time
import requests

port = 5672

try:
    env_file = 'env.ini'

    capreg_config_file = 'continuous-integration-deploy-suite/config_capreg.ini'
    capreg_config_header = 'config_details'

    capreg_config_property_rmq_user = 'rmq_user'
    capreg_config_property_rmq_password = 'rmq_password'

    capreg_config_property_cli_user = 'cli_user'
    capreg_config_property_cli_password = 'cli_password'

    capreg_config_property_rackhd_ip = 'rackhd_ipaddress'
    capreg_config_property_vcenter = 'vcenter'
    capreg_config_property_vcenter_user = 'vcenter_user'
    capreg_config_property_vcenter_password = 'vcenter_password'

except:
    print('Possible configuration error')

try:

    ipaddress = af_support_tools.get_config_file_property(config_file=env_file, heading='Base_OS', property='hostname')

    rmq_username = af_support_tools.get_config_file_property(config_file=capreg_config_file, heading=capreg_config_header,
                                                             property=capreg_config_property_rmq_user)

    rmq_password = af_support_tools.get_config_file_property(config_file=capreg_config_file, heading=capreg_config_header,
                                                             property=capreg_config_property_rmq_password)

    cli_username = af_support_tools.get_config_file_property(config_file=capreg_config_file, heading=capreg_config_header,
                                                             property=capreg_config_property_cli_user)

    cli_password = af_support_tools.get_config_file_property(config_file=capreg_config_file, heading=capreg_config_header,
                                                             property=capreg_config_property_cli_password)

    rackHD_IP = af_support_tools.get_config_file_property(config_file=capreg_config_file, heading=capreg_config_header,
                                                          property=capreg_config_property_rackhd_ip)

    vCenterFQDN = af_support_tools.get_config_file_property(config_file=capreg_config_file, heading=capreg_config_header,
                                                            property=capreg_config_property_vcenter)

    vCenterUser = af_support_tools.get_config_file_property(config_file=capreg_config_file, heading=capreg_config_header,
                                                            property=capreg_config_property_vcenter_user)

    vCenterPassword = af_support_tools.get_config_file_property(config_file=capreg_config_file, heading=capreg_config_header,
                                                                property=capreg_config_property_vcenter_password)

except:
    print('Possible configuration error')

#######################################################################################################################

try:
    # These are the cli commands needed to start a new docker instance for the named adapter/provider
    startCiscoProvider = 'docker run --net=host -v /opt/dell/cpsd/rcm-fitness/conf:/opt/dell/rcm-fitness/conf -td cpsd-hal-data-provider-cisco-network'
    startPoweredgeProvider = 'docker run --net=host -v /opt/dell/cpsd/rcm-fitness/conf/:/opt/dell/rcm-fitness/conf/ -td cpsd-hal-data-provider-poweredge'
    startRackHDAdapter = 'docker run --net=host -v /opt/dell/cpsd/:/opt/dell/cdsd -v /opt/dell/cpsd/rackhd-adapter-service/keystore/:/opt/dell/cpsd/rackhd-adapter-service/keystore/ -td cpsd-rackhd-adapter-service'
    startNodeDiscoverPaqx = 'docker run --net=host -v /opt/dell/cpsd/:/opt/dell/cdsd -v /opt/dell/cpsd/node-discovery-paqx/keystore/:/opt/dell/cpsd/node-discovery-paqx/keystore/ -td cpsd-node-discovery-paqx'
    startEndpointRegisteryService = 'systemctl start dell-endpoint-registration'
    startVcenterAdapter = 'docker run --net=host -v /opt/dell/cpsd/:/opt/dell/cdsd -v /opt/dell/cpsd/vcenter-adapter-service/keystore/:/opt/dell/cpsd/vcenter-adapter-service/keystore/ -td cpsd-vcenter-adapter-service'

    # The following are the number of Capabilities Tested. If this total number does not match what is returned then the test will need to be updated.
    numOfCiscoProviderCapabilities = 2
    numOfPowerEdgeCapabilities = 2
    numOfRackHDAdapterCapabilities = 7
    numOfNodeDiscoveredPaqxCapabilities = 1
    numOfEndPointRegisteryCapabilities = 1
    numOfVcenterApapterCapabilities = 8
    numOfcoprHDCapabilities = 1

    totalNumOfCapabilitiesTested = numOfCiscoProviderCapabilities \
                                   + numOfPowerEdgeCapabilities \
                                   + numOfRackHDAdapterCapabilities \
                                   + numOfNodeDiscoveredPaqxCapabilities \
                                   + numOfEndPointRegisteryCapabilities \
                                   + numOfVcenterApapterCapabilities \
                                   + numOfcoprHDCapabilities

except:
    print('Possible configuration error')


#######################################################################################################################

@pytest.mark.core_services_mvp
#@pytest.mark.skip
def test_capabilityRegistry_Control_and_Binding():
    # Every 7 seconds the Capability Registery sends out a message asking "who's out there?" This is a "ping" message.
    # Each service that is alive will respond with a "pong" message.  The correlationID value will be the same on all
    # messages so this is used to track that we are getting the correct message and not just "any" message.
    print('\nRunning Test on system: ', ipaddress)

    cleanup()
    bindQueues()

    # Until there is full integration of services we need to register the RackHD & VCenter manually by sending these messages
    print('\nPrerequisite: Manually configuring RackHD & VCenter')
    vCenterConfigApplicationProperties()
    consulBypassMsgRackHD()
    vCenterRegistrationMsg()
    time.sleep(10)

    # PART 1
    # Testing that the capability.registry.control is sending its ping message.  Its expected that in the body of the
    # message should be the Docker Container ID of the capability-registration-service. This value is compared to the
    # actual Docker ContainerID value.
    # The correlationID of the consumed message is saved and will be used in the capabilityRegistryBinding() test to
    # trace the response "pong" messages.
    time.sleep(7)
    # Ensure the COontrol & Binding Queues are empty to start
    af_support_tools.rmq_purge_queue(host=ipaddress, port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                     queue='test.capability.registry.control')
    af_support_tools.rmq_purge_queue(host=ipaddress, port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                     queue='test.capability.registry.binding')

    print('\nTest: The Capability Registry Control. Verify the Ping message')

    # Wait for & consume a "Ping" Message. The message is left in the queue to be consumed again. The correlationID is
    # in the header.  The return_basic_properties flag is set to True in order to get the header value. When
    # basic_ properties are returned the message cannot be converted to json which is the reason its "consumed" twice.
    waitForMsg('test.capability.registry.control')
    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.capability.registry.control',
                                                          remove_message=False, return_basic_properties=True)

    # Save the correlationID to be used in next part of the test
    correlationID = return_message[0].correlation_id
    correlationID = json.dumps(correlationID)

    print('The CorrelationID for this Control Msg:', correlationID)

    # The message is consumed again, checked for errors and converted to JSON.
    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.capability.registry.control')

    checkForErrors(return_message)
    return_json = json.loads(return_message, encoding='utf-8')
    retunedValue = return_json['hostname']

    # Get the actual Container ID value and compare it to the RMQ message body
    containerID = getdockerID('capability-registry-service')  # getdockerID() logs into vm and returns the dockerID

    # The value in the msg body should match the container ID. If they do not match indicates multiple containers
    assert containerID == retunedValue
    # time.sleep(3)

    print('The Capability Registry Control Ping message is sent and has the correct containerID:', containerID)
    print('\n*******************************************************\n')

    ####################################################################################################################
    #
    # PART 2
    # Testing that the expected providers/adapters are sending their respective Pong messages in responce to the Control
    # Ping message.  The CorrelationID from the control Ping message is used.

    print("Test: The Capability Registry Binding. Verify the Pong message from each provider / adapter")

    # This is the list of current/providers
    capabilityProviderCisco = 'cisco-network-data-provider'
    capabilityProviderEndpoint = 'endpoint-registry'
    capabilityProviderPowerEdge = 'poweredge-compute-data-provider'
    capabilityProviderRackhdAdapter = 'rackhd-adapter'
    capabilityProviderNodeDiscoveryPaqx = 'node-discovery-paqx'
    capabilityProviderVcenter = 'vcenter-adapter'
    capabilityProviderCoprhd = 'coprhd-adapter'

    # Each provider/adapter is given a flag that will be set to True once its responded. This method is used as the order
    # in which the responses come in is random. When all are tested the allTested flag is set and the test completes.
    ciscoProviderTested = False
    endpointTested = False
    powerEdgeProviderTested = False
    rackhdAdapterTested = False
    nodeDiscoveryTested = False
    vcenterAdapterTested = False
    coprhdtested = False
    allTested = False

    # To prevent the test waiting indefinitely we need to provide a timeout.  When new adapters/providers are added to
    # the test the expectedNumberOfBindings value will increase.
    errorTimeout = 0
    expectedNumberOfBindings = 7

    # Keep consuming messages until this condition is no longer true
    while allTested == False and errorTimeout <= expectedNumberOfBindings:

        # Only a message that comes in with the same correlationID as the Ping message is tested
        waitForMsg('test.capability.registry.binding')
        return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                              rmq_password=rmq_password,
                                                              queue='test.capability.registry.binding',
                                                              remove_message=False, return_basic_properties=True)

        testcorrelationID = return_message[0].correlation_id
        testcorrelationID = json.dumps(testcorrelationID)

        if testcorrelationID == correlationID:  # Only check messages that have the same CorrelationID as the ping message

            return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                                  rmq_password=rmq_password,
                                                                  queue='test.capability.registry.binding')
            checkForErrors(return_message)

            if capabilityProviderVcenter in return_message:
                print('Test:', capabilityProviderVcenter, 'Binding Message returned\n')
                vcenterAdapterTested = True

            if capabilityProviderNodeDiscoveryPaqx in return_message:
                print('Test:', capabilityProviderNodeDiscoveryPaqx, 'Binding Message returned\n')
                nodeDiscoveryTested = True

            if capabilityProviderRackhdAdapter in return_message:
                print('Test:', capabilityProviderRackhdAdapter, 'Binding Message returned\n')
                rackhdAdapterTested = True

            if capabilityProviderPowerEdge in return_message:
                print('Test:', capabilityProviderPowerEdge, 'Binding Message returned\n')
                powerEdgeProviderTested = True

            if capabilityProviderCisco in return_message:
                print('Test:', capabilityProviderCisco, 'Binding Message returned\n')
                ciscoProviderTested = True

            if capabilityProviderEndpoint in return_message:
                print('Test:', capabilityProviderEndpoint, 'Binding Message returned\n')
                endpointTested = True

            if capabilityProviderCoprhd in return_message:
                print('Test:', capabilityProviderCoprhd, 'Binding Message returned\n')
                coprhdtested = True

            if ciscoProviderTested == True \
                    and endpointTested == True \
                    and powerEdgeProviderTested == True \
                    and nodeDiscoveryTested == True \
                    and rackhdAdapterTested == True \
                    and vcenterAdapterTested == True \
                    and coprhdtested == True:
                allTested = True

        # A timeout is included to prevent an infinite loop waiting for a response.
        # If a response hasn't been received the flag will still be false and this can be used to return an error.
        if errorTimeout == expectedNumberOfBindings:
            if ciscoProviderTested == False:
                print('ERROR:', capabilityProviderCisco, 'Binding Message is not returned')

            if endpointTested == False:
                print('ERROR:', capabilityProviderEndpoint, 'Binding Message is not returned')

            if powerEdgeProviderTested == False:
                print('ERROR:', capabilityProviderPowerEdge, 'Binding Message is not returned')

            if rackhdAdapterTested == False:
                print('ERROR:', capabilityProviderRackhdAdapter, 'Binding Message is not returned')

            if nodeDiscoveryTested == False:
                print('ERROR:', capabilityProviderNodeDiscoveryPaqx, 'Binding Message is not returned')

            if vcenterAdapterTested == False:
                print('ERROR:', capabilityProviderVcenter, 'Binding Message is not returned')

            if coprhdtested == False:
                print('ERROR:', capabilityProviderCoprhd, 'Binding Message is not returned')

            assert False, 'Not all expected bindings are replying'

        errorTimeout += 1

    print('\n*******************************************************\n')

    cleanup()


@pytest.mark.core_services_mvp
#@pytest.mark.skip
def test_capabilityRegistry_ListCapabilities():
    # We are testing that all expected capabilites are returned when a capability Registry Request Message is sent.
    # All providers and their capabilities should be listed

    cleanup()
    bindQueues()

    print("\nTest: Send in a list capabilities message and to verify all providers are present")

    # Send in a "list capabilities message"
    originalcorrelationID = 'capability-registry-list-test-correlationid'
    the_payload = '{}'

    af_support_tools.rmq_publish_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                         rmq_password=rmq_password,
                                         exchange='exchange.dell.cpsd.hdp.capability.registry.request',
                                         routing_key='dell.cpsd.hdp.capability.registry.request',
                                         headers={
                                             '__TypeId__': 'com.dell.cpsd.hdp.capability.registry.list.capability.providers'},
                                         payload=the_payload,
                                         payload_type='json',
                                         correlation_id={originalcorrelationID})

    # Wait for and consume the Capability Response Message
    waitForMsg('test.capability.registry.response')
    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.capability.registry.response')

    checkForErrors(return_message)
    checkForFailures(return_message)

    # New proviers/adapters and their capabilites can be added here.

    # Verify the Cisco Network Adapter Response.
    ciscoName = 'cisco-network-data-provider'
    ciscoCapabilities1 = 'device-data-discovery'
    ciscoCapabilities2 = 'device-endpoint-validation'
    assert ciscoName in return_message, (ciscoName, 'not returned')
    assert ciscoCapabilities1 in return_message, (ciscoCapabilities1, 'capability is not available')
    assert ciscoCapabilities2 in return_message, (ciscoCapabilities2, 'capability is not available')
    print('\nAll expected cisco-network-data-provider Capabilities Returned')

    # Verify the Node Discovery Response
    nodeDisName = 'node-discovery-paqx'
    nodeDisCapabilities1 = 'list-discovered-nodes'
    assert nodeDisName in return_message, (nodeDisName, 'not returned')
    assert nodeDisCapabilities1 in return_message, (nodeDisCapabilities1, 'capability is not available')
    print('All expected node-discovery-paqx Capabilities Returned')

    # Verify the Endpoint Registery Response
    endPointRegName = 'endpoint-registry'
    endPointRegCapabilities1 = 'endpoint-registry-lookup'
    assert endPointRegName in return_message, (endPointRegName, 'not returned')
    assert endPointRegCapabilities1 in return_message, (endPointRegCapabilities1, 'capability is not available')
    print('All expected endpoint-registry Capabilities Returned')

    # Verify the PowerEdge Response
    powerEdgeName = 'poweredge-compute-data-provider'
    powerEdgeCapabilities1 = 'device-data-discovery'
    powerEdgeCapabilities2 = 'device-endpoint-validation'
    assert powerEdgeName in return_message, (powerEdgeName, 'not returned')
    assert powerEdgeCapabilities1 in return_message, (powerEdgeCapabilities1, 'capability is not available')
    assert powerEdgeCapabilities2 in return_message, (powerEdgeCapabilities2, 'capability is not available')
    print('All expected poweredge-compute-data-provider Capabilities Returned')

    # Verify the RackHD Apapter Response
    nodeDisName = 'rackhd-adapter'
    nodeDisCapabilities1 = 'rackhd-consul-register'
    nodeDisCapabilities2 = 'rackhd-list-nodes'
    nodeDisCapabilities3 = 'rackhd-upgrade-firmware-dellr730-server'
    nodeDisCapabilities4 = 'rackhd-upgrade-firmware-dell-idrac'
    nodeDisCapabilities5 = 'node-discovered-event'
    nodeDisCapabilities6 = 'rackhd-install-esxi'
    nodeDisCapabilities7 = 'rackhd-list-node-catalogs'
    assert nodeDisName in return_message, (nodeDisName, 'not returned')
    assert nodeDisCapabilities1 in return_message, (nodeDisCapabilities1, 'capability is not available')
    assert nodeDisCapabilities2 in return_message, (nodeDisCapabilities2, 'capability is not available')
    assert nodeDisCapabilities3 in return_message, (nodeDisCapabilities3, 'capability is not available')
    assert nodeDisCapabilities4 in return_message, (nodeDisCapabilities4, 'capability is not available')
    assert nodeDisCapabilities5 in return_message, (nodeDisCapabilities5, 'capability is not available')
    assert nodeDisCapabilities6 in return_message, (nodeDisCapabilities6, 'capability is not available')
    assert nodeDisCapabilities7 in return_message, (nodeDisCapabilities7, 'capability is not available')
    print('All expected rackhd-adapter Capabilities Returned')

    # Verify the VCenter Response
    vcenterName = 'vcenter-adapter'
    vcenterCapabilities1 = 'vcenter-consul-register'
    vcenterCapabilities2 = 'vcenter-discover'
    vcenterCapabilities3 = 'vcenter-enterMaintenance'
    vcenterCapabilities4 = 'vcenter-destroy-virtualMachine'
    vcenterCapabilities5 = 'vcenter-powercommand'
    vcenterCapabilities6 = 'vcenter-discover-cluster'
    vcenterCapabilities7 = 'vcenter-remove-host'
    vcenterCapabilities8 = 'vcenter-addhostvcenter'
    assert vcenterName in return_message, (vcenterName, 'not returned')
    assert vcenterCapabilities1 in return_message, (vcenterCapabilities1, 'capability is not available')
    assert vcenterCapabilities2 in return_message, (vcenterCapabilities2, 'capability is not available')
    assert vcenterCapabilities3 in return_message, (vcenterCapabilities3, 'capability is not available')
    assert vcenterCapabilities4 in return_message, (vcenterCapabilities4, 'capability is not available')
    assert vcenterCapabilities5 in return_message, (vcenterCapabilities5, 'capability is not available')
    assert vcenterCapabilities6 in return_message, (vcenterCapabilities6, 'capability is not available')
    assert vcenterCapabilities7 in return_message, (vcenterCapabilities7, 'capability is not available')
    assert vcenterCapabilities8 in return_message, (vcenterCapabilities8, 'capability is not available')
    print('All expected vcenter-adapter Capabilities Returned')

    # Verify the CoprHD Response
    coprHDName = 'coprhd-adapter'
    coprHDCapabilities1 = 'coprhd-consul-register'
    assert coprHDName in return_message, (coprHDName, 'not returned')
    assert coprHDCapabilities1 in return_message, (coprHDCapabilities1, 'capability is not available')

    print('All expected coprhd-adapter Capabilities Returned')

    print('\nTested Number of Capabilities:', totalNumOfCapabilitiesTested)

    # We will check how many "capabilities" are returned in the message and compare that to how many we are testing. We
    # do this becuase if new capabilites are added this test to this point would still Pass. If more capabilities are in
    # the responce then we know the test needs to be updated.

    returnedNumofCap = return_message.count('"profile"')  # count how many "profiles" (capabilities) are in the retuned msg.
    print('Actual Number of Capabilites Returned:', returnedNumofCap, '\n')

    # totalNumOfCapabilitiesTested value is calculated in the global settings above.
    if returnedNumofCap > totalNumOfCapabilitiesTested:
        print('Warning: test needs to be updated. Not all capabilities are tested')

    # This assert is disabled as it is prefered that the test does not fail if it needs updating.
    #assert totalNumOfCapabilitiesTested == returnedNumofCap, 'Test needs updating, more capabilites are available than are being tested'

    print('\n*******************************************************\n')
    cleanup()



@pytest.mark.core_services_mvp
#@pytest.mark.skip
def test_capabilityRegistry_Exchanges():

    # Verify the capability.registry Exchanges are bound to the correct queues

    # Format: test_queues_on_exchange(exchange, expected queue)

    print('\n*******************************************************')

    print("\nTest: Verify the the Capability Registry Binding is bound to the correct queues\n")
    test_queues_on_exchange('exchange.dell.cpsd.hdp.capability.registry.binding',
                            'queue.dell.cpsd.hdp.capability.registry.binding')


    print("\nTest: Verify the the Capability Registry Control is bound to the correct queues\n")
    test_queues_on_exchange('exchange.dell.cpsd.hdp.capability.registry.control',
                            'queue.dell.cpsd.hdp.capability.registry.control.cisco-network-data-provider')
    test_queues_on_exchange('exchange.dell.cpsd.hdp.capability.registry.control',
                            'queue.dell.cpsd.hdp.capability.registry.control.endpoint-registry')
    test_queues_on_exchange('exchange.dell.cpsd.hdp.capability.registry.control',
                            'queue.dell.cpsd.hdp.capability.registry.control.node-discovery-paqx')
    test_queues_on_exchange('exchange.dell.cpsd.hdp.capability.registry.control',
                            'queue.dell.cpsd.hdp.capability.registry.control.poweredge-compute-data-provider')
    test_queues_on_exchange('exchange.dell.cpsd.hdp.capability.registry.control',
                            'queue.dell.cpsd.hdp.capability.registry.control.rackhd-adapter')
    test_queues_on_exchange('exchange.dell.cpsd.hdp.capability.registry.control',
                            'queue.dell.cpsd.hdp.capability.registry.control.vcenter-adapter')


    print("\nTest: Verify the the Capability Registry Event is bound to the correct queues\n")
    test_queues_on_exchange('exchange.dell.cpsd.hdp.capability.registry.event',
                            'queue.dell.cpsd.hdp.capability.registry.event.node-discovery-paqx')
    test_queues_on_exchange('exchange.dell.cpsd.hdp.capability.registry.event',
                            'queue.dell.cpsd.hdp.capability.registry.event.dne-paqx')
    # test_queues_on_exchange('exchange.dell.cpsd.hdp.capability.registry.event', 'queue.dell.cpsd.hdp.capability.registry.event.fru-paqx')
    test_queues_on_exchange('exchange.dell.cpsd.hdp.capability.registry.event',
                            'queue.dell.cpsd.hdp.capability.registry.event.rackhd-adapter')
    test_queues_on_exchange('exchange.dell.cpsd.hdp.capability.registry.event',
                            'queue.dell.cpsd.hdp.capability.registry.event.vcenter-adapter')


    print("\nTest: Verify the the Capability Registry Request is bound to the correct queues\n")
    test_queues_on_exchange('exchange.dell.cpsd.hdp.capability.registry.request',
                            'queue.dell.cpsd.hdp.capability.registry.request')


    print("\nTest: Verify the the Capability Registry Response is bound to the correct queues\n")
    test_queues_on_exchange('exchange.dell.cpsd.hdp.capability.registry.response',
                            'queue.dell.cpsd.hdp.capability.registry.response.coprhd-adapter')
    test_queues_on_exchange('exchange.dell.cpsd.hdp.capability.registry.response',
                            'queue.dell.cpsd.hdp.capability.registry.response.dne-paqx')
    # test_queues_on_exchange('exchange.dell.cpsd.hdp.capability.registry.response', 'queue.dell.cpsd.hdp.capability.registry.response.fru-paqx')
    # test_queues_on_exchange('exchange.dell.cpsd.hdp.capability.registry.response', 'queue.dell.cpsd.hdp.capability.registry.response.hal-orchestrator-service')
    test_queues_on_exchange('exchange.dell.cpsd.hdp.capability.registry.response',
                            'queue.dell.cpsd.hdp.capability.registry.response.node-discovery-paqx')
    test_queues_on_exchange('exchange.dell.cpsd.hdp.capability.registry.response',
                            'queue.dell.cpsd.hdp.capability.registry.response.rackhd-adapter')
    test_queues_on_exchange('exchange.dell.cpsd.hdp.capability.registry.response',
                            'queue.dell.cpsd.hdp.capability.registry.response.vcenter-adapter')

    print('\n*******************************************************')


# It's likely this test will be removed as the functionality to stop & start containers is being removed
@pytest.mark.core_services_mvp_extended
def test_capaabilityRegistery_StopProvider():
    # When a provider/adapter becomes unavailable it is expected that a "Unregister" message is received
    # In this test we  1. verify the status of the docker container, 2. Stop the docker Container. 3. We verify that a
    # unregistered.event is received. And 4. that the provider/adapter is no longer listed in the
    # Capabilities List. 5. The container is then restarted and we verify 6. A new register msg is received and that
    # 7. the Capabilites are again listed.

    cleanup()
    bindQueues()
    time.sleep(15)

    # Function format: capabilityRegistryStopProvider(container, provider name, capability1, capability2(optional), capability3(optional)):

    # TODO Some are commented out due to on going dev work and they would currently fail.

    capabilityRegistryStopProvider('cpsd-hal-data-provider-cisco-network', 'cisco-network-data-provider', 'device-data-discovery', 'device-endpoint-validation')
    capabilityRegistryStopProvider('cpsd-hal-data-provider-poweredge', 'poweredge-compute-data-provider', 'device-data-discovery', 'device-endpoint-validation')
    # Not Reregistering capabilityRegistryStopProvider('cpsd-rackhd-adapter-service', 'rackhd-adapter', 'rackhd-consul-register', 'rackhd-list-nodes', 'rackhd-upgrade-firmware-dellr730-server', 'rackhd-upgrade-firmware-dell-idrac', 'node-discovered-event', 'rackhd-install-esxi', 'rackhd-list-node-catalogs')
    # Not Reregistering capabilityRegistryStopProvider('cpsd-node-discovery-paqx', 'node-discovery-paqx', 'list-discovered-nodes')
    # No Container to restart capabilityRegistryStopProvider('cpsd-core-endpoint-registry-service', 'endpoint-registry', 'endpoint-registry-lookup')
    # Not Reregistering capabilityRegistryStopProvider('cpsd-vcenter-adapter-service', 'vcenter-adapter', 'vcenter-consul-register', 'vcenter-discover', 'vcenter-enterMaintenance')


    cleanup()


@pytest.mark.core_services_mvp_extended
def test_capaabilityRegistery_KillProvider():
    cleanup()
    bindQueues()
    time.sleep(15)

    # When a provider/adapter becomes unavailable it is expected that a "Unregister" message is received
    # In this test we  1. verify the status of the docker container, 2. Kill the docker Container. 3. We verify that a
    # unregistered.event is received. And 4. that the provider/adapter is no longer listed in the
    # Capabilities List. 5. A new container is then started and we verify 6. A new register msg is received and that
    # 7. the Capabilites are again listed.

    # Function format: capabilityRegistryStopProvider(container, provider, docker-command, capability1, capability2(optional), capability3(optional)):

    # TODO Some are commented out due to on going dev work and they would currently fail. RackHD Capabilites don't come back on restart.

    capabilityRegistryKillProvider('cpsd-hal-data-provider-cisco-network', 'cisco-network-data-provider', startCiscoProvider, 'device-data-discovery', 'device-endpoint-validation')
    capabilityRegistryKillProvider('cpsd-hal-data-provider-poweredge', 'poweredge-compute-data-provider', startPoweredgeProvider, 'device-data-discovery', 'device-endpoint-validation')
    # Not Reregistering capabilityRegistryKillProvider('cpsd-rackhd-adapter-service', 'rackhd-adapter', startRackHDAdapter, 'rackhd-consul-register', 'rackhd-list-nodes', 'rackhd-upgrade-firmware-dellr730-server', 'rackhd-upgrade-firmware-dell-idrac', 'node-discovered-event', 'rackhd-install-esxi', 'rackhd-list-node-catalogs')
    # Not Reregistering capabilityRegistryKillProvider('cpsd-node-discovery-paqx', 'node-discovery-paqx', startNodeDiscoverPaqx, 'list-discovered-nodes')
    capabilityRegistryKillProvider('cpsd-core-endpoint-registration-service', 'endpoint-registry',startEndpointRegisteryService, 'endpoint-registry-lookup')
    # Not Reregistering capabilityRegistryStopProvider('cpsd-vcenter-adapter-service', 'vcenter-adapter', startVcenterAdapter, 'vcenter-consul-register', 'vcenter-discover', 'vcenter-enterMaintenance', 'vcenter-destroy-virtualMachine', 'vcenter-powercommand', 'vcenter-discover-cluster')

    cleanup()


#######################################################################################################################


def capabilityRegistryStopProvider(container, provider, capability1, capability2=None, capability3=None,
                                   capability4=None, capability5=None, capability6=None, capability7=None):
    # When a provider/adapter becomes unavailable it is expected that a "Unregister" message is received
    # In this test we  1. verify the status of the docker container, 2. Stop the docker Container. 3. We verify that a
    # unregistered.event is received. And 4. that the provider/adapter is no longer listed in the
    # Capabilities List. 5. The container is then restarted and we verify 6. A new register msg is received and that
    # 7. the Capabilites are again listed.

    print('** Test Name: Test the unregister msg with the', provider, 'stopped **\n')



    # Check the status of the service
    dockerStatus = getdockerStatus(container)
    print('Current ', container, ' status: ', dockerStatus)

    # Stop the service
    dockerID = getdockerID(container)
    sendCommand = 'docker stop ' + dockerID
    print(sendCommand)

    af_support_tools.rmq_purge_queue(host=ipaddress, port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                     queue='test.capability.registry.response')

    af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                      command=sendCommand, return_output=False)

    dockerStatus = getdockerStatus(container)
    print('Current ', container, ' status: ', dockerStatus)

    # Wait for & consume the unregister message. The msg is deliberately left in the queue to be consumed again without
    # the headers so it can be easily converted to readable json.
    waitForMsg('test.hdp.capability.registry.event')
    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.hdp.capability.registry.event',
                                                          remove_message=False, return_basic_properties=True)

    checkForErrors(return_message)
    checkForFailures(return_message)

    # Get the __TypeID__ value and assert it is the unregistered.event message.
    headerValue = return_message[0].headers
    headerValue = json.dumps(headerValue)
    typeIDValue = '{"__TypeId__": "com.dell.cpsd.hdp.capability.registry.capability.provider.unregistered.event"}'
    assert typeIDValue == headerValue, '__TypeId__ returned and expected do not match'

    # Consume the message again, (removing it from the queue this time) and verify the name that unregistered
    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.hdp.capability.registry.event')

    return_json = json.loads(return_message, encoding='utf-8')
    providerName = return_json['capabilityProvider']['identity']['name']

    assert providerName == provider

    print('\nTest Pass:', provider, 'Unregister message has been received')

    # ******************************************************************************************************************
    # Send in a "list capabilities message" and the stopped provider should be gone

    the_payload = '{}'

    af_support_tools.rmq_publish_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                         rmq_password=rmq_password,
                                         exchange='exchange.dell.cpsd.hdp.capability.registry.request',
                                         routing_key='dell.cpsd.hdp.capability.registry.request',
                                         headers={
                                             '__TypeId__': 'com.dell.cpsd.hdp.capability.registry.list.capability.providers'},
                                         payload=the_payload,
                                         payload_type='json')

    time.sleep(3)

    waitForMsg('test.capability.registry.response')
    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.capability.registry.response')
    checkForErrors(return_message)
    checkForFailures(return_message)

    if providerName in return_message:
        print(providerName, ' is still responding')
        assert False

    print('\nTest Pass:', provider, 'as expected is no longer in Capabilities list')

    # ******************************************************************************************************************
    # Unregister message has been received so now Restart the service and check for new Register Message

    print('Restarting ', container, 'image')
    sendCommand = 'docker start ' + dockerID
    print(sendCommand)
    af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                      command=sendCommand, return_output=False)

    time.sleep(3)
    dockerStatus = getdockerStatus(container)
    print('Current ', container, ' status: ', dockerStatus)

    # Wait for & consume the register message. The msg is deliberately left in the queue to be consumed again without
    # the headers so it can be easily converted to readable json.
    waitForMsg('test.hdp.capability.registry.event')
    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.hdp.capability.registry.event',
                                                          remove_message=False, return_basic_properties=True)
    checkForErrors(return_message)
    checkForFailures(return_message)

    # Get the __TypeID__ value and assert it is the registered.event message.
    headerValue = return_message[0].headers
    headerValue = json.dumps(headerValue)
    typeIDValue = '{"__TypeId__": "com.dell.cpsd.hdp.capability.registry.capability.provider.registered.event"}'
    assert typeIDValue == headerValue

    print('\nTest Pass:', provider, 'new Register message has been received')

    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.hdp.capability.registry.event')

    checkForErrors(return_message)
    checkForFailures(return_message)

    return_json = json.loads(return_message, encoding='utf-8')
    providerName = return_json['capabilityProvider']['identity']['name']

    assert providerName == provider

    if providerName not in return_message:
        print(providerName, ' is not responding')
        assert False

    print('\nTest Pass:', providerName, 'as expected is now in Capabilities list')

    # Verify all the expected Capabilities are present in the message
    capabilityName1 = capability1
    assert capabilityName1 in return_message
    print('\nTest Pass:', capabilityName1, 'capability is present')
    if capabilityName1 not in return_message:
        print(capabilityName1, ' is not present')
        assert False

    if capability2:
        capabilityName2 = capability2
        assert capabilityName2 in return_message
        print('Test Pass:', capabilityName2, 'capability is present')
        if capabilityName2 not in return_message:
            print(capabilityName2, ' is not present')
            assert False

    if capability3:
        capabilityName3 = capability3
        assert capabilityName3 in return_message
        print('Test Pass:', capabilityName3, 'capability is present')
        if capabilityName3 not in return_message:
            print(capabilityName3, ' is not present')
            assert False

    if capability4:
        capabilityName4 = capability4
        assert capabilityName4 in return_message
        print('Test Pass:', capabilityName4, 'capability is present')
        if capabilityName4 not in return_message:
            print(capabilityName4, ' is not present')
            assert False

    if capability5:
        capabilityName5 = capability5
        assert capabilityName5 in return_message
        print('Test Pass:', capabilityName5, 'capability is present')
        if capabilityName5 not in return_message:
            print(capabilityName5, ' is not present')
            assert False

    if capability6:
        capabilityName6 = capability6
        assert capabilityName6 in return_message
        print('Test Pass:', capabilityName6, 'capability is present')
        if capabilityName6 not in return_message:
            print(capabilityName6, ' is not present')
            assert False

    if capability7:
        capabilityName7 = capability7
        assert capabilityName7 in return_message
        print('Test Pass:', capabilityName7, 'capability is present')
        if capabilityName7 not in return_message:
            print(capabilityName7, ' is not present')
            assert False

    print('\n** Test Complete **')
    print('\n*******************************************************\n')


def capabilityRegistryKillProvider(container, provider, docker, capability1, capability2=None, capability3=None,
                                   capability4=None, capability5=None, capability6=None, capability7=None):
    # When a provider/adapter becomes unavailable it is expected that a "Unregister" message is received
    # In this test we  1. verify the status of the docker container, 2. Kill the docker Container. 3. We verify that a
    # unregistered.event is received. And 4. that the provider/adapter is no longer listed in the
    # Capabilities List. 5. A new container is then started and we verify 6. A new register msg is received and that
    # 7. the Capabilites are again listed.

    print('** Test Name: Test the unregister msg with the', provider, 'killed **\n')


    # Check the status of the service
    dockerStatus = getdockerStatus(container)
    print('Current ', container, ' status: ', dockerStatus)

    # Kill the service
    dockerID = getdockerID(container)
    sendCommand = 'docker kill ' + dockerID
    print(sendCommand)

    af_support_tools.rmq_purge_queue(host=ipaddress, port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                     queue='test.capability.registry.response')

    af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                      command=sendCommand, return_output=False)

    dockerStatus = getdockerStatus(container)
    print('Current ', container, ' status: ', dockerStatus)

    # Wait for & consume the unregister message. The msg is deliberately left in the queue to be consumed again without
    # the headers so it can be easily converted to readable json.
    waitForMsg('test.hdp.capability.registry.event')
    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.hdp.capability.registry.event',
                                                          remove_message=False, return_basic_properties=True)

    checkForErrors(return_message)
    checkForFailures(return_message)

    # Get the __TypeID__ value and assert it is the unregistered.event message.
    headerValue = return_message[0].headers
    headerValue = json.dumps(headerValue)

    typeIDValue = '{"__TypeId__": "com.dell.cpsd.hdp.capability.registry.capability.provider.unregistered.event"}'

    assert typeIDValue == headerValue

    # Consume the message again, (removing it from the queue this time) and verify the name that unregistered
    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.hdp.capability.registry.event')

    return_json = json.loads(return_message, encoding='utf-8')
    providerName = return_json['capabilityProvider']['identity']['name']

    assert providerName == provider

    print('\nTest Pass:', provider, 'Unregister message has been received')

    # ******************************************************************************************************************
    # Send in a "list capabilities message" and the killed provider should be gone

    the_payload = '{}'

    af_support_tools.rmq_publish_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                         rmq_password=rmq_password,
                                         exchange='exchange.dell.cpsd.hdp.capability.registry.request',
                                         routing_key='dell.cpsd.hdp.capability.registry.request',
                                         headers={
                                             '__TypeId__': 'com.dell.cpsd.hdp.capability.registry.list.capability.providers'},
                                         payload=the_payload,
                                         payload_type='json')

    time.sleep(3)

    waitForMsg('test.capability.registry.response')
    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.capability.registry.response')
    checkForErrors(return_message)
    checkForFailures(return_message)

    if providerName in return_message:
        print(providerName, ' is still responding')
        assert False

    print('\nTest Pass:', provider, 'as expected is no longer in Capabilities list')

    # ******************************************************************************************************************
    # Unregister message has been received so now start a new container for the service and check for new Register Message

    print('Creating a new ', container, 'image')
    sendCommand = docker
    print(sendCommand)
    af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                      command=sendCommand, return_output=False)

    time.sleep(3)

    dockerStatus = getdockerStatus(container)
    print('Current ', container, ' status: ', dockerStatus)

    # Wait for & consume the register message. The msg is deliberately left in the queue to be consumed again without
    # the headers so it can be easily converted to readable json.
    waitForMsg('test.hdp.capability.registry.event')
    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.hdp.capability.registry.event',
                                                          remove_message=False, return_basic_properties=True)
    checkForErrors(return_message)
    checkForFailures(return_message)

    # Get the __TypeID__ value and assert it is the registered.event message.
    headerValue = return_message[0].headers
    headerValue = json.dumps(headerValue)

    typeIDValue = '{"__TypeId__": "com.dell.cpsd.hdp.capability.registry.capability.provider.registered.event"}'
    assert typeIDValue == headerValue

    print('\nTest Pass:', provider, 'new Register message has been received')

    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.hdp.capability.registry.event')

    checkForErrors(return_message)
    checkForFailures(return_message)

    return_json = json.loads(return_message, encoding='utf-8')
    providerName = return_json['capabilityProvider']['identity']['name']

    assert providerName == provider

    if providerName not in return_message:
        print(providerName, ' is not responding')
        assert False

    print('\nTest Pass:', providerName, 'as expected is now in Capabilities list')

    # Verify all the expected Capabilities are present in the message
    capabilityName1 = capability1
    assert capabilityName1 in return_message
    print('\nTest Pass:', capabilityName1, 'capability is present')
    if capabilityName1 not in return_message:
        print(capabilityName1, ' is not present')
        assert False

    if capability2:
        capabilityName2 = capability2
        assert capabilityName2 in return_message
        print('Test Pass:', capabilityName2, 'capability is present')
        if capabilityName2 not in return_message:
            print(capabilityName2, ' is not present')
            assert False

    if capability3:
        capabilityName3 = capability3
        assert capabilityName3 in return_message
        print('Test Pass:', capabilityName3, 'capability is present')
        if capabilityName3 not in return_message:
            print(capabilityName3, ' is not present')
            assert False

    if capability4:
        capabilityName4 = capability4
        assert capabilityName4 in return_message
        print('Test Pass:', capabilityName4, 'capability is present')
        if capabilityName4 not in return_message:
            print(capabilityName4, ' is not present')
            assert False

    if capability5:
        capabilityName5 = capability5
        assert capabilityName5 in return_message
        print('Test Pass:', capabilityName5, 'capability is present')
        if capabilityName5 not in return_message:
            print(capabilityName5, ' is not present')
            assert False

    if capability6:
        capabilityName6 = capability6
        assert capabilityName6 in return_message
        print('Test Pass:', capabilityName6, 'capability is present')
        if capabilityName6 not in return_message:
            print(capabilityName6, ' is not present')
            assert False

    if capability7:
        capabilityName7 = capability7
        assert capabilityName7 in return_message
        print('Test Pass:', capabilityName7, 'capability is present')
        if capabilityName7 not in return_message:
            print(capabilityName7, ' is not present')
            assert False

    print('\n** Test Complete **')
    print('\n*******************************************************\n')


#######################################################################################################################
# These are functions needed to manually configure vcenter & rackhd details.

def vCenterConfigApplicationProperties():
    # We need a way for the Vcenter Cluster Discover code to be able to get the VCenter Credentials. Currently the only
    # way to do this is with a application.properties file in the vcenter-adapter container that has the name &
    # credentials. This function writes that file and restarts the container.

    applicationProperties = 'spring.rabbitmq.host=localhost' \
                            '\nspring.rabbitmq.port=5672' \
                            '\nspring.rabbitmq.username=guest' \
                            '\nspring.rabbitmq.password=guest' \
                            '\nserver.port=0' \
                            '\n' \
                            '\n#TO BE REMOVED: this is temp solution. Will get these from credential service once it is ready and remove this file.' \
                            '\n#put this file under here QA can change the vcenter credential without rebuild code.' \
                            '\n#vcenter.address=https://<iporHost>:443' \
                            '\nvcenter.address=https://' + vCenterFQDN + ':443' \
                                                                         '\nvcenter.username=' + vCenterUser + '' \
                                                                                                               '\nvcenter.password=' + vCenterPassword + ''

    # Get the containerID and and remove the file.
    vCenterContainerID = getdockerID('cpsd-vcenter-adapter-service')
    sendCommand = 'docker exec -i ' + vCenterContainerID + ' sh -c "rm application.properties"'
    af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                      command=sendCommand, return_output=False)

    time.sleep(1)

    # Write to the application.properties file specifying the vcenter name & credentials.
    sendCommand = 'docker exec -i ' + vCenterContainerID + ' sh -c "echo -e \'' + applicationProperties + '\' >> application.properties"'
    af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                      command=sendCommand, return_output=False)

    # Restart the vcenter doocker container.
    sendCommand = 'docker restart ' + vCenterContainerID
    af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                      command=sendCommand, return_output=False)

    time.sleep(3)


def vCenterRegistrationMsg():
    # Until there is a way to automatically register a vcenter we need to register it manually by sending this message.

    af_support_tools.rmq_purge_queue(host=ipaddress, port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                     queue='test.controlplane.vcenter.response')

    af_support_tools.rmq_purge_queue(host=ipaddress, port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                     queue='test.endpoint.registration.event')

    the_payload = '{"messageProperties":{"timestamp":"2010-01-01T12:00:00Z","correlationId":"vcenter-registtration-corr-id","replyTo":"localhost"},"registrationInfo":{"address":"https://' + vCenterFQDN + ':443","username":"' + vCenterUser + '","password":"' + vCenterPassword + '"}}'

    af_support_tools.rmq_publish_message(host=ipaddress, rmq_username=rmq_username, rmq_password=rmq_password,
                                         exchange='exchange.cpsd.controlplane.vcenter.request',
                                         routing_key='controlplane.hypervisor.vcenter.endpoint.register',
                                         headers={
                                             '__TypeId__': 'com.dell.cpsd.vcenter.registration.info.request'},
                                         payload=the_payload)

    waitForMsg('test.controlplane.vcenter.response')
    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.controlplane.vcenter.response',
                                                          remove_message=True)
    checkForErrors(return_message)
    return_json = json.loads(return_message, encoding='utf-8')
    assert return_json['responseInfo']['message']=='SUCCESS', 'ERROR: Vcenter validation failure'


    waitForMsg('test.endpoint.registration.event')
    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.endpoint.registration.event',
                                                          remove_message=True)

    checkForErrors(return_message)
    return_json = json.loads(return_message, encoding='utf-8')
    assert return_json['endpoint']['type'] == 'vcenter', 'vcenter not registered with endpoint'


def consulBypassMsgRackHD():
    # Until consul is  working properly & integrated with the rackhd adapter in the same environment we need to register
    # it manually by sending this message.

    the_payload = '{"endpoint":{"type":"rackhd","instances":[{"url":"http://' + rackHD_IP + ':8080"}]}}'

    af_support_tools.rmq_publish_message(host=ipaddress, rmq_username=rmq_username, rmq_password=rmq_password,
                                         exchange='exchange.dell.cpsd.endpoint.registration.event',
                                         routing_key='dell.cpsd.endpoint.discovered',
                                         headers={
                                             '__TypeId__': 'com.dell.cpsd.endpoint-registry.endpointsdiscoveredevent'},
                                         payload=the_payload)

    time.sleep(3)


#######################################################################################################################
# These are common functions that are used throughout the main test.


def bindQueues():
    af_support_tools.rmq_bind_queue(host=ipaddress,
                                    port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                    queue='test.capability.registry.control',
                                    exchange='exchange.dell.cpsd.hdp.capability.registry.control',
                                    routing_key='#')

    af_support_tools.rmq_bind_queue(host=ipaddress,
                                    port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                    queue='test.capability.registry.binding',
                                    exchange='exchange.dell.cpsd.hdp.capability.registry.binding',
                                    routing_key='#')

    af_support_tools.rmq_bind_queue(host=ipaddress,
                                    port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                    queue='test.capability.registry.request',
                                    exchange='exchange.dell.cpsd.hdp.capability.registry.request',
                                    routing_key='#')

    af_support_tools.rmq_bind_queue(host=ipaddress,
                                    port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                    queue='test.capability.registry.response',
                                    exchange='exchange.dell.cpsd.hdp.capability.registry.response',
                                    routing_key='#')

    af_support_tools.rmq_bind_queue(host=ipaddress,
                                    port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                    queue='test.cisco.network.data.provider.request',
                                    exchange='exchange.dell.cpsd.hdp.hal.data.provider.cisco.network.data.provider.request',
                                    routing_key='#')

    af_support_tools.rmq_bind_queue(host=ipaddress,
                                    port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                    queue='test.data.provider.work.response',
                                    exchange='exchange.dell.cpsd.hdp.hal.data.provider.work.response',
                                    routing_key='#')

    af_support_tools.rmq_bind_queue(host=ipaddress,
                                    port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                    queue='test.hdp.capability.registry.event',
                                    exchange='exchange.dell.cpsd.hdp.capability.registry.event',
                                    routing_key='#')

    af_support_tools.rmq_bind_queue(host=ipaddress,
                                    port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                    queue='test.endpoint.registration.event',
                                    exchange='exchange.dell.cpsd.endpoint.registration.event',
                                    routing_key='#')

    af_support_tools.rmq_bind_queue(host=ipaddress,
                                    port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                    queue='test.controlplane.vcenter.response',
                                    exchange='exchange.cpsd.controlplane.vcenter.response',
                                    routing_key='#')


def cleanup():
    print('Cleaning up...')

    af_support_tools.rmq_delete_queue(host=ipaddress, port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                      queue='test.capability.registry.control')

    af_support_tools.rmq_delete_queue(host=ipaddress, port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                      queue='test.capability.registry.binding')

    af_support_tools.rmq_delete_queue(host=ipaddress, port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                      queue='test.capability.registry.request')

    af_support_tools.rmq_delete_queue(host=ipaddress, port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                      queue='test.capability.registry.response')

    af_support_tools.rmq_delete_queue(host=ipaddress, port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                      queue='test.cisco.network.data.provider.request')

    af_support_tools.rmq_delete_queue(host=ipaddress, port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                      queue='test.data.provider.work.response')

    af_support_tools.rmq_delete_queue(host=ipaddress, port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                      queue='test.hdp.capability.registry.event')

    af_support_tools.rmq_delete_queue(host=ipaddress, port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                      queue='test.endpoint.registration.event')

    af_support_tools.rmq_delete_queue(host=ipaddress, port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                      queue='test.controlplane.vcenter.response')


def waitForMsg(queue):
    # This function keeps looping untill a message is in the specified queue. We do need it to timeout and throw an error
    # if a message never arrives. Once a message appears in the queue the function is complete and main continues.

    # The length of the queue, it will start at 0 but as soon as we get a response it will increase
    q_len = 0

    # Represents the number of seconds that have gone by since the method started
    timeout = 0

    # Max number of seconds to wait
    max_timeout = 100

    # Amount of time in seconds that the loop is going to wait on each iteration
    sleeptime = 1

    while q_len < 1:
        time.sleep(sleeptime)
        timeout += sleeptime

        q_len = af_support_tools.rmq_message_count(host=ipaddress,
                                                   port=port,
                                                   rmq_username=rmq_username,
                                                   rmq_password=rmq_password,
                                                   queue=queue)

        if timeout > max_timeout:
            print('ERROR: Message took too long to return. Something is wrong')
            cleanup()
            break


def checkForErrors(return_message):
    checklist = 'errors'
    if checklist in return_message:
        print('\nBUG: Error in Response Message\n')
        assert False  # This assert is to fail the test


def checkForFailures(return_message):
    checklist = 'failureReasons'
    if checklist in return_message:
        return_json = json.loads(return_message, encoding='utf-8')
        errorMsg = return_json['failureReasons'][0]['message']
        print('The following error has been returned :', errorMsg)
        print('Possible component validation issue')
        assert False  # This assert is to fail the test


def getdockerID(imageName):
    image = imageName

    sendCommand = 'docker ps | grep ' + image + ' | awk \'{print $1}\''
    containerID = af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                                    command=sendCommand, return_output=True)

    containerID = containerID.strip()
    return (containerID)


def getdockerStatus(imageName):
    image = imageName

    sendCommand = 'docker ps --all | grep ' + image + ' | awk \'{print $7}\''
    containerStatus = af_support_tools.send_ssh_command(host=ipaddress, username=cli_username, password=cli_password,
                                                        command=sendCommand, return_output=True)

    containerStatus = containerStatus.strip()
    return (containerStatus)


def rest_queue_list(user=rmq_username, password=rmq_password, host=ipaddress, port=15672, virtual_host=None,exchange=None):
    url = 'http://%s:%s/api/exchanges/%s/%s/bindings/source' % (host, port, virtual_host, exchange)
    response = requests.get(url, auth=(user, password))
    queues = [q['destination'] for q in response.json()]
    return queues


def test_queues_on_exchange(suppliedExchange, suppliedQueue):
    queues = rest_queue_list(user=rmq_username, password=rmq_password, host=ipaddress, port=15672, virtual_host='%2f',
                             exchange=suppliedExchange)
    queues = json.dumps(queues)

    assert suppliedQueue in queues, 'The queue "' + suppliedQueue + '" is not bound to the exchange "' + suppliedExchange + '"'
    print(suppliedExchange, '\nis bound to\n', suppliedQueue, '\n')


#######################################################################################################################
