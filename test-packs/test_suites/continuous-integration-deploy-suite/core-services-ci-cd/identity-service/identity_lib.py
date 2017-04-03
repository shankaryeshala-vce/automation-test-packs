import af_support_tools
import json
import time


payload_file = 'identity_service/payload.ini'
payload_header = 'identity_service'


# Always specify user names & password here at the start. Makes changing them later much easier,
rmq_username = 'test'
rmq_password = 'test'
port = 5672


def get_element_uuids(ipaddress):
    print("Building list of ElementUuids...")
    elementuuids = []
    the_payload = af_support_tools.get_config_file_property(config_file=payload_file,
                                                            heading=payload_header,
                                                            property="identifyelement")

    af_support_tools.rmq_publish_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                         rmq_password=rmq_password,
                                         exchange='exchange.dell.cpsd.eids.identity.request',
                                         routing_key='dell.cpsd.eids.identity.request',
                                         headers={'__TypeId__': 'dell.cpsd.core.identity.identify.element'},
                                         payload=the_payload,
                                         payload_type='json')

    waitForMsg('test.identity.response', ipaddress)
    return_message = af_support_tools.rmq_consume_message(host=ipaddress, port=port, rmq_username=rmq_username,
                                                          rmq_password=rmq_password,
                                                          queue='test.identity.response')

    return_json = json.loads(return_message, encoding='utf-8')

    for _ in range(len(return_json['elementIdentifications'])):
        # These Uuid Values are used to create the payloads for the describe_element Test
        elementuuids.append(return_json['elementIdentifications'][_]['elementUuid'])

    return elementuuids


# Delete the test queue
def cleanup(ipaddress):
    print('Cleaning up...')

    af_support_tools.rmq_delete_queue(host=ipaddress, port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                      queue='test.identity.request')

    af_support_tools.rmq_delete_queue(host=ipaddress, port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                      queue='test.identity.response')


# Create & bind the test queues
def bind_queues(ipaddress):
    print('Creating the test EIDS Queues')
    af_support_tools.rmq_bind_queue(host=ipaddress,
                                    port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                    queue='test.identity.request',
                                    exchange='exchange.dell.cpsd.eids.identity.request',
                                    routing_key='#')

    af_support_tools.rmq_bind_queue(host=ipaddress,
                                    port=port, rmq_username=rmq_username, rmq_password=rmq_password,
                                    queue='test.identity.response',
                                    exchange='exchange.dell.cpsd.eids.identity.response',
                                    routing_key='#')


# Create the payloads used in the test
def create_messages():
    print('Creating payload files')

    # Create the payload and set it in the specified file.  my_payload is whatever you need to use. Hint: the correllationId field can be used as a description which makes it easier to locate in the Trace log.
    my_payload = '{"timestamp":"2017-01-27T14:18:51Z","correlationId":"c92b8be9-a892-4a76-a8d3-933c85ead7bb","reply-to":"dell.cpsd.eids.identity.request.sds.gouldc-mint","elementIdentities":[{"correlationUuid":"fb4e839d-aba1-409e-82d7-7e4632d6b647","identity":{"elementType":"group","classification":"GROUP","parents":[{"elementType":"VCESYSTEM","classification":"SYSTEM","businessKeys":[{"businessKeyType":"CONTEXTUAL","key":"IDENTIFIER","value":"VXB-340"},{"businessKeyType":"ABSOLUTE","key":"SERIAL_NUMBER","value":"RTP-VXB340-DQAV34YX"}]}],"businessKeys":[{"businessKeyType":"CONTEXTUAL","key":"IDENTIFIER","value":"SystemNetwork"}]}},{"correlationUuid":"d4964090-76b8-4d4a-8068-4cd8ff258462","identity":{"elementType":"SWITCH","classification":"DEVICE","parents":[{"elementType":"group","classification":"GROUP","parents":[{"elementType":"VCESYSTEM","classification":"SYSTEM","businessKeys":[{"businessKeyType":"CONTEXTUAL","key":"IDENTIFIER","value":"VXB-340"},{"businessKeyType":"ABSOLUTE","key":"SERIAL_NUMBER","value":"RTP-VXB340-DQAV34YX"}]}],"businessKeys":[{"businessKeyType":"CONTEXTUAL","key":"IDENTIFIER","value":"SystemNetwork"}]}],"businessKeys":[{"businessKeyType":"CONTEXTUAL","key":"COMPONENT_TAG","value":"MGMT-N3A"}]}},{"correlationUuid":"93eb24fd-b8b0-49fa-8911-17f1cba72034","identity":{"elementType":"SWITCH","classification":"DEVICE","parents":[{"elementType":"group","classification":"GROUP","parents":[{"elementType":"VCESYSTEM","classification":"SYSTEM","businessKeys":[{"businessKeyType":"CONTEXTUAL","key":"IDENTIFIER","value":"VXB-340"},{"businessKeyType":"ABSOLUTE","key":"SERIAL_NUMBER","value":"RTP-VXB340-DQAV34YX"}]}],"businessKeys":[{"businessKeyType":"CONTEXTUAL","key":"IDENTIFIER","value":"SystemNetwork"}]}],"businessKeys":[{"businessKeyType":"CONTEXTUAL","key":"COMPONENT_TAG","value":"MGMT-N3B"}]}},{"correlationUuid":"0c180853-bff6-4813-9099-3f80816ce450","identity":{"elementType":"VCESYSTEM","classification":"SYSTEM","businessKeys":[{"businessKeyType":"CONTEXTUAL","key":"IDENTIFIER","value":"VXB-340"},{"businessKeyType":"ABSOLUTE","key":"SERIAL_NUMBER","value":"RTP-VXB340-DQAV34YX"}]}}]}'
    af_support_tools.set_config_file_property(config_file=payload_file,
                                              heading=payload_header,
                                              property="identifyelement",
                                              value=my_payload)

    # Create the payload and set it in the specified file.  my_payload is whatever you need to use. Hint: the correllationId field can be used as a description which makes it easier to locate in the Trace log.
    my_payload = '{"timestamp":"2017-03-15T09:40:17Z","correlationId":"key-accuracy-0000-0000-0000","reply-to":"dell.cpsd.eids.identity.request.sds.test","elementIdentities":[{"correlationUuid":"12345-abcdef-54321-fedcba","identity":{"elementType":"TESTELEMENT","classification":"DEVICE","parents":[],"businessKeys":[{"businessKeyType":"CONTEXTUAL","key":"NAME","value":"THE_NAME"},{"businessKeyType":"CONTEXTUAL","key":"DESCRIPTION","value":"THE_DESCRIPTION"},{"businessKeyType":"CONTEXTUAL","key":"IPADDRESS","value":"THE_IPADDRESS"}],"contextualKeyAccuracy":2}}]}'
    af_support_tools.set_config_file_property(config_file=payload_file,
                                              heading=payload_header,
                                              property='keyaccuracy',
                                              value=my_payload)

    my_payload = '{"timestamp":"2017-01-27T14:18:51Z","correlationId":"key-accuracy-identify-0000-0000","reply-to":"dell.cpsd.eids.identity.request.sds.test","elementIdentities":[{"correlationUuid":"12345-abcdef-54321-fedcba","identity":{"elementType":"TESTELEMENT","classification":"DEVICE","parents":[],"businessKeys":[{"businessKeyType":"CONTEXTUAL","key":"NAME","value":"THE_NAME"},{"businessKeyType":"CONTEXTUAL","key":"DESCRIPTION","value":"THE_DESCRIPTION"}]}}]}'
    af_support_tools.set_config_file_property(config_file=payload_file,
                                              heading=payload_header,
                                              property='keyaccuracyid_ab',
                                              value=my_payload)

    my_payload = '{"timestamp":"2017-01-27T14:18:51Z","correlationId":"key-accuracy-identify-0000-0000","reply-to":"dell.cpsd.eids.identity.request.sds.test","elementIdentities":[{"correlationUuid":"12345-abcdef-54321-fedcba","identity":{"elementType":"TESTELEMENT","classification":"DEVICE","parents":[],"businessKeys":[{"businessKeyType":"CONTEXTUAL","key":"NAME","value":"THE_NAME"},{"businessKeyType":"CONTEXTUAL","key":"IPADDRESS","value":"THE_IPADDRESS"}]}}]}'
    af_support_tools.set_config_file_property(config_file=payload_file,
                                              heading=payload_header,
                                              property='keyaccuracyid_ac',
                                              value=my_payload)

    my_payload = '{"timestamp":"2017-01-27T14:18:51Z","correlationId":"key-accuracy-identify-0000-0000","reply-to":"dell.cpsd.eids.identity.request.sds.test","elementIdentities":[{"correlationUuid":"12345-abcdef-54321-fedcba","identity":{"elementType":"TESTELEMENT","classification":"DEVICE","parents":[],"businessKeys":[{"businessKeyType":"CONTEXTUAL","key":"NAME","value":"THE_NAME"}]}}]}'
    af_support_tools.set_config_file_property(config_file=payload_file,
                                              heading=payload_header,
                                              property='keyaccuracyid_neg',
                                              value=my_payload)

    my_payload = '{"timestamp":"2017-01-27T14:18:51Z","correlationId":"c92b8be9-a892-4a76-a8d3-933c85ead7bb","reply-to":"dell.cpsd.eids.identity.request.sds.gouldc-mint","elementIdentities":[{"correlationUuid":"0c180853-bff6-4813-9099-3f80816ce450","identity":{"elementType":"","classification":"SYSTEM","businessKeys":[{"businessKeyType":"CONTEXTUAL","key":"IDENTIFIER","value":"VXB-340"},{"businessKeyType":"ABSOLUTE","key":"SERIAL_NUMBER","value":"RTP-VXB340-DQAV34YX"}]}}]}'
    af_support_tools.set_config_file_property(config_file=payload_file,
                                              heading=payload_header,
                                              property='ident_no_element_type',
                                              value=my_payload)

    my_payload = '{"timestamp":"2017-01-27T14:51:57Z","correlationId":"5d7f6d34-4271-4593-9bad-1b95589e5189","reply-to":"dell.cpsd.eids.identity.request.hal.gouldc-mint","elementUuids":[]}'
    af_support_tools.set_config_file_property(config_file=payload_file,
                                              heading=payload_header,
                                              property='describe_no_element',
                                              value=my_payload)

    # my_payload = '{"timestamp":"2017-01-27T14:18:51Z","correlationId":"c92b8be9-a892-4a76-a8d3-933c85ead7bb","reply-to":"dell.cpsd.eids.identity.request.sds.gouldc-mint","elementIdentities":[{"correlationUuid":"0c180853-bff6-4813-9099-3f80816ce450","identity":{"elementType":"VCESYSTEM","classification":,"businessKeys":[{"businessKeyType":"CONTEXTUAL","key":"IDENTIFIER","value":"VXB-340"},{"businessKeyType":"ABSOLUTE","key":"SERIAL_NUMBER","value":"RTP-VXB340-DQAV34YX"}]}}]}'
    # af_support_tools.set_config_file_property(config_file=payload_file,
    #                                           heading=payload_header,
    #                                           property='ident_no_class',
    #                                           value=my_payload)
    #
    # my_payload = '{"timestamp":"2017-01-27T14:18:51Z","correlationId":"c92b8be9-a892-4a76-a8d3-933c85ead7bb","reply-to":"dell.cpsd.eids.identity.request.sds.gouldc-mint","elementIdentities":[{"correlationUuid":"0c180853-bff6-4813-9099-3f80816ce450","identity":{"elementType":"VCESYSTEM","classification":"SYSTEM","businessKeys":[{"businessKeyType":,"key":"IDENTIFIER","value":"VXB-340"},{"businessKeyType":"ABSOLUTE","key":"SERIAL_NUMBER","value":"RTP-VXB340-DQAV34YX"}]}}]}'
    # af_support_tools.set_config_file_property(config_file=payload_file,
    #                                           heading=payload_header,
    #                                           property='ident_no_context',
    #                                           value=my_payload)


# This create payload is seperate as it needs to be called later
def create_describe_message(uuidTest):
    print("Building Describe Element Message...")
    # Create the payload and set it in the specified file.  my_payload is whatever you need to use. Hint: the correllationId field can be used as a description which makes it easier to locate in the Trace log.
    my_payload = '{"timestamp":"2017-01-27T14:51:57Z","correlationId":"5d7f6d34-4271-4593-9bad-1b95589e5189","reply-to":"dell.cpsd.eids.identity.request.hal.gouldc-mint","elementUuids":["' + uuidTest + '"]}'
    af_support_tools.set_config_file_property(config_file=payload_file,
                                              heading=payload_header,
                                              property='describeelement',
                                              value=my_payload)


def waitForMsg(queue, ipaddress):
    print("Waiting for message on queue:" + queue)
    # This function keeps looping until a message is in the specified queue. We do need it to timeout and throw an error
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
            cleanup(ipaddress)
            break
