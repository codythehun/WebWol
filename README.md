# WebWol
A simple but secure webpage to remotely turn on your computers on your LAN, through running and exposing this service on one of your machines that are always up (such as a router or NAS). It's written in python and uses the flask framework.

## Features
   * Single user app for now
   * Discover all running hosts on your LAN automatically (using the scapy library)
   * Remember the discovered hosts
   * Manually add new hosts
   * Forget hosts
   * Send WOL magic packet to any of your hosts

## Installation instructions
1. Clone this repository
2. Install flask, wakeonlan and scapy
3. Create config.py next to server.py and add the following variables to it:
  * username
  * password
  * secret_key: generate it with os.urandom(24)
  * port: the webpage will use this port instead of standard http, for additional security (choose something above 1024 and below 65536)
  * db_file: file path to store database
5. Run server.py
6. The page is accessible from http://host_ip:port/wakey
7. Optionally, set it up to start automatically on your router or other machine. I set it up on my NAS.
