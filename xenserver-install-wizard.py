#!/usr/bin/env python

import sys, subprocess, argparse
import xapi, replace, grub, grub2, network, iptables, storage, templates, logging, hostname, openstack, toolstack
import platform
import os
from tui import Tui

def reboot():
	print >>sys.stderr, "Triggering an immediate reboot"
	cmd = [ "/sbin/reboot" ]
	x = subprocess.call(cmd)
	if x <> 0:
		print >>sys.stderr, "FAILED: to trigger a reboot (%s)" % (" ".join(cmd))

def stop_xend(tui):
	need_to_reboot = False

	print >>sys.stderr, "Permanently stopping xend"
	distro = platform.dist()[0].lower()
	if distro in ["fedora", "redhat", "centos"]:
		if subprocess.call(["chkconfig", "--level", "345", "xend", "off"]) <> 0:
			print >>sys.stderr, "FAILED: to disable xend"
	elif distro in ["ubuntu", "debian"]:
		r = toolstack.analyse(tui)
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
	parser = argparse.ArgumentParser()
	parser.add_argument('--yes-to-all', action='store_true')
	parser.add_argument('--reboot', dest="auto_reboot", action='store_true')
	args = parser.parse_args()

	tui = Tui(args.yes_to_all)

	r = logging.analyse(tui)
	if r:
		replace.file(r[0], r[1])
		logging.restart()
	need_to_reboot = stop_xend (tui)
	xapi.start ()
	need_to_reboot = False
        if os.path.isfile("/etc/default/grub"):
                r = grub2.analyse(tui)
        else:
		r = grub.analyse(tui)
	if r:
		need_to_reboot = True
		replace.file(r[0], r[1])
		if os.path.isfile("/etc/default/grub"):
			subprocess.call(["update-grub"])
	r = network.analyse(tui)
	if r:
		need_to_reboot = True
		for change in r:
			replace.file(change[0], change[1])
	r = iptables.analyse(tui)
	if r:
		replace.file(r[0], r[1])
	storage.analyse(tui)
	openstack.analyse(tui)
	hostname.analyse(tui)
	templates.create()
	print "Welcome to XenServer!"
	if need_to_reboot:
		if args.auto_reboot:
			reboot()
		if tui.yesno("A reboot is needed before XenServer is fully ready. Would you like to reboot now?", False):
			reboot()
