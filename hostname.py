#!/usr/bin/env

import sys, subprocess
import xapi

def hostname():
	x = subprocess.Popen(["/bin/hostname", "-s"], stdout = subprocess.PIPE)
	y = x.communicate()
	return str(y[0]).strip()

def analyse(tui):
	x = xapi.open()
	x.login_with_password("root", "")
	try:
		hosts = x.xenapi.host.get_all()
		if len(hosts) <> 1:
			print >>sys.stderr, "FAILED: to find localhost (is this host already pooled?)"
			return
		current = x.xenapi.host.get_name_label(hosts[0])
		h = hostname ()
		if current <> h and h <> "":
			x.xenapi.host.set_name_label(hosts[0], h)

	finally:
		x.logout()

