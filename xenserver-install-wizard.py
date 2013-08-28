#!/usr/bin/env python

import sys, subprocess
import xapi, replace, tui, grub, network, iptables, storage, templates, logging, hostname, openstack, toolstack
import platform

def reboot():
	print >>sys.stderr, "Triggering an immediate reboot"
	cmd = [ "/sbin/reboot" ]
	x = subprocess.call(cmd)
	if x <> 0:
		print >>sys.stderr, "FAILED: to trigger a reboot (%s)" % (" ".join(cmd))

def stop_xend():
	need_to_reboot = False

	print >>sys.stderr, "Permanently stopping xend"
	distro = platform.dist()[0].lower()
	if distro in ["fedora", "redhat", "centos"]:
		if subprocess.call(["chkconfig", "--level", "345", "xend", "off"]) <> 0:
			print >>sys.stderr, "FAILED: to disable xend"
	elif distro in ["ubuntu", "debian"]:
		r = toolstack.analyse()
		if r:
			need_to_reboot = True
			for change in r:
				replace.file(change[0], change[1])
	else: 
		print >>sys.stderr, "FAILED: don't know how to disable xend"
	if subprocess.call(["service", "xend", "stop"]) <> 0:
		print >>sys.stderr, "FAILED: to stop xend"
	return need_to_reboot

if __name__ == "__main__":
	r = logging.analyse()
	if r:
		replace.file(r[0], r[1])
		logging.restart()
	need_to_reboot = stop_xend ()
	xapi.start ()
	need_to_reboot = False
	r = grub.analyse()
	if r:
		need_to_reboot = True
		replace.file(r[0], r[1])
	r = network.analyse()
	if r:
		need_to_reboot = True
		for change in r:
			replace.file(change[0], change[1])
	r = iptables.analyse()
	if r:
		replace.file(r[0], r[1])
	storage.analyse()
	openstack.analyse()
	hostname.analyse()
	templates.create()
	print "Welcome to XenServer!"
	if need_to_reboot:
		if tui.yesno("A reboot is needed before XenServer is fully ready. Would you like to reboot now?"):
			reboot()
