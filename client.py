# JOEL BREMNER
# 73313842

import sys
import socket

def create_req(name, sock):

    while True:
        recv_name = input("Reciever Name: ")
        if len(recv_name) >= 1 and len(recv_name) <= 255:
            break
        print("Please select a name of character length at least 1 and byte length at most 255")
    
    while True:
        message = input("Message: ")
        if len(message) >= 1 and len(message) <= 65535:
            break
        print("Please select a message of character length at least one and byte length at most 65535")
    
    packet = bytearray([0xAE, 0x73, 2, len(name), len(recv_name), len(message) >> 8 & 0xff, len(message) & 0xff])


    packet_string = name + recv_name + message
    packet.extend(packet_string.encode("UTF-8"))

    amount = sock.send(packet)
    if amount < len(packet):
        print("failed")

def read_req(name, sock):
    packet = bytearray([0xAE, 0x73, 1, len(name), 0, 0, 0])
    packet.extend(name.encode("UTF-8"))
    amount = sock.send(packet)
    if amount < len(packet):
        print("failed")
    
    read_response(sock)

def read_response(sock):
    fixed_header = sock.recv(5)
    # print(fixed_header)
    # Check magic number
    if fixed_header[0] != 0xAE and fixed_header[1] != 0x37:
        print("Incorrect Magic Number")
        sys.exit()
    # check id field = 3
    if fixed_header[2] != 3:
        print("Incorrect ID")
        sys.exit()
    # check for more msgs
    if not (fixed_header[4] == 0 or fixed_header[4] == 1):
        print("Incorrect More Msgs Field")
        sys.exit()
    
    for i in range(fixed_header[3]):
        header = sock.recv(3)
        # Check Header
        if header[0] < 1:
            print("SenderLen has to be at least 1")
            sys.exit()
        if header[1] < 1 and header[2] < 1:
            print("MessageLen has to be at least 1")
            sys.exit()

        msg = sock.recv((header[1] << 8 | header[2]) + header[0])
        msg = msg.decode("UTF-8")
        print(f"Sender: {msg[:header[0]]}, Message: {msg[header[0]:]}")

    if fixed_header[4] == 1:
        print("THERE ARE STILL MORE MESSAGES TO VIEW, TO VIEW REQUEST A READ AGAIN")

    

def main():

    if len(sys.argv) < 5 or len(sys.argv) > 5:
        print("Please run such that: Python3 client.py <address> <port> <name> <create/read>")
        sys.exit()
    
    filename = sys.argv[0] 
    address = sys.argv[1] 
    port = int(sys.argv[2]) 
    name = sys.argv[3] 
    create_read = sys.argv[4] 
    
    if len(name) < 1 or len(name) > 255:
        print("Please input a name at least one char long and at most 255 char long")
        sys.exit()
    
    if not (create_read == "read" or create_read == "create"):
        print("Please select a valid create/read")
        sys.exit()
    
    if port < 1024 or port > 64000:
            print("Invalid port number, please select a port such that: 1,023 < port < 64,001")
            sys.exit(1)

    try:
        services = socket.getaddrinfo(address, port, socket.AF_INET, socket.SOCK_STREAM, proto=0, flags=0)
        family, type, proto, canonname, address = services[0]

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(address)
        sock.settimeout(1)
        print("Connected")

        if create_read == "create":
            create_req(name, sock)
        
        if create_read == "read":
            read_req(name, sock)
    
    except ValueError: # raised by the int() conversion
        print(f"ERROR: Port ’{port}’ is not an integer")
    except UnicodeDecodeError: # raised by .decode()
        print("ERROR: Reponse decoding failure")
    except socket.gaierror: # raised by address errors such as in getaddrinfo()
        print(f"ERROR: Host ’{address}’ does not exist")
    except OSError as err: # raised by all socket methods
        print(f"ERROR: {err}") # print the error string

    
    finally: # reguardless of an exception or not, close the socket
        if sock != None:
            sock.close()    


    
main()