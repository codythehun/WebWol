from scapy.all import *
import socket

def scan_subnet(subnet_address='192.168.1.*'):
    #TODO: send arp requests on lan interface only, as WOL doesn't work on wifi
    answered_packets, unanswered_packets = arping(subnet_address)
    for sent,received in answered_packets:
        mac = received.hwsrc
        ip = received.psrc
        hostname = None
        try:
            hostname, aliases, ips = socket.gethostbyaddr(ip)
        except socket.herror:
            hostname = None
        yield (hostname, mac, ip)
            
            
