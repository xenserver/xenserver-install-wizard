#!/usr/bin/env python

import sys, subprocess
import xapi, tui

def mkdir(path):
	x = subprocess.call(["/bin/mkdir", "-p", path])
	if x <> 0:
		print >>sys.stderr, "ERROR: failed to mkdir -p %s" % path

def generate_uuid():
	x = subprocess.Popen(["/usr/bin/uuidgen"], stdout = subprocess.PIPE)
	y = x.communicate()
	ret = x.wait ()
	if ret <> 0:
		print >>sys.stderr, "ERROR: failed to generate a uuid"
        return str(y[0].strip())

def analyse():
	x = xapi.open()
	x.login_with_password("root", "")
	try:
		srs = x.xenapi.SR.get_all_records()
		for sr in srs.keys():
			if srs[sr]["type"] == "ext":
				return
		if not(tui.yesno("Would you like to configure some local storage for openstack?")):
			return
		uuid = generate_uuid ()
		hosts = x.xenapi.host.get_all()
		if len(hosts) <> 1:
			print >>sys.stderr, "ERROR: host is already in a pool"
			return
		path = "/var/run/sr-mount/%s" % uuid
		mkdir(path)
		sr = x.xenapi.SR.introduce(uuid, path, "Files stored in %s" % path, "ext", "default", False, {})
		pbd = x.xenapi.PBD.create({ "host": hosts[0], "SR": sr, "device_config": {"path": path}})
		x.xenapi.PBD.plug(pbd)
		pool = x.xenapi.pool.get_all()[0]
		pool_r = x.xenapi.pool.get_record(pool)
		default_sr = pool_r["default_SR"]
		x.xenapi.pool.set_default_SR(pool, sr)
		print >>sys.stderr, "OK: created local ext SR for openstack"

	finally:
		x.logout()

if __name__ == "__main__":
	analyse()
	
