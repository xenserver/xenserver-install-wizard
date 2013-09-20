#!/usr/bin/env python

import sys, subprocess, os, os.path
import xapi, network

def sysconfig_file(device):
	return "/etc/sysconfig/network-scripts/ifcfg-%s" % device

def load_sysconfig(device):
	if not(os.path.exists(sysconfig_file(device))):
		return None
	f = open(sysconfig_file(device), "r")
	try:
		results = {}
		for line in f.readlines():
			bits = line.split("=")
			if len(bits) < 2:
				continue
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

def analyse(tui, config):
	devices = config["devices"]

	x = xapi.open()	
	x.login_with_password("root", "")
	try:
		file_changes = []
		interfaces_to_reconfigure = {}
		for d in devices:
			sysconfig = load_sysconfig(d)
			if not sysconfig:
				print >>sys.stderr, "There is no ifcfg- file for NIC %s: skipping" % d
				continue
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
				interfaces_to_reconfigure[d] = ("DHCP", "", "", "", "")
			if "BOOTPROTO" in sysconfig and sysconfig["BOOTPROTO"] == "none":
				if "IPADDR" in sysconfig and "NETWORK" in sysconfig and "NETMASK" in sysconfig:
					ipaddr = sysconfig["IPADDR"]
					network = sysconfig["NETWORK"]
					netmask = sysconfig["NETMASK"]
					interfaces_to_reconfigure[d] = ("Static", ipaddr, netmask, network, "")
		return (file_changes, interfaces_to_reconfigure)
	finally:
		x.logout()

def restart():
	if subprocess.call(["service", "network", "restart"]) <> 0:
		 print >>sys.stderr, "FAILED: to restart networking"

if __name__ == "__main__":
	from tui import Tui
	config = {
		"devices": [ "em1", "em2" ],
		"management": "em1",
	}
	file_changes = analyse(Tui(False), config)
	if file_changes:
		for change in file_changes:
			print "I propose changing %s to:" % change[0]
			for line in change[1]:
				print line
