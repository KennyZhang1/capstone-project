import socket
import time

# Test client for TCP connection to pico server

# IP address of Pico TCP server
server_ip = "192.168.121.23"

# open socket conenction to PICO W and repeatedly send a message
while True:
    ai = socket.getaddrinfo(server_ip, 80)
    addr = ai[0][-1]
    
    s = socket.socket()
    s.connect(addr)
    
    s.send(b"HELLO WORLD") 
    
    s.close()
    time.sleep(0.1)