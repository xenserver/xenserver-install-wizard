#!/usr/bin/env python

import sys, subprocess
import xapi, tui

def mkdir(path):
	x = subprocess.call(["/bin/mkdir", "-p", path])
	if x <> 0:
		print >>sys.stderr, "ERROR: failed to mkdir -p %s" % path

def analyse():
	x = xapi.open()
	x.login_with_password("root", "")
	try:
		pool = x.xenapi.pool.get_all()[0]
		pool_r = x.xenapi.pool.get_record(pool)
		default_sr = pool_r["default_SR"]
		try:
			sr_r = x.xenapi.SR.get_record(default_sr)
			print >>sys.stderr, "OK: default SR is set"
		except:
			path = tui.text("Where would you like to store disk images?", "/usr/share/xapi/images")
			hosts = x.xenapi.host.get_all()
			if len(hosts) <> 1:
				print >>sys.stderr, "ERROR: host is already in a pool"
				return
			mkdir(path)
			sr = x.xenapi.SR.create(hosts[0], { "path": path }, "0", path, "Files stored in %s" % path, "ffs", "default", False)
			x.xenapi.pool.set_default_SR(pool, sr)
			x.xenapi.pool.set_suspend_image_SR(pool, sr)
			x.xenapi.pool.set_crashdump_SR(pool, sr)
			print >>sys.stderr, "OK: created default SR"

	finally:
		x.logout()
		xapi.stop()

if __name__ == "__main__":
	analyse()
	
