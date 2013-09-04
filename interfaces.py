#!/usr/bin/env python

import sys, subprocess, os, os.path
import xapi, network

interfaces = "/etc/network/interfaces"

def load_interfaces(filename):
	f = open(filename, "r")
	try:
		return f.readlines()
	finally:
		f.close()

def analyse(tui, config, filename = interfaces):
	# 'config' is the system configuration from xapi + the user's choice of
	# a management PIF. 'filename' is the path of the interfaces file.
	devices = config["devices"]
	old_interfaces = load_interfaces(filename)
	
	file_changes = []
	interfaces_to_reconfigure = {}

	new_interfaces = []
	need_to_replace_interfaces = False
	# temporary state
	device_name = None
	device_address = None
	device_netmask = None
	device_gateway = None
	for line in old_interfaces:
		line = line[0:len(line)-1]
		if line.startswith("auto "):
			intf = line[len("auto "):]
			if intf in devices:
				print >>sys.stderr, "Disabling automatic bringup of %s" % intf
				new_interfaces.append("# " + line)
				new_interfaces.append("# ^^^^^^^^ xenserver-install-wizard copied this interface configuration to xapi")
				new_interfaces.append("")
				need_to_replace_interfaces = True
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
					interfaces_to_reconfigure[bits[1]] = ("DHCP", "", "", "", "")
				elif bits[3] == "static":
					device_name = bits[1]
					# the configuration is on the following lines
			new_interfaces.append(line)
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
			interfaces_to_reconfigure[device_name] = ("Static", device_name, device_address, device_netmask, device_gateway)
			new_interfaces.append(line)
		else:
			new_interfaces.append(line)
		
	if need_to_replace_interfaces:
		file_changes.append((filename, new_interfaces),)
		return (file_changes, interfaces_to_reconfigure)

def restart():
	if subprocess.call(["/etc/init.d/networking", "restart"]) <> 0:
		 print >>sys.stderr, "FAILED: to restart networking"

if __name__ == "__main__":
	from tui import Tui
	old_interfaces = "networking/etc-network-interfaces"
	config = {
		"devices": [ "em1", "em2" ],
		"management": "em1",
	}
	result = analyse(Tui(False), config, old_interfaces)
	if not result:
		print "ERROR: I'm proposing to make no changes"
		exit(1)
	file_changes, new_interfaces = result
	for device in new_interfaces:
		print "I will reconfigure %s to %s" % (device, repr(new_interfaces[device]))
	print "I will configure %s as the management PIF" % (config["management"])
	if file_changes:
		for change in file_changes:
			print "I propose changing %s to:" % change[0]
			for line in change[1]:
				print line
