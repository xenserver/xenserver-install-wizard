#!/usr/bin/env python

import sys, subprocess, os, os.path
import xapi, tui, network

interfaces = "/etc/network/interfaces"

def load_interfaces():
	f = open(interfaces, "r")
	try:
		return f.readlines()
	finally:
		f.close()

def analyse():
	mgmt, devices = network.choose_mgmt()
	x = xapi.open()	
	x.login_with_password("root", "")
	try:
		file_changes = []

		old_interfaces = load_interfaces()
		new_interfaces = []
		# temporary state
		device_name = None
		device_address = None
		device_netmask = None
		device_gateway = None
		for line in old_interfaces:
			if line.startswith("auto "):
				intf = line[len("auto "):]
				if intf in devices:
					print >>sys.stderr, "Disabling automatic bringup of %s" % intf
					new_interfaces.append("# " + line)
				else:
					new_interfaces.append(line)
			elif line.startswith("iface "):
				bits = line.split()
				device_name = None
				device_address = None
				device_netmask = None
				device_gateway = None
				if len(bits) > 3 and bits[1] in devices and bits[2] == "inet":
					if bits[3] == "dhcp":
						print >>sys.stderr, "Configuring %s with dhcp" % bits[1]
						x.xenapi.PIF.reconfigure_ip(device_to_pif[d], "DHCP", "", "", "", "")
					elif bits[3] == "static":
						device_name = bits[1]
			elif device_name != None and line.strip().startswith("address "):
				device_address = line.strip()[len("address "):]
				new_interfaces.append(line)
			elif device_name != None and line.strip().startswith("netmask "):
				device_netmask = line.strip()[len("netmask "):]
				new_interfaces.append(line)
			elif device_name != None and line.strip().startswith("gateway "):
				device_gateway = line.strip()[len("gateway "):]
				new_interfaces.append(line)
			elif device_name != None and (line == "" or line[0] == " " or line[0] == "\t"):
				print >>sys.stderr, "Configuring %s with address %s netmask %s gateway %s" % (device_name, device_address, device_netmask, device_gateway)
				x.xenapi.PIF.reconfigure_ip(device_to_pif[d], "Static", device_address, device_netmask, "", "")
				new_interfaces.append(line)
			else:
				new_interfaces.append(line)
		
		print >>sys.stderr, "Setting PIF as management"
		x.xenapi.host.management_reconfigure(device_to_pif[mgmt])
		if new_interfaces <> old_interfaces:
			file_changes.append(((interfaces, new_interfaces),))
		return file_changes
	finally:
		x.logout()

def restart():
	if subprocess.call(["/etc/init.d/networking", "restart"]) <> 0:
		 print >>sys.stderr, "FAILED: to restart networking"

if __name__ == "__main__":
	file_changes = analyse()
	if file_changes:
		for change in file_changes:
			print "I propose changing %s to:" % change[0]
			for line in change[1]:
				print line
