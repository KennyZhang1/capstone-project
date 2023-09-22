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

# Main loop. Open socket to server and send a blink command
while True:
    ai = socket.getaddrinfo(server_ip, 80) 
    addr = ai[0][-1]

    s = socket.socket()
    s.connect(addr)
    s.send(b"BLINK")
    
    # Recieve response from server
    response = s.recv(1024)
    res_dec = response.decode("UTF-8")
    print(res_dec)
   
    s.close()          
    time.sleep(0.5)    