#!/usr/bin/env python

import sys, subprocess, os, os.path
import xapi, tui

def choose_mgmt():
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
		return (mgmt, devices)
	finally:
		x.logout()

