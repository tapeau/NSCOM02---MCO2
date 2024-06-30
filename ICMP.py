from socket import *
from statistics import mean
import os
import sys
import struct
import time
import select

ICMP_ECHO_REQUEST = 8

def checksum(string):
    csum = 0
    countTo = (len(string) // 2) * 2
    count = 0

    while count < countTo:
        thisVal = ord(chr(string[count+1])) * 256 + ord(chr(string[count]))
        csum = csum + thisVal
        csum = csum & 0xffffffff
        count = count + 2
    if countTo < len(string):
        csum = csum + ord(string[len(string) - 1])
        csum = csum & 0xffffffff
    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer

def receiveOnePing(mySocket, ID, timeout, destAddr):
    timeLeft = timeout
    while 1:
        startedSelect = time.time()
        whatReady = select.select([mySocket], [], [], timeLeft)
        howLongInSelect = (time.time() - startedSelect)
        if whatReady[0] == []: # Timeout
            return None
        
        timeReceived = time.time()
        recPacket, addr = mySocket.recvfrom(1024)
        #Fill in start
        
        #Fetch the ICMP header from the IP packet
        header = recPacket[20:28]
        type, code, checksum, packetID, sequence = struct.unpack("!bbHHh", header)
        if type == 0 and packetID == ID: # type should be 0
            byte_in_double = struct.calcsize("d")
            timeSent = struct.unpack("d", recPacket[28:28+byte_in_double])[0]
            delay = timeReceived - startedSelect
            ttl = struct.unpack("!b", recPacket[8:9])[0]
            return (delay, ttl, byte_in_double)
        
        #Fill in end
        
        timeLeft = timeLeft - howLongInSelect
        if timeLeft <= 0:
            return "Request timed out."

def sendOnePing(mySocket, ID, sequence, destAddr):
    # Header is type (8), code (8), checksum (16), id (16), sequence (16)
    myChecksum = 0
    # Make a dummy header with a 0 checksum
    
    # struct -- Interpret strings as packed binary data
    header = struct.pack("!bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, sequence)
    data = struct.pack("!d", time.time())
    # Calculate the checksum on the data and the dummy header.
    myChecksum = checksum(header + data)
    
    # Get the right checksum, and put in the header
    if sys.platform == 'darwin':
        # Convert 16-bit integers from host to network byte order
        myChecksum = htons(myChecksum) & 0xffff
    else:
        qmyChecksum = htons(myChecksum)
    
    header = struct.pack("!bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, sequence)
    packet = header + data
    mySocket.sendto(packet, (destAddr, 1)) # AF_INET address must be tuple, not str
    # Both LISTS and TUPLES consist of a number of objects
    # which can be referenced by their position number within the object.

def doOnePing(destAddr, sequence, timeout):
    icmp = getprotobyname("icmp")
    # SOCK_RAW is a powerful socket type. For more details: http://sockraw.org/papers/sock_raw
    
    #Fill in start
    #create socket
    mySocket = socket(AF_INET, SOCK_RAW, icmp)
    #Fill in end
    
    myID = os.getpid() & 0xFFFF # Return the current process i
    
    #Fill in start
    #send a single ping using the socket, dst addr and ID
    sendOnePing(mySocket, myID, sequence, destAddr)
    #add delay using timeout
    delay = receiveOnePing(mySocket, myID, timeout, destAddr)
    #close socket
    mySocket.close()
    
    #Fill in end
    
    return delay

def ping(host, timeout=1):
    # timeout=1 means: If one second goes by without a reply from the server,
    # the client assumes that either the client's ping or the server's pong is lost
    
    dest = gethostbyname(host)
    print("")
    print("Pinging " + dest + " with 32 bytes of data using Python:")
    
    # Initialize additional variables
    loss = 0
    recTime = [0, 0, 0, 0]
    minTime = sys.maxsize
    maxTime = 0
    
    # Send ping requests to a server separated by approximately one second
    for i in range(4):
        result = doOnePing(dest, i, timeout)
        if not result:
            print("Request timed out.")
            loss += 1
        else:
            delay = int(result[0]*1000)
            recTime[i] = delay
            if delay < minTime: minTime = delay
            if delay > maxTime: maxTime = delay
            ttl = result[1]
            bytes = result[2]
            # Print results similar to that of Windows ping
            print("Reply from " + dest + ": bytes=" + str(bytes) + " time=" + str(delay) + "ms TTL=" + str(abs(ttl)))
        time.sleep(1)# one second
    
    # Print ping statistics
    print("")
    print("Ping statistics for " + dest + ":")
    print("\tPackets: Sent = " + str(4) + ", Received = " + str(4-loss) + ", Lost = " + str(loss) + " (" + str(int((loss/4)*100)) + "% loss),")
    print("Approximate round trip times in milli-seconds:")
    print("\tMinimum = " + str(minTime) + "ms, Maximum = " + str(maxTime) + "ms, Average = " + str(int(round(mean(recTime)))) + "ms")

ping("example.com")
