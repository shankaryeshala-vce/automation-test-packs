import json
import sys
import base64
import re
from datetime import datetime
from time import strftime


def parseFile(logfile,corrIds, msgIds, msges):
    # read-in the json tracefile

    try:

        for line in logfile:
            json_data = json.loads(line)
            payloadStr = base64.b64decode(json_data['payload'])
            print(payloadStr)
            strPayload = str(payloadStr,'utf-8')
            payload = json.loads(strPayload)

            message = dict(json_data)
            del json_data['payload']
            json_data['payload'] = payload

            msges.append(json_data)
            corrIds.append(payload['correlationId'])
            if 'message_id' in json_data['properties']:
                msgIds.append(json_data['properties']['message_id']),

    except:
        print('Possible Error with Firehose logfile - check that it exists and is JSON formatted ?')

    return corrIds, msgIds, msges

#-------------------------------------------------------------------------------
def addMsgLatency(messageList, messageIdList):
	# add a latency value to each messge
    for mId in messageIdList:
        for m in messageList:
            if 'message_id' in m['properties']:
                if m['properties']['message_id'] == mId:
                    if m['type'] == 'published':
                        m['latency'] = 0
                    else:
                        m['latency'] = calcMsgLatency(messageList, mId, m['timestamp']).total_seconds()
                        #print('latency as stored in dict', m['latency'])
            else:
                m['latency'] = 0   # account for case where no messageId is available

#-------------------------------------------------------------------------------

def calcMsgLatency(mList, msgId, rxtimestamp):
    # calculate message latency
    txtimestamp = rxtimestamp
    for n in mList:
        if 'message_id' in n['properties']:
            if n['properties']['message_id'] == msgId:
                if n['type'] == 'published':
                    txtimestamp = n['timestamp']
	#print(txtimestamp,'----',rxtimestamp),
        txtime = datetime.strptime(txtimestamp, '%Y-%m-%d %H:%M:%S:%f')
        rxtime = datetime.strptime(rxtimestamp, '%Y-%m-%d %H:%M:%S:%f')
    #print('txtime-rctime : ==============',txtime, rxtime, (rxtime-txtime))

    return (rxtime-txtime)

#-------------------------------------------------------------------------------
def calcCorrLatency(ms,cIds,latencyDict,maxLatency):
	# populate dictionary with correlationIds and latencies
    errorFlag = False
    for c in cIds:
        firstTimestamp = 0
        for m in ms:
            if 'correlationId' in m['payload']:
                if m['payload']['correlationId']== c:
                    if firstTimestamp == 0 :
                        firstTimestamp = datetime.strptime(m['timestamp'], '%Y-%m-%d %H:%M:%S:%f')
                    lastTimestamp = datetime.strptime(m['timestamp'], '%Y-%m-%d %H:%M:%S:%f')

        latencyDict[c] = (lastTimestamp-firstTimestamp).total_seconds()
        if latencyDict[c] > maxLatency:
            errorFlag = True
    return errorFlag

#-------------------------------------------------------------------------------

def uniquefy(lst):
   # uniquefy the contents of a list, order preserving
   checked = []
   for e in lst:
       if e not in checked:
           checked.append(e)
   return checked

#-------------------------------------------------------------------------------

def printMsgs_to_file(corrLst, msgLst,corrWithLatency, printFields, outFile):
        # print message fields  grouped by correlationId
        for corrId in corrLst:
                #print
                outFile.write('\nCorrelationId = %14s    :    Associated latency = %s ------------------------\n' % (corrId,corrWithLatency[corrId]))
                for m in msgLst:
                        if 'correlationId' in m['payload']:
                                if m['payload']['correlationId'] == corrId :
                                    for f in printFields:
                                        if f in m:
                                            outFile.write(str(m[f]))
                                        if f in m['properties']:
                                            outFile.write(str(m['properties'][f]))
                                        if f in m['properties']['headers']:
                                            outFile.write(str(m['properties']['headers'][f]))
                                        if f in  m['payload']:
                                            pass
                                            #print m['payload'][f],
                                        outFile.write('')
                                        if f not in (m,m['properties'],m['properties']['headers'], m['payload']):
                                            outFile.write('\t')
                                    outFile.write('\n')
#---------------------------------------------------------------------------------

def generateTimingsLog(infile,maxLatencyAllowed):
    """
    A function designed to accept a rabbitmq firehose logfile in JSON format
    The logfile is parsed and a latency timing is calculated for each message sequence spanning
    one correlationId.
    Latency calculations for each message pairing (publish/receive) are also calculated
    Each correlationId latency calculated is compared against the maxLatencyAllowed parameter passed-in
    and if any correlationId latency is too large, an error Flag = 'True' is returned to the calling program

    Returned value : Boolean = True if one of the correlationId Latencies calculated was greater then the maxAllowed value passed in
                     Boolean = False if all correlationId latencies are less then the maxAllowed value

    Other output : a lgogile with all timings is written to /tmp/summarisedrabbitMQTrace<timestamp>.log
    """

    # open a unique logfile based on current date/time
    try :
        outfileName = datetime.now().strftime(u"/tmp/summarisedrabbitMQTrace_%Y%m%d-%H%M%S.log")
        outfile = open(outfileName, 'w')
    except :
        print(u'could not open output summarised timings logfile')

    correlationIds = []                  # a list to store all correlationIds
    messageIds = []                      # a list to store all messageIds
    messages = []                        # a list to store mesaage dictionaries
    correlationWithLatency = {}

    # firstly, populate correlationIds and messages lists
    correlationIds, messageIds, messages = parseFile(infile, correlationIds, messageIds, messages)

    # remove duplication from messageId and correlationId lists
    messageIds = uniquefy(messageIds)
    correlationIds = uniquefy(correlationIds)

    # calculate the latency of each message and then each correaltion sequence
    addMsgLatency(messages,messageIds)
    latencyTooLargeFlag = calcCorrLatency(messages,correlationIds,correlationWithLatency,maxLatencyAllowed)

    fields_to_print = ['timestamp', 'latency', 'type', 'message_id', '__TypeId__']

    # print out the results
    printMsgs_to_file(correlationIds,messages,correlationWithLatency,fields_to_print,outfile)

    return latencyTooLargeFlag


