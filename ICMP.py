'''
Ping implementation in fulfillment of Major Course Output #2 for NSCOM02 Term 3 - AY 2023-2024

GitHub Repository:
https://github.com/tapeau/NSCOM02.python-ping

Additional Credits / References:
- https://www.tutorialspoint.com/python/python_command_line_arguments.htm
- https://docs.python.org/3/library/ipaddress.html
'''
# Import libraries
from socket import *
from statistics import mean
import os
import sys
import struct
import time
import select
import ipaddress

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

def evaluateICMPError(type, code):
    if type == 3:
        if code == 0: return "ERROR: Network unreachable."
        elif code == 1: return "ERROR: Host unreachable."
        elif code == 2: return "ERROR: Protocol unreachable."
        elif code == 3: return "ERROR: Port unreachable."
        elif code == 4: return "ERROR: Fragmentation needed and DF (Don't Fragment) bit set."
        elif code == 5: return "ERROR: Source route failed."
        elif code == 6: return "ERROR: Destination network unknown."
        elif code == 7: return "ERROR: Destination host unknown."
        elif code == 8: return "ERROR: Source host isolated."
        elif code == 9: return "ERROR: Network administratively prohibited."
        elif code == 10: return "ERROR: Host administratively prohibited."
        elif code == 11: return "ERROR: Network unreachable for TOS."
        elif code == 12: return "ERROR: Host unreachable for TOS."
        elif code == 13: return "ERROR: Communication administratively prohibited by filtering."
        elif code == 14: return "ERROR: Host precedence violation."
        elif code == 15: return "ERROR: Precedence cutoff in effect."
    elif type == 4:
        return "ERROR: Source quench."
    elif type == 5:
        return "ERROR: Redirect message - a more efficient route is available."
    elif type == 11:
        return "ERROR: Time exceeded."
    elif type == 12:
        return "ERROR: Parameter problem."
    else:
        return "ERROR: ICMP error."

def receiveOnePing(mySocket, ID, timeout, destAddr):
    timeLeft = timeout
    while 1:
        startedSelect = time.time()
        whatReady = select.select([mySocket], [], [], timeLeft)
        if whatReady[0] == []: # Timeout
            return None
        
        timeReceived = time.time()
        recPacket, addr = mySocket.recvfrom(1024)
        #Fill in start
        
        #Fetch the ICMP header from the IP packet
        header = recPacket[20:28]
        type, code, checksum, packetID, sequence = struct.unpack("!bbHHh", header)
        
        # Check type and code
        if type == 0 and code == 0 and packetID == ID:
            byteDouble = struct.calcsize("d")
            ttl = struct.unpack("!b", recPacket[8:9])[0]
            delay = timeReceived - startedSelect
            return (delay, ttl, byteDouble)
        else:
            print(evaluateICMPError(type, code))
            return (-1.0, -1, -1)
        
        #Fill in end

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

def ping(host, amount, timeout=1):
    # timeout=1 means: If one second goes by without a reply from the server,
    # the client assumes that either the client's ping or the server's pong is lost
    
    # Initialize additional variables
    dest = 0
    loss = 0
    listTime = [0] * amount
    minTime = sys.maxsize
    maxTime = 0
    
    # Check if passed host is an IP address or a name
    try:
        dest = ipaddress.ip_address(host)
        dest = host
        print("\nPinging " + dest + " with " + str(8*amount) + " bytes of data using Python:")
    except ValueError:
        try:
            dest = gethostbyname(host)
            print("\nPinging " + host + " [" + dest + "] with " + str(8*amount) + " bytes of data using Python:")
        except gaierror:
            print("ERROR: Cannot resolve hostname \'" + host + "\'.")
            return
    
    # Send ping requests to a server separated by approximately one second
    for i in range(amount):
        result = doOnePing(dest, i, timeout)
        if not result:
            print("Request timed out.")
            loss += 1
        elif result == (-1.0, -1, -1):
            pass
        else:
            delay = int(result[0]*1000)
            listTime[i] = delay
            if delay < minTime: minTime = delay
            if delay > maxTime: maxTime = delay
            ttl = result[1]
            bytes = result[2]
            # Print results similar to that of Windows ping
            print("Reply from " + dest + ": bytes=" + str(bytes) + " time=" + str(delay) + "ms TTL=" + str(abs(ttl)))
        time.sleep(1) # one second
    
    # Print ping statistics
    if minTime == sys.maxsize: minTime = 0
    print("")
    print("Ping statistics for " + dest + ":")
    print("\tPackets: Sent = " + str(amount) + ", Received = " + str(amount-loss) + ", Lost = " + str(loss) + " (" + str(int((loss/amount)*100)) + "% loss),")
    print("Approximate round trip times in milli-seconds:")
    print("\tMinimum = " + str(minTime) + "ms, Maximum = " + str(maxTime) + "ms, Average = " + str(int(round(mean(listTime)))) + "ms")

if __name__ == "__main__":
    try:
        # Check for passed arguments
        if len(sys.argv) < 3:
            print("ERROR: Incomplete arguments passed.\n\t(Usage: python ICMP.py <server> <amount>)")
        elif len(sys.argv) > 3:
            print("ERROR: Too many arguments passed.\n\t(Usage: python ICMP.py <server> <amount>)")
        else:
            # Check if 2nd argument is a digit
            if sys.argv[2].isdigit() == False:
                print("ERROR: 2nd argument must be a positive integer.")
            else:
                # Call the ping function
                ping(sys.argv[1], int(sys.argv[2]))
    except KeyboardInterrupt:
        print("Exiting program...")
        sys.exit(1)
