import private_settings
import urllib
import xml.dom.minidom
from easyzone import easyzone
import dns.rdtypes.ANY.CNAME
import dns.rdtypes.ANY.NS
import sys
import dns.rdtypes.ANY.MX
import dns.rdtypes.IN.A
import dns.rdtypes.ANY.TXT
import dns.exception
import dns.rdata
import dns.rdataclass
import dns.rdatatype
import dns.rrset
import dns.zone
import dns.name

CONFIG_FILEPATH = "settings.txt"
NAMECHEAP_URI = "https://api.namecheap.com/xml.response"


#?ApiUser=apiexample&ApiKey=56b4c87ef4fd49cb96d915c0db68194&UserName=apiexample&Command=namecheap.domains.getList&ClientIp=192.168.1.109

#make request



url = """
%s?ApiUser=%s&ApiKey=%s&UserName=%s&Command=namecheap.domains.dns.getHosts&ClientIp=%s&SLD=%s&TLD=%s
""" % ( NAMECHEAP_URI, private_settings.API_USER, private_settings.API_KEY, private_settings.USERNAME,private_settings.CLIENT_IP,private_settings.SLD, private_settings.TLD )
filehandle = urllib.urlopen( url )
contents = filehandle.read()

#iterate over hosts and put them into the zone file
domain = private_settings.SLD + "." + private_settings.TLD + "."
zone = easyzone.Zone(domain)
dns_name = dns.name.from_text(domain)
zone._zone = dns.zone.Zone(dns_name)
print str(zone._zone.origin)
hosts_doc = xml.dom.minidom.parseString( contents ) 
hosts = hosts_doc.getElementsByTagName("host")

#create SOA
exrds = dns.rdataset.from_text('IN', 'SOA', 300, 'ns1.register-server.com hostmaster.registrar-servers.com 2012031900 10001 10001 10001 3601')

zone._zone.replace_rdataset("@", exrds)

for host in hosts:
    #get all the properties out of the XML
    address = host.getAttribute("Address")
    TTL = host.getAttribute("TTL")
    mx_pref = host.getAttribute("MXPref")
    record_type = host.getAttribute("Type")
    name = host.getAttribute("Name")


    if record_type == "FRAME" or record_type == "URL":
        print "not adding: " + str(host.toxml())
        continue
    
    #start writing the zone 
    zone.add_name( name )
    name_zone = zone.names[name]

    name_records = name_zone.records(record_type, create=True)
    if record_type == "MX":
        name_records.add( (int(mx_pref), str(address)) ) 
    else:
        name_records.add( str(address ))



zone.filename = sys.argv[1]
zone.save(autoserial=True)
