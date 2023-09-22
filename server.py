# JOEL BREMNER
# 73313842

import sys
import socket

# Storage for all messages
class storage:
    def __init__(self):
        self.db = {}

    def add(self, sender_name, recv_name, sent_message):
        if recv_name in self.db.keys():
            existing = self.db.get(recv_name)
            existing.append((sender_name, sent_message))
            self.db[recv_name] = existing
        else:
            self.db[recv_name] = [(sender_name, sent_message)]

    def read(self, sender_name):
        messages = self.db.get(sender_name)
        if messages == None:
            return [0, ("SYSTEM", "NO MESSAGES STORED FOR THIS USER")]
        elif len(messages) == 0:
            return [0, ("SYSTEM", "NO REMAINING MESSAGES")]
        elif len(messages) > 255:
            returned_msg = [1]
            for i in range(255):
                returned_msg.append(messages[i])
            self.db[sender_name] = messages[i+1:]

        else:
            returned_msg = [0]
            for i in range(len(messages)):
                returned_msg.append(messages[i])
            
            self.db[sender_name] = []
        

        return returned_msg
    
DB = storage()

# Prepare msg response packets
def msg_response(num_items, more_msg, messages, conn, sender_name):
    fixed_header = bytearray([0xAE, 0x73, 3, num_items, more_msg])
    conn.send(fixed_header)

    for msg in messages:
        packet = bytearray([len(msg[0]), len(msg[1]) >> 8 & 0xff, len(msg[1]) & 0xff])
        packet.extend(msg[0].encode("UTF-8"))
        packet.extend(msg[1].encode("UTF-8"))
        conn.send(packet)

    print(f"{num_items} Messages sent from storage to {sender_name}")

# Handle create Request
def proc_create(header, message):
    sender_name = message[0:header[3]]
    recv_name = message[header[3]:(header[3] + header[4])]
    sent_message = message[(header[3] + header[4]):]

    DB.add(sender_name, recv_name, sent_message)
    print(f"Message Sent and stored from {sender_name} to {recv_name}")

# Handle read Request
def proc_read(header, message, conn):
    sender_name = message[0:header[3]]
    db_messages = DB.read(sender_name)
    msg_response(len(db_messages)-1, db_messages[0], db_messages[1:], conn, sender_name)

def main():
    try:
        sock = None
        conn = None
        if len(sys.argv) != 2:
            raise ValueError
            
        port = int(sys.argv[1]) # "Port number"

        if port < 1024 or port > 64000:
            print("Invalid port number, please select a port such that: 1,023 < port < 64,001")
            sys.exit(1)

        address = ("0.0.0.0", port)
        sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0, fileno=None)

        sock.bind(address)
        print(f"Server listening on port {port}")

        sock.listen()

        # Looping Accept and packet handling
        while True:
            conn, cleint_address = sock.accept()
            print(f"Accepted connection from {cleint_address}")

            packet = conn.recv(65542)
            
            # Check Magic Number
            if packet[0] != 0xAE and packet[1] != 0x37:
                print("Incorrect Magic Number")
                sys.exit()
            
            if packet[3] < 1:
                print("NameLen field must be at least length 1")
                sys.exit()
            

            header = packet[0:7]
            message = packet[7:].decode("UTF-8")

            if packet[2] == 1:
                if packet[4] != 0:
                    print("If reading ReceiverLen must be 0")
                    sys.exit()
                proc_read(header, message, conn)
                if packet[5] != 0 or packet[6] != 0:
                    print("MessageLength must be 0")
                    sys.exit()
            elif packet[2] == 2:
                if packet[4] < 1:
                    print("When creating ReceiverLen must be greater than 0")
                    sys.exit()
                if packet[5] == 0 and packet[6] == 0:
                    print("Must have message length of atleast 1")
                    sys.exit()
                proc_create(header, message)
            else:
                print("Incorect Id Field")
                sys.exit()
            
            conn.close()
    
    except ValueError:
        print("Please select a valid port number")
    except OSError as err: # raised by all socket methods
        print(f"ERROR: {err}") # print the error string

    finally: 
        if sock != None:
            sock.close()
        if conn != None:
            conn.close()

main()