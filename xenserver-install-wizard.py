#!/usr/bin/env python

import sys, subprocess
import replace, tui, grub, networking, iptables, storage

def reboot():
	print >>sys.stderr, "Triggering an immediate reboot"
	cmd = [ "/sbin/reboot" ]
	x = subprocess.call(cmd)
	if x <> 0:
		print >>sys.stderr, "FAILED: to trigger a reboot (%s)" % (" ".join(cmd))

if __name__ == "__main__":
	need_to_reboot = False
	r = grub.analyse()
	if r:
		need_to_reboot = True
		replace.file(r[0], r[1])
	r = networking.analyse()
	if r:
		need_to_reboot = True
		for change in r:
			replace.file(change[0], change[1])
	r = iptables.analyse()
	if r:
		replace.file(r[0], r[1])
		iptables.restart()
	storage.analyse()
	print "Welcome to XenServer!"
	if need_to_reboot:
		if tui.yesno("A reboot is needed to fully activate XenServer. Would you like to reboot now?"):
			reboot()
	
