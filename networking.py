#!/usr/bin/env python

import sys
import xapi, tui

def sysconfig_file(device):
	return "/etc/sysconfig/network-scripts/ifcfg-%s" % device

def load_sysconfig(device):
	f = open(sysconfig_file(device), "r")
	try:
		results = {}
		for line in f.readlines():
			bits = line.split("=")
			key = bits[0].strip().strip("'").strip("\"")
			val = bits[1].strip().strip("'").strip("\"")
			results[key] = val
		return results
	finally:
		f.close()

def save_sysconfig(x):
	lines = []
	for k in x.keys():
		lines.append("%s=\"%s\"" % (k, x[k]))
	return lines

def analyse():
	x = xapi.open()	
	x.login_with_password("root", "")
	try:
		hosts = x.xenapi.host.get_all()
		if len(hosts) <> 1:
			print >>sys.stderr, "WARNING: cannot configuring networking if already pooled"
			return
		pifs = x.xenapi.PIF.get_all_records()
		for pif in pifs:
			if pifs[pif]["management"]:
				print >>sys.stderr, "OK: found a configured management interface"
				return
		if not(tui.yesno("Would you like me to set up host networking for XenServer?")):
			print >>sys.stderr, "WARNING: host networking is not set up"
			return
		print "PIF scan %s" % hosts[0]
		x.xenapi.PIF.scan(hosts[0])
		print "PIF.get_all_records"
		pifs = x.xenapi.PIF.get_all_records()
		device_to_pif = {}
		devices = []
		for pif in pifs:
			pif_r = pifs[pif]
			devices.append(pif_r["device"])
			device_to_pif[pif_r["device"]] = pif
		devices.sort()
		options = []
		for d in devices:
			options.append((d, "<insert description>",))
		mgmt = tui.choose("Please select a management interface", options)
		file_changes = []
		for d in devices:
			sysconfig = load_sysconfig(d)
			new_sysconfig = {}
			for key in sysconfig:
				if key == "NM_CONTROLLED" and sysconfig["NM_CONTROLLED"] == "yes":
					new_sysconfig["NM_CONTROLLED"] = "no"
					print >>sys.stderr, "Setting ifcfg-%s:NM_CONTROLLED to no" % d
				elif key == "ONBOOT" and sysconfig["ONBOOT"] == "yes":
					new_sysconfig["ONBOOT"] = "no"
					print >>sys.stderr, "Setting ifcfg-%s:ON_BOOT to no" % d
				else:
					new_sysconfig[key] = sysconfig[key]
			if sysconfig <> new_sysconfig:
				file_changes.append((sysconfig_file(d), save_sysconfig(new_sysconfig),))

			if "BOOTPROTO" in sysconfig and sysconfig["BOOTPROTO"] == "dhcp":
				print >>sys.stderr, "Setting PIF to DHCP"
				x.xenapi.PIF.reconfigure_ip(device_to_pif[d], "DHCP", "", "", "", "")
			if "BOOTPROTO" in sysconfig and sysconfig["BOOTPROTO"] == "none":
				if "IPADDR" in sysconfig and "NETWORK" in sysconfig and "NETMASK" in sysconfig:
					ipaddr = sysconfig["IPADDR"]
					network = sysconfig["NETWORK"]
					netmask = sysconfig["NETMASK"]
					print >>sys.stderr, "Setting PIF to static"
					x.xenapi.PIF.reconfigure_ip(device_to_pif[d], "Static", ipaddr, netmask, network, "")
			if d == mgmt:
				print >>sys.stderr, "Setting PIF as management"
				x.xenapi.host.management_reconfigure(device_to_pif[d])
		return file_changes
	finally:
		x.logout()

if __name__ == "__main__":
	file_changes = analyse()
	if file_changes:
		for change in file_changes:
			print "I propose changing %s to:" % change[0]
			for line in change[1]:
				print line
