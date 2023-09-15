# Basic TCP client for Pico W
import network
import time
import socket

# WIFI credentials and server IP
ssid = ""
password = ""
server_ip = ""

# use wlan to connect
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)
while not wlan.isconnected() and wlan.status() >= 0:
    print("Waiting to connect:")
    time.sleep(1)
 
# Should be connected and have an IP address
wlan.status() # 3 == success
wlan.ifconfig()
print(wlan.ifconfig())

# Main loop. Open socket to server and send Hello world
while True:
    ai = socket.getaddrinfo(server_ip, 80) 
    addr = ai[0][-1]

    s = socket.socket()
    s.connect(addr)
    s.send(b"Hello from client!")
   
    s.close()          
    time.sleep(0.1)    