# WebWol
A simple but secure webpage to remotely turn on your computer. It's written in python and uses the flask framework, and the wakeonlan package.
It's a single user app, and it can only manage a single machine right now.

## Installation instructions
1. Clone this repository
2. Install flask and wakeonlan
3. Set up a fix ip configuration for the machine you wan't to manage (use fix ips, or set up a static lease DHCP on your router)
4. Create config.py next to server.py and add the following variables to it:
  * username
  * password
  * secret_key: generate it with os.urandom(24)
  * port: the webpage will use this port instead of standard http, for additional security (choose something above 1024 and below 65536)
  * ip_addr: the ip address of the machine you wan't to manage
  * mac_addr: the mac address of the machine you wan't to manage
5. Run server.py
6. Optionally, set it up to start automatically on your router or other machine. I set it up on my NAS.
