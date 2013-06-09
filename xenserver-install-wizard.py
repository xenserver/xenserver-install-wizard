#!/usr/bin/env python

import sys, subprocess
import tui, grub, networking, iptables, storage

def replace_file(name, lines):
	print "Create a backup of %s" % name
	print "Replace %s with:" % name
	for line in lines:
		print line


def reboot():
	print >>sys.stderr, "Triggering an immediate reboot"

if __name__ == "__main__":
	need_to_reboot = False
	r = grub.analyse()
	if r:
		need_to_reboot = True
		replace_file(r[0], r[1])
	r = networking.analyse()
	if r:
		for change in r:
			replace_file(change[0], change[1])
	r = iptables.analyse()
	if r:
		replace_file(r[0], r[1])
		iptables.restart()
	storage.analyse()
	print "Welcome to XenServer!"
	if need_to_reboot:
		if tui.yesno("A reboot is needed to fully activate XenServer. Would you like to reboot now?"):
			reboot()
	
